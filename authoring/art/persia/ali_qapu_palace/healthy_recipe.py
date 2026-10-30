"""Ali Qapu ordered source recipe. Dimensions are compressed game-art choices."""
import bpy,math,json,random
from mathutils import Vector
import asset_runner as R

P=R.PREFIX
CONTACTS=[]
ANATOMY={'ground_z':.18,'terrace_top':4.22,'shaft_bottom':4.35,'shaft_top':8.18,'capital_top':8.48,'roof_bearing':8.70,'core_top':13.30,
         'column_x':[-5.25,-3.9375,-1.5,1.5,3.9375,5.25],'column_y':[-5.65,-3.65,-1.45]}

def c():return bpy.data.collections[P+'healthy_LOD0']
def contact(a,b,name=None):CONTACTS.append({'name':name or a+' to '+b,'lower':a,'upper':b})
def block(n,pos,size,s='brick',stage='walls',role='architecture'):
 return R.block(n,pos,size,s,c(),stage,role)
def arch(n,x,y,z,w,h,opening,spring,rise,s='plaster',rotate=0):
 fn=None
 if rotate:
  ca,sa=math.cos(rotate),math.sin(rotate)
  fn=lambda xx,yy,zz:(x+xx*ca-yy*sa,y+xx*sa+yy*ca,zz)
  xx=0;yy0=-.20;yy1=.20
 else:xx=x;yy0=y-.20;yy1=y+.20
 o=R.archwall(n,xx,yy0,yy1,z,w,h,opening,spring,rise,s,c(),segments=24,transform=fn)
 o['construction_stage']='walls' if z<4.3 else 'vaults'
 o['arch_source']=json.dumps({'x':x,'y':y,'z':z,'w':w,'h':h,'opening':opening,'spring':spring,'rise':rise,'surface':s,'rotate':rotate})
 return o
def inset_lattice(n,x,y,z,w,h,rotate=0):
 # The grille is seated inside an actual masonry opening, never on a solid wall.
 ca,sa=math.cos(rotate),math.sin(rotate)
 def pt(xx,yy,zz):return(x+xx*ca-yy*sa,y+xx*sa+yy*ca,z+zz)
 for i in range(7):
  q=R.beam(n+'V'+str(i),pt(-w/2+i*w/6,0,0),pt(-w/2+i*w/6,0,h),.018,'timber',c(),'finish','lattice')
 for i in range(5):R.beam(n+'H'+str(i),pt(-w/2-.10,0,i*h/4),pt(w/2+.10,0,i*h/4),.018,'timber',c(),'finish','lattice')
def start():
 R.setup_scene();R.collection(P+'healthy_LOD0',bpy.context.scene.collection)
 block('PavingPlate',(0,0,.09),(11.55,12.84,.18),'stone','foundation','ground')
 # Three primary solid masses are made from walls/openings, not filled boxes.
 block('TerraceFloor',(0,-2.95,4.11),(11.1,6.4,.22),'stone','vaults')
 # Side walls carry the porch deck continuously to the ground.
 for side in (-1,1):
  n='BaseSide'+str(side)
  block(n,(side*5.35,-2.95,2.09),(.40,6.4,3.82),'brick')
  contact('PavingPlate',n);contact(n,'TerraceFloor')
 R.show_state();R.view(center=(0,0,5.8),distance=23)
def gateway():
 arch('MainGateway',0,-6.0,.18,4.1,3.82,2.65,2.10,1.25)
 for side in (-1,1):
  for level in (0,1):
   n=f'GateSide{side}Level{level}'
   arch(n,side*3.22,-6.0,.18+level*1.91,2.34,1.91,1.12,1.02,.56)
   inset_lattice(n+'Lattice',side*3.22,-5.98,.42+level*1.91,1.02,.90)
  block('GateOuterPier'+str(side),(side*4.97,-6.0,2.09),(.84,.4,3.82),'plaster')
 contact('PavingPlate','MainGateway');contact('MainGateway','TerraceFloor')
 # A deep, connected barrel vault over the through-passage.
 R.vault('GatewayBarrel',0,-5.8,.28,2.28,1.325,1.05,.18,'brick',c(),segments=32,along=8)
 for side in (-1,1):
  block('PassageBearing'+str(side),(side*1.42,-2.75,1.23),(.19,6.1,2.10),'brick')
  contact('PavingPlate','PassageBearing'+str(side));contact('PassageBearing'+str(side),'GatewayBarrel')
def rear_mass():
 levels=[.18,2.18,4.22,6.38,8.65,10.83,13.10]
 # Front and rear facade: three structural bays per floor, each with real reveals.
 for level,(z0,z1) in enumerate(zip(levels,levels[1:])):
  for front,y in [('Front',.25),('Rear',6.10)]:
   if level==5:continue
   for j,x in enumerate((-2.8,0,2.8)):
    n=f'Core{front}Level{level}Bay{j}'
    width=1.90 if level==4 else (2.25 if level==0 and j==1 else .94)
    spring=2.15 if level==4 else (1.03 if level else 1.05);rise=1.40 if level==4 else (.54 if width<2 else .70)
    arch(n,x,y,z0,2.8,(13.10-z0) if level==4 else z1-z0,width,spring,rise)
    if level or j!=1:inset_lattice(n+'Lattice',x,y,z0+.24,width*.88,2.52 if level==4 else .88)
    if level==4:
     block(n+'NicheFascia',(x,y-.215 if front=='Front' else y+.215,12.82),(2.5,.025,.19),'ink','finish','tile_detail')
  for side in (-1,1):
   for j,y in enumerate((1.225,3.175,5.125)):
    n=f'CoreSide{side}Level{level}Bay{j}'
    arch(n,side*4.0,y,z0,1.95,z1-z0,.76,1.02,.48,rotate=math.pi/2)
    inset_lattice(n+'Lattice',side*4.0,y,z0+.23,.68,.83,rotate=math.pi/2)
  # Floor diaphragms stop below/above the ground passage rather than filling it.
  if level:
   block('CoreFloor'+str(level),(0,3.175,z0-.05),(8.4,6.25,.10),'timber','walls' if level<2 else 'vaults')
 block('CoreRoof',(0,3.175,13.20),(8.4,6.25,.20),'roof','vaults')
 for side in (-1,1):
  block('CoreParapetSide'+str(side),(side*4.09,3.175,13.34),(.18,6.25,.28),'brick','vaults')
 for y in (.14,6.21):block('CoreParapet'+str(y),(0,y,13.34),(8.35,.18,.28),'brick','vaults')
 contact('CoreRoof','CoreParapetSide1')
def column_module(row=0,index=0):
 x=ANATOMY['column_x'][index];y=ANATOMY['column_y'][row];n=f'Col{row}_{index}'
 R.lathe(n+'Base',(x,y,4.22),[(.22,0),(.22,.06),(.15,.13)],'stone',c(),8,'vaults','column_base')
 R.lathe(n+'ColumnShaft',(x,y,4.35),[(.14,0),(.14,.12),(.085,3.83)],'timber',c(),8,'vaults','column')
 R.lathe(n+'Capital',(x,y,8.18),[(.085,0),(.11,.09),(.19,.25),(.24,.30)],'carving',c(),8,'vaults','capital')
 contact('TerraceFloor',n+'Base');contact(n+'Base',n+'ColumnShaft');contact(n+'ColumnShaft',n+'Capital')
def roof():
 for row,y in enumerate(ANATOMY['column_y']):
  n='RoofLongBeam'+str(row);block(n,(0,y,8.59),(11.38,.24,.22),'timber','vaults')
  for i in range(6):contact(f'Col{row}_{i}Capital',n)
 for j,x in enumerate(ANATOMY['column_x']):
  n='RoofCrossBeam'+str(j);block(n,(x,-2.70,8.77),(.18,6.42,.14),'timber','vaults','roof_frame')
  contact('RoofLongBeam0',n)
 # Shallow closed hipped roof, tied into the rear masonry face.
 v=[(-5.73,-6.16,8.84),(5.73,-6.16,8.84),(5.73,.48,8.84),(-5.73,.48,8.84),
    (-4.98,-5.42,9.25),(4.98,-5.42,9.25),(4.98,.25,9.25),(-4.98,.25,9.25),
    (-5.73,-6.16,8.94),(5.73,-6.16,8.94),(5.73,.48,8.94),(-5.73,.48,8.94)]
 f=[(0,3,2,1),(8,9,5,4),(9,10,6,5),(10,11,7,6),(11,8,4,7),(4,5,6,7),(0,1,9,8),(1,2,10,9),(2,3,11,10),(3,0,8,11)]
 R.mesh('TerraceRoof',v,f,'roof',c(),'vaults','architecture')
 contact('RoofCrossBeam0','TerraceRoof')
 # Shallow supported coffer inserts under roof, small enough to remain subordinate.
 for i in range(20):
  for j in range(10):
   x=-5.24+i*.55;y=-5.76+j*.60
   block(f'RoofCoffer{i}_{j}',(x,y,8.855),(.48,.52,.03),'carving','finish','roof_relief')
def details():
 # Original patterned tile panels are framed by masonry, rather than floating signage.
 for y in (-6.211,6.311):
  for x in (-3.20,0,3.20):
   block('TilePanel'+str(x)+'_'+str(y),(x,y,3.78),(2.00,.022,.24),'ink','finish','tile_detail')
 for side in (-1,1):
  for z in (2.12,4.18,6.34,8.61,10.79,13.08):
   block(f'BeltSide{side}_{z}',(side*4.22,3.175,z),(.055,6.17,.10),'carving','finish','trim')
 for i in range(46):
  x=-5.55+i*.246
  block('RoofDentil'+str(i),(x,-6.13,8.93),(.12,.16,.22),'timber','finish','roof_relief')
 for i,x in enumerate((-3.7,0,3.7)):
  block('FrontOwnerCloth'+str(i),(x,-6.22,3.15),(.66,.035,.90),'owner','finish','owner')
 for side in (-1,1):
  block('SideOwnerCloth'+str(side),(side*4.24,3.3,10.25),(.035,.75,1.0),'owner','finish','owner')
 # Recess the terrace slab before seating its basin liner and raised coping.
 floor=bpy.data.objects[R.PREFIX+'TerraceFloor']
 cutter=R.block('BasinCutter',(0,-3.1,4.30),(1.38,1.0,.30),'stone',c())
 bpy.context.view_layer.objects.active=floor;floor.select_set(True)
 modifier=floor.modifiers.new('Recessed basin','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
 bpy.ops.object.modifier_apply(modifier=modifier.name)
 bpy.data.objects.remove(cutter,do_unlink=True);R.retile_surface(floor)
 # The bottom is below slab top 4.22; coping overlaps its real pocket edge.
 for sx in (-1,1):block('BasinRimX'+str(sx),(sx*.77,-3.10,4.28),(.16,1.32,.12),'stone','finish')
 for sy in (-1,1):block('BasinRimY'+str(sy),(0,-3.10+sy*.58,4.28),(1.4,.16,.12),'stone','finish')
 block('BasinBottom',(0,-3.1,4.155),(1.38,1.0,.01),'metal','finish','props')
 for k,(x,y) in enumerate(((-2.8,-6.30),(3.05,-6.30))):
  block('Chest'+str(k),(x,y,.42),(.65,.22,.48),'timber','finish','props');contact('PavingPlate','Chest'+str(k))
  for j in range(5):
   R.lathe(f'Carpet{k}_{j}',(x-.2+j*.10,y+.22,.18),[(.05,0),(.06,.42),(.05,.46)],'cloth',c(),16,'finish','props')
 for side in (-1,1):
  block('GuardRackFoot'+str(side),(side*4.1,-6.29,.27),(.6,.22,.18),'timber','finish','props')
  for j in range(3):R.beam(f'GuardSpear{side}_{j}',(side*4.1-.15+j*.15,-6.29,.36),(side*4.1-.15+j*.15,-6.29,1.65),.025,'timber',c(),'finish','props')
 # Wear is concentrated at the route and bases; no broad floating dirt plates.
 rr=random.Random(1821)
 for i in range(42):
  x=rr.choice([-1,1])*rr.uniform(1.65,4.8);y=rr.uniform(-5.4,5.7)
  block('WornPaver'+str(i),(x,y,.181),(.16+rr.random()*.3,.14+rr.random()*.2,.002),'grime','finish','surface_wear')
def finish(save=True):
 # Reconstruct the complete contact list independently of interactive step order.
 CONTACTS.clear()
 for side in (-1,1):
  contact('PavingPlate','BaseSide'+str(side));contact('BaseSide'+str(side),'TerraceFloor')
  contact('PavingPlate','PassageBearing'+str(side));contact('PassageBearing'+str(side),'GatewayBarrel')
 contact('PavingPlate','MainGateway');contact('MainGateway','TerraceFloor')
 for row in range(3):
  for i in range(6):
   n=f'Col{row}_{i}'
   for a,b in [('TerraceFloor',n+'Base'),(n+'Base',n+'ColumnShaft'),(n+'ColumnShaft',n+'Capital'),(n+'Capital','RoofLongBeam'+str(row))]:contact(a,b)
 for j in range(6):contact('RoofLongBeam0','RoofCrossBeam'+str(j))
 contact('RoofCrossBeam0','TerraceRoof');contact('CoreRoof','CoreParapetSide1')
 for k in range(2):contact('PavingPlate','Chest'+str(k))
 if save:(R.ROOT/'anchors.json').write_text(json.dumps({'anatomy':ANATOMY,'contacts':CONTACTS,'coordinate_contract':'Blender Z up, ground=0.18; measured decoded donor axes match this source convention; source bounds only.'},indent=2)+'\n')
 R.show_state();R.view(center=(0,0,6),distance=23)
 if save:R.save()
def build_all(save=True):
 start();gateway();rear_mass()
 for row in range(3):
  for i in range(6):column_module(row,i)
 roof();details();finish(save)
