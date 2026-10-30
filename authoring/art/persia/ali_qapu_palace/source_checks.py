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
  elif len(o.data.materials)!=1 or o.data.materials[0].name!=R.PREFIX+'SharedAtlas':errors.append('unexpected material assignment '+o.name)
  if any(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices):errors.append('nonfinite vertex '+o.name)
  if any(p.area<1e-11 for p in o.data.polygons):errors.append('degenerate face '+o.name)
  for layer in o.data.uv_layers:
   if any(not all(math.isfinite(x) and -.0001<=x<=1.0001 for x in t.uv) for t in layer.data):errors.append('invalid UV '+o.name);break
  if o.get('surface') not in ('owner','cloth','ink','paper','carving'):
   for poly in o.data.polygons:
    axis=max(range(3),key=lambda j:abs(poly.normal[j]));axes=[i for i in range(3) if i!=axis]
    tile=R.TILES.index(o.get('surface','brick'));tx=tile%4;ty=3-tile//4
    for li in poly.loop_indices:
     v=o.data.vertices[o.data.loops[li].vertex_index].co
     expected=((tx+.04+.92*(v[axes[0]]-(-8,-8,0)[axes[0]])/16)/4,(ty+.04+.92*(v[axes[1]]-(-8,-8,0)[axes[1]])/16)/4)
     if any(abs(a-b)>2e-6 for a,b in zip(o.data.uv_layers[0].data[li].uv,expected)):
      errors.append('structural UV scale/origin '+o.name);break
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
 from semantic_checks import check
 semantics,extra=check()
 errors.extend(extra)
 result={'passed':not errors,'errors':errors,'compositions':rows,'semantic_checks':semantics,'complete':complete,'cap':cap,'native_gates':'deferred'}
 (R.ROOT/'evidence'/(report_name or ('source-checks.json' if complete else 'healthy-checks.json'))).write_text(json.dumps(result,indent=2)+'\n')
 print('SOURCE_CHECKS',result['passed'],len(errors),errors[:15]);return result

if __name__=='__main__':run()
