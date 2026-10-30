"""Family-local, surviving-source LODs; only the parent executes Blender.

No healthy geometry is rebuilt after damage. Orthogonal unions retain exact
occupied volume; curved extrusion profiles are sampled from surviving vertices.
The approximately half/quarter targets remain measured gates, not assertions.
"""
import math
import re
import json
import bpy
import bmesh
import state_geometry as G
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform, closest_point_on_tri


def tri(o):
    return sum(len(p.vertices)-2 for p in o.data.polygons)


def bounds(R,o):
    a,b=R.bounds(o)
    return tuple(a),tuple(b)


def inherited(original,new,state,level):
    for k in original.keys():new[k]=original[k]
    new['healthy_source']=original.get('healthy_source',original.name)
    new['source_state']=state;new['lod_level']=level
    return new


def box(R,o):
    if o.get('fracture') or o.get('fracture_cap_vertex_indices') or o.get('retained_native_dependency') or len(o.data.vertices)!=8:return None
    a,b=bounds(R,o)
    if any(b[i]-a[i]<1e-6 for i in range(3)):return None
    if any(any(min(abs((o.matrix_world@v.co)[i]-a[i]),abs((o.matrix_world@v.co)[i]-b[i]))>2e-5 for i in range(3)) for v in o.data.vertices):return None
    return a,b


def orthogonal_surface(boxes):
    """Exact union as a consistently welded closed grid boundary, no bbox fill.

    Greedy rectangular face merging is deliberately avoided: it creates T joins.
    The caller dissolves coplanar topology after the complete manifold exists.
    Quantization is bounded to five micrometres and checked against source bounds.
    """
    axes=[sorted({round(v[i],5) for a,b in boxes for v in (a,b)}) for i in range(3)]
    lookup=[{v:i for i,v in enumerate(a)} for a in axes]
    occupied=set()
    for a,b in boxes:
        spans=[range(lookup[i][round(a[i],5)],lookup[i][round(b[i],5)]) for i in range(3)]
        for x in spans[0]:
            for y in spans[1]:
                for z in spans[2]:occupied.add((x,y,z))
    verts=[];faces=[];indices={}
    def index(v):
        if v not in indices:indices[v]=len(verts);verts.append(tuple(axes[i][v[i]] for i in range(3)))
        return indices[v]
    for cell in sorted(occupied):
        for axis in range(3):
            u,v=[i for i in range(3) if i!=axis]
            for sign in (-1,1):
                neighbor=list(cell);neighbor[axis]+=sign
                if tuple(neighbor) in occupied:continue
                face=[]
                for du,dv in ((0,0),(1,0),(1,1),(0,1)):
                    point=list(cell);point[axis]+=sign>0;point[u]+=du;point[v]+=dv
                    face.append(index(tuple(point)))
                faces.append(tuple(face))
    return verts,faces


def clean_planar(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    try:
        bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,use_dissolve_boundaries=False,
            verts=list(bm.verts),edges=list(bm.edges),delimit=set())
        # Degree-two collinear points on an existing crease are redundant.
        candidates=[]
        for v in bm.verts:
            if len(v.link_edges)!=2:continue
            a,b=[e.other_vert(v).co-v.co for e in v.link_edges]
            if a.length>1e-8 and b.length>1e-8 and a.normalized().dot(b.normalized())<-.9999999:candidates.append(v)
        if candidates:bmesh.ops.dissolve_verts(bm,verts=candidates,use_face_split=False,use_boundary_tear=False)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data)
    finally:bm.free()
    o.data.update()


def combine_boxes(H,key,state,objects,destination,level):
    groups={};used=set();R=H.R
    for o in objects:
        if o.get('role') not in ('architecture','fittings','roofs'):continue
        b=box(R,o)
        if b is None:continue
        signature=(o.get('structural_group',''),o.get('surface',''),o.get('construction_stage',''))
        if not signature[0]:continue
        groups.setdefault(signature,[]).append((o,b))
    for serial,(signature,parts) in enumerate(sorted(groups.items())):
        if len(parts)<2:continue
        # Large coordinate products are not silently materialized in RAM.
        grid=math.prod(len({round(v[i],5) for o,(a,b) in parts for v in (a,b)}) for i in range(3))
        if grid>100000:continue
        verts,faces=orthogonal_surface([b for o,b in parts])
        q=R.mesh(key+'_'+state+'_LOD'+str(level)+'_ExactMembers'+str(serial),verts,faces,
            signature[1],destination,signature[2],'architecture')
        clean_planar(q);R.retile_surface(q)
        before=(tuple(min(b[0][i] for o,b in parts) for i in range(3)),tuple(max(b[1][i] for o,b in parts) for i in range(3)))
        after=bounds(R,q)
        if any(abs(before[j][i]-after[j][i])>2e-5 for j in range(2) for i in range(3)):
            G.remove(q);raise ValueError('Exact member union changed bounds: '+str(signature))
        if tri(q)>=sum(tri(o) for o,b in parts):G.remove(q);continue
        inherited(parts[0][0],q,state,level)
        q['role']='architecture' if any(o.get('role')=='architecture' for o,b in parts) else parts[0][0].get('role')
        q['healthy_source']='SOURCE_UNION|'+key+'|'+state+'|'+str(serial)
        q['lod_source_parts']=json.dumps([o.get('healthy_source',o.name) for o,b in parts])
        q['lod_replacement_basis']='Exact union of present closed orthogonal members, preserving openings, disconnected components and occupied volume; no bounding-box shell'
        used.update(o.name for o,b in parts)
    return used


def profile_loop(o,axis):
    points=[tuple(o.matrix_world@v.co) for v in o.data.vertices]
    levels=sorted({round(p[axis],5) for p in points})
    if len(levels)<2:return None
    uv=[i for i in range(3) if i!=axis]
    sections=[{tuple(round(p[i],5) for i in uv) for p in points if abs(p[axis]-z)<2e-5} for z in levels]
    if len(sections[0])<5 or any(s!=sections[0] for s in sections[1:]):return None
    # Cap mesh may have many quads (vaults); their external edges give its loop.
    cap=[p for p in o.data.polygons if all(abs(points[i][axis]-levels[0])<2e-5 for i in p.vertices)]
    counts={}
    for p in cap:
        for a,b in zip(p.vertices,list(p.vertices[1:])+[p.vertices[0]]):
            edge=tuple(sorted((a,b)));counts[edge]=counts.get(edge,0)+1
    edges=[e for e,n in counts.items() if n==1];adj={}
    for a,b in edges:adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
    if not adj or any(len(a)!=2 for a in adj.values()):return None
    start=min(adj);order=[start];previous=None;current=start
    while True:
        choices=[v for v in adj[current] if v!=previous]
        following=choices[0]
        if following==start:break
        if following in order:return None
        order.append(following);previous,current=current,following
    if len(order)!=len(adj):return None  # Multiple loops: don't seal a hollow eye.
    return uv,levels,[tuple(points[j][i] for i in uv) for j in order]


def reduce_outline(points,level):
    n=len(points);keep=set()
    for axis in (0,1):
        keep.add(min(range(n),key=lambda i:points[i][axis]));keep.add(max(range(n),key=lambda i:points[i][axis]))
    # Sharp corners include original jambs, notches, fracture returns and seats.
    for i,p in enumerate(points):
        u=[p[j]-points[(i-1)%n][j] for j in (0,1)];v=[points[(i+1)%n][j]-p[j] for j in (0,1)]
        a=math.hypot(*u);b=math.hypot(*v)
        if a*b and (u[0]*v[0]+u[1]*v[1])/(a*b)<math.cos(.50):keep.add(i)
    extent=max(max(p[j] for p in points)-min(p[j] for p in points) for j in (0,1))
    tolerance=extent*(.008 if level==1 else .025)
    def split(indices):
        if len(indices)<3:return
        a=points[indices[0]];b=points[indices[-1]];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
        distance=lambda i:abs(dx*(a[1]-points[i][1])-(a[0]-points[i][0])*dy)/length if length else math.dist(a,points[i])
        k=max(range(1,len(indices)-1),key=lambda k:distance(indices[k]))
        if distance(indices[k])>tolerance:keep.add(indices[k]);split(indices[:k+1]);split(indices[k:])
    anchors=sorted(keep)
    for a,b in zip(anchors,anchors[1:]+[anchors[0]+n]):split([i%n for i in range(a,b+1)])
    return [points[i] for i in sorted(keep)]


def source_uv(original,new):
    """Transfer from the actual surviving surface, including fracture atlas tiles.

    Nearest points are clamped to source triangles before barycentric mapping,
    so each generated UV remains within the original source triangle's island.
    A tiny face-interior bias disambiguates coincident arch/cap corner UVs.
    """
    original.data.calc_loop_triangles()
    vertices=[original.matrix_world@v.co for v in original.data.vertices]
    triangles=list(original.data.loop_triangles)
    tree=BVHTree.FromPolygons(vertices,[tuple(t.vertices) for t in triangles],all_triangles=True)
    for p in new.data.polygons:
        center=new.matrix_world@p.center
        for loop in p.loop_indices:
            v=new.matrix_world@new.data.vertices[new.data.loops[loop].vertex_index].co
            probe=v*.999+center*.001
            hit,normal,index,distance=tree.find_nearest(probe)
            if index is None:raise ValueError('Cannot transfer surviving source UV: '+original.name)
            t=triangles[index];a,b,c=[vertices[i] for i in t.vertices]
            point=closest_point_on_tri(probe,a,b,c)
            for layer in new.data.uv_layers:
                src=original.data.uv_layers.get(layer.name) or original.data.uv_layers.active
                if src is None:raise ValueError('Source has no UV layer: '+original.name)
                uv=[Vector((*src.data[i].uv,0.)) for i in t.loops]
                layer.data[loop].uv=barycentric_transform(point,a,b,c,*uv)[:2]


def extrusion(H,key,state,o,destination,level,serial):
    if o.get('retained_native_dependency'):return None
    R=H.R
    for axis in (0,1):
        data=profile_loop(o,axis)
        if data is None:continue
        uv,levels,outline=data;reduced=reduce_outline(outline,level)
        if len(reduced)>=len(outline) and len(levels)==2:continue
        verts=[]
        for z in (levels[0],levels[-1]):
            for p in reduced:
                v=[0.,0.,0.];v[axis]=z;v[uv[0]]=p[0];v[uv[1]]=p[1];verts.append(tuple(v))
        n=len(reduced);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        faces +=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        q=R.mesh(key+'_'+state+'_LOD'+str(level)+'_SurvivingProfile'+str(serial),verts,faces,
            o.get('surface','brick'),destination,o.get('construction_stage','walls'),o.get('role','architecture'))
        if tri(q)>=tri(o):G.remove(q);continue
        source_uv(o,q)
        inherited(o,q,state,level)
        if 'fracture_cap_vertex_indices' in q:del q['fracture_cap_vertex_indices']
        q['lod_replacement_basis']='Coarse profile sampled solely from actual constant-section surviving source; extrema and sharp breach/jamb/seat corners retained, no healthy regeneration'
        return q
    return None


def union_survivors(H,key,state,destination,level):
    """Exact boolean union of already reduced, present support/wall solids.

    This removes internal joining faces in damaged rooms without synthesizing a
    healthy room. Every operand is an actual generated surviving source proxy.
    The owned destination must be evaluated during Boolean application.
    """
    groups={};R=H.R;merged=0
    for o in list(destination.all_objects):
        if o.type!='MESH' or o.get('retained_native_dependency') or o.get('role') not in ('architecture','fittings','roofs'):continue
        signature=(o.get('structural_group',''),o.get('surface',''),o.get('construction_stage',''))
        if signature[0]:groups.setdefault(signature,[]).append(o)
    hidden=destination.hide_viewport;destination.hide_viewport=False
    try:
        bpy.context.view_layer.update()
        for serial,(signature,parts) in enumerate(sorted(groups.items())):
            if len(parts)<2:continue
            before=[bounds(R,o) for o in parts]
            expected=(tuple(min(a[i] for a,b in before) for i in range(3)),tuple(max(b[i] for a,b in before) for i in range(3)))
            count=sum(tri(o) for o in parts)
            q=G.clone(parts[0],destination,'SupportUnion'+str(serial))
            for operand in parts[1:]:G.boolean(q,operand,'UNION')
            if not q.data.polygons:raise ValueError('Surviving support union lost all faces: '+str(signature))
            clean_planar(q)
            after=bounds(R,q)
            if any(abs(expected[j][i]-after[j][i])>2e-5 for j in range(2) for i in range(3)):
                raise ValueError('Surviving support union lost an operand: '+str(signature))
            if tri(q)>=count:G.remove(q);continue
            q['healthy_source']='SURVIVING_SUPPORT_UNION|'+key+'|'+state+'|'+str(serial)
            q['lod_source_parts']=json.dumps([o.get('healthy_source',o.name) for o in parts])
            q['lod_replacement_basis']='Exact union of actual surviving reduced room/support members; internal joining faces dissolved, breach and exterior preserved'
            if 'fracture_cap_vertex_indices' in q:del q['fracture_cap_vertex_indices']
            q['role']='architecture' if any(o.get('role')=='architecture' for o in parts) else parts[0].get('role')
            for o in parts:G.remove(o)
            merged+=1
    finally:destination.hide_viewport=hidden
    return merged


def build_lod(H,key,state,source,destination,level,profile):
    if level not in (1,2) or destination.all_objects:raise ValueError('Fresh LOD1/2 destination required')
    R=H.R;objects=sorted([o for o in source.all_objects if o.type=='MESH'],key=lambda o:o.name)
    omissions=profile.get('lod_omit_name_fragments',{}).get(str(level),[])
    retained=[];debris=0
    joists={}
    for o in objects:
        match=re.search(r'(.*(?:Joist|Rafter))([0-9]+)(?:__|$)',o.name)
        if match and not o.get('retained_native_dependency'):joists.setdefault(match[1],[]).append((int(match[2]),o))
    omitted_joists=set()
    for run in joists.values():
        run.sort();count=len(run);indices={0,count-1,(count-1)//2}
        if level==1:indices|={(count-1)//4,3*(count-1)//4}
        # Only actual source members are retained; never regenerate a missing one.
        omitted_joists.update(o.name for i,(index,o) in enumerate(run) if i not in indices)
    for o in objects:
        if not o.get('retained_native_dependency'):
            if o.get('role') in ('fine_detail','wear') or any(s in o.name for s in omissions) or o.name in omitted_joists:continue
            if o.get('role')=='debris':
                keep='Fallen' in o.name or debris%(3 if level==1 else 9)==0;debris+=1
                if not keep:continue
        retained.append(o)
    consumed=combine_boxes(H,key,state,retained,destination,level)
    for serial,o in enumerate(retained):
        if o.name in consumed:continue
        if not o.get('preserve_custom_source_uv'):
            q=extrusion(H,key,state,o,destination,level,serial)
            if q is not None:continue
        q=G.clone(o,destination,'LOD'+str(level));q['lod_level']=level
        if not o.get('retained_native_dependency'):
            if (o.get('fracture') or o.get('fracture_cap_vertex_indices')) and o.get('role') in ('architecture','roofs','fittings'):
                clean_planar(q)  # Keep every nonplanar fracture crest/breach.
            elif len(q.data.polygons)>24:
                modifier=q.modifiers.new('Family distant curved source','DECIMATE')
                modifier.ratio=.40 if level==1 else .16;modifier.use_collapse_triangulate=True
                with bpy.context.temp_override(object=q,active_object=q,selected_objects=[q],selected_editable_objects=[q]):bpy.ops.object.modifier_apply(modifier=modifier.name)
                if not q.get('preserve_custom_source_uv'):R.retile_surface(q)
    unions=union_survivors(H,key,state,destination,level)
    before=sum(tri(o) for o in objects);after=sum(tri(o) for o in destination.all_objects if o.type=='MESH')
    destination['family_lod_target']=.50 if level==1 else .25
    destination['family_lod_ratio']=after/before if before else 0.
    destination['family_lod_scope']='Actual surviving source profiles/exact orthogonal union; ratio, topology, support and readability require parent qualification'
    return dict(body=key,state=state,lod=level,source_triangles=before,lod_triangles=after,ratio=after/before if before else 0.,surviving_support_unions=unions)
