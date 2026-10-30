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
  x=rr.uniform(-4.9,4.9);y=rr.uniform(-5.6,5.7);w=rr.uniform(.10,.34);h=rr.uniform(.06,.22)
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
 for name,o in obs.items():
  if 'OwnerCloth' in name:tattered_cloth(o,level)
 for name in ('CoreParapetSide-1','CoreParapetSide1'):
  cut(obs[name],13.46-level*.035,.003)

 for j in range(level+1):
  x=(-4.97 if j%2==0 else 4.97);z=.65+j*.48
  outline=[(x-.22,z-.12),(x-.29,z+.08),(x-.08,z+.22),(x+.19,z+.12),(x+.26,z-.04),(x+.05,z-.17)]
  R.extrude_xz(state+'__ExposedPier'+str(j),outline,-6.203,-6.196,'brick',root(state),'finish',role='surface_wear')
 if level>=2:debris(state,8,402+level)
 if level>=3:
  for n,o in list(obs.items()):
   if n.startswith('RoofDentil') and int(n.removeprefix('RoofDentil'))<8:remove(o)
  debris(state,18,503+level)
 if level>=4:
  # Remove the right roof end; retain roof vertices on supported bays to its left.
  o=obs['TerraceRoof'];bm=bmesh.new();bm.from_mesh(o.data)
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(3.8,0,0),plane_no=(1,0,0),dist=.000001,clear_outer=True)
  edges=[e for e in bm.edges if e.is_boundary]
  if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();R.retile_surface(o)
  for n,q in list(obs.items()):
   if n.startswith('RoofCoffer') and R.bounds(q)[0][0]>3.7:remove(q)
   elif n.startswith('RoofDentil') and int(n.removeprefix('RoofDentil'))>37:remove(q)
  debris(state,36,604+level)
 if level>=5:
  # A top-right core corner fails; its grilles/friezes/floors fail with it.
  for n,q in list(obs.items()):
   try:lo,hi=R.bounds(q)
   except ReferenceError:continue
   if n.startswith('Core') and lo[0]>1.1 and hi[2]>10.0:
    if q.get('role') in ('lattice','tile_detail','trim'):remove(q)
    else:cut(q,9.65,.025)
   elif n.startswith('CoreSide1Level') and hi[2]>10.0:
    if q.get('role')=='lattice':remove(q)
    else:cut(q,9.65,.025)
  # Upper floors, roof and cornice must fail with the missing upper-right wall.
  for n,q in list(obs.items()):
   try:lo,hi=R.bounds(q)
   except ReferenceError:continue
   if n in ('CoreRoof','CoreFloor5','CoreParapet0.14','CoreParapet6.21'):
    bm=bmesh.new();bm.from_mesh(q.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(1.35,0,0),plane_no=(1,0,0),dist=.000001,clear_outer=True)
    edges=[e for e in bm.edges if e.is_boundary]
    if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(q.data);bm.free();R.retile_surface(q)
   elif n=='SideOwnerCloth1' or (n.startswith('BeltSide1_') and lo[2]>9.6):remove(q)
  debris(state,55,705)
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
 state='ruins';rr=random.Random(419)
 for o in list(root('healthy').all_objects):
  role=o.get('role');lo,hi=R.bounds(o)
  if role=='ground':clone(o,state)
  elif role=='architecture' and lo[2]<2.6:
   q=clone(o,state);q=cut(q,rr.uniform(1.3,2.4),.02)
   if q:broken_cap(q)
 # Fallen timber and carved capital fragments are grounded; no hanging roof.
 for i in range(22):
  x=rr.uniform(-4.7,4.7);y=rr.uniform(-5.4,5.5)
  q=R.block(state+'__FallenBeam'+str(i),(x,y,.27),(.16,rr.uniform(.5,1.8),.18),'timber',root(state),'finish','debris',rr.random()*math.pi)
 for i in range(8):R.lathe(state+'__CapitalFragment'+str(i),(rr.uniform(-4.7,4.7),rr.uniform(-5.2,5.2),.18),[(.16,0),(.24,.18),(.19,.3)],'carving',root(state),8,'finish','debris')
 debris(state,135,810)
 R.block(state+'__OwnerFragment',(-1.8,-5.85,.47),(.36,.035,.32),'owner',root(state),'finish','owner')
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
   for side in (-1,1):
    x=side*4.65
    for y in (1.0,5.5):R.beam(f'construct_{stage}__Post{side}_{y}',(x,y,.18),(x,y,12.7),.10,'timber',col,'walls','construction')
    for z in (2.0,4.4,6.8,9.2,11.6):
     R.beam(f'construct_{stage}__Ledger{side}_{z}',(x,.9,z),(x,5.6,z),.10,'timber',col,'walls','construction')
     R.block(f'construct_{stage}__Deck{side}_{z}',(x,3.25,z+.09),(.75,4.7,.08),'timber',col,'walls','construction')
    R.beam(f'construct_{stage}__Brace{side}',(x,1,.18),(x,5.5,12.7),.09,'timber',col,'walls','construction')
 print('CONSTRUCTION_READY')
def build_all():
 for i in range(1,6):damage(i)
 ruins();construction();R.show_state()
