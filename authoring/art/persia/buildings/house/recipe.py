"""Original Persian domestic architecture. Staged source recipe, no native edits.

House plan/age choices are explicit here; generic support never chooses massing.
Coordinates are authored Blender metres, with a conservative first-body envelope.
"""
from pathlib import Path
import sys,math,json,random
import bpy,bmesh
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'house')
F=.14
ANCHORS={}
CONTRACTS=[]
CURRENT='A1a'

# Open courts and unequal room arrangements are intentional original game-art
# interpretations; no modern house is asserted to be a medieval elevation.
PLANS={
 'a':{'rooms':[(-.15,1.22,3.98,1.86),(-1.46,-.79,1.36,2.16)],'entry':(.44,-2.57),'work':(1.30,-.86),'court':(.43,-.47)},
 'b':{'rooms':[(-.82,1.38,2.64,1.54),(1.48,.55,1.34,3.20)],'entry':(-.25,-2.57),'work':(-1.18,-.85),'court':(-.37,-.39)},
 'c':{'rooms':[(-1.22,.58,1.80,3.34),(1.24,1.35,1.72,1.80)],'entry':(.48,-2.57),'work':(1.24,-.85),'court':(.25,-.24)},
}

def room_height(index,age):
    if index==0:return {1:2.15,2:2.20,3:2.60,4:4.10}[age]
    return {1:2.01,2:2.20,3:1.92,4:1.92}[age]

def door_height(index,age):return min(1.95,room_height(index,age)-.22)

def root(key=None,state='healthy',lod=0):
    return R.collection(R.PREFIX+(key or CURRENT)+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)

def col(role):return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,root())

def tag(o,stage,role,group=''):
    o['body_key']=CURRENT;o['construction_stage']=stage;o['role']=role
    if group:o['structural_group']=group
    return o

def B(name,xyz,size,surface='plaster',stage='walls',role='architecture',group=''):
    return tag(R.block(CURRENT+'_'+name,xyz,size,surface,col(role),stage,role),stage,role,group)

def wall(name,x,y,w,d,h,surface='plaster',bottom=F,group=''):
    return B(name,(x,y,bottom+h/2),(w,d,h),surface,'walls','architecture',group)

def contact(name,a,b,axis,target=0,tolerance=.003):
    CONTRACTS.append({'body':CURRENT,'name':name,'a':a.name,'b':b.name,'axis':axis,'target':target,'tolerance':tolerance})

def setup():
    R.setup_scene();R.view(pos=(12,-15,13),center=(0,-.2,1.1),distance=10,solid=True)
    s=bpy.context.scene;s['historical_basis']='Nishapur excavation domestic court organization; later regional domestic porch comparisons. See HOUSE_PILOT_EVIDENCE.md. Age progression is artistic.'

def foundation(key='A1a'):
    global CURRENT
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body already exists; explicit reset required')
    outline=[(-2.20,-2.93),(-1.75,-3.04),(.33,-3.065),(2.17,-2.91),(2.275,-1.18),(2.22,1.76),(1.94,2.49),(-.62,2.565),(-2.17,2.37),(-2.275,.48)]
    verts=[(x,y,z) for z in (-.04,.11) for x,y in outline];n=len(outline)
    ground=tag(R.mesh(CURRENT+'_EarthBed',verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'earth',col('ground'),'foundation','ground'),'foundation','ground')
    inner=[(x*.94,-.25+(y+.25)*.94) for x,y in outline]
    vs=[(x,y,z) for z in (.09,.14) for x,y in inner]
    paving=tag(R.mesh(CURRENT+'_CourtBase',vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'earth',col('ground'),'foundation','ground'),'foundation','ground')
    for index,(x,y,w,d) in enumerate(PLANS[key[-1]]['rooms']):
        g='room_'+str(index);opening=min(.83,w*.37);piece=(w-opening)/2;front=y-d/2+.10
        for label,xx,yy,ww,dd in [('Back',x,y+d/2-.10,w,.24),('West',x-w/2+.10,y,.24,d-.40),('East',x+w/2-.10,y,.24,d-.40)]+[('Front'+str(side),x+side*(opening/2+piece/2),front,piece,.24) for side in [-1,1]]:
            B(g+'_Footing'+label,(xx,yy,F+.0175),(ww,dd,.075),'brick','foundation','ground',g)
    ANCHORS[key]={'ground_top':F,'native_body_key':key,'court':PLANS[key[-1]]['court'],'entry':PLANS[key[-1]]['entry'],'chosen_horizontal_bounds':[[-2.275,-3.065],[2.275,2.565]],'main_wall_top':F+room_height(0,int(key[1]))}
    print('FOUNDATION',key,'top',F)

def room(index,age,roof=True):
    x,y,w,d=PLANS[CURRENT[-1]]['rooms'][index];t=.20
    h=room_height(index,age)
    surface='plaster';g='room_'+str(index)
    # Thick walls bound a real room; opening faces the visible front court.
    back=wall(g+'_Back',x,y+d/2-t/2,w,t,h,surface,group=g)
    west=wall(g+'_West',x-w/2+t/2,y,t,d-.40,h,surface,group=g)
    if age==4 and index==0 and CURRENT[-1]=='c':
        # An occupied upper-side window breaks the long domestic facade. This is
        # an authored regional interpretation, not an excavated exact aperture.
        wy=.90;ww=.62;wb=F+2.72;wh=.74;cx=x+w/2-t/2
        east=wall(g+'_EastLower',cx,y,t,d-.40,wb-F,surface,group=g)
        wall(g+'_EastHead',cx,y,t,d-.40,F+h-(wb+wh),surface,bottom=wb+wh,group=g)
        ymin=y-(d-.40)/2;ymax=y+(d-.40)/2
        for label,a,b in [('Front',ymin,wy-ww/2),('Rear',wy+ww/2,ymax)]:
            wall(g+'_EastWindowPier'+label,cx,(a+b)/2,t,b-a,wh,surface,bottom=wb,group=g)
        B(g+'_SideWindowShutter',(cx-.07,wy,wb+wh/2),(.045,ww*.85,wh*.90),'timber','finish','fittings',g)
        B(g+'_SideWindowSill',(cx+.015,wy,wb-.025),(.29,ww+.12,.05),'stone','walls','architecture',g)
        for side in [-1,1]:B(g+'_SideWindowJamb'+str(side),(cx+.105,wy+side*(ww/2-.025),wb+wh/2),(.035,.05,wh-.10),'timber','finish','fittings',g)
        for zz in [wb+.025,wb+wh-.025]:B(g+'_SideWindowFrame'+str(zz),(cx+.105,wy,zz),(.035,ww,.05),'timber','finish','fittings',g)
    else:east=wall(g+'_East',x+w/2-t/2,y,t,d-.40,h,surface,group=g)
    for label,part in [('Back',back),('West',west),('East',east)]:
        contact(g+'_Foundation'+label,part,bpy.data.objects[R.PREFIX+CURRENT+'_'+g+'_Footing'+label],'bottom-top',target=-.055)
    opening=min(.83,w*.37);doorh=door_height(index,age);front=y-d/2+t/2
    piece=(w-opening)/2
    for side in [-1,1]:
        pier=wall(g+'_FrontPier'+str(side),x+side*(opening/2+piece/2),front,piece,t,h,surface,group=g)
        contact(g+'_FoundationFront'+str(side),pier,bpy.data.objects[R.PREFIX+CURRENT+'_'+g+'_FootingFront'+str(side)],'bottom-top',target=-.055)
    floorh=2.05
    headh=(floorh+.10-doorh) if age>=3 and index==0 else h-doorh
    lintel=wall(g+'_DoorHead',x,front,opening,t,headh,surface,bottom=F+doorh,group=g)
    sill=B(g+'_DoorSill',(x,front-.03,F+.025),(opening+.12,.34,.05),'stone','foundation','ground',g)
    leaf=B(g+'_RecessedDoor',(x,front+.10,F+doorh*.48),(opening*.82,.045,doorh*.96),'timber','finish','fittings',g)
    # Tiny explicit wood frame: both posts meet the sill and lintel.
    for side in [-1,1]:
        B(g+'_DoorJamb'+str(side),(x+side*(opening*.46),front-.105,F+.05+(doorh-.10)/2),(.055,.04,doorh-.10),'timber','finish','fittings',g)
    B(g+'_DoorLintel',(x,front-.105,F+doorh-.025),(opening,.04,.05),'timber','finish','fittings',g)
    if age>=3 and index==0:
        # Actual upper opening through the facade, with a seated wooden shutter.
        if age==4:
            upper=R.archwall(CURRENT+'_'+g+'_UpperHead',x,front-t/2,front+t/2,F+floorh+.10,opening+.12,h-floorh-.10,opening,h-floorh-.54,.28,surface,col('architecture'),segments=12)
            tag(upper,'walls','architecture',g)
        else:wall(g+'_UpperHead',x,front,opening,t,.16,surface,bottom=F+h-.16,group=g)
        wh=h-floorh-.26
        B(g+'_UpperShutter',(x,front+.10,F+floorh+.10+wh/2),(opening*.84,.045,wh),'timber','finish','fittings',g)
        B(g+'_UpperSill',(x,front-.02,F+floorh+.05),(opening+.12,.31,.10),'stone','walls','architecture',g)
        if CURRENT[-1]=='c' and age==4:
            # A real internal stairwell in this narrow house replaces an external
            # stair that would collide with its front porch/plot boundary.
            x0=x-w/2+.10;x1=x+w/2-.10;y0=y-d/2+.10;y1=y+d/2-.10
            gapx0=x-w/2+.20;gapx1=gapx0+.52;gapy0=-.74;gapy1=1.60
            for label,xa,xb,ya,yb in [('EastFloor',gapx1,x1,y0,y1),('WestLedger',x0,gapx0,y0,y1),('FrontLanding',gapx0,gapx1,y0,gapy0),('RearLanding',gapx0,gapx1,gapy1,y1)]:
                B(g+'_'+label,((xa+xb)/2,(ya+yb)/2,F+floorh-.05),(xb-xa,yb-ya,.10),'timber','walls','architecture',g)
            for j in range(13):B('InternalStair'+str(j),(gapx0+.225,-.65+j*.18,F+(j+1)*floorh/26),(.45,.18,(j+1)*floorh/13),'stone','walls','architecture','stair')
        else:B(g+'_UpperFloor',(x,y,F+floorh-.05),(w-.20,d-.20,.10),'timber','walls','architecture',g)
    if roof:room_roof(index,age,h)
    return {'back':back,'west':west,'east':east,'head':lintel,'sill':sill,'door':leaf}

def room_roof(index,age,h=None):
    x,y,w,d=PLANS[CURRENT[-1]]['rooms'][index];g='room_'+str(index)
    if h is None:
        h=room_height(index,age)
    z=F+h
    if age==2 and index==0:
        # A shallow vault runs along the room width; transform its cross-section
        # so the spring bears on the front/back walls, not in empty air.
        tr=lambda u,v,zz:(x+v,y+u,zz)
        v=R.vault(CURRENT+'_'+g+'_Vault',0,-w/2,w/2,z,(d-.20)/2,.40,.12,'roof',col('roofs'),segments=24,along=3,transform=tr,stage='vaults')
        tag(v,'vaults','roofs',g)
        # Closed end spandrels carry the vault at both ends.
        for side in [-1,1]:
            outline=[(-d/2+.10,z),(d/2-.10,z)]+[((d-.20)/2*math.cos(a),z+.40*math.sin(a)) for a in [j*math.pi/24 for j in range(1,24)]]
            ob=R.extrude_xz(CURRENT+'_'+g+'_VaultEnd'+str(side),outline,x+side*w/2-.04,x+side*w/2+.04,'plaster',col('roofs'),'vaults',lambda u,v,zz:(v,y+u,zz),'roofs');tag(ob,'vaults','roofs',g)
    else:
        # The A4a upper porch meets this side-wing roof at one elevation. Split
        # the roof around the porch instead of stacking coplanar slab faces.
        porch_rect=None
        if age==4 and index==1:
            mx,my,mw,md=PLANS[CURRENT[-1]]['rooms'][0];py=my-md/2-.42
            porch_rect=(mx-mw*.4,mx+mw*.4,py-.46,py+.46)
        access_rect=None
        if age==3 and index==1 and CURRENT[-1]!='c':
            mx,my,mw,md=PLANS[CURRENT[-1]]['rooms'][0]
            stairx=x+w/2+.25 if x<0 else x-w/2-.25
            cy=my-md/2-.88-.07
            access_rect=(min(stairx-.22,x+w/2-.16) if x<0 else stairx-.22,max(stairx+.22,x-w/2+.16) if x>0 else stairx+.22,cy-.24,cy+.24)
        def pieces(name,xx,yy,ww,dd,zz,hh,surface,role):
            bounds=(xx-ww/2,xx+ww/2,yy-dd/2,yy+dd/2)
            rects=[bounds]
            clip=porch_rect or (access_rect if 'Parapet' in name else None)
            if clip:
                a,b,c,e=bounds;p,q,r,s=clip
                ix0,ix1=max(a,p),min(b,q);iy0,iy1=max(c,r),min(e,s)
                if ix1>ix0 and iy1>iy0:
                    rects=[v for v in [(a,ix0,c,e),(ix1,b,c,e),(ix0,ix1,c,iy0),(ix0,ix1,iy1,e)] if v[1]-v[0]>.0001 and v[3]-v[2]>.0001]
            return [B(name+('_JointPart'+str(j) if len(rects)>1 else ''),((a+b)/2,(c+e)/2,zz),(b-a,e-c,hh),surface,'vaults',role,g) for j,(a,b,c,e) in enumerate(rects)]
        caps=pieces(g+'_Roof',x,y,w+.05,d+.05,z+.065,.13,'roof','roofs')
        back=bpy.data.objects[R.PREFIX+CURRENT+'_'+g+'_Back']
        for j,cap in enumerate(caps):
            lo,hi=R.bounds(cap);blo,bhi=R.bounds(back)
            if min(hi[0],bhi[0])-max(lo[0],blo[0])>.01 and min(hi[1],bhi[1])-max(lo[1],blo[1])>.01:contact(g+'_RoofBearing'+str(j),cap,back,'bottom-top')
        # Light parapet follows an occupied flat-roof perimeter.
        for side in [-1,1]:
            pieces(g+'_ParapetX'+str(side),x+side*(w/2-.07),y,.14,d,z+.205,.15,'plaster','roofs')
            pieces(g+'_ParapetY'+str(side),x,y+side*(d/2-.07),w-.28,.14,z+.205,.15,'plaster','roofs')
        # Roof joists terminate within the bearing walls; visible ends are modest.
        for i in range(max(2,int(w/.43))):
            xx=x-w/2+.22+i*(w-.44)/max(1,max(2,int(w/.43))-1)
            B(g+'_Joist'+str(i),(xx,y,z-.04),(.075,d+.14,.08),'timber','vaults','fittings',g)
    if age==4 and index==0:porch(x,y-d/2-.42,w*.80,F+2.05,g)

def porch(x,y,w,z,g):
    # Timber porch has a masonry floor, post bases, actual column bearings and
    # a roof built from the top beam, rather than separately eyeballed pieces.
    floor=B(g+'_PorchFloor',(x,y,z-.06),(w,.92,.12),'stone','vaults','architecture',g)
    count=2 if w<2.0 else 4
    bearing=B(g+'_PorchLowerBeam',(x,y-.35,z-.29),(w+.10,.18,.14),'timber','walls','architecture',g)
    ledger=B(g+'_PorchWallLedger',(x,y+.35,z-.17),(w,.14,.10),'timber','walls','architecture',g)
    for j in range(max(3,int(w/.45))):
        xx=x-w/2+.08+j*(w-.16)/max(1,max(3,int(w/.45))-1)
        joist=B(g+'_PorchFloorJoist'+str(j),(xx,y,z-.17),(.075,.92,.10),'timber','walls','fittings',g)
        contact(g+'_PorchFloorBearing'+str(j),joist,floor,'top-bottom')
        contact(g+'_PorchJoistBeam'+str(j),joist,bearing,'bottom-top')
    contact(g+'_PorchLedgerFloor',ledger,floor,'top-bottom')
    for i in [0,count-1]:
        xx=x-w/2+.10+i*(w-.20)/(count-1)
        lower=B(g+'_PorchLowerSupport'+str(i),(xx,y-.35,F+(z-.36-F)/2),(.15,.15,z-.36-F),'timber','walls','architecture',g)
        contact(g+'_PorchLowerBearing'+str(i),lower,bearing,'top-bottom')
    posttop=z+1.90
    for i in range(count):
        xx=x-w/2+.10+i*(w-.20)/(count-1)
        post=B(g+'_PorchPost'+str(i),(xx,y-.35,z+.95),(.095,.095,1.90),'timber','vaults','architecture',g)
        contact(g+'_PorchPostFoot'+str(i),post,floor,'bottom-top')
    beam=B(g+'_PorchBeam',(x,y-.35,posttop+.055),(w+.10,.14,.11),'timber','vaults','architecture',g)
    shade=B(g+'_PorchShade',(x,y,posttop+.14),(w+.16,1.04,.06),'roof','vaults','roofs',g)
    for i in range(7):B(g+'_PorchRafter'+str(i),(x-w/2+i*w/6,y,posttop+.10),(.055,1.02,.07),'timber','vaults','fittings',g)
    # Source owner textile is short and supported along the roof edge.
    B(g+'_PorchOwner',(x,y-.48,posttop-.05),(w*.65,.025,.16),'owner','finish','owner',g)

def first_room():
    age=int(CURRENT[1]);room(0,age,roof=False)
    print('FIRST_ROOM',CURRENT,'thick walls and real front doorway; roof not yet added')

def architecture():
    age=int(CURRENT[1]);room_roof(0,age);room(1,age)
    ex,ey=PLANS[CURRENT[-1]]['entry'];opening=.87;w=4.30
    # Low front boundary preserves courtyard visibility; entrance is a genuine gap.
    for side in [-1,1]:
        low=-w/2 if side<0 else ex+opening/2;high=ex-opening/2 if side<0 else w/2
        wall('BoundaryFront'+str(side),(low+high)/2,ey,high-low,.18,.68,'plaster',group='boundary')
    # The occupied rooms form the perimeter where they meet it. Do not place a
    # second low wall over the same exterior face (the old b-plan black stripe).
    for label,xx in [('East',2.06),('West',-2.06)]:
        spans=[(-2.475,1.975)]
        for rx,ry,rw,rd in PLANS[CURRENT[-1]]['rooms']:
            if min(xx+.09,rx+rw/2)-max(xx-.09,rx-rw/2)<=0:continue
            low,high=ry-rd/2,ry+rd/2;remainder=[]
            for a,b in spans:
                if high<=a or low>=b:remainder.append((a,b))
                else:
                    if low>a:remainder.append((a,low))
                    if high<b:remainder.append((high,b))
            spans=remainder
        for j,(a,b) in enumerate(spans):
            wall('Boundary'+label+('Part'+str(j) if len(spans)>1 else ''),xx,(a+b)/2,.18,b-a,.60,'plaster',group='boundary')
    B('EntrySill',(ex,ey,F+.025),(opening+.08,.38,.05),'stone','foundation','ground','boundary')
    for side in [-1,1]:B('EntryPost'+str(side),(ex+side*.46,ey,F+1.00),(.10,.18,2.00),'timber','walls','fittings','boundary')
    B('EntryLintel',(ex,ey,F+2.04),(1.03,.20,.08),'timber','walls','fittings','boundary')
    if age>=3 and CURRENT[-1]!='c':
        # Narrow supported exterior stair runs along a side wing and terminates
        # at the upper domestic floor; no floating ladder or unusable long ramp.
        x,y,w,d=PLANS[CURRENT[-1]]['rooms'][1]
        mx,my,mw,md=PLANS[CURRENT[-1]]['rooms'][0]
        stairx=x+w/2+.25 if x<0 else x-w/2-.25
        if age==4:stairx=max(mx-mw*.40+.22,min(stairx,mx+mw*.40-.22))
        landing_front=my-md/2-.88
        step_rise=(room_height(1,age)+.13)/13
        for j in range(13):
            B('Stair'+str(j),(stairx,landing_front-1.75+j*.14,F+(j+1)*step_rise/2),(.44,.14,(j+1)*step_rise),'stone','walls','architecture','stair')
        if age==3:
            # A slightly raised supported landing bridges the narrow stair-to-
            # roof joint through a genuine break in the side parapet.
            cy=landing_front-.07
            xa,xb=(x+w/2-.16,stairx+.22) if x<0 else (stairx-.22,x-w/2+.16)
            roof_top=F+room_height(1,age)+.13
            landing=B('RoofAccessLanding',((xa+xb)/2,cy,roof_top-.02),(xb-xa,.48,.10),'stone','vaults','architecture','stair')
            topstep=bpy.data.objects[R.PREFIX+CURRENT+'_Stair12'];cap=bpy.data.objects[R.PREFIX+CURRENT+'_room_1_Roof']
            contact('LandingStairEmbed',landing,topstep,'bottom-top',target=-.07)
            contact('LandingRoofEmbed',landing,cap,'bottom-top',target=-.07)
    print('ARCHITECTURE',CURRENT,'rooms, supported roofs and low courtyard boundary')

def props():
    age=int(CURRENT[1]);wx,wy=PLANS[CURRENT[-1]]['work'];ex,ey=PLANS[CURRENT[-1]]['entry']
    # Water and food processing are grouped along the court edge, leaving entry clear.
    R.lathe(CURRENT+'_StorageJar',(wx,wy,F),[(.14,0),(.23,.09),(.25,.30),(.16,.43),(.15,.49),(.12,.49),(.12,.43)],'pottery',col('props'),sides=16,stage='finish',role='props')
    R.lathe(CURRENT+'_Basket',(wx-.34,wy+.20,F),[(.14,0),(.20,.23),(.18,.27),(.14,.27),(.14,.23)],'cloth',col('props'),sides=12,stage='finish',role='props')
    table=B('WorkTable',(wx,wy+.63,F+.425),(.64,.42,.07),'timber','finish','props')
    for sx in [-1,1]:
        for sy in [-1,1]:
            leg=B('WorkTableLeg'+str(sx)+str(sy),(wx+sx*.24,wy+.63+sy*.13,F+.195),(.06,.06,.39),'timber','finish','props')
            contact('TableLeg'+str(sx)+str(sy),leg,table,'top-bottom')
    # A short side textile hangs from an actual post bracket, outside the clear
    # gate opening. This replaces the first preview's modern-looking doormat.
    bracket=B('GateOwnerBracket',(ex-.595,ey,F+2.00),(.37,.08,.06),'timber','finish','fittings','boundary')
    banner=B('GateOwnerBanner',(ex-.64,ey-.05,F+1.845),(.28,.02,.25),'owner','finish','owner','boundary')
    contact('GateBannerTop',banner,bracket,'top-bottom')
    x,y,w,d=PLANS[CURRENT[-1]]['rooms'][0]
    B('OwnerFascia',(x,y-d/2-.012,F+room_height(0,age)-.10),(min(1.3,w*.45),.024,.15),'owner','finish','owner','room_0')
    # Bedded pavers and a small drain have measured ground contact.
    rr=random.Random(2700+age*19+ord(CURRENT[-1]))
    for j in range(6):
        B('EntryPaver'+str(j),(ex+rr.uniform(-.05,.05),ey+.30+j*.30,F+.018),(.51,.26,.036),'stone','foundation','ground')
    for j in range(6):
            B('StackedFirewood'+str(j),(wx+.37+(j%2)*.08,wy+.16+(j//2)*.10,F+.035+(j%2)*.07),(.34,.07,.07),'timber','finish','props')
    # Localized shallow earth darkening, with thickness seated in its source ground.
    for j in range(3):
        B('DoorTrafficWear'+str(j),(ex+(j-1)*.18,ey+.34+j*.16,F+.003),(.30,.35,.006),'grime','finish','wear')
    print('PROPS',CURRENT,'water/food/work groups, owner cloth, bedded entrance')

def detail():
    age=int(CURRENT[1]);rr=random.Random(811+age*11+ord(CURRENT[-1]))
    for index,(x,y,w,d) in enumerate(PLANS[CURRENT[-1]]['rooms']):
        g='room_'+str(index);h=room_height(index,age)
        z=F+h
        # Individually bedded coping pieces are silhouette detail; the continuous
        # parapet below remains structural in reduced LODs.
        if not (age==2 and index==0):
            for side in [-1,1]:
                count=max(3,int(w/.29))
                for j in range(count):
                    cw=(w-.06)/count
                    xx=x-w/2+.03+(j+.5)*cw;yy=y+side*(d/2-.07)
                    if age==4 and index==1:
                        mx,my,mw,md=PLANS[CURRENT[-1]]['rooms'][0];py=my-md/2-.42
                        if xx+(cw-.012)/2>mx-mw*.4 and xx-(cw-.012)/2<mx+mw*.4 and yy+.09>py-.46 and yy-.09<py+.46:continue
                    B(g+'_Coping'+str(side)+'_'+str(j),(xx,yy,z+.315+rr.uniform(-.009,.009)),(cw-.012,.18,.07),'roof','finish','fine_detail',g)
            # Earthen roofs remain continuous clay surfaces. Raised regular strips
            # falsely suggested a modern tiled roof in the first visual review.
        # Slatted doors are built on their recessed structural leaf.
        opening=min(.83,w*.37);doorh=door_height(index,age);front=y-d/2+.10
        for j in range(5):
            B(g+'_DoorSlat'+str(j),(x-opening*.38+(j+.5)*opening*.76/5,front+.071,F+doorh*.48),(opening*.76/5-.009,.018,doorh*.91),'timber','finish','fine_detail',g)
        for zz in [.28,.79]:B(g+'_DoorCrossbar'+str(zz),(x,front+.057,F+doorh*zz),(opening*.77,.015,.045),'timber','finish','fine_detail',g)
    wx,wy=PLANS[CURRENT[-1]]['work']
    # A small domestic quern and bowl are seated directly on the earth courtyard.
    R.lathe(CURRENT+'_Quern',(wx-.31,wy+.85,F),[(.18,0),(.19,.06),(.17,.11),(.05,.12)],'stone',col('props'),sides=24,stage='finish',role='props')
    R.lathe(CURRENT+'_FoodBowl',(wx+.14,wy+.63,F+.46),[(.07,0),(.10,.06),(.09,.07),(.065,.04)],'pottery',col('props'),sides=16,stage='finish',role='props')
    print('DETAIL',CURRENT,'bedded coping, recessed door slats and domestic quern')

def show(key='A1a',state='healthy',lod=0):
    s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s;R.view(pos=(12,-15,13),center=(0,-.25,1),distance=10,solid=True)

def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_BODY_READY',key)

def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n')
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n')

def reset_owned():
    # Explicit call only; never triggered by importing the recipe.
    for o in list(bpy.data.objects):
        if o.name.startswith(R.PREFIX):
            mesh=o.data if o.type=='MESH' else None;bpy.data.objects.remove(o,do_unlink=True)
            if mesh and not mesh.users:bpy.data.meshes.remove(mesh)
    for c in list(bpy.data.collections):
        if c.name.startswith(R.PREFIX):bpy.data.collections.remove(c)
    CONTRACTS.clear();ANCHORS.clear()
