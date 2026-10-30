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
 for i in range(4):
  rows.append(contact('paving to crossing '+str(i),'PavingPlate','CrossingArch'+str(i)))
 rows.append(contact('drum to central dome','OctagonalDomeBearing','CentralTradingDome'))
 for arm in range(4):
  for side in (-1,1):
   for depth in (0,1):
    n=f'Arm{arm}Shop{side}Room{depth}';rows.append(contact('shop wall bearing '+n,n+'Side3.985',n+'Roof'))
 for n in ('TextileStall','GoodsStall','WeighingDesk'):
  for sx in (-1,1):
   for sy in (-1,1):rows.append(contact('paving to canopy post','PavingPlate',n+f'Post{sx}{sy}'))
  for sx in (-1,1):
   rows.append(contact('post to canopy end bar',n+f'Post{sx}1',n+f'EndBar{sx}'))
   # The ridge end and its end bar overlap in XYZ, rather than hanging in cloth.
   a,b=R.bounds(bpy.data.objects[R.PREFIX+n+'Ridge']);c,d=R.bounds(bpy.data.objects[R.PREFIX+n+f'EndBar{sx}'])
   overlap=[min(b[i],d[i])-max(a[i],c[i]) for i in range(3)]
   rows.append({'name':'ridge to end bar','parts':[n+'Ridge',n+f'EndBar{sx}'],'overlap_xyz':overlap,'passed':min(overlap)>=-.001})
 out={'passed':all(r['passed'] for r in rows),'interfaces':rows,'note':'Measured source bearing planes; not a native collision or placement test.'}
 (R.ROOT/'evidence/contact-checks.json').write_text(json.dumps(out,indent=2)+'\n');print('CONTACT_CHECKS',out['passed'],len(rows));return out
def write(save=True):
 s=bpy.data.scenes[R.PREFIX[:-1]];result={'schema':1,'asset':R.PREFIX[3:-1],'status':'source_art_complete_native_validation_deferred','hp_thresholds':None,'native_bindings':None,'states':{}}
 for c in s.collection.children:
  if not c.name.startswith(R.PREFIX):continue
  parts=[]
  for o in list(c.all_objects):
   if o.type!='MESH':continue
   parts.append({'name':o.name,'healthy_source':o.get('healthy_source'),'role':o.get('role'),'stage':o.get('construction_stage'),'surface':o.get('surface'),'triangles':tris([o]),'mesh_uv_sha256':fingerprint(o),'collection':o.users_collection[0].name})
  result['states'][c.name]={'parts':parts,'triangles':sum(p['triangles'] for p in parts),'bounds':extent(c.all_objects),'exclusive_with':'every other state/LOD or construction composition'}
 healthy=result['states'][R.PREFIX+'healthy_LOD0']['parts'];finish=result['states'][R.PREFIX+'construct_finish']['parts']
 result['construction_finish_restores_healthy_exactly']={p['name']:p['mesh_uv_sha256'] for p in healthy}=={p['healthy_source']:p['mesh_uv_sha256'] for p in finish}
 assert result['construction_finish_restores_healthy_exactly']
 result['source_dependencies']=[{'path':'textures/'+k+'.png','sha256':hashlib.sha256((R.ROOT/'textures'/(k+'.png')).read_bytes()).hexdigest()} for k in ('albedo','normal','roughness','metalness','owner_mask')]
 if save:(R.ROOT/'state-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print('MANIFEST',len(result['states']),'EXACT_HEALTHY_FINISH',True);return result
