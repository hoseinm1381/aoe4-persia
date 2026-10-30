"""Editable closed-solid state operations, independent of family architecture.

Adapted from this task's qualified House operations. Family profiles choose the
actual failure bay, retained fabric and debris area. These helpers do not invent
native thresholds, animations or selection behavior.
"""
import bpy,bmesh,random,math

def remove(ob):
    me=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
    if not me.users:bpy.data.meshes.remove(me)

def clone(ob,collection,suffix):
    q=ob.copy();q.data=ob.data.copy();q.name=ob.name+'__'+suffix;q.data.name=q.name+'_mesh';collection.objects.link(q)
    q['healthy_source']=ob.get('healthy_source',ob.name);q['source_state']=suffix
    return q

def project_caps(R,ob,indices,surface):
    tile=R.TILES.index(surface);tx=tile%4;ty=3-tile//4
    for p in ob.data.polygons:
        if p.index not in indices:continue
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        points=[ob.data.vertices[ob.data.loops[i].vertex_index].co for i in p.loop_indices]
        low=[min(v[a] for v in points) for a in axes];scale=max(2.,*(max(v[a] for v in points)-low[j] for j,a in enumerate(axes)))
        for li,v in zip(p.loop_indices,points):
            uv=((tx+.04+.92*(v[axes[0]]-low[0])/scale)/4,(ty+.04+.92*(v[axes[1]]-low[1])/scale)/4)
            for layer in ob.data.uv_layers:layer.data[li].uv=uv

def cut(R,ob,point,normal,surface=None):
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
    boundary=[e for e in bm.edges if e.is_boundary]
    caps=bmesh.ops.holes_fill(bm,edges=boundary,sides=0).get('faces',[]) if boundary else []
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.faces.index_update();bm.verts.index_update();cap_indices={f.index for f in caps if f.is_valid}
    cap_vertices=sorted({v.index for f in caps if f.is_valid for v in f.verts})
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    if not ob.data.polygons:remove(ob);return None
    ob['fracture_cap_vertex_indices']=cap_vertices
    project_caps(R,ob,cap_indices,surface or ob.get('surface','brick'))
    return ob

def boolean(ob,operand,operation):
    bpy.context.view_layer.update()
    mod=ob.modifiers.new('Owned editable fracture','BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=operand
    if 'material_mode' in mod.bl_rna.properties:mod.material_mode='INDEX'
    with bpy.context.temp_override(object=ob,active_object=ob,selected_objects=[ob],selected_editable_objects=[ob]):bpy.ops.object.modifier_apply(modifier=mod.name)

def corner_cutter(R,collection,name,corner,extent):
    """Connected unequal masonry losses extending outward from +X,-Y corner."""
    cx,cy,top=corner;e=extent;parts=[]
    for j,(xa,yb,za) in enumerate([(cx-e*.55,cy+e*.48,top-e*.95),(cx-e*.95,cy+e*.235,top-e*.37),(cx-e*.235,cy+e*.8,top-e*.54)]):
        xb=cx+e*.6;ya=cy-e*.6;zb=top+e
        ob=R.block(name+str(j),((xa+xb)/2,(ya+yb)/2,(za+zb)/2),(xb-xa,yb-ya,zb-za),'brick',collection)
        ob.data.materials.append(R.material())
        for p in ob.data.polygons:p.material_index=1
        ob.hide_render=True;parts.append(ob)
    q=parts[0]
    for other in parts[1:]:boolean(q,other,'UNION');remove(other)
    return q

def subtract(R,ob,cutter,fracture_surface=None):
    a,A=R.bounds(ob);b,B=R.bounds(cutter)
    if any(min(A[i],B[i])-max(a[i],b[i])<=1e-6 for i in range(3)):return ob
    ob.data.materials.append(R.material());boolean(ob,cutter,'DIFFERENCE')
    if not ob.data.polygons:remove(ob);return None
    surface=ob.get('surface','brick');core=fracture_surface or ('brick' if surface=='plaster' else 'rubble' if surface in ['roof','stone'] else surface)
    project_caps(R,ob,{p.index for p in ob.data.polygons if p.material_index==1},core)
    for p in ob.data.polygons:p.material_index=0
    while len(ob.data.materials)>1:ob.data.materials.pop(index=len(ob.data.materials)-1)
    ob['fracture']='Three unequal connected losses, family-specific failed bay'
    return ob

def broken_cap(ob,seed):
    rr=random.Random(seed);bm=bmesh.new();bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    hi=max(v.co.z for v in bm.verts);lo=min(v.co.z for v in bm.verts);h=hi-lo;amp=min(.13,h*.2)
    marked=ob.get('fracture_cap_vertex_indices',[])
    if 'fracture_cap_vertex_indices' in ob and not marked:
        bm.free();return  # An uncut surviving support has no exposed fracture cap.
    top=[bm.verts[i] for i in marked] if marked else [v for v in bm.verts if v.co.z>hi-min(.1,h*.2)]
    top_set=set(top)
    # A cut through an arcade can leave a very thin band above its opening.
    # Bound the new relief by that actual band, and use a continuous XY field:
    # neighboring cap points cannot leap past the unchanged inner surface.
    clearances=[v.co.z-e.other_vert(v).co.z for v in top for e in v.link_edges
                if e.other_vert(v) not in top_set and v.co.z-e.other_vert(v).co.z>1e-6]
    if clearances:amp=min(amp,min(clearances)*.18)
    phase=rr.uniform(0,math.tau)
    for v in top:v.co.z+=amp*(.3*math.sin(v.co.x*2.3+phase)+.25*math.cos(v.co.y*2.7-phase)-.43)
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if all(v in top for v in f.verts)])
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()

def rubble(R,collection,name,area,ground,count,seed,scale=1):
    rr=random.Random(seed);lo,hi=area
    for j in range(count):
        w,d,h=rr.uniform(.11,.25)*scale,rr.uniform(.09,.23)*scale,rr.uniform(.055,.17)*scale
        x=rr.uniform(lo[0]+w/2,hi[0]-w/2);y=rr.uniform(lo[1]+d/2,hi[1]-d/2)
        vertices=[(x+sx*w/2,y+sy*d/2,ground) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        vertices +=[(x+sx*w*.39,y+sy*d*.39,ground+h*rr.uniform(.65,1)) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        ob=R.mesh(name+str(j),vertices,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'rubble',collection,'finish','debris')
        ob['collapse_source']='Family profile masonry/roof bay';ob['ground_plane']=ground

def simplify(R,source,destination,level,profile):
    """Preserve structural solids; reduce curved meshes and authored fine props.

    Actual ratios are measured afterward. A low-poly solid is never collapsed
    merely to hit a ratio: family review may require a dedicated replacement.
    """
    omissions=profile.get('lod_omit_name_fragments',{}).get(str(level),[])
    for index,ob in enumerate(sorted(source.all_objects,key=lambda o:o.name)):
        if ob.type!='MESH':continue
        role=ob.get('role')
        if role in ['fine_detail','wear'] or any(s in ob.name for s in omissions):continue
        if role=='debris' and index%(3 if level==1 else 7):continue
        q=clone(ob,destination,'LOD'+str(level));q['lod_level']=level
        if len(q.data.polygons)>24 and not q.get('retained_native_dependency'):
            mod=q.modifiers.new('Curved source reduction','DECIMATE');mod.ratio=.48 if level==1 else .20;mod.use_collapse_triangulate=True
            with bpy.context.temp_override(object=q,active_object=q,selected_objects=[q],selected_editable_objects=[q]):bpy.ops.object.modifier_apply(modifier=mod.name)
            if not q.get('preserve_custom_source_uv'):R.retile_surface(q)
