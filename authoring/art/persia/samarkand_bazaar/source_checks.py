"""Independent geometry, dependencies, bounds and lifecycle-source acceptance."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,struct
import asset_runner as R
from mathutils import Vector
from mathutils.bvhtree import BVHTree
STATES=['healthy']+[f'damage_{i}' for i in range(1,6)]+['ruins']

def tris(obs):return sum(len(p.vertices)-2 for o in obs if o.type=='MESH' for p in o.data.polygons)
def fingerprint(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for layer in o.data.uv_layers:
  for x in layer.data:h.update(struct.pack('<2f',*x.uv))
 return h.hexdigest()
def extent(obs):
 vs=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices]
 return ([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]) if vs else ([],[])
def run(complete=True,report_name=None):
 errors=[];rows=[];semantics={};scene=bpy.data.scenes.get(R.PREFIX[:-1]);cap=json.loads((R.ROOT/'evidence/stock-budget.json').read_text())['budget']['cap']
 fit=json.loads((R.ROOT/'evidence/fit-contract.json').read_text());lo,hi=fit['bounds_min'],fit['bounds_max']
 if not scene:errors.append('asset scene missing')
 expected=STATES if complete else ['healthy']
 allobs=[]
 for state in expected:
  for lod in (range(3) if complete else [0]):
   name=f'{R.PREFIX}{state}_LOD{lod}';c=bpy.data.collections.get(name)
   if not c:errors.append('missing '+name);continue
   obs=[o for o in c.all_objects if o.type=='MESH'];a,b=extent(obs);n=tris(obs)
   if not obs:errors.append('empty '+name);continue
   if n>cap:errors.append('triangle cap '+name)
   if a[0]<lo[0]-.001 or b[0]>hi[0]+.001 or a[1]<lo[1]-.001 or b[1]>hi[1]+.001 or b[2]>hi[2]+.001:errors.append('measured envelope '+name)
   rows.append({'state':state,'lod':lod,'triangles':n,'objects':len(obs),'bounds_min':a,'bounds_max':b})
   allobs+=obs
 if complete:
  for state in STATES:
   base=next((x['triangles'] for x in rows if x['state']==state and x['lod']==0),0)
   for level,target in ((1,.5),(2,.25)):
    row=next((x for x in rows if x['state']==state and x['lod']==level),None)
    if row and base and abs(row['triangles']/base-target)>.10:errors.append('LOD target ratio '+state+'/'+str(level))
  for stage in ('foundation','walls','vaults','finish'):
   c=bpy.data.collections.get(R.PREFIX+'construct_'+stage)
   if not c:errors.append('missing construction '+stage)
   else:allobs.extend(o for o in c.all_objects if o.type=='MESH')
  healthy=bpy.data.collections.get(R.PREFIX+'healthy_LOD0');finish=bpy.data.collections.get(R.PREFIX+'construct_finish')
  if healthy and finish:
   expected={o.name:fingerprint(o) for o in healthy.all_objects if o.type=='MESH'}
   actual={o.get('healthy_source'):fingerprint(o) for o in finish.all_objects if o.type=='MESH'}
   if expected!=actual:errors.append('construction finish not exact healthy')
  healthy=next((r for r in rows if r['state']=='healthy' and r['lod']==0),None)
  ruin=next((r for r in rows if r['state']=='ruins' and r['lod']==0),None)
  if healthy and ruin and ruin['bounds_max'][2]>healthy['bounds_max'][2]*.30+.001:errors.append('ruin height >30% including rock')
 for o in set(allobs):
  if o.data.users!=1:errors.append('shared mesh '+o.name)
  if len(o.users_collection)!=1:errors.append('ambiguous collection '+o.name)
  if len(o.data.uv_layers)!=2:errors.append('UV0/UV1 '+o.name)
  if any(abs(x)>1e-6 for x in o.location) or any(abs(x)>1e-6 for x in o.rotation_euler) or any(abs(x-1)>1e-6 for x in o.scale):errors.append('unapplied transform '+o.name)
  if not o.data.materials:errors.append('missing material '+o.name)
  if any(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices):errors.append('nonfinite vertex '+o.name)
  if any(p.area<1e-11 for p in o.data.polygons):errors.append('degenerate face '+o.name)
  for layer in o.data.uv_layers:
   if any(not all(math.isfinite(x) and -.0001<=x<=1.0001 for x in t.uv) for t in layer.data):errors.append('invalid UV '+o.name);break
  bm=bmesh.new();bm.from_mesh(o.data)
  if any(not e.is_manifold for e in bm.edges):errors.append('nonmanifold '+o.name)
  if bm.calc_volume(signed=True)<-1e-8:errors.append('inward volume '+o.name)
  bm.free()
  if 'Brotherhood' in R.PREFIX and o.get('role')=='curved_structure':
   if any(p.normal.z>.8 and (p.center.x-2.12)**2+(p.center.y-.47)**2<.40**2 for p in o.data.polygons):errors.append('lookout aperture capped across hollow centre '+o.name)
 for kind in ('albedo','normal','roughness','metalness','owner_mask'):
  p=R.ROOT/'textures'/(kind+'.png')
  if not p.is_file():errors.append('missing texture '+kind)
 for im in bpy.data.images:
  if not im.name.startswith(R.PREFIX):continue
  if list(im.size)!=[2048,2048]:errors.append('atlas size '+im.name)
  if im.source=='FILE' and not Path(bpy.path.abspath(im.filepath)).is_file():errors.append('unresolved image '+im.name)
 if 'Bazaar' in R.PREFIX:
  healthy=bpy.data.collections.get(R.PREFIX+'healthy_LOD0')
  if healthy:
   rooms=[o for o in healthy.all_objects if 'Room' in o.name and o.name.endswith('Floor')]
   if len(rooms)!=16:errors.append('physical shop room count is not16')
   vs=[];fs=[]
   for o in healthy.all_objects:
    if o.type!='MESH':continue
    off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
   tree=BVHTree.FromPolygons(vs,fs,all_triangles=False);openings=[]
   for arm in range(4):
    for bay in (1,3):
     aa=bpy.data.objects[R.PREFIX+f'Arm{arm}Rooflight{bay}Curb-1'];bb=bpy.data.objects[R.PREFIX+f'Arm{arm}Rooflight{bay}Curb1']
     a,b=extent([aa,bb]);pos=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2,8))
     hit,normal,index,dist=tree.ray_cast(pos,Vector((0,0,-1)),15)
     passed=hit is not None and hit.z<2.85
     openings.append({'arm':arm,'rooflight':bay,'first_downward_hit_z':hit.z if hit else None,'open':passed})
     if not passed:errors.append('rooflight blocked '+str(arm)+'/'+str(bay))
   semantics={'physical_shop_rooms':len(rooms),'rooflight_rays':openings}
 result={'passed':not errors,'errors':errors,'compositions':rows,'semantic_checks':semantics,'complete':complete,'cap':cap,'native_gates':'deferred'}
 (R.ROOT/'evidence'/(report_name or ('source-checks.json' if complete else 'healthy-checks.json'))).write_text(json.dumps(result,indent=2)+'\n')
 print('SOURCE_CHECKS',result['passed'],len(errors),errors[:15]);return result

if __name__=='__main__':run()
