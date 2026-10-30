"""Reusable measured source checks. Family anatomy/state policy lives elsewhere."""
import bpy,bmesh,hashlib,struct,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def triangles(objects):return sum(len(p.vertices)-2 for o in objects if o.type=='MESH' for p in o.data.polygons)

def digest(ob):
    def q(x):return round(float(x),5) or 0.0
    vertices=[tuple(q(x) for x in v.co) for v in ob.data.vertices];faces=[]
    for p in ob.data.polygons:
        loops=[vertices[ob.data.loops[i].vertex_index]+tuple(q(x) for layer in ob.data.uv_layers for x in layer.data[i].uv) for i in p.loop_indices]
        faces.append(min(tuple(loops[j:]+loops[:j]) for j in range(len(loops))))
    return hashlib.sha256(json.dumps([sorted(vertices),[l.name for l in ob.data.uv_layers],sorted(faces)],separators=(',',':')).encode()).hexdigest()

def world_points(ob):return [ob.matrix_world@v.co for v in ob.data.vertices]
def bounds(ob):
    vs=world_points(ob)
    return ([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]) if vs else (None,None)

def mesh_report(ob):
    errors=[];native=bool(ob.get('retained_native_dependency'))
    if ob.data.users!=1:errors.append('shared mesh datablock')
    if not native and (any(abs(x)>1e-6 for x in (*ob.location,*ob.rotation_euler)) or any(abs(x-1)>1e-6 for x in ob.scale)):errors.append('unapplied authored transform')
    if abs(ob.matrix_world.determinant())<1e-9:errors.append('singular transform')
    if len(ob.data.uv_layers)<(1 if native else 2):errors.append('missing UV layers')
    for layer in ob.data.uv_layers:
        if any(not all(math.isfinite(v) for v in loop.uv) for loop in layer.data):errors.append('nonfinite UV')
        if not native and any(not all(-1e-4<=v<=1.0001 for v in loop.uv) for loop in layer.data):errors.append('authored atlas UV outside unit tile')
    bm=bmesh.new();bm.from_mesh(ob.data)
    open_edges=sum(not e.is_manifold for e in bm.edges);degenerate=sum(f.calc_area()<1e-10 for f in bm.faces);volume=bm.calc_volume(signed=True)
    if degenerate:errors.append('zero-area face')
    if not native and open_edges:errors.append('open authored solid')
    if not native and any(e.is_manifold and not e.is_contiguous for e in bm.edges):errors.append('inconsistent face winding')
    if not native and volume<=0:errors.append('inward/zero volume')
    bm.free()
    if native and not ob.get('native_source_geometry_sha256'):errors.append('native exception without source provenance')
    return {'object':ob.name,'passed':not errors,'errors':errors,'triangles':triangles([ob]),
        'native_preserved_surface':native and not bool(ob.get('native_derived_LOD')),
        'native_derived_source_surface':bool(ob.get('native_derived_LOD')),
        'nonmanifold_edges':open_edges,'signed_volume':volume}

def contact_report(contract):
    a=bpy.data.objects.get(contract['a']);b=bpy.data.objects.get(contract['b'])
    if a is None or b is None:return {**contract,'passed':False,'error':'missing generated contact object'}
    alo,ahi=bounds(a);blo,bhi=bounds(b);axis=contract.get('axis','bottom-top')
    axes={'bottom-top':(2,False),'top-bottom':(2,True),'right-left':(0,True),'left-right':(0,False),'front-back':(1,False),'back-front':(1,True)}
    if axis not in axes:return {**contract,'passed':False,'error':'unsupported scalar axis; author a measured interface contract'}
    direction,reverse=axes[axis];gap=ahi[direction]-blo[direction] if reverse else alo[direction]-bhi[direction]
    overlap=[min(ahi[i],bhi[i])-max(alo[i],blo[i]) for i in range(3) if i!=direction]
    tol=contract.get('tolerance',.003)
    return {**contract,'measured_gap':gap,'projected_xy_overlap':overlap,'passed':abs(gap-contract.get('target',0))<=tol and min(overlap)>=-tol}

def interface_report(contract):
    """Measure actual generated surface proximity at a named planned joint.

    Distances are explicit diagnostics. They are not a full collision proof.
    A point embedded inside a wide beam is expected to have nonzero distance
    to its surface; the family must state the allowed embed distance.
    """
    point=Vector(contract['authored_contact_point']);rows=[]
    allowed=contract.get('intentional_socket_overlap_metres',0)+contract.get('tolerance',.004)
    for name in [contract['a'],contract['b']]:
        ob=bpy.data.objects.get(name)
        if ob is None:return {**contract,'passed':False,'error':'missing generated interface object '+name}
        tree=BVHTree.FromPolygons(world_points(ob),[tuple(p.vertices) for p in ob.data.polygons])
        nearest=tree.find_nearest(point);distance=nearest[3] if nearest else None
        tolerance=contract.get('tolerance',.004)
        inside=False;intersections=0;bounded=True
        if distance is not None and distance>tolerance:
            direction=Vector((1,.307,.173)).normalized();origin=point.copy()
            for _ in range(64):
                hit=tree.ray_cast(origin,direction)
                if hit[0] is None:break
                intersections+=1;origin=hit[0]+direction*1e-6
            else:bounded=False
            inside=bounded and intersections%2==1
        passed=distance is not None and (distance<=tolerance or (inside and distance<=allowed))
        rows.append({'object':name,'point_surface_distance':distance,'allowed_intentional_embed':allowed,'surface_tolerance':tolerance,'point_inside_closed_surface':inside,'ray_intersections':intersections,'ray_bounded':bounded,'passed':passed})
    return {**contract,'generated_surface_measurements':rows,'passed':all(r['passed'] for r in rows)}

def composition_report(collection,envelope=None,cap=None):
    obs=[o for o in collection.all_objects if o.type=='MESH'];points=[p for o in obs for p in world_points(o)]
    lo=[min(p[i] for p in points) for i in range(3)] if points else None
    hi=[max(p[i] for p in points) for i in range(3)] if points else None
    count=triangles(obs);errors=[]
    if not obs:errors.append('empty composition')
    if cap is not None and count>cap:errors.append('stock compound triangle cap exceeded')
    if envelope and lo and any(lo[i]<envelope['min'][i]-1e-5 or hi[i]>envelope['max'][i]+1e-5 for i in range(3)):errors.append('verified source envelope exceeded')
    return {'collection':collection.name,'parts':len(obs),'triangles':count,'bounds_min':lo,'bounds_max':hi,'passed':not errors,'errors':errors}
