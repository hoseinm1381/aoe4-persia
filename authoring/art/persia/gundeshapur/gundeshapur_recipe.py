"""Gundeshapur recipe: inspect each named phase through live Blender MCP."""
from pathlib import Path
import bpy,bmesh,math,json,random,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
import asset_runner as R
RNG=random.Random(74691)
W=12.8;D=13.44;GROUND=.28
PARTS={};CONTACTS=[]

def cols():
    scene=R.setup_scene();root=R.collection(R.PREFIX+'healthy_LOD0',scene.collection)
    return {stage:R.collection(R.PREFIX+'healthy_'+stage,root) for stage in ('foundation','walls','vaults','finish')}
def add(o):PARTS[o.name]=o;return o
def box(n,c,s,t,stage='walls',role='architecture',rot=0):return add(R.block(n,c,s,t,C[stage],stage,role,rot))
def beam(n,a,b,w,t='timber',stage='finish',role='props'):return add(R.beam(n,a,b,w,t,C[stage],stage,role))
def lathe(n,c,r,t='pottery',sides=24,stage='finish',role='props',cap=True):return add(R.lathe(n,c,r,t,C[stage],sides,stage,role,cap))
def contact(name,a,b,axis,face_a='max',face_b='min',tolerance=.03):
    ba=R.bounds(a);bb=R.bounds(b)
    va=ba[1 if face_a=='max' else 0][axis];vb=bb[1 if face_b=='max' else 0][axis]
    CONTACTS.append({'interface':name,'a':a.name,'b':b.name,'axis':axis,'face_a':face_a,'face_b':face_b,'signed_gap':vb-va,'tolerance':tolerance,'passed':abs(vb-va)<=tolerance})

def phase1():
    global C
    C=cols()
    # One low plinth and open paved court, entirely inside the existing visual bounds.
    plinth=box('Plinth',(0,0,.08),(12.8,13.44,.32),'stone','foundation')
    box('CourtBed',(0,-.4,.25),(7.3,10.4,.10),'earth','foundation')
    hall=add(R.archwall('IwanFacade',0,2.20,2.72,GROUND,5.5,5.12,2.85,2.05,1.73,'plaster',C['walls'],segments=32))
    left=box('HallWestWall',(-2.54,4.32,2.63),(.42,3.20,4.70),'plaster')
    right=box('HallEastWall',(2.54,4.32,2.63),(.42,3.20,4.70),'plaster')
    rear=add(R.archwall('HallRearDoor',0,5.80,6.15,GROUND,5.5,4.70,1.45,1.35,1.02,'plaster',C['walls'],segments=20))
    roof=add(R.vault('HallVault',0,2.72,5.80,4.98,2.33,.39,.18,'roof',C['vaults'],segments=48,along=8))
    contact('hall west wall seats vault',left,roof,2,tolerance=.03)
    domebase=box('DomeChamber',(0,5.0,4.72),(3.08,2.55,.68),'plaster','vaults')
    drum=lathe('DomeDrum',(0,5.0,5.06),[(1.48,0),(1.48,.37),(1.42,.45)],'plaster',40,'vaults','architecture')
    dome=lathe('ReadingDome',(0,5.0,5.50),[(1.44*math.cos(i*math.pi/2/14),1.16*math.sin(i*math.pi/2/14)) for i in range(14)]+[(.035,1.16)],'roof',56,'vaults','architecture')
    contact('dome drum on rear chamber',domebase,drum,2,tolerance=.02)
    contact('dome shell seated on drum',drum,dome,2,tolerance=.02)
    for sign,side in ((-1,'West'),(1,'East')):
        floor=box(side+'WingFloor',(sign*5.05,-1.72,.29),(2.32,7.78,.18),'stone','foundation')
        back=box(side+'WingOuterWall',(sign*6.08,-1.72,1.62),(.26,7.78,2.68),'plaster')
        for j,y in enumerate((-4.60,-2.70,-.80,1.10)):
            o=add(R.archwall(side+f'Bay{j+1}',y,3.77,4.10,GROUND,1.90,2.68,1.48,1.28,.95,'plaster',C['walls'],segments=24,transform=lambda x,yy,z,s=sign:(s*yy,x,z)))
            partition=box(side+f'Partition{j}',(sign*5.09,y-.95,1.62),(2.12,.14,2.68),'plaster')
        box(side+'WingNorthEnd',(sign*5.07,2.10,1.62),(2.28,.22,2.68),'plaster')
        o=add(R.vault(side+'WingVault',sign*5.05,-5.61,2.21,2.96,1.15,.47,.17,'roof',C['vaults'],segments=32,along=12))
        contact(side+' outer wall carries roof',back,o,2,tolerance=.03)
        box(side+'RearConnector',(sign*4.52,2.50,1.42),(3.50,.70,2.28),'plaster')
        box(side+'FrontBoundary',(sign*4.15,-5.95,.68),(4.33,.30,.80),'plaster')
        box(side+'EntryPier',(sign*1.90,-5.95,.96),(.48,.48,1.36),'stone')
        box(side+'EntryCap',(sign*1.90,-5.95,1.69),(.60,.60,.10),'carving','finish')
    for i,(y,z,w) in enumerate(((-6.48,.02,3.50),(-6.29,.11,3.35),(-6.10,.20,3.20))):box('EntranceStep'+str(i),(0,y,z),(w,.37,.18),'stone','foundation')
    R.show_state();R.view();write_step('01-anatomy')
    print('PHASE1_COMPLETE',len(PARTS))

def archrim(name,cx,y,zbase,rx,rz,spring,segments=28,transform=None):
    for i in range(segments):
        a=i*math.pi/segments+.005;b=(i+1)*math.pi/segments-.005
        outline=[(cx+rx*math.cos(a),zbase+spring+rz*math.sin(a)),
                 (cx+(rx+.13)*math.cos(a),zbase+spring+(rz+.13)*math.sin(a)),
                 (cx+(rx+.13)*math.cos(b),zbase+spring+(rz+.13)*math.sin(b)),
                 (cx+rx*math.cos(b),zbase+spring+rz*math.sin(b))]
        add(R.extrude_xz(name+f'_{i:02}',outline,y-.08,y+.035,'brick',C['finish'],'finish',transform,'trim'))

def phase2():
    global C
    C=cols()
    # Vault end infill closes the roof-to-endwall interface.
    for sign,side in ((-1,'West'),(1,'East')):
        outline=[(sign*5.05+1.15*math.cos(i*math.pi/32),2.96+.47*math.sin(i*math.pi/32)) for i in range(33)]
        for yy,label in ((-5.60,'South'),(2.10,'North')):
            add(R.extrude_xz(side+label+'VaultTympanum',outline,yy-.08,yy+.08,'plaster',C['walls']))
    # First repeat module is an arched masonry rim; all copies have independent meshes.
    archrim('IwanVoussoir',0,2.17,GROUND,1.425,1.73,2.05,40)
    for sign,side in ((-1,'West'),(1,'East')):
        for j,y in enumerate((-4.60,-2.70,-.80,1.10)):
            archrim(side+f'Bay{j+1}Rim',y,3.73,GROUND,.74,.95,1.28,20,lambda x,yy,z,s=sign:(s*yy,x,z))
            # Fascia is visible from the courtyard, with four coherent short owner banners.
            box(side+f'Bay{j+1}OwnerFascia',(sign*3.7525,y,2.78),(.035,1.54,.16),'owner','finish','owner')
            for zz in (.53,.68):box(side+f'Bay{j+1}Skirting{zz}',(sign*3.73,y,zz),(.04,1.56,.09),'brick','finish','trim')
        for y in (-5.46,-3.65,-1.75,.15,2.05):
            box(side+f'Buttress_{y}',(sign*6.20,y,1.14),(.28,.44,1.72),'stone','walls')
        box(side+'WingUpperBand',(sign*6.235,-1.72,2.85),(.10,7.80,.18),'carving','finish','trim')
        # Repeated roof ribs and narrow brick courses give shape at game distance.
        for j,y in enumerate([-5.5+i*.32 for i in range(25)]):
            add(R.vault(side+f'RoofRib{j:02}',sign*5.05,y,y+.035,2.96,1.319,.639,.025,'roof',C['finish'],segments=24,along=1,stage='finish'))
        for j,y in enumerate((-4.6,-.8)):
            rod=beam(side+f'BannerRod{j}',(sign*3.62,y-.35,2.75),(sign*3.62,y+.35,2.75),.055)
            verts=[];faces=[];nx=6;ny=7
            for v in range(ny+1):
                for u in range(nx+1):
                    yy=y-.31+.62*u/nx;zz=2.70-.65*v/ny
                    verts.append((sign*(3.60-.055*math.sin(u*math.pi*2/nx)*(v/ny)),yy,zz))
            for v in range(ny):
                for u in range(nx):a=v*(nx+1)+u;faces.append((a,a+1,a+nx+2,a+nx+1))
            cloth=add(R.mesh(side+f'HangingTextile{j}',verts,faces,'owner',C['finish'],'finish','owner'))
            sol=cloth.modifiers.new('Source cloth thickness','SOLIDIFY');sol.thickness=.012
            bpy.context.view_layer.objects.active=cloth;cloth.select_set(True);bpy.ops.object.modifier_apply(modifier=sol.name);cloth.select_set(False)
        box(side+'IwanOwnerPanel',(sign*2.06,2.1875,2.35),(.36,.025,2.32),'owner','finish','owner')
        for z in (.58,4.24):box(side+f'IwanOwnerFrame{z}',(sign*2.06,2.163,z),(.52,.075,.13),'carving','finish','trim')
        box(side+'HallBaseBand',(sign*2.69,4.32,.56),(.12,3.27,.24),'stone','finish','trim')
        box(side+'HallSideCornice',(sign*2.71,4.32,4.90),(.19,3.27,.17),'carving','finish','trim')
    box('IwanCrowningFrieze',(0,2.17,5.21),(5.70,.25,.17),'carving','finish','trim')
    box('IwanCorniceShadow',(0,2.13,5.05),(5.62,.23,.10),'brick','finish','trim')
    # Recessed door and shutter panels; no invented readable historical inscription.
    box('RearDoorInset',(0,6.09,1.19),(1.24,.10,1.80),'timber','finish')
    for sign,side in ((-1,'West'),(1,'East')):
        for y in (3.15,4.40,5.45):
            box(side+f'HighRecess{y}',(sign*2.755,y,3.70),(.025,.46,.71),'timber','finish')
            for j in range(3):box(side+f'RecessScreen{y}_{j}',(sign*2.78,y-.15+j*.15,3.70),(.025,.035,.71),'carving','finish','trim')
    # Courtyard pavers are slightly irregular but sit on the bed.
    verts=[];faces=[]
    for row in range(17):
        for col in range(12):
            x=-3.42+col*.58+(row%2)*.12;y=-5.25+row*.44
            if abs(x)>3.40:continue
            w=.54+RNG.uniform(-.035,.035);dd=.40+RNG.uniform(-.025,.025);z=.315+RNG.uniform(-.008,.008)
            # Narrow real hand-cut edges instead of a global bevel modifier.
            off=len(verts);verts += [(x-w/2,y-dd/2,z-.035),(x+w/2,y-dd/2,z-.035),(x+w/2,y+dd/2,z-.035),(x-w/2,y+dd/2,z-.035),
                                    (x-w/2+.025,y-dd/2+.025,z),(x+w/2-.025,y-dd/2+.025,z),(x+w/2-.025,y+dd/2-.025,z),(x-w/2+.025,y+dd/2-.025,z)]
            faces.extend(tuple(off+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    add(R.mesh('CourtPaving',verts,faces,'stone',C['foundation'],'foundation','ground'))
    # Roof bands on the main barrel remain tied to the actual curve.
    for i,y in enumerate([2.8+j*.25 for j in range(12)]):
        add(R.vault('HallRoofCourse'+str(i),0,y,y+.04,4.98,2.51,.57,.022,'roof',C['finish'],segments=40,along=1,stage='finish'))
    R.show_state();R.view();write_step('02-architectural-detail')
    print('PHASE2_COMPLETE',len(PARTS))

def pot(name,x,y,height,radius,base=GROUND+.03,surface='pottery'):
    rings=[(.48*radius,0),(.78*radius,.05*height),(radius,.30*height),(.94*radius,.60*height),(.65*radius,.79*height),(.55*radius,.90*height),(.62*radius,.94*height),(.62*radius,height),(.47*radius,height),(.46*radius,.88*height),(.48*radius,.82*height)]
    return lathe(name,(x,y,base),rings,surface,28)

def mat(name,x,y,w,d,angle=0,rolled=False):
    if not rolled:
        o=box(name,(x,y,GROUND+.045),(w,d,.045),'cloth','finish','props',angle)
        return o
    # Cylinder axis Y, built from closed rings rather than disconnected stacks.
    v=[];f=[];sides=20
    for yy in (-d/2,d/2):
        for i in range(sides):
            a=i*math.tau/sides;v.append((x+.13*math.cos(a),y+yy,GROUND+.13+.13*math.sin(a)))
    f=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    return add(R.mesh(name,v,f,'cloth',C['finish'],'finish','props'))

def phase3():
    global C
    C=cols()
    # Three activity groups, not a random prop scatter.
    for j,(x,y) in enumerate(((-3.08,1.02),(-4.63,.97))):
        chest=box('DocumentChest'+str(j),(x,y,GROUND+.23),(.83,.48,.46),'timber','finish','props')
        box('DocumentChestLid'+str(j),(x,y,GROUND+.49),(.88,.52,.07),'timber','finish','props')
        for xx in (x-.25,x+.25):box('ChestBinding'+str(j)+str(xx),(xx,y-.251,GROUND+.23),(.04,.035,.45),'metal','finish','props')
    mat('TeachingMat',-2.55,.85,.93,1.25,angle=-.12)
    for j,(x,y) in enumerate(((-3.18,.33),(-3.38,.43),(-3.35,.03))):mat('RolledTeachingMat'+str(j),x,y,.23,.68,rolled=True)
    desk=box('ScribesDesk',(-4.88,1.0,GROUND+.55),(1.30,.61,.12),'timber','finish','props')
    for xx in (-5.37,-4.39):
        for yy in (.78,1.22):box('DeskLeg'+str(xx)+str(yy),(xx,yy,GROUND+.25),(.08,.08,.50),'timber','finish','props')
    for j in range(4):box('DocumentBundle'+str(j),(-5.23+j*.27,1.0,GROUND+.65),(.22,.34,.045),'paper','finish','props',-.04+j*.03)
    pot('InkPot',-4.34,1.09,.15,.08,GROUND+.61,'ink')
    beam('WritingReed',(-4.56,.85,GROUND+.65),(-4.27,.92,GROUND+.65),.014,'timber')
    for j,(x,y,h,r) in enumerate(((3.12,-1.65,.77,.29),(3.42,-1.36,.52,.24),(3.17,-.94,.38,.20),(4.65,-.94,.66,.27),(4.91,-.65,.47,.22),(3.35,-2.05,.35,.23))):pot('ServiceJar'+str(j),x,y,h,r)
    # A sturdy rack anchored to four feet; herb bundles hang below its top rails.
    x0,x1=2.72,3.38;y0,y1=-.10,.97;top=1.66
    posts=[]
    for xx in (x0,x1):
        for yy in (y0,y1):posts.append(beam('HerbRackPost'+str(xx)+str(yy),(xx,yy,GROUND),(xx,yy,top),.07))
    for xx in (x0,x1):beam('HerbRackTop'+str(xx),(xx,y0,top),(xx,y1,top),.065)
    for yy in (y0,y1):beam('HerbRackCross'+str(yy),(x0-.035,yy,top),(x1+.035,yy,top),.065)
    for j in range(5):
        yy=y0+.12+j*.20
        beam('DryingRod'+str(j),(x0,yy,top-.02),(x1,yy,top-.02),.025,'timber')
        for k in range(4):
            xx=x0+.12+k*.13
            beam(f'HerbTwine{j}_{k}',(xx,yy,top-.02),(xx,yy,top-.29),.009,'cloth')
            # Small tapered leafy sprays, not solid green spheres.
            for m in range(4):
                a=m*math.tau/4;cx=xx+.045*math.cos(a);cy=yy+.045*math.sin(a)
                beam(f'HerbStem{j}_{k}_{m}',(xx,yy,top-.24),(cx,cy,top-.49),.012,'leaves')
                for q in (0,1):
                    z=top-.34-q*.07;v=[(cx,cy,z+.05),(cx+.06,cy-.02,z),(cx,cy,z-.05),(cx-.06,cy+.02,z)]
                    leaf=leaf_mesh(f'HerbLeaf{j}_{k}_{m}_{q}',v)
    # Two woven baskets, one partly filled with harvested plants.
    for j,(x,y) in enumerate(((3.13,-2.70),(3.40,-2.42))):
        lathe('WovenBasket'+str(j),(x,y,GROUND+.02),[(.18,0),(.28,.08),(.30,.33),(.32,.39),(.28,.42),(.25,.33)],'cloth',32)
        for ring in range(8):lathe(f'BasketWeave{j}_{ring}',(x,y,GROUND+.06+ring*.043),[(.24+ring*.009,0),(.25+ring*.009,.012),(.24+ring*.009,.018),(.23+ring*.009,.008),(.24+ring*.009,0)],'timber',32,cap=False)
    # Small, grouped supplies near entry, leaving the axial approach open.
    for j,(x,y,z) in enumerate(((3.00,-5.15,GROUND+.19),(3.62,-5.08,GROUND+.19),(3.30,-5.05,GROUND+.58))):
        box('SupplyCrate'+str(j),(x,y,z),(.53,.45,.38),'timber','finish','props',.05-j*.04)
        for xx in (x-.18,x+.18):box(f'CrateBatten{j}_{xx}',(xx,y-.235,z),(.035,.035,.38),'timber','finish','props')
    for j,(x,y) in enumerate(((2.87,-4.43),(3.21,-4.50))):pot('EntryAmphora'+str(j),x,y,.56,.23)
    # A small planted bed supports the scholarly/medical story without a formal garden.
    box('HerbBedSoil',(-2.72,-2.07,GROUND+.05),(1.03,1.67,.10),'earth','finish','props')
    for xx in (-3.27,-2.17):box('HerbBedEdge'+str(xx),(xx,-2.07,GROUND+.10),(.09,1.85,.17),'stone','finish','props')
    for yy in (-2.96,-1.18):box('HerbBedEnd'+str(yy),(-2.72,yy,GROUND+.10),(1.15,.10,.17),'stone','finish','props')
    for j in range(22):
        x=-3.08+RNG.random()*.72;y=-2.76+RNG.random()*1.36
        for k in range(4):
            a=k*math.pi/2;ex=x+.12*math.cos(a);ey=y+.12*math.sin(a)
            beam(f'BedStem{j}_{k}',(x,y,GROUND+.10),(ex,ey,GROUND+.27),.015,'leaves')
            leaf_mesh(f'BedLeaf{j}_{k}',[(x,y,GROUND+.15),(ex+.06,ey,GROUND+.25),(ex,ey,GROUND+.35),(ex-.06,ey,GROUND+.25)])
    # Dust follows usage: localized islands around work groups, not a black surround.
    for j,(x,y,rx,ry) in enumerate(((-3.04,.65,.62,.70),(3.22,-1.6,.65,1.20),(3.28,-5.0,.92,.66),(-2.71,-2.1,.67,1.02),(0,-5.55,1.30,.32))):
        v=[(x+rx*(.88+RNG.random()*.12)*math.cos(i*math.tau/20),y+ry*(.88+RNG.random()*.12)*math.sin(i*math.tau/20),GROUND+.032) for i in range(20)]
        # Thin closed earth patches sit below the paver tops; small edge areas show dirt.
        add(R.mesh('WorkDust'+str(j),v+[(x,y,z-.012) for x,y,z in v],[tuple(range(20)),tuple(reversed(range(20,40)))]+[(i,(i+1)%20,(i+1)%20+20,i+20) for i in range(20)],'grime',C['finish'],'finish','ground'))
    R.show_state();R.view(solid=False);write_step('03-working-courtyard')
    print('PHASE3_COMPLETE',len(PARTS))

def write_step(name):
    rows=[]
    for o in bpy.data.collections[R.PREFIX+'healthy_LOD0'].all_objects:
        if o.type=='MESH':rows.append({'name':o.name,'role':o.get('role'),'stage':o.get('construction_stage'),'surface':o.get('surface'),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)})
    (ROOT/'evidence'/(name+'.json')).write_text(json.dumps({'step':name,'objects':rows,'triangles':sum(r['triangles'] for r in rows),'contacts':CONTACTS,'historical_status':'Informed interpretation, not excavated reconstruction'},indent=2)+'\n')


def leaf_mesh(name,v):
    # Tiny closed leaf cross section; no coincident double-sided polygons.
    vv=v+[(x,y+.008,z) for x,y,z in v]
    return add(R.mesh(name,vv,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'leaves',C['finish'],'finish','props'))


def phase4():
    """Localized healthy wear, tile repairs and purposeful architectural carpentry."""
    global C
    C=cols();rr=random.Random(4119)
    # Geometric terracotta patch courses: shallow curved individual tiles seated in wing roofs.
    for sign,side in ((-1,'West'),(1,'East')):
        for row in range(18):
            yy=-5.34+row*.415
            for k in range(8):
                a=k*math.pi/8+.018;b=(k+1)*math.pi/8-.018
                add(R.vault(side+f'ClayTile{row:02}_{k}',sign*5.05,yy,yy+.36,2.96,1.320,.640,.015,'roof',C['finish'],segments=3,along=1,angle0=a,angle1=b,stage='finish'))
    # Timber doors/screens sit against bay partition backs, with assembled framing.
    for sign,side in ((-1,'West'),(1,'East')):
        for j,y in enumerate((-4.6,-2.7,-.8,1.1)):
            x=sign*5.89
            box(side+f'RoomDoor{j}',(x,y,1.21),(.075,.69,1.82),'timber','finish','props')
            for k in range(6):box(side+f'RoomDoorPlank{j}_{k}',(x-sign*.048,y-.29+k*.116,1.21),(.018,.012,1.76),'ink','finish','trim')
            for z in (.64,1.70):box(side+f'DoorBrace{j}_{z}',(x-sign*.058,y,z),(.045,.74,.062),'timber','finish','trim')
            for yy in (y-.38,y+.38):box(side+f'DoorFrame{j}_{yy}',(x-sign*.04,yy,1.25),(.10,.095,1.98),'timber','finish','trim')
    # Irregular thin mineral loss is attached to the wall faces. Intentional 1 mm overlap;
    # these are surface repair layers, not structural holes in a healthy building.
    def loss(name,cx,cz,w,h,plane,side='front'):
        n=14;shape=[]
        for i in range(n):
            a=i*math.tau/n;r=.80+rr.random()*.20;shape.append((cx+w/2*r*math.cos(a),cz+h/2*r*math.sin(a)))
        if side=='front':o=R.extrude_xz(name,shape,plane-.012,plane+.001,'brick',C['finish'],'finish',role='surface_wear')
        else:o=R.extrude_xz(name,shape,plane-.001,plane+.012,'brick',C['finish'],'finish',transform=lambda u,v,z:(v,u,z),role='surface_wear')
        add(o);o['contact_note']='surface loss applique: 1 mm overlap with original plaster plane'
        # Sparse small islands of surviving plaster interrupt the exposed patch.
        return o
    for j,(x,z,w,h) in enumerate(((-2.50,.67,.28,.39),(2.47,.87,.39,.45),(-1.94,3.94,.30,.18),(1.98,.64,.22,.18))):loss('IwanMaintenanceLoss'+str(j),x,z,w,h,2.20)
    for sign,side in ((-1,'West'),(1,'East')):
        for j,(y,z,w,h) in enumerate(((-4.98,.78,.70,.48),(-2.61,.53,.86,.28),(.64,.73,.49,.41))):loss(side+'OuterPlasterWear'+str(j),y,z,w,h,sign*6.21,'side')
        # Drain outlets and edge gutters, weathering follows water and feet.
        for j,y in enumerate((-4.85,-1.26,1.65)):
            box(side+f'DrainMouth{j}',(sign*6.222,y,.40),(.025,.19,.12),'ink','finish','trim')
            box(side+f'DrainLedge{j}',(sign*6.245,y,.31),(.09,.24,.06),'stone','finish','trim')
        for j in range(22):
            yy=-5.50+j*.347
            box(side+f'FoundationBrick{j}',(sign*6.23,yy,.39),(.10,.31,.13),'brick','finish','trim')
        # Thin repair bricks along the two most-used entrance thresholds.
        for k in range(7):box(side+f'EntryThresholdBrick{k}',(sign*5.07,-5.48+k*.065,.391),(1.96,.05,.022),'stone','finish','trim')
    # Stucco vertical seams are narrow and restrained; they mark maintenance, not ornament.
    for sign,side in ((-1,'West'),(1,'East')):
        for j in range(9):box(side+f'PierBrickEdge{j}',(sign*2.66,2.185,.57+j*.23),(.095,.045,.15),'brick','finish','trim')
    # A small stack of used timbers in the entrance activity group.
    for k in range(5):beam('SupplyTimber'+str(k),(4.15,-4.91,GROUND+.06+k*.065),(4.15,-3.84,GROUND+.06+k*.065),.065,'timber')
    R.show_state();R.view();write_step('04-healthy-wear')
    print('PHASE4_COMPLETE')


def contact_repairs(legacy_panel_offsets=False):
    for o in bpy.data.collections[R.PREFIX+'healthy_LOD0'].all_objects:
        if not legacy_panel_offsets:continue
        if 'OwnerFascia' in o.name:
            sign=-1 if 'West' in o.name else 1
            for v in o.data.vertices:v.co.x+=sign*.0225
        elif 'IwanOwnerPanel' in o.name:
            for v in o.data.vertices:v.co.y+=.0155
        elif 'IwanOwnerFrame' in o.name:
            for v in o.data.vertices:v.co.y+=.018
    global C
    C=cols()
    for sign,side in ((-1,'West'),(1,'East')):
        for j,y in enumerate((-4.6,-.8)):
            for k,yy in enumerate((y-.34,y+.34)):
                beam(side+f'BannerWallBracket{j}_{k}',(sign*3.62,yy,2.75),(sign*3.80,yy,2.75),.045,'timber')


def support_repair():
    # Full rear drum bearing, inside the measured original envelope.
    ob=bpy.data.objects[R.PREFIX+'DomeChamber']
    for v in ob.data.vertices:v.co.y=5+(v.co.y-5)*3.08/2.55
    for name in ('HallWestWall','HallEastWall'):
        ob=bpy.data.objects[R.PREFIX+name]
        for v in ob.data.vertices:v.co.y=2.72+(v.co.y-2.72)*3.48/3.20
    ob=bpy.data.objects[R.PREFIX+'HallRearDoor']
    for v in ob.data.vertices:v.co.y+=.40
    ob=bpy.data.objects[R.PREFIX+'RearDoorInset']
    for v in ob.data.vertices:v.co.y+=.40
    ob=bpy.data.objects[R.PREFIX+'HallVault']
    for v in ob.data.vertices:v.co.y=2.72+(v.co.y-2.72)*3.83/3.08
    global C
    C=cols()
    for j,y in enumerate((5.85,6.10,6.35)):
        add(R.vault('HallRearRoofCourse'+str(j),0,y,y+.04,4.98,2.51,.57,.022,'roof',C['finish'],segments=40,along=1,stage='finish'))

def batch_healthy():
    # Preserve module names in provenance while consolidating repetitive small detail meshes.
    groups=[('HerbLeaf','HerbRackLeaves'),('HerbStem','HerbRackStems'),('HerbTwine','HerbRackTwine'),('BedLeaf','PlantedHerbLeaves'),('BedStem','PlantedHerbStems')]
    groups += [(side+'ClayTile',side+'ClayTileCourses') for side in ('West','East')]
    groups += [(side+'RoofRib',side+'RoofRibs') for side in ('West','East')]
    groups += [('IwanVoussoir','IwanMasonryRim')]
    groups += [(side+f'Bay{i}Rim',side+f'Bay{i}MasonryRim') for side in ('West','East') for i in range(1,5)]
    for prefix,name in groups:
        obs=[o for o in bpy.data.collections[R.PREFIX+'healthy_LOD0'].all_objects if o.name.startswith(R.PREFIX+prefix)]
        if len(obs)<2:continue
        for o in bpy.context.selected_objects:o.select_set(False)
        for o in obs:o.select_set(True)
        bpy.context.view_layer.objects.active=obs[0]
        names=[o.name for o in obs];bpy.ops.object.join();ob=bpy.context.object;ob.name=R.PREFIX+name;ob.data.name=ob.name+'_mesh';ob['module_parts']=json.dumps(names)
        ob.select_set(False)
    print('HEALTHY_BATCHED',len(bpy.data.collections[R.PREFIX+'healthy_LOD0'].all_objects))
