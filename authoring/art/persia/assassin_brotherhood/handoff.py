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
 for side in (-1,1):
  for i in range(3):rows.append(contact('footing to curtain',f'CurtainFooting{side}',f'Curtain{side}_{i}'))
 rows.append(contact('paving to main gate','CourtPaving','GuardedGateway'))
 rows.append(contact('command wall to roof','CommandRear','CommandRoof'))
 rows.append(contact('roof to dome bearing','CommandRoof','CommandDomeBearing'))
 rows.append(contact('dome bearing to dome','CommandDomeBearing','LowCommandDome'))
 for x in (-2.24,-1.43):
  for y in (-.55,.36):
   rows.append(contact('roof to watch post','CommandRoof','WatchPost'+str(x)+str(y)))
   rows.append(contact('post to watch canopy','WatchPost'+str(x)+str(y),'WatchCanopy'))
 for x in (.86,1.84):rows.append(contact('paving to cistern post','CourtPaving','CisternPost'+str(x)))
 rows.append(contact('paving to cistern head','CourtPaving','CisternHead'))
 for x in (-1.25,-.50):
  rows.append(contact('paving to archive desk leg','CourtPaving','ArchiveDeskLeg'+str(x)))
  rows.append(contact('desk leg to desk','ArchiveDeskLeg'+str(x),'ArchiveDesk'))
 rows.append(contact('desk to ledger','ArchiveDesk','ArchiveLedger'))
 for i in range(4):rows.append(contact('desk to scroll','ArchiveDesk','ArchiveScroll'+str(i)))
 # Turning path is checked at its actual shared tread/landing planes.
 rows.append(contact('lower stair to landing top','LowerFlight','TurningLanding'))
 # Above test is a stacked-plane formula and not applicable to coplanar treads;
 # replace it with measured top elevation continuity and shared XY footprint.
 rows.pop()
 def top(name):return R.bounds(bpy.data.objects[R.PREFIX+name])[1][2]
 rows += [{'name':'lower flight landing datum','signed_gap':top('TurningLanding')-top('LowerFlight'),'passed':abs(top('TurningLanding')-top('LowerFlight'))<.001},
          {'name':'upper flight threshold datum','signed_gap':top('GateThreshold')-top('UpperFlight'),'passed':0<=top('GateThreshold')-top('UpperFlight')<.015}]
 for first,second,axis in [('LowerFlight','TurningLanding',0),('TurningLanding','UpperFlight',1),('UpperFlight','GateThreshold',1)]:
  a,b=R.bounds(bpy.data.objects[R.PREFIX+first]);c,d=R.bounds(bpy.data.objects[R.PREFIX+second]);gap=c[axis]-b[axis]
  rows.append({'name':'turning path edge continuity','parts':[first,second],'axis':axis,'signed_gap':gap,'passed':-.25<=gap<=.015})
 for owner,rod in [('CommandOwner','CommandBannerRod'),('WatchOwner','WatchBannerRod')]+[(f'GateOwner{side}',f'GateBannerRod{side}') for side in (-1,1)]:rows.append(contact('cloth to support rod',owner,rod))
 healthy=bpy.data.collections[R.PREFIX+'healthy_LOD0'];low,high=extent(healthy.all_objects);rock=R.bounds(bpy.data.objects[R.PREFIX+'LowRockTerrace'])[1][2]
 rows.append({'name':'rock height limit','ratio':rock/high[2],'maximum':.15,'passed':rock/high[2]<=.15})
 out={'passed':all(r['passed'] for r in rows),'interfaces':rows,'note':'Numerical source interfaces; native placement and walkability remain deferred.'}
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
