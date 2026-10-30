"""Original Samarkand market interpretation. Staged, anchored, source-art only."""
import math,json,random
from pathlib import Path
import bpy
from mathutils import Vector
import asset_runner as R

P=R.PREFIX; G=.24; ZSPRING=2.72
STEPS=['foundation','structure','roofs','shops','trade','finish']
ANCHORS={
 'GROUND':(0,0,0),'PAVING_TOP':(0,0,G),'CROSSING_SPRING':(0,0,2.84),
 'DOME_BEARING':(0,0,4.60),'DOME_APEX':(0,0,7.52),
 'NORTH_ENTRANCE':(0,5.95,G),'SOUTH_ENTRANCE':(0,-5.95,G),
 'EAST_ENTRANCE':(5.95,0,G),'WEST_ENTRANCE':(-5.95,0,G)}

def scene():return R.setup_scene()
def root():return R.collection(P+'healthy_LOD0',scene().collection)
def col(stage):return R.collection(P+'healthy_'+stage,root())
def xy(a):
 c,s=math.cos(a),math.sin(a)
 return lambda x,y,z:(c*x-s*y,s*x+c*y,z)
def block(name,center,size,surf='brick',stage='walls',role='architecture',angle=0):
 return R.block(name,center,size,surf,col(stage),stage,role,angle)
def local_block(name,center,size,surf,stage,angle=0,role='architecture'):
 return block(name,xy(angle)(*center),size,surf,stage,role,angle)
def arch(name,cx,y0,y1,z0,ow,height,iw,spring,rise,surf,c,angle=0,stage='walls',pointed=True):
 # Two subtly pointed shoulders derived from a continuous masonry opening.
 n=24;outline=[(cx-ow/2,z0),(cx-ow/2,z0+height),(cx+ow/2,z0+height),(cx+ow/2,z0),(cx+iw/2,z0)]
 for i in range(n+1):
  t=i*math.pi/n
  dx=iw/2*math.cos(t)
  if pointed and rise>=iw/2:
   offset=(rise*rise-(iw/2)**2)/iw;radius=iw/2+offset
   lift=math.sqrt(max(0,radius*radius-(abs(dx)+offset)**2))
  else:lift=rise*math.sin(t)
  outline.append((cx+dx,z0+spring+lift))
 outline.append((cx-iw/2,z0))
 return R.extrude_xz(name,outline,y0,y1,surf,c,stage,transform=xy(angle))

def revolve(name,center,profile,surf,c,sides=48,stage='vaults',role='roof'):
 x,y,z=center;verts=[];faces=[]
 for r,h in profile:
  for i in range(sides):
   a=i*math.tau/sides;verts.append((x+r*math.cos(a),y+r*math.sin(a),z+h))
 for j in range(len(profile)):
  k=(j+1)%len(profile)
  for i in range(sides):n=(i+1)%sides;faces.append((j*sides+i,j*sides+n,k*sides+n,k*sides+i))
 return R.mesh(name,verts,faces,surf,c,stage,role)

def dome(name,cx,cy,z,r,h,t,surf='roof',sides=48,rings=16):
 profile=[]
 for i in range(rings+1):
  a=(math.pi/2-.015)*i/rings;profile.append((r*math.cos(a),h*math.sin(a)))
 for i in range(rings,-1,-1):
  a=(math.pi/2-.015)*i/rings;profile.append(((r-t)*math.cos(a),(h-t)*math.sin(a)))
 return revolve(name,(cx,cy,z),profile,surf,col('vaults'),sides)

def ring(name,cx,cy,z,r,t,h,surf='brick',sides=48,stage='vaults',role='trim'):
 return revolve(name,(cx,cy,z),[(r,0),(r,h),(r-t,h),(r-t,0)],surf,col(stage),sides,stage,role)

def shop_roof(name,mid,a):
 # A domical vault grows from the actual rectangular wall bearings, avoiding
 # unsupported round overhangs over the narrow front/back shop rooms.
 verts=[];faces=[];N=24;M=7
 for sh in (0,1):
  for j in range(M+1):
   t=(math.pi/2-.018)*j/M;blend=j/M
   for i in range(N):
    aa=i*math.tau/N;ca,sa=math.cos(aa),math.sin(aa)
    shape=(1-blend)/max(abs(ca),abs(sa))+blend
    x=mid+(.66-sh*.075)*math.cos(t)*ca*shape
    y=4.80+(.91-sh*.075)*math.cos(t)*sa*shape
    verts.append(xy(a)(x,y,2.34+(.58-sh*.075)*math.sin(t)))
 layer=(M+1)*N
 for sh in (0,1):
  for j in range(M):
   for i in range(N):q=sh*layer+j*N+i;n=sh*layer+j*N+(i+1)%N;faces.append((q,n,n+N,q+N))
 for j in (0,M):
  for i in range(N):q=j*N+i;n=j*N+(i+1)%N;faces.append((q,n,n+layer,q+layer))
 return R.mesh(name,verts,faces,'roof',col('vaults'),'vaults','roof')

def foundation():
 scene();root()
 block('CourtBed',(0,0,.06),(13.3,13.3,.12),'earth','foundation','ground')
 block('PavingPlate',(0,0,.17),(12.95,12.95,.14),'stone','foundation','ground')
 # Small relief is economical and remains editable, one mesh per paving course.
 for row in range(12):
  y=-5.78+row*1.05
  R.block('PavingJoint'+str(row),(0,y,.242),(12.55,.025,.008),'grime',col('finish'),'finish','surface_wear')
 for axis in range(2):
  for sign in (-1,1):
   c=(sign*6.32,0,.255) if axis==0 else (0,sign*6.32,.255)
   sz=(.11,12.64,.03) if axis==0 else (12.64,.11,.03)
   block('PavingBorder'+str(axis)+str(sign),c,sz,'stone','foundation','ground')
 # Entry thresholds share a single datum with the court.
 for k in range(4):local_block('EntryThreshold'+str(k),(0,5.98,.245),(2.52,.46,.03),'stone','foundation',k*math.pi/2,'ground')
 guides=R.collection('Guides_SamarkandBazaar',scene().collection)
 for name,pos in ANCHORS.items():
  e=bpy.data.objects.new(P+'ANCHOR_'+name,None);guides.objects.link(e);e.location=pos;e.empty_display_size=.2;e['anchor_role']=name
 guides.hide_render=guides.hide_viewport=True
 print('BAZAAR_FOUNDATION_READY')

def structure():
 c=col('walls')
 for i in range(4):
  a=i*math.pi/2
  arch('CrossingArch'+str(i),0,2.11,2.39,G,4.78,4.23,2.52,2.15,1.53,'brick',c,a)
  # Four load-bearing arch bands: no screen pretending to be a thick portal.
  arch('CrossingArchReveal'+str(i),0,2.385,2.445,G,3.04,3.78,2.52,2.15,1.53,'carving',col('finish'),a,'finish')
  for sy in (-1,1):
   local_block('CrossingCorner'+str(i)+str(sy),(sy*2.21,2.20,2.30),(.36,.42,4.12),'brick','walls',a)
  # The short market arms have supported end and intermediate arches.
  for j,y in enumerate((2.42,3.72,5.83)):
   arch(f'Arm{i}PierArch{j}',0,y-.11,y+.11,G,2.92,3.73,2.30,2.00,1.40,'brick',c,a)
  for side in (-1,1):
   for j,(y0,y1) in enumerate(((2.42,3.94),(5.66,5.94))):
    local_block(f'Arm{i}Side{side}Solid{j}',(side*1.37,(y0+y1)/2,(G+ZSPRING)/2),(.26,y1-y0,ZSPRING-G),'plaster','walls',a)
   # A cut opening leads sideways into each shop front.
   trans=lambda x,y,z:xy(a)(side*y,x,z)
   R.archwall(f'Arm{i}ShopDoor{side}',4.80,1.24,1.50,G,1.72,2.48,1.13,1.45,.61,'brick',c,24,trans)
   local_block(f'Arm{i}SideBearing{side}',(side*1.34,4.18,2.71),(.25,3.53,.16),'brick','walls',a)
  # Continuous gallery spring cornices physically bear the roof shell.
  for side in (-1,1):local_block(f'Arm{i}Cornice{side}',(side*1.40,4.18,2.84),(.19,3.60,.13),'brick','vaults',a)
 # Corner squinches transition from square wall bearings to the octagonal drum.
 for sx in (-1,1):
  for sy in (-1,1):
   plan=[(sx*2.39,sy*2.39),(sx*2.39,sy*.91),(sx*.91,sy*2.39)]
   v=[(x,y,z) for z in (4.36,4.60) for x,y in plan]
   R.mesh('Squinch'+str(sx)+str(sy),v,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'brick',col('vaults'),'vaults','architecture')
 ring('OctagonalDomeBearing',0,0,4.43,2.39,.29,.17,'brick',8,'vaults','architecture')
 print('BAZAAR_STRUCTURE_READY')

def roofs():
 dome('CentralTradingDome',0,0,4.60,2.35,2.92,.19)
 ring('DomeSpringBand',0,0,4.60,2.38,.12,.13,'brick',64)
 # Narrow masonry ribs follow the shell rather than floating straight rails.
 for j in range(12):
  a=j*math.tau/12;verts=[];faces=[];N=24
  for edge in (-1,1):
   for i in range(N+1):
    t=i*(math.pi/2-.08)/N;rad=2.35*math.cos(t);z=4.6+2.92*math.sin(t)
    aa=a+edge*.011;verts.append((rad*math.cos(aa),rad*math.sin(aa),z+.015))
  # A thin closed raised course anchored to the outer shell.
  bottom=[(x,y,z-.035) for x,y,z in verts];v=verts+bottom;n=len(verts)
  for i in range(N):faces.extend([(i,i+1,N+2+i,N+1+i),(n+i,n+N+1+i,n+N+2+i,n+i+1)])
  for start in (0,N+1):
   for i in range(N):q=start+i;faces.append((q,n+q,n+q+1,q+1))
  faces.extend([(0,N+1,n+N+1,n),(N,n+N,n+2*N+1,2*N+1)])
  R.mesh('DomeRib'+str(j),v,faces,'brick',col('finish'),'finish','roof_relief')
 for arm in range(4):
  a=arm*math.pi/2
  # Split actual shell around two rooflights. The absent crown cells are real openings.
  intervals=[(2.43,3.16,False),(3.16,3.55,True),(3.55,4.66,False),(4.66,5.05,True),(5.05,5.94,False)]
  for j,(y0,y1,hole) in enumerate(intervals):
   for k,(a0,a1) in enumerate(((0,1.34),(1.80,math.pi)) if hole else ((0,math.pi),)):
    q=R.vault(f'Arm{arm}Vault{j}_{k}',0,y0,y1,ZSPRING,1.36,1.15,.16,'roof',col('vaults'),40,2,xy(a),a0,a1)
    q['role']='roof'
   if hole:
    for sign in (-1,1):local_block(f'Arm{arm}Rooflight{j}Curb{sign}',(sign*.34,(y0+y1)/2,3.96),(.075,y1-y0+.08,.10),'stone','finish',a,'roof_relief')
  # End coping and small warm tile accents, below the central dome.
  arch(f'Arm{arm}PortalBand',0,5.945,6.01,G,3.08,3.77,2.32,2.00,1.40,'carving',col('finish'),a,'finish')
 print('BAZAAR_ROOFS_READY')

def shops(arms=(0,1,2,3)):
 # Two opposite front/back pairs per arm: 8 pairs, exactly 16 rooms.
 for arm in arms:
  a=arm*math.pi/2
  for side in (-1,1):
   for depth in (0,1):
    mid=side*(1.53+.59+depth*1.19);name=f'Arm{arm}Shop{side}Room{depth}'
    local_block(name+'Floor',(mid,4.80,.29),(1.19,1.72,.10),'stone','foundation',a,'ground')
    # Side partitions are continuous through each pair and carry the domical roof.
    for yy in (3.985,5.615):local_block(name+'Side'+str(yy),(mid,yy,1.34),(1.19,.16,2.0),'plaster','walls',a)
    if depth==1:local_block(name+'Back',(side*3.85,4.80,1.34),(.18,1.80,2.0),'brick','walls',a)
    else:
     # The recessed rear opening links shop and store, and has genuine wall thickness.
     trans=lambda x,y,z,side=side,a=a:xy(a)(side*y,x,z)
     R.archwall(name+'RearDoor',4.80,2.64,2.80,.34,1.63,2.0,.75,1.17,.42,'brick',col('walls'),20,trans)
    shop_roof(name+'Roof',mid,a)
    # Tiny visible bench supports, with tops aligned to the front of the shop.
    if depth==0:
     for yy in (4.18,5.42):local_block(name+'BenchFoot'+str(yy),(side*1.65,yy,.47),(.42,.16,.26),'stone','finish',a,'props')
     local_block(name+'Bench',(side*1.65,4.80,.64),(.48,1.40,.09),'stone','finish',a,'props')
     # Outward-facing spare stalls make trade readable from the ordinary camera.
     local_block(name+'OuterLintel',(mid,5.74,2.43),(1.11,.16,.18),'timber','finish',a,'trim')
 print('BAZAAR_16_SHOP_ROOMS_READY')

def canopy(name,x,y,z,w,d,colr='owner'):
 c=col('finish')
 for sx in (-1,1):
  for sy in (-1,1):
   R.beam(name+f'Post{sx}{sy}',(x+sx*w/2,y+sy*d/2,G),(x+sx*w/2,y+sy*d/2,z),.075,'timber',c,'finish','props')
  R.beam(name+f'EndBar{sx}',(x+sx*w/2,y-d/2,z),(x+sx*w/2,y+d/2,z),.075,'timber',c,'finish','props')
 R.beam(name+'Ridge',(x-w/2,y,z),(x+w/2,y,z),.07,'timber',c,'finish','props')
 verts=[];faces=[];N=20
 for sh in (0,1):
  for j in range(7):
   for i in range(N+1):
    u=i/N;v=j/6;verts.append((x+(u-.5)*w,y+(v-.5)*d,z-.18*abs(2*v-1)+.025*math.sin(u*math.pi*8)-sh*.02))
 n=(N+1)*7
 for sh in (0,1):
  for j in range(6):
   for i in range(N):q=sh*n+j*(N+1)+i;faces.append((q,q+1,q+N+2,q+N+1))
 for j in (0,6):
  for i in range(N):q=j*(N+1)+i;faces.append((q,q+1,q+1+n,q+n))
 for i in (0,N):
  for j in range(6):q=j*(N+1)+i;faces.append((q,q+N+1,q+N+1+n,q+n))
 return R.mesh(name+'Cloth',verts,faces,colr,c,'finish','owner' if colr=='owner' else 'props')

def trade():
 c=col('finish')
 canopy('TextileStall',-4.92,-3.6,2.05,2.05,1.30)
 for sx in (-1,1):block('TextileTableLeg'+str(sx),(-4.92+sx*.65,-3.6,.64),(.13,.60,.80),'timber','finish','props')
 block('TextileTable',(-4.92,-3.6,1.08),(1.68,.70,.08),'timber','finish','props')
 for j in range(5):
  R.lathe('ClothRoll'+str(j),(-5.45+j*.26,-3.6,1.23),[(.12,0),(.12,.55)],'owner' if j%3==0 else 'cloth',c,16,'finish','props')
 for j in range(3):block('FoldedRug'+str(j),(-4.92,-3.55,1.16+j*.09),(.73,.58,.065),'cloth','finish','props')
 # Goods stall, jars with real necks and shoulders, tied sacks and pallets.
 canopy('GoodsStall',4.92,-3.6,2.05,2.05,1.30,'cloth')
 for j in range(4):block('GoodsPallet'+str(j),(4.92,-3.90+j*.20,.31),(1.85,.15,.14),'timber','finish','props')
 for j in range(7):
  x=4.38+(j%3)*.48;y=-3.85+(j//3)*.35
  R.lathe('GoodsJar'+str(j),(x,y,.38),[(.19,0),(.27,.12),(.29,.43),(.21,.63),(.12,.72),(.12,.80),(.09,.80),(.09,.70)],'pottery',c,24,'finish','props')
 for j in range(4):
  R.lathe('TiedSack'+str(j),(4.30+j*.36,-2.61,G),[(.18,0),(.25,.20),(.22,.50),(.07,.62),(.11,.66)],'cloth',c,24,'finish','props')
 # A clear weighing/record-keeping group at the west return, off the main approach.
 canopy('WeighingDesk',-4.92,3.70,2.05,2.05,1.26)
 for x in (-5.48,-4.38):block('DeskLeg'+str(x),(x,3.70,.69),(.12,.62,.90),'timber','finish','props')
 block('LedgerDesk',(-4.92,3.70,1.18),(1.58,.74,.08),'timber','finish','props')
 block('OpenLedger',(-5.20,3.69,1.235),(.47,.35,.035),'paper','finish','props')
 R.beam('ScalesStem',(-4.56,3.70,1.22),(-4.56,3.70,1.90),.055,'metal',c)
 R.beam('ScalesCrossarm',(-4.89,3.70,1.86),(-4.23,3.70,1.86),.035,'metal',c)
 for x in (-4.88,-4.24):
  R.beam('ScaleHanger'+str(x),(x,3.70,1.86),(x,3.70,1.48),.012,'metal',c)
  R.lathe('ScalePan'+str(x),(x,3.70,1.45),[(.02,0),(.16,.04),(.17,.07),(.15,.07),(.02,.02)],'metal',c,20)
 print('BAZAAR_TRADE_READY')

def finish():
 c=col('finish');rr=random.Random(1189)
 # Restraint: small turquoise tile insets near four entrance reveals.
 for arm in range(4):
  a=arm*math.pi/2
  for sign in (-1,1):
   for j in range(7):local_block(f'Portal{arm}BlueTile{sign}_{j}',(sign*1.34,6.025,.72+j*.31),(.12,.025,.20),'ink','finish',a,'trim')
  for sign in (-1,1):
   R.beam(f'Portal{arm}BannerRod{sign}',xy(a)(sign*1.52,5.99,2.76),xy(a)(sign*1.52,6.25,2.76),.045,'timber',c)
   local_block(f'Portal{arm}HangingOwner{sign}',(sign*1.52,6.20,2.43),(.29,.025,.62),'owner','finish',a,'owner')
 # Localized cracks/wear live near thresholds, corners and wet rooflight edges.
 for j in range(18):
  a=j%4*math.pi/2;sign=-1 if j%2 else 1
  local_block('ThresholdWear'+str(j),(sign*(1.50+rr.random()*.35),5.82,.251),(.13+rr.random()*.16,.18,.008),'grime','finish',a,'surface_wear')
 for j in range(4):
  local_block('EntryStep'+str(j),(0,6.30,.12),(2.66,.32,.24),'stone','foundation',j*math.pi/2,'ground')
 # Record semantic shop count, meaningful activity groups and proposed anatomy.
 s=scene();s['shop_pairs']=8;s['shop_rooms']=16;s['market_arms']=4
 s['reference_status']='Historically informed Timurid/Persianate market; exact plan interpreted'
 (R.ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n')
 R.show_state();R.view(center=(0,0,2.4),distance=19)
 print('BAZAAR_HEALTHY_READY',len(root().all_objects))

def build_step(step):
 if step not in STEPS:raise ValueError(step)
 globals()[step]()

def build_all(reset_owned=False):
 if root().all_objects:
  if not reset_owned:raise RuntimeError('Canonical source exists; explicit reset_owned=True required')
  for o in list(scene().objects):
   if o.name.startswith(P):
    me=o.data if o.type=='MESH' else None;bpy.data.objects.remove(o,do_unlink=True)
    if me and not me.users:bpy.data.meshes.remove(me)
 for step in STEPS:build_step(step)
