"""Alamut-inspired inhabited headquarters; compressed historical interpretation."""
import bpy,math,json,random
from mathutils import Vector
import asset_runner as R

P=R.PREFIX;G=.88;CY=-2.05
STEPS=['foundation','walls','command','roofs','activity','finish']
ANCHORS={'GROUND':(0,-5.8,0),'COURT_TOP':(0,-2.0,G),'LOWER_LANDING':(-.05,-5.32,.44),
 'GATE_THRESHOLD':(0,-3.92,G),'GATE_CROWN':(0,-3.92,3.95),
 'COMMAND_FLOOR':(-.95,.10,G),'COMMAND_ROOF':(-.95,.1,4.98),
 'WATCH_APEX':(-1.835,-.095,6.22),'CISTERN_HEAD':(1.35,-1.10,G)}

def scene():return R.setup_scene()
def root():return R.collection(P+'healthy_LOD0',scene().collection)
def col(stage):return R.collection(P+'healthy_'+stage,root())
def block(name,center,size,surf='stone',stage='walls',role='architecture',rotation=0):return R.block(name,center,size,surf,col(stage),stage,role,rotation)
def prism(name,outline,z0,z1,surf,stage='foundation',role='ground'):
 n=len(outline);v=[(x,y,z) for z in (z0,z1) for x,y in outline]
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return R.mesh(name,v,f,surf,col(stage),stage,role)
def revolve(name,center,profile,surface,c,sides=40,stage='vaults',role='roof'):
 x,y,z=center;v=[];f=[]
 for radius,h in profile:
  for i in range(sides):
   a=i*math.tau/sides;v.append((x+radius*math.cos(a),y+radius*math.sin(a),z+h))
 for j in range(len(profile)):
  for i in range(sides):n=(i+1)%sides;k=(j+1)%len(profile);f.append((j*sides+i,j*sides+n,k*sides+n,k*sides+i))
 return R.mesh(name,v,f,surface,c,stage,role)
def ring(name,x,y,z,r,t,h,surf='stone',sides=32,stage='walls',role='architecture'):
 return revolve(name,(x,y,z),[(r,0),(r,h),(r-t,h),(r-t,0)],surf,col(stage),sides,stage,role)
def arch(name,cx,y0,y1,z0,ow,height,iw,spring,rise,surf='brick',stage='walls',transform=None):
 outline=[(cx-ow/2,z0),(cx-ow/2,z0+height),(cx+ow/2,z0+height),(cx+ow/2,z0),(cx+iw/2,z0)]
 for i in range(25):
  a=i*math.pi/24;dx=iw/2*math.cos(a)
  if rise>=iw/2:
   offset=(rise*rise-(iw/2)**2)/iw;radius=iw/2+offset
   lift=math.sqrt(max(0,radius*radius-(abs(dx)+offset)**2))
  else:lift=rise*math.sin(a)
  outline.append((cx+dx,z0+spring+lift))
 outline.append((cx-iw/2,z0))
 return R.extrude_xz(name,outline,y0,y1,surf,col(stage),stage,transform=transform)
def merlons(name,axis,c,z,length,spacing=.55,width=.27):
 n=max(2,int(length/spacing));start=-length/2+length/n/2
 for i in range(n):
  p=list(c);p[axis]+=start+i*length/n;p[2]=z+.19
  size=(.28,width,.38) if axis==0 else (width,.28,.38)
  block(name+str(i),p,size,'stone','vaults','defence_detail')

def stairs(name,start,direction,run,rise,width,steps):
 # One connected stepped prism: each riser shares real edges with its treads.
 x,y,z=start;outline=[(0,0),(run,0),(run,rise)]
 for i in range(steps-1,-1,-1):
  outline.append((run*i/steps,rise*(i+1)/steps))
  if i:outline.append((run*i/steps,rise*i/steps))
 def trans(u,v,h):return (x+u,y+v,z+h) if direction=='X' else (x+v,y+u,z+h)
 return R.extrude_xz(name,outline,-width/2,width/2,'stone',col('foundation'),'foundation',trans,'ground')

def foundation():
 scene();root()
 block('GroundPlate',(0,-2.0,.035),(6.98,8.30,.07),'earth','foundation','ground')
 plan=[(-3.25,-4.95),(-1.85,-5.08),(-.57,-4.87),(-.57,-4.03),(.60,-4.03),(.60,-4.75),(2.50,-4.58),(3.27,-3.30),(3.20,.40),(2.40,1.80),(.60,2.12),(-2.50,1.70),(-3.30,.40),(-3.20,-3.50)]
 # Fractured layered rock with a genuine entrance notch for the turning stair.
 v=[];f=[];rr=random.Random(491);N=len(plan)
 for layer in range(4):
  fac=(1.035,.99,1.018,.97)[layer];z=(.07,.30,.54,.78)[layer]
  for x,y in plan:
   # Do not distort the entry notch or change its clear width.
   notch=abs(x)<.65 and y<-4
   jitterx=rr.uniform(-.055,.055) if layer in (1,2) and not notch else 0
   jittery=rr.uniform(-.055,.055) if layer in (1,2) and not notch else 0
   v.append((x if notch else x*fac+jitterx,y if notch else CY+(y-CY)*fac+jittery,z))
 for k in range(3):
  for i in range(N):j=(i+1)%N;f.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
 f += [tuple(reversed(range(N))),tuple(3*N+i for i in range(N))]
 R.mesh('LowRockTerrace',v,f,'rubble',col('foundation'),'foundation','terrain')
 block('CourtPaving',(0,-1.12,.83),(5.72,5.75,.10),'stone','foundation','ground')
 for side in (-1,1):block('CurtainFooting'+str(side),(side*2.90,-1.20,.82),(.44,5.58,.12),'stone','foundation','ground')
 # The first flight turns at a broad landing, then climbs through the notch.
 stairs('LowerFlight',(-1.72,-5.40,.07),'X',1.30,.37,.72,4)
 block('TurningLanding',(-.12,-5.40,.255),(.90,.88,.37),'stone','foundation','ground')
 stairs('UpperFlight',(0,-5.00,.44),'Y',1.02,.44,.88,4)
 block('GateThreshold',(0,-3.91,.86),(1.26,.32,.06),'stone','foundation','ground')
 # A narrow drainage channel is recessed between court and east retaining edge.
 block('DrainBed',(2.66,-2.02,.799),(.11,3.75,.012),'grime','foundation','ground')
 guides=R.collection('Guides_AssassinBrotherhood',scene().collection)
 for n,pos in ANCHORS.items():
  o=bpy.data.objects.new(P+'ANCHOR_'+n,None);guides.objects.link(o);o.location=pos;o.empty_display_size=.12;o['anchor_role']=n
 guides.hide_viewport=guides.hide_render=True
 print('BROTHERHOOD_FOUNDATION_READY')

def walls():
 # Unequal wall heights follow the stepped rocky setting, not four identical towers.
 for side in (-1,1):
  for i,(a,b,h) in enumerate(((-3.96,-1.9,1.55),(-1.9,.0,2.45),(.0,1.52,2.72 if side==-1 else 2.22))):
   x=side*2.90;top=G+h
   block(f'Curtain{side}_{i}',(x,(a+b)/2,G+h/2),(.36,b-a,h),'stone')
   block(f'CurtainCoping{side}_{i}',(x,(a+b)/2,top+.04),(.43,b-a+.05,.10),'stone','vaults','defence_detail')
   merlons(f'CurtainMerlon{side}_{i}_',1,(x,(a+b)/2,0),top+.09,b-a,width=.36)
 for side in (-1,1):
  block('GateWing'+str(side),(side*1.96,-3.95,G+.775),(1.68,.40,1.55),'stone')
  merlons('GateWingMerlon'+str(side),0,(side*1.96,-3.95,0),2.45,1.66,width=.40)
 arch('GuardedGateway',0,-4.15,-3.75,G,2.30,2.95,1.22,1.53,.70,'stone')
 arch('GateBrickReveal',0,-4.19,-4.145,G,1.59,2.50,1.23,1.53,.70,'brick','finish')
 block('GateCrown',(0,-3.95,3.89),(2.39,.48,.13),'stone','vaults','defence_detail')
 merlons('GateCrownMerlon',0,(0,-3.95,0),3.95,2.33,width=.45)
 block('NorthCurtain',(0,1.47,2.02),(5.75,.32,2.28),'stone')
 merlons('NorthMerlon',0,(0,1.47,0),3.16,5.72,width=.33)
 # Gate returns: short heavy supports whose bottoms touch the paved court.
 for side in (-1,1):block('GateButtress'+str(side),(side*.96,-3.62,1.68),(.35,.60,1.60),'brick')
 print('BROTHERHOOD_WALLS_READY')

def command():
 # Two storeys, central vaulted entrance and genuine upper loggia opening.
 x=-.88;y=.08;W=3.40;D=2.42;H=4.10
 block('CommandFloor',(x,y,.94),(W,D,.12),'stone','foundation','ground')
 for side in (-1,1):block('CommandSide'+str(side),(x+side*(W/2-.12),y,G+H/2),(.24,D,H),'plaster')
 block('CommandRear',(x,1.20,G+H/2),(W,.24,H),'brick')
 arch('CommandLowerArch',x,-1.14,-.90,G,W,2.15,1.30,1.32,.70,'brick')
 block('UpperFloor',(x,.03,3.03),(3.39,2.40,.18),'timber','walls','architecture')
 arch('CommandUpperLoggia',x,-1.14,-.90,3.12,W,1.86,1.30,.93,.72,'plaster')
 # Deep framed side recesses are built as a real surrounding opening and inset panel.
 arch('CommandDoorSurround',x,-1.19,-1.14,G,1.82,2.08,1.30,1.32,.70,'carving','finish')
 block('CommandDoor',(x,-.88,1.75),(1.22,.07,1.68),'timber','finish','props')
 for xx in (x-.46,x+.46):R.beam('DoorBrace'+str(xx),(xx,-.925,1.04),(xx,-.925,2.48),.045,'metal',col('finish'))
 # A smaller open lookout is a subordinate defensive building on the east side.
 ring('SmallLookoutWall',2.12,.47,G,.68,.20,2.55,'stone',40,'walls','curved_structure')
 block('LookoutFloor',(2.12,.47,3.40),(1.12,1.12,.09),'timber','vaults','architecture')
 for j in range(8):
  a=j*math.tau/8;block('LookoutMerlon'+str(j),(2.12+.61*math.cos(a),.47+.61*math.sin(a),3.62),(.22,.22,.35),'stone','vaults','defence_detail',a)
 print('BROTHERHOOD_COMMAND_READY')

def roofs():
 # The command roof is a defended terrace with a low inferred dome, not a tall minaret.
 block('CommandRoof',(-.88,.08,5.00),(3.52,2.55,.14),'stone','vaults','architecture')
 for side in (-1,1):block('RoofParapet'+str(side),(-.88+side*1.63,.08,5.24),(.17,2.50,.34),'brick','vaults','defence_detail')
 block('RoofRearParapet',(-.88,1.27,5.24),(3.40,.17,.34),'brick','vaults','defence_detail')
 # Small domed rear chamber, carried on an eight-sided low drum.
 ring('CommandDomeBearing',-.20,.49,5.07,.88,.13,.23,'brick',8,'vaults','architecture')
 profile=[]
 for sh in (0,1):
  indices=range(13) if sh==0 else range(12,-1,-1)
  for i in indices:
   a=(math.pi/2-.02)*i/12;profile.append(((.89-sh*.11)*math.cos(a),(.65-sh*.11)*math.sin(a)))
 revolve('LowCommandDome',(-.20,.49,5.30),profile,'roof',col('vaults'),40)
 # Main lookout canopy physically bears on four timber posts on the roof.
 for x in (-2.24,-1.43):
  for y in (-.55,.36):R.beam('WatchPost'+str(x)+str(y),(x,y,5.07),(x,y,6.10),.075,'timber',col('vaults'),'vaults','architecture')
 block('WatchCanopy',(-1.835,-.095,6.16),(1.10,1.20,.12),'timber','vaults','roof')
 for x in (-2.24,-1.43):R.beam('WatchRail'+str(x),(x,-.55,5.55),(x,.36,5.55),.05,'timber',col('finish'),'finish','props')
 R.beam('WatchCrossRail',(-2.24,-.55,5.55),(-1.43,-.55,5.55),.05,'timber',col('finish'))
 # Supported service-room vaults are low, leaving the courtyard readable.
 for i,(x,y) in enumerate(((-2.22,-2.18),(2.22,-2.35))):
  for side in (-1,1):block(f'Store{i}Wall{side}',(x+side*.43,y,1.49),(.15,1.55,1.22),'stone')
  block(f'Store{i}Rear',(x,y+.71,1.49),(.93,.16,1.22),'brick')
  q=R.vault(f'Store{i}Vault',x,y-.8,y+.8,2.10,.49,.50,.11,'roof',col('vaults'),32,3,stage='vaults');q['role']='roof'
 print('BROTHERHOOD_ROOFS_READY')

def activity():
 c=col('finish')
 # Covered cistern opening and a drawing bucket: a closed source model, not terrain excavation.
 ring('CisternHead',1.35,-1.10,G,.48,.13,.46,'stone',40,'finish','props')
 R.lathe('CisternWater',(1.35,-1.10,G+.05),[(.34,0),(.34,.012)],'ink',c,32,'finish','props')
 for x in (.86,1.84):R.beam('CisternPost'+str(x),(x,-1.10,G),(x,-1.10,2.12),.065,'timber',c)
 R.beam('CisternCrossbar',(.86,-1.10,2.12),(1.84,-1.10,2.12),.085,'timber',c)
 R.beam('CisternRope',(1.35,-1.10,2.12),(1.35,-1.10,1.38),.017,'cloth',c)
 R.lathe('CisternBucket',(1.35,-1.10,1.10),[(.13,0),(.16,.29),(.135,.29),(.11,.045)],'timber',c,24)
 # Supply pallets and jars stay off the gate-to-command route.
 for i in range(5):block('SupplyPallet'+str(i),(-2.18,-2.72+i*.21,.95),(.67,.16,.14),'timber','finish','props')
 for j in range(5):
  x=-2.40+(j%2)*.38;y=-2.62+(j//2)*.34
  R.lathe('StoreJar'+str(j),(x,y,1.02),[(.13,0),(.20,.13),(.21,.43),(.11,.57),(.10,.64)],'pottery',c,24)
 for j in range(3):R.lathe('GrainSack'+str(j),(2.13,-2.88+j*.38,G),[(.13,0),(.22,.18),(.19,.43),(.055,.56),(.08,.59)],'cloth',c,24)
 # Archive activity under the front loggia: ordinary wooden furniture and manuscripts.
 for x in (-1.25,-.50):block('ArchiveDeskLeg'+str(x),(x,-.54,1.16),(.075,.42,.55),'timber','finish','props')
 block('ArchiveDesk',(-.88,-.54,1.47),(1.02,.55,.075),'timber','finish','props')
 block('ArchiveLedger',(-1.00,-.54,1.525),(.38,.31,.035),'paper','finish','props')
 for j in range(4):R.lathe('ArchiveScroll'+str(j),(-.55,-.73+j*.11,1.5075),[(.035,0),(.035,.26)],'paper',c,12)
 # Small wall lamps are unlit props. No new point lights or runtime effects.
 for x in (-1.02,1.02):
  R.beam('GateLampBracket'+str(x),(x,-4.17,2.62),(x,-4.36,2.62),.035,'metal',c)
  block('GateLamp'+str(x),(x,-4.35,2.48),(.15,.14,.24),'metal','finish','props')
 print('BROTHERHOOD_ACTIVITY_READY')

def finish():
 c=col('finish');rr=random.Random(807)
 # Battered retaining piers articulate the wall mass at changes of level.
 for side in (-1,1):
  for j,y in enumerate((-3.70,-1.90,.05)):
   h=(1.62,2.52,2.70 if side==-1 else 2.25)[j]
   lower=[(side*2.86,y-.22,G),(side*3.23,y-.22,G),(side*3.23,y+.22,G),(side*2.86,y+.22,G)]
   upper=[(side*2.86,y-.16,G+h),(side*3.09,y-.16,G+h),(side*3.09,y+.16,G+h),(side*2.86,y+.16,G+h)]
   R.mesh(f'BatteredPier{side}_{j}',lower+upper,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone',col('walls'),'walls','architecture')
 arch('UpperLoggiaReveal',-.88,-1.205,-1.14,3.12,1.66,1.75,1.30,.93,.72,'brick','finish')
 # Brick/tile ornament belongs to the command portal, not every curtain wall.
 for side in (-1,1):
  for j in range(9):block('CommandBlueTile'+str(side)+'_'+str(j),(-.88+side*.82,-1.198,1.10+j*.15),(.10,.024,.105),'ink','finish','trim')
 for j in range(10):block('CommandBrickBand'+str(j),(-2.43+j*.34,-1.19,2.91),(.25,.04,.10),'carving','finish','trim')
 # Sculpted stone courses reinforce the defended silhouette; minor joints are texture.
 for side in (-1,1):
  for j in range(10):
   y=-3.75+j*.48
   block('CurtainFootStone'+str(side)+'_'+str(j),(side*3.10,y,1.00),(.13,.37,.20),'rubble','finish','stone_relief')
 # Restrained textile ownership cues at the gate, command loggia and upper lookout.
 for side in (-1,1):
  R.beam('GateBannerRod'+str(side),(side*.91,-4.19,3.20),(side*.91,-4.49,3.20),.045,'timber',c)
  block('GateOwner'+str(side),(side*.91,-4.43,2.85),(.25,.025,.65),'owner','finish','owner')
 block('CommandOwner',(-.88,-1.22,3.58),(.66,.025,.55),'owner','finish','owner')
 R.beam('CommandBannerRod',(-1.59,-1.22,3.87),(-.17,-1.22,3.87),.045,'timber',c)
 block('WatchOwner',(-1.835,-.59,5.59),(.55,.025,.47),'owner','finish','owner')
 R.beam('WatchBannerRod',(-2.24,-.59,5.84),(-1.43,-.59,5.84),.045,'timber',c)
 # Bring the archive group into the court, east of the unobstructed main approach.
 for o in list(root().all_objects):
  if o.type=='MESH' and 'Archive' in o.name:
   for v in o.data.vertices:v.co+=Vector((1.58,-1.46,0))
 # Localized plaster loss follows the lower exterior, with exposed brick insets.
 for j in range(8):
  x=-2.35+rr.random()*2.95;z=1.03+rr.random()*.3
  block('CommandWear'+str(j),(x,-1.205,z),(.18+rr.random()*.2,.009,.08+rr.random()*.1),'brick','finish','surface_wear')
 s=scene();s['reference_status']='Alamut 11th-13th-century fortified headquarters; compressed layout and roofs interpreted'
 s['rock_height_limit']='15% of healthy height; validate numerically'
 (R.ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n')
 R.show_state();R.view(pos=(13,-20,14),center=(0,-2.0,2.6),distance=12)
 print('BROTHERHOOD_HEALTHY_READY',len(root().all_objects))

def build_step(step):
 if step not in STEPS:raise ValueError(step)
 globals()[step]()
def build_all(reset_owned=False):
 if list(root().all_objects):
  if not reset_owned:raise RuntimeError('Existing canonical source: explicit reset_owned=True required')
  for o in list(scene().objects):
   if o.name.startswith(P):
    me=o.data if o.type=='MESH' else None;bpy.data.objects.remove(o,do_unlink=True)
    if me and not me.users:bpy.data.meshes.remove(me)
 for step in STEPS:build_step(step)
