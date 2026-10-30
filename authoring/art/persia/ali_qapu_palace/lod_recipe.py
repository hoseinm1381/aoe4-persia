"""Source LODs: reconstruct arch curves, retain support planes, simplify details."""
import bpy,bmesh,json,math,re
import asset_runner as R
from states_recipe import STATES
from source_checks import tris
def merge(name,obs,col):
 v=[];f=[];uv=[[],[]]
 for o in obs:
  off=len(v);v.extend(tuple(x.co) for x in o.data.vertices)
  for p in o.data.polygons:
   f.append(tuple(off+i for i in p.vertices))
   for k in range(2):uv[k].extend(tuple(o.data.uv_layers[k].data[i].uv) for i in p.loop_indices)
 q=R.mesh(name,v,f,obs[0]['surface'],col,obs[0].get('construction_stage','finish'),obs[0].get('role','architecture'))
 for k in range(2):
  for a,b in zip(q.data.uv_layers[k].data,uv[k]):a.uv=b
 return q
def arch_proxy(o,name,col,level):
 a=json.loads(o['arch_source']);x,y,z=a['x'],a['y'],a['z'];angle=a['rotate'];fn=None;cx=x;dep=a.get('depth',.4);y0=y-dep/2;y1=y+dep/2
 if angle:
  ca,sa=math.cos(angle),math.sin(angle);fn=lambda xx,yy,zz:(x+xx*ca-yy*sa,y+xx*sa+yy*ca,zz);cx=0;y0=-dep/2;y1=dep/2
 q=R.archwall(name,cx,y0,y1,z,a['w'],a['h'],a['opening'],a['spring'],a['rise'],a['surface'],col,segments=10 if level==1 else 5,transform=fn)
 q['construction_stage']=o.get('construction_stage','walls');return q
def curved_proxy(o,name,col,level):
 key='gable_source' if 'gable_source' in o else 'vault_source';a=json.loads(o[key]);fn=None
 if a['orientation']=='left_front':
  y=a['bay_y'];fn=lambda xx,yy,zz:(-2.25-yy,y+xx,zz)
 elif a['orientation']=='left_roof':
  y=a['bay_y'];fn=lambda xx,yy,zz:(yy,y+xx,zz)
 if key=='gable_source':q=R.gablewall(name,*a['args'],a['surface'],col,segments=10 if level==1 else 5,transform=fn)
 else:q=R.vault(name,*a['args'],a['surface'],col,segments=12 if level==1 else 6,along=2 if level==1 else 1,transform=fn)
 q['construction_stage']=o.get('construction_stage','walls');return q
def build(state,level,target):
 col=R.collection(f'{R.PREFIX}{state}_LOD{level}',bpy.data.scenes[R.PREFIX[:-1]].collection)
 source=[o for o in bpy.data.collections[R.PREFIX+state+'_LOD0'].all_objects if o.type=='MESH'];groups={};temps=[];omitted=[]
 for index,o in enumerate(source):
  role=o.get('role','architecture');name=o.name;skip=role in ('roof_relief','surface_wear')
  if role=='lattice':
   m=re.search(r'Lattice([HV])(\d+)$',name)
   if m:
    axis,n=m.group(1),int(m.group(2));skip=skip or (level==1 and n not in ({0,2,4,6} if axis=='V' else {0,2,4}))
    if level==2:skip=skip or n not in ({3} if axis=='V' else {2})
  if level==2 and role=='wheel_spoke':
   m=re.search(r'Spoke(\d+)$',name);skip=skip or bool(m and int(m.group(1))%2)
  if role=='debris' and 'Rubble' in name:skip=skip or index%(2 if level==1 else 3)!=0
  if skip:omitted.append(name);continue
  if 'arch_source' in o:
   q=arch_proxy(o,f'Proxy{state}_{level}_{index}',col,level);temps.append(q);o=q;role='architecture'
  elif 'gable_source' in o or 'vault_source' in o:
   q=curved_proxy(o,f'Proxy{state}_{level}_{index}',col,level);temps.append(q);o=q;role='architecture'
  flexible=role not in ('architecture','ground','owner','structure','column','column_base','capital','lattice')
  if state=='ruins':flexible=role not in ('ground','owner')
  groups.setdefault((o['surface'],role,o.get('construction_stage','finish'),flexible),[]).append(o)
 base=tris(source);fixed=sum(tris(v) for k,v in groups.items() if not k[3]);flex=sum(tris(v) for k,v in groups.items() if k[3]);ratio=max(.12,min(1,(base*target-fixed)/max(flex,1)))
 for i,(key,obs) in enumerate(groups.items()):
  q=merge(f'{state}_LOD{level}__{i:03}_{key[0]}_{key[1]}',obs,col)
  if key[3] and ratio<1:
   mod=q.modifiers.new('Selective detail reduction','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
   with bpy.context.temp_override(object=q,active_object=q,selected_objects=[q],selected_editable_objects=[q]):bpy.ops.object.modifier_apply(modifier=mod.name)
   R.retile_surface(q)
  q['source_state']=state;q['lod_level']=level;q['source_parts']=json.dumps([x.get('healthy_source',x.name) for x in obs])
 for q in temps:
  me=q.data;bpy.data.objects.remove(q,do_unlink=True)
  if not me.users:bpy.data.meshes.remove(me)
 actual=tris(col.all_objects);row={'state':state,'lod':level,'triangles':actual,'base':base,'ratio':actual/base,'target':target,'fixed':fixed,'omitted':omitted};print('LOD',state,level,actual,round(actual/base,3));return row
def all_lods():
 rows=[build(state,level,target) for state in STATES for level,target in ((1,.5),(2,.25))]
 (R.ROOT/'evidence/lod-budget.json').write_text(json.dumps(rows,indent=2)+'\n');R.show_state();return rows
