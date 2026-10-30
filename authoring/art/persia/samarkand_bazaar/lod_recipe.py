"""Source LODs: preserve architectural voids and owner patches; simplify curves first."""
import bpy,bmesh,json
import asset_runner as R
from states_recipe import STATES
from source_checks import tris

def merge(name,objects,col):
 verts=[];faces=[];uvs=[[],[]]
 for o in objects:
  off=len(verts);verts.extend(tuple(v.co) for v in o.data.vertices)
  for p in o.data.polygons:
   faces.append(tuple(i+off for i in p.vertices))
   for k in range(2):uvs[k].extend(tuple(o.data.uv_layers[k].data[i].uv) for i in p.loop_indices)
 first=objects[0];q=R.mesh(name,verts,faces,first['surface'],col,first.get('construction_stage','finish'),first.get('role','architecture'))
 for k in range(2):
  for x,v in zip(q.data.uv_layers[k].data,uvs[k]):x.uv=v
 q['source_parts']=json.dumps([o.name for o in objects]);return q
def build(state,level,target):
 scene=bpy.data.scenes[R.PREFIX[:-1]];c=R.collection(f'{R.PREFIX}{state}_LOD{level}',scene.collection)
 source=list(bpy.data.collections[R.PREFIX+state+'_LOD0'].all_objects);base=tris(source);omitted=[];groups={};debris_index=0
 for o in source:
  if o.type!='MESH':continue
  skip=o.get('role') in ('roof_relief','surface_wear')
  if level==2:
   if o.get('role')=='debris' and 'Rubble' in o.name:
    debris_index+=1;skip=skip or debris_index%2==0
   skip=skip or (o.get('role')=='trim' and o.get('surface') in ('ink','carving'))
  if skip:omitted.append(o.name);continue
  flexible=o.get('role') not in ('architecture','ground','owner')
  if state=='ruins':flexible=o.get('role') not in ('ground','owner')
  groups.setdefault((o['surface'],o.get('role'),o.get('construction_stage'),flexible),[]).append(o)
 fixed=sum(tris(v) for k,v in groups.items() if not k[3]);flex=sum(tris(v) for k,v in groups.items() if k[3])
 ratio=max(.045,min(1,(base*target-fixed)/max(flex,1)))
 for i,(key,obs) in enumerate(groups.items()):
  q=merge(f'{state}_LOD{level}__{i:02}_{key[0]}_{key[1]}',obs,c)
  if key[3] and ratio<1:
   mod=q.modifiers.new('Source curve/detail reduction','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
   with bpy.context.temp_override(object=q,active_object=q,selected_objects=[q],selected_editable_objects=[q]):bpy.ops.object.modifier_apply(modifier=mod.name)
   R.retile_surface(q)
  q['lod_level']=level;q['source_state']=state;q['structure_preserved']=not key[3]
 actual=tris(c.all_objects)
 row={'state':state,'level':level,'base_triangles':base,'triangles':actual,'ratio':actual/base,'target_ratio':target,'fixed_triangles':fixed,'curve_detail_ratio':ratio,'omitted_secondary_parts':omitted}
 print('LOD',state,level,actual,round(actual/base,4));return row
def all_lods():
 rows=[]
 for state in STATES:
  for level,target in ((1,.5),(2,.25)):rows.append(build(state,level,target))
 (R.ROOT/'evidence/lod-budget.json').write_text(json.dumps(rows,indent=2)+'\n');R.show_state();return rows
