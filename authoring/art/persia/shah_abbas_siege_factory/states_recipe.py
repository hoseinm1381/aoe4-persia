"""Palace source compositions; no native thresholds or runtime wiring."""
import bpy,bmesh,math,json,random
from mathutils import Vector,Matrix
import asset_runner as R
P=R.PREFIX
STATES=['healthy']+[f'damage_{i}' for i in range(1,6)]+['ruins']
def scene():return bpy.data.scenes[P[:-1]]
def root(state):return R.collection(P+state+'_LOD0',scene().collection)
def clone(o,state,target=None):
 q=o.copy();q.data=o.data.copy();q.name=P+state+'__'+o.name.removeprefix(P);q.data.name=q.name+'_mesh'
 (target if target is not None else root(state)).objects.link(q)
 q['healthy_source']=o.get('healthy_source',o.name);q['state']=state;return q
def remove(o):
 me=o.data;bpy.data.objects.remove(o,do_unlink=True)
 if me.users==0:bpy.data.meshes.remove(me)
def cut(o,height,tilt=0):
 bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=(0,0,height),plane_no=(tilt,0,1),clear_outer=True)
 edges=[e for e in bm.edges if e.is_boundary]
 if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
 if not bm.faces:bm.free();remove(o);return None
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();R.retile_surface(o)
 for key in ('arch_source','gable_source','vault_source'):
  if key in o:del o[key]
 return o
def debris(state,count,seed):
 rr=random.Random(seed)
 for i in range(count):
  x=rr.uniform(-3.85,3.3);y=rr.uniform(-4.05,4.05);w=rr.uniform(.10,.30);h=rr.uniform(.06,.20)
  o=R.block(state+'__Rubble'+str(seed)+'_'+str(i),(x,y,.18+h/2),(w,w*.7,h),'brick' if i%3 else 'stone',root(state),'finish','debris',rr.random())
def copy_state(state):return {o.name.removeprefix(P):clone(o,state) for o in list(root('healthy').all_objects) if o.type=='MESH'}
def tattered_cloth(o,level):
 lo,hi=R.bounds(o);axis=0 if hi[0]-lo[0]>hi[1]-lo[1] else 1;rr=random.Random(o.get('healthy_source',o.name));height=hi[2]-lo[2]
 bm=bmesh.new();bm.from_mesh(o.data)
 edges=[e for e in bm.edges if all(abs(v.co.z-lo[2])<.001 for v in e.verts)]
 if edges:bmesh.ops.subdivide_edges(bm,edges=edges,cuts=2,use_grid_fill=False)
 offsets={}
 for v in bm.verts:
  if abs(v.co.z-lo[2])<.001:
   key=round(v.co[axis],6)
   if key not in offsets:offsets[key]=min(height*.72,.07*level+rr.uniform(.025,.11))
   v.co.z+=offsets[key]
 bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if any(v.co.z<lo[2]+height*.73 for v in f.verts)])
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();R.retile_surface(o)

def damage(level):
 state='damage_'+str(level);obs=copy_state(state)
 for name,o in list(obs.items()):
  if 'OwnerCloth' in name:tattered_cloth(o,level)

 for j in range(level+1):
  x=-1.50+(j%3)*2.4;z=.55+(j//3)*.45
  outline=[(x-.04,z-.13),(x-.05,z+.05),(x+.03,z+.18),(x+.10,z+.11),(x+.10,z-.11)]
  R.extrude_xz(state+'__ExposedPier'+str(j),outline,2.436,2.445,'brick',root(state),'finish',role='surface_wear')
 if level>=2:debris(state,10,610+level)
 if level>=3:
  o=obs['CanopyRoof'];bm=bmesh.new();bm.from_mesh(o.data)
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(2.95,0,0),plane_no=(1,0,0),dist=.000001,clear_outer=True)
  edges=[e for e in bm.edges if e.is_boundary]
  if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();R.retile_surface(o)
  debris(state,20,710+level)
 if level>=4:
  remove(obs['LeftBay0Vault']);cut(obs['LeftBay0Arch'],1.8,.015)
  debris(state,34,810+level)
 if level>=5:
  for n,q in list(obs.items()):
   if n.startswith(('Pulley','Tackle','ReturnTie')):remove(q)
  for n in ('LiftHeader','LiftBrace-1','LiftBrace1','TackleRope','TackleHook','CanopyRoof'):
   q=obs.get(n)
   if q:
    try:remove(q)
    except ReferenceError:pass
  for n in ('LiftUpright-1','LiftUpright1'):cut(obs[n],1.85,.02)
  R.block(state+'__FallenHeader',(-.95,-1.2,.30),(2.3,.24,.24),'timber',root(state),'finish','debris',.25)
  debris(state,48,915)
 print('DAMAGE_READY',state)
def broken_cap(o):
 seed=o.get('healthy_source',o.name);rr=random.Random(seed);lo,hi=R.bounds(o)
 if hi[2]-lo[2]<.20:remove(o);return
 jitter=min(.14,(hi[2]-lo[2])*.20)
 bm=bmesh.new();bm.from_mesh(o.data)
 tops=[f for f in bm.faces if f.normal.z>.2 and any(v.co.z>hi[2]-.03 for v in f.verts)]
 if tops:bmesh.ops.triangulate(bm,faces=tops)
 for v in bm.verts:
  if v.co.z>hi[2]-.03:v.co.z-=rr.uniform(jitter*.2,jitter)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 if rr.random()<.7:o['surface']='brick';o.color=R.COLOURS[R.TILES.index('brick')]
 R.retile_surface(o)

def ruins():
 state='ruins';rr=random.Random(929)
 for o in list(root('healthy').all_objects):
  lo,hi=R.bounds(o)
  if o.get('role')=='ground':clone(o,state)
  elif o.get('role')=='architecture' and lo[2]<1.0:
   q=clone(o,state);q=cut(q,rr.uniform(.65,1.15),.025)
   if q:broken_cap(q)
 for i in range(15):
  R.block(state+'__BrokenTimber'+str(i),(rr.uniform(-3.5,3),rr.uniform(-3.7,3.8),.26),(rr.uniform(.4,1.1),.15,.16),'timber',root(state),'finish','debris',rr.random()*math.pi)
 debris(state,125,1051)
 R.block(state+'__OwnerFragment',(-2.4,2.35,.43),(.4,.035,.3),'owner',root(state),'finish','owner')
 print('RUINS_READY')
def construction():
 stages=['foundation','walls','vaults','finish']
 for i,stage in enumerate(stages):
  col=R.collection(P+'construct_'+stage,scene().collection)
  for o in list(root('healthy').all_objects):
   if o.get('construction_stage') in stages[:i+1]:
    q=clone(o,'construct_'+stage,col)
    if i in (1,2) and q.get('surface')=='plaster':q['surface']='brick';R.retile_surface(q)
  if i in (1,2):
   for x in (-3.6,3.05):
    for y in (2.0,3.9):R.beam(f'construct_{stage}__Post{x}_{y}',(x,y,.18),(x,y,3.9),.09,'timber',col,'walls','construction')
    for z in (1.6,3.3):R.beam(f'construct_{stage}__Ledger{x}_{z}',(x,1.95,z),(x,3.95,z),.09,'timber',col,'walls','construction')
    R.beam(f'construct_{stage}__Brace{x}',(x,2,.18),(x,3.9,3.8),.08,'timber',col,'walls','construction')
 print('CONSTRUCTION_READY')
def build_all():
 for i in range(1,6):damage(i)
 ruins();construction();R.show_state()
