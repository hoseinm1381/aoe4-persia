"""Interpreted Safavid workshop; original layout within unchanged donor envelope."""
import bpy,math,json,random
from mathutils import Vector
import asset_runner as R
P=R.PREFIX
CONTACTS=[]
ANATOMY={'ground_z':.18,'rear_wall_top':3.15,'side_spring':2.30,'canopy_post_top':2.80,'frame_top':5.32,'layout':'rear vaulted hall, left casting/store bays, right carriage canopy, open work court'}
def c():return bpy.data.collections[P+'healthy_LOD0']
def block(n,pos,size,s='brick',stage='walls',role='architecture',rotation=0):return R.block(n,pos,size,s,c(),stage,role,rotation)
def contact(a,b):CONTACTS.append({'name':a+' to '+b,'lower':a,'upper':b})
def wheel(n,x,y,z,r=.39):
 # Connected annular tyre lies in the XZ plane; no solid disks conceal spokes.
 sides=32;verts=[];faces=[]
 for xx,rr in ((x-.06,r),(x+.06,r),(x-.06,r-.07),(x+.06,r-.07)):
  for i in range(sides):a=i*math.tau/sides;verts.append((xx,y+rr*math.cos(a),z+rr*math.sin(a)))
 for i in range(sides):
  j=(i+1)%sides
  faces.extend([(i,j,j+sides,i+sides),(2*sides+i,3*sides+i,3*sides+j,2*sides+j),(i,2*sides+i,2*sides+j,j),(sides+i,sides+j,3*sides+j,3*sides+i)])
 R.mesh(n+'Tyre',verts,faces,'timber',c(),'finish','wheel')
 for i in range(10):
  a=i*math.tau/10;R.beam(n+'Spoke'+str(i),(x,y,z),(x,y+(r-.055)*math.cos(a),z+(r-.055)*math.sin(a)),.035,'timber',c(),'finish','wheel_spoke')
 R.beam(n+'Hub',(x-.10,y,z),(x+.10,y,z),.15,'timber',c(),'finish','props')
def tube(n,x,y,z,length,radius,surface='metal',rotate=0):
 # Hollow, closed-wall barrel with a real bore; profile lies along Y.
 sides=32;verts=[];faces=[]
 rings=[(0,radius*.8),(length*.10,radius),(length*.18,radius*.89),(length*.70,radius*.68),(length,radius*.76),(length,radius*.48),(.10,radius*.48)]
 for along,rr in rings:
  for i in range(sides):
   a=i*math.tau/sides;xx=rr*math.cos(a);zz=rr*math.sin(a)
   verts.append((x+xx*math.cos(rotate)-along*math.sin(rotate),y+xx*math.sin(rotate)+along*math.cos(rotate),z+zz))
 for j in range(len(rings)-1):
  for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
 # Rear cap closes outer and inner rings without filling the muzzle aperture.
 faces.append(tuple(reversed(range(sides))))
 last=(len(rings)-1)*sides;faces.append(tuple(last+i for i in range(sides)))
 return R.mesh(n,verts,faces,surface,c(),'finish','barrel')
def start():
 R.setup_scene();R.collection(P+'healthy_LOD0',bpy.context.scene.collection)
 block('PavingPlate',(-.28,0,.09),(7.70,8.70,.18),'earth','foundation','ground')
 for i in range(18):
  block('RoutePaver'+str(i),(.6-max(0,min(1,(-3.95+i*.43-.8)/1.5))*.88,-3.95+i*.43,.194),(.95,.36,.028),'stone','foundation','ground')
 block('RearBackWall',(-.28,4.12,1.665),(7.3,.28,2.97),'brick')
 contact('PavingPlate','RearBackWall')
 R.show_state();R.view(center=(-.28,0,1.8),distance=14)
def rear_bay(j=0):
 x=-2.68+j*2.4;n='RearBay'+str(j)
 args=[x,2.44,2.76,.18,1.2,3.15,.74,.83,2.13,.82]
 o=R.gablewall(n+'Door',*args,'plaster',c(),segments=24)
 o['gable_source']=json.dumps({'args':args,'surface':'plaster','orientation':'none'})
 for side in (-1,1):
  block(n+'Bearing'+str(side),(x+side*1.12,3.29,1.665),(.16,1.66,2.97),'brick')
  contact('PavingPlate',n+'Bearing'+str(side))
 args=[x,2.48,4.26,3.15,1.04,.61,.13]
 o=R.vault(n+'Vault',*args,'roof',c(),segments=36,along=6)
 o['vault_source']=json.dumps({'args':args,'orientation':'none','surface':'roof'})
 for side in (-1,1):contact(n+'Bearing'+str(side),n+'Vault')
def left_bay(j=0):
 y=-1.88+j*1.55;n='LeftBay'+str(j)
 fn=lambda xx,yy,zz:(-2.25-yy,y+xx,zz)
 args=[0,-.17,.13,.18,.775,2.30,.67,.53,1.66,.66]
 o=R.gablewall(n+'Arch',*args,'plaster',c(),segments=24,transform=fn)
 o['gable_source']=json.dumps({'args':args,'surface':'plaster','orientation':'left_front','bay_y':y})
 for side in (-1,1):
  block(n+'Bearing'+str(side),(-3.14,y+side*.705,1.24),(1.78,.14,2.12),'brick')
  contact('PavingPlate',n+'Bearing'+str(side))
 block(n+'Back',(-3.96,y,1.24),(.18,1.55,2.12),'brick')
 tf=lambda xx,yy,zz:(yy,y+xx,zz)
 args=[0,-4.05,-2.12,2.30,.635,.53,.14]
 o=R.vault(n+'Vault',*args,'roof',c(),segments=32,along=5,transform=tf)
 o['vault_source']=json.dumps({'args':args,'orientation':'left_roof','bay_y':y,'surface':'roof'})
 for side in (-1,1):contact(n+'Bearing'+str(side),n+'Vault')
def carriage_canopy():
 for i,x in enumerate((1.98,3.27)):
  for j,y in enumerate((-2.85,1.64)):
   n=f'CanopyPost{i}_{j}';block(n,(x,y,1.49),(.14,.14,2.62),'timber','vaults','structure')
   contact('PavingPlate',n)
  n='CanopyLongBeam'+str(i);block(n,(x,-.605,2.90),(.18,4.72,.20),'timber','vaults','structure')
  for j in range(2):contact(f'CanopyPost{i}_{j}',n)
 for j,y in enumerate((-2.85,-1.35,.15,1.64)):
  n='CanopyCross'+str(j);block(n,(2.625,y,3.055),(1.65,.13,.11),'timber','vaults','structure');contact('CanopyLongBeam0',n)
 block('CanopyRoof',(2.625,-.605,3.17),(1.79,4.85,.12),'roof','vaults','architecture');contact('CanopyCross0','CanopyRoof')
def casting():
 # Recess is built into a raised masonry enclosure, without terrain editing.
 block('CastingBed',(-.95,.14,.25),(1.55,1.35,.14),'stone','foundation','ground')
 for side in (-1,1):
  block('PitSide'+str(side),(-.95+side*.72,.14,.47),(.16,1.35,.30),'brick')
  block('PitEnd'+str(side),(-.95,.14+side*.595,.47),(1.3,.16,.30),'brick')
  contact('CastingBed','PitSide'+str(side));contact('CastingBed','PitEnd'+str(side))
 R.lathe('ClayMould',(-.95,.14,.32),[(.22,0),(.24,.17),(.18,.64),(.19,.78),(.13,.78),(.12,.24)],'pottery',c(),32,'finish','mould')
 R.lathe('CoreSpindle',(-.95,.14,.32),[(.035,0),(.035,1.12)],'timber',c(),12,'finish','props')
 contact('CastingBed','ClayMould');contact('CastingBed','CoreSpindle')
 # Low furnace with an arched dark opening and a short vent, not a chimney tower.
 R.archwall('FurnaceFace',-.8,1.32,1.64,.18,1.3,1.5,.65,.48,.42,'brick',c(),segments=24)
 block('FurnaceBack',(-.8,2.04,.93),(1.3,.36,1.5),'brick')
 for side in (-1,1):block('FurnaceSide'+str(side),(-.8+side*.53,1.72,.93),(.24,.8,1.5),'brick')
 block('FurnaceRoof',(-.8,1.72,1.78),(1.3,.94,.20),'brick','vaults')
 R.lathe('FurnaceVent',(-.8,1.72,1.88),[(.24,0),(.22,.42),(.14,.42),(.14,.1)],'brick',c(),16,'vaults','props')
 contact('PavingPlate','FurnaceFace');contact('FurnaceBack','FurnaceRoof');contact('FurnaceRoof','FurnaceVent')
 # Bounded pouring channel connects furnace vicinity to the casting surround.
 R.beam('PouringChannel',(-.80,1.30,.56),(-.95,.72,.56),.11,'pottery',c(),'finish','props')
def equipment():
 # Carriage assembly on the right: wheel bottoms exactly meet the ground.
 for i,x in enumerate((2.15,3.02)):
  block('CarriageRail'+str(i),(x,-.72,.74),(.13,1.7,.22),'timber','finish','props')
 for j,y in enumerate((-1.35,.0)):
  R.beam('CarriageAxle'+str(j),(1.85,y,.57),(3.36,y,.57),.12,'timber',c(),'finish','props')
  for side in (-1,1):wheel(f'Wheel{j}_{side}',2.585+side*.65,y,.57,.39)
 tube('FinishedGun',2.585,-1.58,1.07,1.55,.21)
 for i,x in enumerate((2.15,3.02)):
  block('GunBearing'+str(i),(x,-.65,.96),(.15,.18,.22),'timber','finish','props');contact('CarriageRail'+str(i),'GunBearing'+str(i))
  for j in range(2):contact('CarriageAxle'+str(j),'CarriageRail'+str(i))
 R.beam('GunTrunnion0',(2.08,-.65,1.03),(2.44,-.65,1.03),.08,'metal',c(),'finish','props')
 R.beam('GunTrunnion1',(2.73,-.65,1.03),(3.09,-.65,1.03),.08,'metal',c(),'finish','props')
 for i in range(2):contact('GunBearing'+str(i),'GunTrunnion'+str(i))
 # An unmounted swivel gun with saddle cradle, all static asset geometry.
 block('SwivelBench',(.85,3.3,.69),(1.05,.7,.10),'timber','finish','props')
 for i,x in enumerate((.43,1.27)):
  for j,y in enumerate((3.05,3.55)):block(f'BenchLeg{i}_{j}',(x,y,.41),(.10,.10,.46),'timber','finish','props')
 for side in (-1,1):block('SaddleCradle'+str(side),(.85+side*.25,3.3,.89),(.12,.48,.30),'timber','finish','props')
 tube('SmallSwivelGun',.85,2.86,1.16,.83,.09)
 R.lathe('SwivelPivot',(.85,3.3,.74),[(.055,0),(.055,.37)],'metal',c(),12,'finish','props');contact('SwivelBench','SwivelPivot')
 # Original barrel-pattern lathe and purposeful storage inside left bays.
 for j in range(3):
  R.lathe('ClayJar'+str(j),(-3.2,-1.9+j*.3,.18),[(.12,0),(.24,.15),(.25,.4),(.13,.58),(.10,.58),(.10,.48)],'pottery',c(),24,'finish','props')
 for i in range(8):R.beam('TimberStock'+str(i),(-3.7,-.42+i*.11,.27),(-2.5,-.42+i*.11,.27),.12,'timber',c(),'finish','props')
 for i in range(6):R.lathe('CannonBall'+str(i),(-2.8+i%3*.18,1.0+i//3*.18,.18),[(.01,0),(.09,.04),(.10,.10),(.06,.17),(.01,.19)],'metal',c(),16,'finish','props')
 block('RecordDesk',(-2.8,3.35,.64),(.86,.54,.12),'timber','finish','props')
 for side in (-1,1):block('DeskPedestal'+str(side),(-2.8+side*.3,3.35,.38),(.15,.44,.40),'timber','finish','props')
 block('Ledger',(-2.8,3.35,.735),(.32,.25,.07),'paper','finish','props')
def lifting_frame():
 # Freestanding narrow human-powered tackle frame; all parts follow load-bearing anchors.
 for side in (-1,1):
  x=-.95+side*.95
  block('LiftFoot'+str(side),(x,.14,.28),(.54,.5,.20),'stone','vaults','structure');contact('PavingPlate','LiftFoot'+str(side))
  block('LiftUpright'+str(side),(x,.14,2.74),(.18,.18,4.72),'timber','vaults','structure');contact('LiftFoot'+str(side),'LiftUpright'+str(side))
 block('LiftHeader',(-.95,.14,5.20),(2.3,.24,.20),'timber','vaults','structure')
 for side in (-1,1):contact('LiftUpright'+str(side),'LiftHeader')
 for side in (-1,1):R.beam('LiftBrace'+str(side),(-.95+side*.95,.14,4.15),(-.95+side*.30,.14,5.10),.10,'timber',c(),'vaults','structure')
 # Pulley axle seats into cheeks suspended from the header. Two rope legs
 # and an arced crown form the return path, with a foot-height cleat.
 for side in (-1,1):
  block('PulleyCheek'+str(side),(-.95,.14+side*.09,4.96),(.12,.045,.30),'metal','finish','tackle')
  contact('PulleyCheek'+str(side),'LiftHeader')
 R.beam('PulleyAxle',(-.95,-.01,4.92),(-.95,.29,4.92),.045,'metal',c(),'finish','tackle')
 wheel=R.lathe('PulleyWheel',(0,0,0),[(.12,-.035),(.15,-.022),(.135,0),(.15,.022),(.12,.035)],'timber',c(),24,'finish','tackle')
 for v in wheel.data.vertices:v.co=Vector((-.95+v.co.x,.14+v.co.z,4.92-v.co.y))
 wheel.data.update();R.retile_surface(wheel)
 contact('PulleyAxle','PulleyWheel')
 # One bridged tube follows the entire return/crown/load path.
 path=[Vector((-1.84,.14,1.25)),Vector((-1.085,.14,1.25)),Vector((-1.085,.14,4.92))]
 path += [Vector((-.95+.135*math.cos(math.pi-i*math.pi/12),.14,4.92+.135*math.sin(math.pi-i*math.pi/12))) for i in range(1,13)]
 path.append(Vector((-.815,.14,2.0)))
 verts=[];faces=[]
 for i,pt in enumerate(path):
  tangent=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized()
  u=Vector((0,.0125,0));v=tangent.cross(u).normalized()*.0125
  verts.extend(tuple(pt+u*math.cos(j*math.tau/6)+v*math.sin(j*math.tau/6)) for j in range(6))
 for i in range(len(path)-1):
  for j in range(6):a=i*6+j;b=i*6+(j+1)%6;faces.append((a,b,b+6,a+6))
 faces.extend([tuple(reversed(range(6))),tuple((len(path)-1)*6+j for j in range(6))])
 R.mesh('TackleRope',verts,faces,'cloth',c(),'finish','rope')
 block('TackleCleat',(-1.84,.14,1.25),(.16,.10,.10),'timber','finish','tackle')
 # Continuous faceted hook, not disjoint rods.
 rings=[]
 for i in range(17):
  a=math.pi*.5+i*math.pi*1.45/16;center=Vector((-.815+.12*math.cos(a),.14,1.90+.12*math.sin(a)))
  radial=Vector((math.cos(a),0,math.sin(a)))*.023;tangent=Vector((0,.023,0))
  rings.extend(tuple(center+radial*math.cos(j*math.tau/8)+tangent*math.sin(j*math.tau/8)) for j in range(8))
 f=[]
 for i in range(16):
  for j in range(8):a=i*8+j;b=i*8+(j+1)%8;f.append((a,b,b+8,a+8))
 f.extend([tuple(reversed(range(8))),tuple(16*8+j for j in range(8))]);R.mesh('TackleHook',rings,f,'metal',c(),'finish','hook')
def details():
 for i,x in enumerate((-2.68,-.28,2.12)):
  block('RearOwnerFascia'+str(i),(x,2.415,3.02),(1.3,.035,.22),'owner','finish','owner')
 for i,y in enumerate((-2.2,-.6,1.0)):block('CanopyOwnerCloth'+str(i),(1.8725,y,2.58),(.035,.65,.55),'owner','finish','owner')
 block('FrontCanopyOwnerCloth',(2.625,-2.92,2.72),(.86,.035,.56),'owner','finish','owner')
 # Work residue remains localized to the firing mouth and supply area.
 block('FurnaceSoot',(-.8,1.315,1.31),(.84,.012,.40),'grime','finish','surface_wear')
 R.lathe('FuelBasket',(-3.28,-3.25,.18),[(.19,0),(.24,.14),(.26,.43),(.22,.43),(.20,.10)],'cloth',c(),20,'finish','props')
 R.lathe('FuelBed',(-3.28,-3.25,.28),[(.20,0),(.20,.13)],'grime',c(),16,'finish','props')
 for i in range(8):
  a=i*math.tau/8
  R.lathe('FuelCharcoal'+str(i),(-3.28+.13*math.cos(a),-3.25+.13*math.sin(a),.40),[(.035,0),(.065,.04),(.045,.13)],'grime',c(),8,'finish','props')
 rr=random.Random(1327)
 for i in range(28):
  x=rr.uniform(-1.8,1.4);y=rr.uniform(-3.9,2.1)
  block('WorkWear'+str(i),(x,y,.181),(.12+rr.random()*.25,.16+rr.random()*.25,.002),'grime','finish','surface_wear')
def finish(save=True):
 if save:(R.ROOT/'anchors.json').write_text(json.dumps({'anatomy':ANATOMY,'contacts':CONTACTS,'limits':'Measured source contacts and source envelope only; native clearance deferred.'},indent=2)+'\n')
 R.show_state();R.view(center=(-.28,0,1.8),distance=14)
 if save:R.save()
def build_all(save=True):
 CONTACTS.clear();start()
 for i in range(3):rear_bay(i);left_bay(i)
 carriage_canopy();casting();equipment();lifting_frame();details();finish(save)
