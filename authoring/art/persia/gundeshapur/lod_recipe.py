"""Reduced-detail sources; shared atlas, single-user meshes, baked transforms."""
import bpy,bmesh,json,math
import asset_runner as R
from states_recipe import STATES

def tris(objects):return sum(len(p.vertices)-2 for o in objects if o.type=='MESH' for p in o.data.polygons)

def heal_closed_loops():
    rows=[]
    for ob in bpy.data.scenes['PS_Gundeshapur'].objects:
        if ob.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(ob.data)
        before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges)
        if before!=len(bm.verts):bm.to_mesh(ob.data);ob.data.update()
        if boundary or nonmanifold:rows.append({'object':ob.name,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold})
        bm.free()
    (R.ROOT/'evidence/topology-diagnostics.json').write_text(json.dumps(rows,indent=2))
    print('OPEN_TOPOLOGY',len(rows))

def merged_group(name,objects,col):
    vertices=[];faces=[];uvs=[[],[]]
    for ob in objects:
        off=len(vertices);vertices.extend(tuple(v.co) for v in ob.data.vertices)
        for p in ob.data.polygons:
            faces.append(tuple(off+i for i in p.vertices))
            for k in range(2):uvs[k].extend(tuple(ob.data.uv_layers[k].data[i].uv) for i in p.loop_indices)
    first=objects[0];ob=R.mesh(name,vertices,faces,first.get('surface','plaster'),col,first.get('construction_stage','walls'),first.get('role','architecture'))
    for k in range(2):
        for a,uv in zip(ob.data.uv_layers[k].data,uvs[k]):a.uv=uv
    ob['source_parts']=json.dumps([o.name for o in objects]);return ob

def build(state,level,target):
    scene=bpy.data.scenes['PS_Gundeshapur'];col=R.collection(R.PREFIX+state+'_LOD'+str(level),scene.collection)
    source=[o for o in bpy.data.collections[R.PREFIX+state+'_LOD0'].all_objects if o.type=='MESH'];base=tris(source)
    obs=[];omitted=[]
    for o in source:
        n=o.name
        skip=any(x in n for x in ('RoofRibs','ClayTileCourses','HallRoofCourse','HallRearRoofCourse','BasketWeave'))
        if level==2:
            skip=skip or o.get('role')=='surface_wear' or (o.get('role')=='trim' and o.get('surface') in ('ink','timber','carving')) or o.get('surface')=='grime'
        if state=='ruins' and level==2 and 'CourtPaving' in n:
            lo,hi=R.bounds(o);o=R.block(state+'_LOD2__SimplifiedCourtPaving',[(lo[i]+hi[i])/2 for i in range(3)],[hi[i]-lo[i] for i in range(3)],'stone',col,'foundation','ground');o['source_parts']='CourtPaving; relief simplified to a closed ground plate'
        if skip:omitted.append(n)
        else:obs.append(o)
    def flexible(o):
        if state=='ruins':return o.get('role')=='debris'
        return o.get('surface') in ('roof','pottery','leaves','cloth') and o.get('role')!='owner'
    fixed=tris([o for o in obs if not flexible(o)]);flex=tris([o for o in obs if flexible(o)])
    ratio=max(.035,min(1,(base*target-fixed)/max(flex,1)))
    groups={}
    for o in obs:groups.setdefault((o.get('surface'),o.get('role'),o.get('construction_stage'),flexible(o)),[]).append(o)
    # The temporary plate is copied into a final named group before removal.
    temporary=[o for o in obs if o.name.startswith(R.PREFIX+state+'_LOD2__SimplifiedCourtPaving')]
    for i,(key,values) in enumerate(groups.items()):
        ob=merged_group(state+f'_LOD{level}__{i:02}_{key[0]}_{key[1]}',values,col)
        if key[3] and ratio<1:
            mod=ob.modifiers.new('Baked curved/detail simplification','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
            with bpy.context.temp_override(object=ob,active_object=ob,selected_objects=[ob],selected_editable_objects=[ob]):bpy.ops.object.modifier_apply(modifier=mod.name)
            from states_recipe import reproject
            reproject(ob)
        ob['lod_level']=level;ob['source_state']=state;ob['preserved_structure']=not key[3]
    from states_recipe import remove
    for o in temporary:remove(o)
    actual=tris(col.all_objects)
    print('LOD',state,level,actual,round(actual/base,4))
    return {'state':state,'level':level,'base':base,'triangles':actual,'ratio':actual/base,'requested':target,'structural_triangles_preserved':fixed,'detail_ratio':ratio,'omitted_secondary_parts':omitted}

def all_lods():
    rows=[]
    for state in STATES:
        for level,target in ((1,.5),(2,.25)):rows.append(build(state,level,target))
    (R.ROOT/'evidence/lod-budget.json').write_text(json.dumps(rows,indent=2)+'\n')
    R.show_state();return rows
