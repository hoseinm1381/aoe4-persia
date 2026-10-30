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
 if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
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
def fallen_vault(state,i,x,y,z=.25):
 o=R.vault(state+'__FallenVault'+str(i),0,-.30,.30,0,1.36,1.15,.16,'roof',col(state,'debris'),18,2,angle0=.3,angle1=1.42,stage='finish')
 o['role']='debris';o['source_component']='market arm barrel vault';settle(o,x,y,z,.65,1.2+i*.71)
 return o
def dome_shard(state,k,x,y):
 N=12;M=5;v=[];f=[]
 for sh in (0,1):
  for j in range(M+1):
   t=.25+j*.12
   for i in range(N+1):
    a=k*.9+i*.065;r=2.35-sh*.19;h=2.92-sh*.19
    v.append((r*math.cos(t)*math.cos(a),r*math.cos(t)*math.sin(a),h*math.sin(t)))
 n=(M+1)*(N+1)
 for sh in (0,1):
  for j in range(M):
   for i in range(N):q=sh*n+j*(N+1)+i;f.append((q,q+1,q+N+2,q+N+1))
 for j in (0,M):
  for i in range(N):q=j*(N+1)+i;f.append((q,q+1,q+n+1,q+n))
 for i in (0,N):
  for j in range(M):q=j*(N+1)+i;f.append((q,q+N+1,q+n+N+1,q+n))
 o=R.mesh(state+'__FallenDome'+str(k),v,f,'roof',col(state,'debris'),'finish','debris');o['source_component']='central trading dome shell'
 settle(o,x,y,.25,1.05,k*.8,maxheight=1.80);return o

def ragged_cap(o,seed):
 rr=random.Random(seed);lo,hi=R.bounds(o);top=hi[2]
 bm=bmesh.new();bm.from_mesh(o.data)
 caps=[f for f in bm.faces if f.normal.z>.35 and any(v.co.z>top-.22 for v in f.verts)]
 if caps:bmesh.ops.triangulate(bm,faces=caps)
 for v in bm.verts:
  if v.co.z>top-.22:v.co.z-=rr.random()*.18
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();R.retile_surface(o)

def damage(level):
 state='damage_'+str(level);obs=copy_state(state)
 # Damage starts on the front/south arm, where ordinary review views can read it.
 for n,o in list(obs.items()):
  if 'HangingOwner' in n:
   cut(o,(0,0,2.15+level*.025),(.03,.07,-1))
 # Genuine cap chips in existing masonry, rather than new dark overlays.
 for n in ('Arm2Side1Solid0','Arm2Side-1Solid0'):
  if n in obs:cut(obs[n],(.05,-3.1,2.67-level*.035),(.01,-.025,1))
 if level>=2:
  o=obs.get('Arm2Cornice1')
  if o:cut(o,(0,-4.9,2.82),(0,-.08,1))
  debris(state,8,(1.6,-4.25),(.35,.8),.12,100+level)
 if level>=3:
  for n in ('Arm2PierArch2','Arm2PortalBand'):
   if n in obs:cut(obs[n],(0,0,3.57),(.015,-.015,1))
  debris(state,22,(0,-5.75),(1.3,.30),.21,200+level)
 if level>=4:
  for n,o in list(obs.items()):
   if n.startswith('Arm2Vault3') or n.startswith('Arm2Vault4') or n.startswith('Arm2Rooflight3'):
    remove(o)
  fallen_vault(state,0,.15,-5.05)
  debris(state,35,(0,-5.0),(1.15,.7),.25,300+level)
 if level>=5:
  for n,o in list(obs.items()):
   try:live_name=o.name
   except ReferenceError:continue
   if live_name not in bpy.data.objects:continue
   if n.startswith('Arm2Vault') or n.startswith('Arm2Rooflight') or (n.startswith('Arm2Shop1') and n.endswith('Roof')):
    remove(o);continue
   if n.startswith('Arm2') and o.get('construction_stage')=='walls':cut(o,(0,0,1.35),(.025,.015,1))
   elif n.startswith('Portal2'):remove(o)
  fallen_vault(state,1,-.45,-3.9)
  debris(state,65,(-1.0,-4.7),(2.2,1.0),.29,400+level)
 R.show_state(state);print('DAMAGE_READY',state)

def ruins():
 state='ruins';rr=random.Random(816)
 for o in list(bpy.data.collections[P+'healthy_LOD0'].all_objects):
  if o.get('construction_stage')=='foundation':clone(o,state)
  elif o.get('construction_stage')=='walls':
   q=clone(o,state);height=2.04 if 'Crossing' in o.name else 1.15+rr.random()*.35
   q=cut(q,(0,0,height),(.025,-.021,1))
   if q:q['surface']='brick';ragged_cap(q,o.name);q.color=R.COLOURS[1]
 for i,(x,y) in enumerate(((-.4,-4.0),(.5,4.0),(-3.7,.6),(3.7,-.5))):fallen_vault(state,i,x,y)
 for i,(x,y) in enumerate(((-1.4,-.9),(1.2,.8),(-.9,1.2))):dome_shard(state,i,x,y)
 debris(state,145,(0,0),(2.5,2.5),.33,90)
 for k in range(4):
  a=k*math.pi/2;debris(state,45,(math.cos(a)*4.4,math.sin(a)*4.4),(.9,.9),.28,91+k)
 R.block(state+'__OwnerFragment',(1.65,-2.40,.89),(.25,.025,.35),'owner',col(state),'finish','owner')
 R.show_state(state);print('RUINS_READY')

def construction():
 stages=['foundation','walls','vaults','finish'];healthy=bpy.data.collections[P+'healthy_LOD0']
 for i,stage in enumerate(stages):
  c=R.collection(P+'construct_'+stage,scene().collection)
  for o in list(healthy.all_objects):
   if o.type=='MESH' and o.get('construction_stage') in stages[:i+1]:
    q=clone(o,'construct_'+stage,c)
    if i in (1,2) and q.get('surface')=='plaster':q['surface']='brick';q.color=R.COLOURS[1];R.retile_surface(q)
  if i in (1,2):
   # Freestanding supported scaffold; no duplicate healthy masonry at finish.
   for x in (-2.8,2.8):
    for y in (-1.4,1.4):R.beam(f'construct_{stage}__Post{x}_{y}',(x,y,.24),(x,y,4.45),.085,'timber',c,'walls','construction')
    for z in (1.7,3.3):R.beam(f'construct_{stage}__Ledger{x}_{z}',(x,-1.45,z),(x,1.45,z),.085,'timber',c,'walls','construction')
    R.beam(f'construct_{stage}__Brace{x}',(x,-1.4,.24),(x,1.4,4.4),.075,'timber',c,'walls','construction')
    R.block(f'construct_{stage}__Deck{x}',(x,0,3.35),(.68,2.95,.09),'timber',c,'walls','construction')
 R.show_state();print('CONSTRUCTION_READY')

def build_all():
 for i in range(1,6):damage(i)
 ruins();construction();R.show_state()

def reset_state(state):
 c=bpy.data.collections.get(P+state+'_LOD0')
 if not c:return
 for o in list(c.all_objects):remove(o)
 for child in list(c.children):bpy.data.collections.remove(child)
 bpy.data.collections.remove(c)
