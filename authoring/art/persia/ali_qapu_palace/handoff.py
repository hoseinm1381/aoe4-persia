"""Record exact source states, restoration, dependencies and numeric contacts."""
from pathlib import Path
import bpy,json,hashlib
import asset_runner as R
from source_checks import fingerprint,tris,extent

def contact(name,lower,upper,axis=2,tolerance=.035):
 a,b=R.bounds(bpy.data.objects[R.PREFIX+lower]);c,d=R.bounds(bpy.data.objects[R.PREFIX+upper]);gap=c[axis]-b[axis]
 return {'name':name,'lower':lower,'upper':upper,'axis':axis,'signed_gap':gap,'allowed_gap':tolerance,'passed':gap<=tolerance and gap>=-.25}
def contacts():
 rows=[]
 for pair in json.loads((R.ROOT/'anchors.json').read_text())['contacts']:
  rows.append(contact(pair['name'],pair['lower'],pair['upper'],pair.get('axis',2),pair.get('tolerance',.015)))
 out={'passed':all(r['passed'] for r in rows),'interfaces':rows,'note':'Measured authored bearing planes; not native collision/placement proof.'}
 (R.ROOT/'evidence/contact-checks.json').write_text(json.dumps(out,indent=2)+'\n');print('CONTACT_CHECKS',out['passed'],len(rows));return out

def material_contract():
 m=R.material();nodes=[]
 def scalar(v):
  if isinstance(v,(float,int,str,bool)):return v
  try:return [float(x) for x in v]
  except TypeError:return None
 for n in sorted(m.node_tree.nodes,key=lambda x:x.name):
  row={'name':n.name,'type':n.bl_idname,'inputs':{},'outputs':{}}
  for k in ('blend_type','operation','space','interpolation'):
   if hasattr(n,k):row[k]=getattr(n,k)
  for label,sockets in [('inputs',n.inputs),('outputs',n.outputs)]:
   for socket in sockets:
    if hasattr(socket,'default_value'):
     val=scalar(socket.default_value)
     if val is not None:row[label][socket.identifier]=val
  if hasattr(n,'image') and n.image:
   row['image']={'name':n.image.name,'colour_space':n.image.colorspace_settings.name,'size':list(n.image.size)}
  nodes.append(row)
 links=sorted((x.from_node.name,x.from_socket.identifier,x.to_node.name,x.to_socket.identifier) for x in m.node_tree.links)
 data={'nodes':nodes,'links':links};data['sha256']=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest();return data

def write(save=True):
 s=bpy.data.scenes[R.PREFIX[:-1]];result={'schema':1,'asset':R.PREFIX[3:-1],'status':'source_art_complete_native_validation_deferred','hp_thresholds':None,'native_bindings':None,'states':{}}
 for c in s.collection.children:
  if not c.name.startswith(R.PREFIX):continue
  parts=[]
  for o in list(c.all_objects):
   if o.type!='MESH':continue
   parts.append({'name':o.name,'healthy_source':o.get('healthy_source'),'role':o.get('role'),'stage':o.get('construction_stage'),'surface':o.get('surface'),'triangles':tris([o]),'mesh_uv_sha256':fingerprint(o),'collection':o.users_collection[0].name,'materials':[m.name for m in o.data.materials]})
  result['states'][c.name]={'parts':parts,'triangles':sum(p['triangles'] for p in parts),'bounds':extent(c.all_objects),'exclusive_with':'every other state/LOD or construction composition'}
 healthy=result['states'][R.PREFIX+'healthy_LOD0']['parts'];finish=result['states'][R.PREFIX+'construct_finish']['parts']
 result['construction_finish_restores_healthy_exactly']={p['name']:p['mesh_uv_sha256'] for p in healthy}=={p['healthy_source']:p['mesh_uv_sha256'] for p in finish}
 assert result['construction_finish_restores_healthy_exactly']
 result['material_contract']=material_contract()
 result['source_dependencies']=[{'path':'textures/'+k+'.png','sha256':hashlib.sha256((R.ROOT/'textures'/(k+'.png')).read_bytes()).hexdigest()} for k in ('albedo','normal','roughness','metalness','owner_mask')]
 if save:(R.ROOT/'state-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print('MANIFEST',len(result['states']),'EXACT_HEALTHY_FINISH',True);return result
