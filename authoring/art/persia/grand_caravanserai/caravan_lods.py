"""Silhouette-aware reduced sources with baked simplification and original shared atlas."""
import bpy,bmesh,json,math
import asset_runner as R
from caravan_states import STATES,remove
def tris(obs):return sum(len(p.vertices)-2 for o in obs if o.type=='MESH' for p in o.data.polygons)
def merge(name,objects,col):
    vs=[];fs=[];uvs=[[],[]]
    for ob in objects:
        offset=len(vs);vs +=[tuple(v.co) for v in ob.data.vertices]
        for p in ob.data.polygons:
            fs.append(tuple(offset+i for i in p.vertices))
            for k in range(2):uvs[k] +=[tuple(ob.data.uv_layers[k].data[i].uv) for i in p.loop_indices]
    a=objects[0];o=R.mesh(name,vs,fs,a.get('surface','brick'),col,a.get('construction_stage','walls'),a.get('role','architecture'))
    for k in range(2):
        for v,uv in zip(o.data.uv_layers[k].data,uvs[k]):v.uv=uv
    o['source_parts']=json.dumps([x.name for x in objects]);return o
def build(state,level):
    base=bpy.data.collections[R.PREFIX+state+'_LOD0'];obs=[o for o in base.all_objects if o.type=='MESH'];count=tris(obs);target=.5 if level==1 else .25
    dest=R.collection(R.PREFIX+state+'_LOD'+str(level),bpy.data.scenes['PS_Caravanserai'].collection)
    selected=[];omitted=[]
    debris_index=0
    for o in obs:
        role=o.get('role');n=o.name
        skip=role=='roof_detail' or level==2 and role in ('brick_detail','surface_wear')
        if level==2 and ('Paving_' in n or 'OuterFooting' in n):skip=True
        if state=='ruins' and role=='debris' and 'Masonry' in n:
            debris_index+=1;skip=debris_index%(2 if level==1 else 4)!=0
        if skip:omitted.append(n)
        else:selected.append(o)
    def flexible(o):
        if o.get('role') in ('owner','ground') or o.get('surface')=='owner':return False
        # Keep wall/arch opening planes and their original brick UV islands intact.
        # Their geometry is cheap; simplifying it causes visible atlas interpolation.
        if o.get('role')=='architecture' and 'Buttress' not in o.name:return False
        # Small loose solids are already economical and can contain equal-cost
        # collapse choices. Keep cargo intact; keep rubble blocks intact while
        # reducing their number above. Only larger curved debris remains flexible.
        if o.get('role')=='cargo':return False
        if o.get('role')=='debris' and len(o.data.polygons)<=12:return False
        return len(o.data.polygons)>12 or len(o.data.vertices)>24 or o.get('role') in ('debris','vaults','cargo')
    fixed=tris([o for o in selected if not flexible(o)]);flex=tris([o for o in selected if flexible(o)])
    ratio=max(.025,min(1,(count*target-fixed)/max(1,flex)))
    groups={}
    for o in selected:groups.setdefault((o.get('surface'),o.get('role'),o.get('construction_stage'),flexible(o)),[]).append(o)
    for i,(key,items) in enumerate(groups.items()):
        ob=merge(state+f'_LOD{level}__{i:02}_{key[0]}_{key[1]}',items,dest)
        if key[3] and ratio<1:
            mod=ob.modifiers.new('Source simplification - baked','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
            with bpy.context.temp_override(object=ob,active_object=ob,selected_objects=[ob],selected_editable_objects=[ob]):bpy.ops.object.modifier_apply(modifier=mod.name)
            # Preserve carried atlas UVs, including healthy fixed brick density.
            # Bound numerical decimator extrapolation to this group's source tile.
            k=R.TILES.index(ob.get('surface','brick'));tx=k%4;ty=3-k//4
            for layer in ob.data.uv_layers:
                for loop in layer.data:loop.uv=(min((tx+.96)/4,max((tx+.04)/4,loop.uv.x)),min((ty+.96)/4,max((ty+.04)/4,loop.uv.y)))
            # Simplified loose cargo/debris receive deterministic local UVs. Their
            # decimator-carried near-tie UVs differ slightly between fresh processes.
            # Structural masonry and owner areas retain their unchanged source UVs.
            if key[1] in ('cargo','debris'):R.retile_surface(ob)
        ob['lod_level']=level;ob['source_state']=state;ob['structural_planes_retained']=not key[3]
    if level==2:
        q=R.block(state+'_LOD2__SimplifiedPaving',(0,-.30,.22),(2.42,8.1,.035),'stone',dest,'finish','ground');q['source_parts']='Fine courtyard pavers; central route retained as one closed plate'
    actual=tris(dest.all_objects)
    result={'state':state,'level':level,'base':count,'triangles':actual,'ratio':actual/count,'target':target,'flexible_ratio':ratio,'fixed_triangles':fixed,'omitted_parts':omitted}
    print('LOD',state,level,actual,round(actual/count,4));return result
def all_lods():
    rows=[build(s,l) for s in STATES for l in [1,2]]
    (R.ROOT/'evidence/lod-budget.json').write_text(json.dumps(rows,indent=2)+'\n');R.show_state();return rows
