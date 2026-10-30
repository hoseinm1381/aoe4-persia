"""Static source compositions. No runtime selectors, effects or HP thresholds."""
import bpy,bmesh,math,json,random
from mathutils import Vector,Matrix
import asset_runner as R

STATES=['healthy']+[f'damage_{i}' for i in range(1,6)]+['ruins']
P=R.PREFIX
def scene():return bpy.data.scenes[P[:-1]]
def root(state):return R.collection(P+state+'_LOD0',scene().collection)
def col(state,stage='finish'):return R.collection(P+state+'_'+stage,root(state))
def clone(o,state,target=None):
 q=o.copy();q.data=o.data.copy();q.name=P+state+'__'+o.name.removeprefix(P);q.data.name=q.name+'_mesh'
 (target or col(state,o.get('construction_stage','finish'))).objects.link(q)
 q['healthy_source']=o.get('healthy_source',o.name);q['state']=state;return q
def remove(o):
 me=o.data;bpy.data.objects.remove(o,do_unlink=True)
 if not me.users:bpy.data.meshes.remove(me)
def cut(o,point,normal):
 bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
 edges=[e for e in bm.edges if e.is_boundary]
 if edges:
  if o.get('role')=='curved_structure':
   # A cut hollow lookout has nested outer/inner loops. Bridge their annulus;
   # filling each loop separately would put overlapping discs over the aperture.
   bmesh.ops.bridge_loops(bm,edges=edges,use_pairs=True)
  else:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
 if bm.faces:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
 if not o.data.polygons:remove(o);return None
 R.retile_surface(o);return o
def copy_state(state):return {o.name.removeprefix(P):clone(o,state) for o in list(bpy.data.collections[P+'healthy_LOD0'].all_objects) if o.type=='MESH'}
def shard(name,state,x,y,z,w,d,h,rr,surface='brick'):
 v=[(x+sx*w/2,y+sy*d/2,z) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
 v += [(x+sx*w*(.28+rr.random()*.2),y+sy*d*(.28+rr.random()*.2),z+h*(.55+rr.random()*.45)) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
 return R.mesh(state+'__'+name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],surface,col(state,'debris'),'finish','debris')
def debris(state,count,center,spread,scale,seed,ground=.25):
 rr=random.Random(seed)
 for i in range(count):
  a=rr.random()*math.tau;r=math.sqrt(rr.random());x=center[0]+r*spread[0]*math.cos(a);y=center[1]+r*spread[1]*math.sin(a)
  h=scale*(.35+rr.random());shard(f'Rubble{seed}_{i}',state,x,y,ground,h*1.6,h,h*.68,rr,'brick' if i%3 else 'stone')
def settle(o,x,y,z,rx=0,rz=0,maxheight=None):
 rot=Matrix.Rotation(rx,4,'X')@Matrix.Rotation(rz,4,'Z')
 for v in o.data.vertices:v.co=rot@v.co
 lo,hi=R.bounds(o);center=[(lo[i]+hi[i])/2 for i in range(3)]
 if maxheight and hi[2]-lo[2]>maxheight:
  scale=maxheight/(hi[2]-lo[2])
  for v in o.data.vertices:v.co=Vector(center)+(v.co-Vector(center))*scale
  lo,hi=R.bounds(o)
 for v in o.data.vertices:v.co+=Vector((x-center[0],y-center[1],z-lo[2]))
 R.retile_surface(o)

def ragged_cap(o,seed):
 rr=random.Random(seed);lo,hi=R.bounds(o);top=hi[2]
 bm=bmesh.new();bm.from_mesh(o.data)
 caps=[f for f in bm.faces if f.normal.z>.35 and any(v.co.z>top-.22 for v in f.verts)]
 if caps:bmesh.ops.triangulate(bm,faces=caps)
 for v in bm.verts:
  if v.co.z>top-.22:v.co.z-=rr.random()*.18
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();R.retile_surface(o)

G=.88
def fallen_hall(state,k,x,y):
 o=R.vault(state+'__FallenServiceVault'+str(k),0,-.28,.28,0,.49,.50,.11,'roof',col(state,'debris'),18,2,angle0=.2,angle1=1.42,stage='finish')
 o['role']='debris';o['source_component']='service-room vault';settle(o,x,y,G,.6,k*.9,maxheight=.70);return o

def damage(level):
 state='damage_'+str(level);obs=copy_state(state)
 for n,o in list(obs.items()):
  if n.startswith('GateOwner'):cut(o,(0,0,2.56+level*.02),(.025,.06,-1))
 if 'CurtainCoping1_0' in obs:cut(obs['CurtainCoping1_0'],(0,-3.2,2.94-level*.015),(.01,.025,1))
 if level>=2:
  cut(obs['GateCrown'],(0,0,3.91),(.03,.01,1))
  debris(state,10,(-1.80,-3.50),(.45,.30),.12,110+level,G)
 if level>=3:
  for n,o in list(obs.items()):
   if n.startswith('GateCrownMerlon') and int(n[-1])%2==0:remove(o)
  debris(state,24,(-1.80,-3.50),(.55,.35),.18,210+level,G)
 if level>=4:
  for n in ('Store1Vault','WatchCanopy'):
   if n in obs:remove(obs[n])
  fallen_hall(state,0,2.04,-2.30)
  debris(state,28,(2.03,-2.33),(.42,.72),.18,310+level,G)
 if level>=5:
  for n,o in list(obs.items()):
   try:live=o.name
   except ReferenceError:continue
   if n=='SmallLookoutWall':cut(o,(0,0,1.72),(.01,.025,1))
   elif n=='LookoutFloor' or n.startswith('LookoutMerlon') or n.startswith('WatchRail') or n=='WatchCrossRail' or n=='WatchOwner':remove(o)
   elif n in ('Curtain1_0','Curtain1_1'):cut(o,(0,0,1.80),(.025,-.025,1))
   elif n.startswith('CurtainMerlon1_0') or n.startswith('CurtainMerlon1_1') or n.startswith('CurtainCoping1_0') or n.startswith('CurtainCoping1_1'):remove(o)
  debris(state,60,(2.10,-1.22),(.45,1.55),.24,410+level,G)
 R.show_state(state);print('BROTHERHOOD_DAMAGE_READY',state)

def ruins():
 state='ruins';rr=random.Random(619)
 for o in list(bpy.data.collections[P+'healthy_LOD0'].all_objects):
  if o.get('construction_stage')=='foundation':clone(o,state)
  elif o.get('construction_stage')=='walls':
   q=clone(o,state);height=1.74 if 'Command' in o.name else 1.40+rr.random()*.20
   q=cut(q,(0,0,height),(.009,-.008,1))
   if q:q['surface']='stone';q.color=R.COLOURS[2];ragged_cap(q,o.name)
 for i,(x,y) in enumerate(((-1.25,-2.0),(.35,-2.75),(1.68,-.35))):fallen_hall(state,i,x,y)
 debris(state,145,(0,-1.60),(2.40,2.05),.25,810,G)
 debris(state,30,(-1.9,-3.48),(.55,.30),.24,811,G)
 R.block(state+'__OwnerFragment',(-1.65,-4.16,1.27),(.23,.025,.28),'owner',col(state),'finish','owner')
 R.show_state(state);print('BROTHERHOOD_RUINS_READY')

def construction():
 stages=['foundation','walls','vaults','finish'];healthy=bpy.data.collections[P+'healthy_LOD0']
 for i,stage in enumerate(stages):
  c=R.collection(P+'construct_'+stage,scene().collection)
  for o in list(healthy.all_objects):
   if o.type=='MESH' and o.get('construction_stage') in stages[:i+1]:
    q=clone(o,'construct_'+stage,c)
    if i in (1,2) and q.get('surface')=='plaster':q['surface']='brick';q.color=R.COLOURS[1];R.retile_surface(q)
  if i in (1,2):
   for x in (-2.77,1.05):
    for y in (-.65,.90):R.beam(f'construct_{stage}__ScaffoldPost{x}_{y}',(x,y,G),(x,y,5.10),.075,'timber',c,'walls','construction')
    for z in (2.20,3.85):R.beam(f'construct_{stage}__Ledger{x}_{z}',(x,-.70,z),(x,.95,z),.075,'timber',c,'walls','construction')
    R.beam(f'construct_{stage}__Brace{x}',(x,-.65,G),(x,.90,5.05),.065,'timber',c,'walls','construction')
    R.block(f'construct_{stage}__Deck{x}',(x,.125,3.89),(.50,1.70,.08),'timber',c,'walls','construction')
 R.show_state();print('BROTHERHOOD_CONSTRUCTION_READY')

def build_all():
 for i in range(1,6):damage(i)
 ruins();construction();R.show_state()

def reset_state(state):
 c=bpy.data.collections.get(P+state+'_LOD0')
 if not c:return
 for o in list(c.all_objects):remove(o)
 for child in list(c.children):bpy.data.collections.remove(child)
 bpy.data.collections.remove(c)
