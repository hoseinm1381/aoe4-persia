"""Original compact ore receipt/sorting yard. Unbuilt healthy-source draft."""
from pathlib import Path
import sys, math, json
import bpy

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'mining_camp')
BODY_KEYS=('Shared',)
CURRENT='Shared'
ANCHORS={}
CONTRACTS=[]
F=.12
P=.24
STORE_X=-4.35
STORE_Y=.70
STORE_W=1.84
STORE_D=2.24
SPRING=P+1.90
INVENTORY=ROOT.parents[3]/'research/persia_buildings/inventory'
MODEL='art/civilizations/common/structures/mining_camp/com_mining_camp_combined/com_mining_camp_combined'
NATIVE_DEPENDENCY={
    'model':MODEL+'.rgm','native_rgm':str(INVENTORY/'native'/(MODEL+'.rgm')),
    'native_rrgeom':str(INVENTORY/'native'/(MODEL+'.rrgeom')),
    'native_rgo':str(INVENTORY/'native'/(MODEL+'.rgo')),
    'rgm_sha256':'2fe9121f3dc2673c266b4c47d00a63767300d7dfb9b811274f8f616e69c36a72',
    'rrgeom_sha256':'416191c558fa02bca7c26a27e1eed2d7aa5b950962bb53570e6f6336cc2debef',
    'rgo_sha256':'0e63d76e2189bff700926604e2303ff9d474d076eece33323192c946dd206fb9',
    'bone_parent_names':{'bone_root':None,'bone_crane_turn':'bone_root','bone_crane_tilt':'bone_crane_turn','bone_stones':'bone_crane_tilt','bone_stones_orientation':'bone_stones','bone_crate':'bone_crane_tilt','bone_crate_orientation':'bone_crate'},
    'socket_contract_file':str(INVENTORY/'MECHANISM_DEPENDENCIES.json'),
    'status':'Static proxy only. Retain/rebind native seven-bone crane and official owner; no rest-pose conversion, world sockets, retargeting or new playback qualified.',
}

def activate():R.configure(ROOT,'mining_camp')

def root(key=None,state='healthy',lod=0):
    activate()
    return R.collection(R.PREFIX+(key or CURRENT)+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)

def col(role):return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,root())

def tag(o,stage,role,group):
    o['body_key']=CURRENT;o['construction_stage']=stage;o['role']=role;o['structural_group']=group
    o['draft_status']='unbuilt recipe; parent verification required'
    if group=='lifting_proxy':o['native_binding_status']='Static healthy preview only; native crane rig/owner retained separately, not replaced'
    return o

def B(name,xyz,size,surface='brick',stage='walls',role='architecture',group='store'):
    activate()
    return tag(R.block(CURRENT+'_'+name,xyz,size,surface,col(role),stage,role),stage,role,group)

def beam(name,a,b,width=.075,surface='timber',stage='walls',role='architecture',group='sorting_shelter'):
    activate()
    return tag(R.beam(CURRENT+'_'+name,a,b,width,surface,col(role),stage,role),stage,role,group)

def obj(name):return bpy.data.objects[R.PREFIX+CURRENT+'_'+name]

def contact(name,a,b,axis='bottom-top',target=0,tolerance=.003):
    CONTRACTS.append({'body':CURRENT,'name':name,'a':a.name,'b':b.name,'axis':axis,'target':target,'tolerance':tolerance})

def interface(name,a,b,point,overlap=.025):
    ANCHORS[CURRENT]['numerical_interfaces'].append({'name':name,'a':a.name,'b':b.name,'authored_contact_point':list(point),'intentional_socket_overlap_metres':overlap,'verification':'Endpoint plan only; actual generated mesh interface must be measured by parent.'})

def foundation(key='Shared'):
    global CURRENT
    if key not in BODY_KEYS:raise ValueError('Only the existing shared mining body is authorized')
    CURRENT=key;activate();R.setup_scene()
    if root().all_objects:raise ValueError('Owned body exists; inspect it before any explicit parent reset')
    ANCHORS[key]={'authored_space':'model-space','native_body_key':key,'ground_top':F,'store_floor_top':P,'store_vault_spring':SPRING,'front_direction':'-Y','numerical_interfaces':[],
        'chosen_horizontal_bounds':[[-5.72,-4.65],[.70,2.34]],'raw_native_rest_bounds':{'min':[-6.13671875,-5.078125,-4.46484375],'max':[1.3388671875,2.8828125,5.30859375]},
        'native_dependency':NATIVE_DEPENDENCY,'lift_proxy_status':'Static source geometry for review, not mapped to the native pose or motions'}
    outline=[(-5.60,-4.53),(-3.32,-4.65),(.40,-4.49),(.70,-2.76),(.65,1.98),(.21,2.34),(-3.95,2.24),(-5.72,1.91)]
    n=len(outline);vs=[(x,y,z) for z in (-.03,F) for x,y in outline]
    tag(R.mesh(CURRENT+'_EarthBed',vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'earth',col('ground'),'foundation','ground'),'foundation','ground','plot')
    floor=B('StorePlinth',(STORE_X,STORE_Y,(F+P)/2),(STORE_W+.16,STORE_D+.16,P-F),'stone','foundation','ground','store')
    contact('StorePlinthBed',floor,obj('EarthBed'))
    apron=B('SortingApron',(-.86,-1.27,F+.045),(2.66,2.66,.09),'stone','foundation','ground','sorting_shelter')
    contact('SortingApronBed',apron,obj('EarthBed'));ANCHORS[key]['sorting_floor_top']=F+.09
    liftbase=B('LiftFoot',(-1.28,.91,F+.12),(.64,.64,.24),'stone','foundation','ground','lifting_proxy');contact('LiftBaseBed',liftbase,obj('EarthBed'))

def first_room():
    # Low secure masonry store with a real arched opening and recessed timber leaf.
    x=STORE_X;y=STORE_Y;w=STORE_W;d=STORE_D;t=.24;h=SPRING-P
    west=B('StoreWest',(x-w/2+t/2,y,P+h/2),(t,d,h),'plaster')
    east=B('StoreEast',(x+w/2-t/2,y,P+h/2),(t,d,h),'plaster')
    back=B('StoreBack',(x,y+d/2-t/2,P+h/2),(w-2*t,t,h),'brick')
    front=y-d/2
    door=tag(R.archwall(CURRENT+'_StoreFrontArch',x,front,front+t,P,w,h,.70,1.37,.43,'brick',col('architecture'),segments=12),'walls','architecture','store')
    sill=B('StoreSill',(x,front+.08,P+.035),(.84,.34,.07),'stone','foundation','ground','store');contact('StoreSillBed',sill,obj('StorePlinth'))
    leaf=B('SecureStoreLeaf',(x,front+.15,P+.07+.825),(.61,.05,1.65),'timber','finish','fittings','store');contact('StoreLeafSill',leaf,sill)
    for z in (P+.43,P+1.31):B('DoorStrap'+str(z),(x,front+.118,z),(.58,.018,.045),'metal','finish','fittings','store')
    ANCHORS[CURRENT]['store_door_clearance']={'width':.70,'arch_spring_above_floor':1.37,'arch_rise':.43,'front_y':front,'note':'Closed healthy door; no door motion claimed'}

def architecture():
    # The vault has thickness and bears on both long walls at their exact top.
    vault=tag(R.vault(CURRENT+'_BrickBarrelRoof',STORE_X,STORE_Y-STORE_D/2-.02,STORE_Y+STORE_D/2+.02,SPRING,.80,.55,.10,'roof',col('roofs'),segments=16,along=2,stage='vaults'),'vaults','roofs','store')
    contact('VaultWestBearing',vault,obj('StoreWest'));contact('VaultEastBearing',vault,obj('StoreEast'))
    # End shells fill the curved gables without sealing the room interior.
    profile=[(-.80,SPRING),(.80,SPRING)]+[(.80*math.cos(j*math.pi/16),SPRING+.55*math.sin(j*math.pi/16)) for j in range(1,16)]
    for label,y in (('Front',STORE_Y-STORE_D/2+.06),('Back',STORE_Y+STORE_D/2-.10)):
        end=tag(R.extrude_xz(CURRENT+'_VaultEnd'+label,[(STORE_X+x,z) for x,z in profile],y,y+.08,'brick',col('architecture'),'vaults',role='architecture'),'vaults','architecture','store')
        contact('VaultEndSeat'+label,end,obj('StoreFrontArch') if label=='Front' else obj('StoreBack'))
    floor=ANCHORS[CURRENT]['sorting_floor_top'];posttop=2.01;beamtop=2.15
    posts={}
    for x in (-1.91,.20):
        for y in (-2.28,-.26):
            post=B('SortPost'+str(x)+str(y),(x,y,(floor+posttop)/2),(.13,.13,posttop-floor),'timber','walls','architecture','sorting_shelter')
            contact('SortPostBed'+str(x)+str(y),post,obj('SortingApron'));posts[(x,y)]=post
    rails=[]
    for y in (-2.28,-.26):
        rail=B('SortBearing'+str(y),(-.855,y,(posttop+beamtop)/2),(2.37,.16,beamtop-posttop),'timber','walls','architecture','sorting_shelter')
        for x in (-1.91,.20):contact('SortRailPost'+str(x)+str(y),rail,posts[(x,y)])
        rails.append(rail)
    joists=[]
    for j in range(6):
        joist=B('SortJoist'+str(j),(-1.92+j*.425,-1.27,beamtop+.04),(.065,2.32,.08),'timber','vaults','fittings','sorting_shelter')
        for k,rail in enumerate(rails):contact('SortJoistRail'+str(j)+str(k),joist,rail)
        joists.append(joist)
    shade=B('SortReedRoof',(-.855,-1.27,beamtop+.11),(2.58,2.46,.06),'cloth','vaults','roofs','sorting_shelter')
    for j,joist in enumerate(joists):contact('SortShadeJoist'+str(j),shade,joist)
    for x in (-1.91,.20):
        sign=1 if x<0 else -1
        brace=beam('SortKnee'+str(x),(x,-2.28,posttop-.33),(x+sign*.33,-2.28,posttop+.02),.06)
        interface('SortKneePost'+str(x),brace,posts[(x,-2.28)],(x,-2.28,posttop-.33),.065)
        interface('SortKneeRail'+str(x),brace,rails[0],(x+sign*.33,-2.28,posttop+.02))

def ore_bin(name,x,y,w=1.10,d=.90):
    h=.52;t=.13
    base=B(name+'Base',(x,y,F+.04),(w,d,.08),'stone','foundation','ground','ore_bins');contact(name+'BaseBed',base,obj('EarthBed'))
    floor=F+.08
    for side in (-1,1):
        B(name+'Side'+str(side),(x+side*(w/2-t/2),y,floor+h/2),(t,d,h),'stone','walls','architecture','ore_bins')
    B(name+'Back',(x,y+d/2-t/2,floor+h/2),(w-2*t,t,h),'stone','walls','architecture','ore_bins')
    B(name+'FrontLip',(x,y-d/2+t/2,floor+.14),(w-2*t,t,.28),'stone','walls','architecture','ore_bins')
    # A fitted closed low heap; deterministic facets rather than loose scatter.
    outline=[(-.40,-.28),(.36,-.30),(.40,.24),(-.34,.28)]
    vs=[(x+xx,y+yy,floor) for xx,yy in outline]+[(x-.22,y-.12,floor+.38),(x+.16,y-.08,floor+.40),(x+.20,y+.16,floor+.31),(x-.20,y+.18,floor+.34)]
    heap=tag(R.mesh(CURRENT+'_'+name+'Ore',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone',col('props'),'finish','props'),'finish','props','ore_bins');contact(name+'OreBed',heap,base)

def bench(name,x,y,w,d,top):
    floor=ANCHORS[CURRENT]['sorting_floor_top'];th=.075;underside=top-th
    slab=B(name+'Top',(x,y,top-th/2),(w,d,th),'timber','finish','props','sorting_bench')
    for sx in (-1,1):
        for sy in (-1,1):
            leg=B(name+'Leg'+str(sx)+str(sy),(x+sx*(w/2-.09),y+sy*(d/2-.075),(floor+underside)/2),(.09,.09,underside-floor),'timber','finish','props','sorting_bench')
            contact(name+'LegSeat'+str(sx)+str(sy),leg,slab,'top-bottom');contact(name+'LegBed'+str(sx)+str(sy),leg,obj('SortingApron'))
    return slab

def trough():
    floor=ANCHORS[CURRENT]['sorting_floor_top'];x=-.87;y=-1.10;top=floor+.72
    slab=bench('WashBench',x,y,1.25,.62,top-.17)
    bed=B('WashTroughFloor',(x,y,top-.14),(1.17,.54,.06),'stone','finish','props','washing')
    contact('WashTroughBed',bed,slab)
    # The rim is four walls surrounding a genuine visible cavity.
    for sx in (-1,1):
        rim=B('WashTroughEnd'+str(sx),(x+sx*.55,y,top-.055),(.07,.54,.11),'stone','finish','props','washing');contact('WashEndOnFloor'+str(sx),rim,bed)
    rear=B('WashTroughBack',(x,y+.235,top-.055),(1.03,.07,.11),'stone','finish','props','washing');contact('WashBackOnFloor',rear,bed)
    # Front wall has an actual 0.10-wide drain gap at the east end.
    for j,(left,right) in enumerate(((-.515,.28),(.38,.515))):
        rim=B('WashTroughFront'+str(j),(x+(left+right)/2,y-.235,top-.055),(right-left,.07,.11),'stone','finish','props','washing');contact('WashFrontOnFloor'+str(j),rim,bed)
    ANCHORS[CURRENT]['wash_trough']={'inner_floor_z':top-.11,'rim_top_z':top,'open_inner_width':1.03,'open_inner_depth':.40,'drain_gap_x':[x+.28,x+.38],'water_rendering':'Dry source trough only; no water material/effect or flow claimed'}
    return top

def lifting_proxy():
    # Evidence supports a native movable crane. This is a static source proxy only.
    base=obj('LiftFoot');floor=F+.24;x=-1.28;y=.91;posttop=2.65
    post=B('LiftUpright',(x,y,(floor+posttop)/2),(.19,.19,posttop-floor),'timber','walls','mechanism_proxy','lifting_proxy');contact('LiftUprightBase',post,base)
    for sx in (-1,1):
        brace=beam('LiftFootStay'+str(sx),(x+sx*.27,y,floor),(x,y,1.11),.09,group='lifting_proxy',role='mechanism_proxy')
        interface('LiftFootStaySocket'+str(sx),brace,post,(x,y,1.11),.095);interface('LiftFootStayBase'+str(sx),brace,base,(x+sx*.27,y,floor))
    pivot=(x,y,2.38);tip=(-2.68,.28,3.03)
    boom=beam('LiftBoom',pivot,tip,.15,group='lifting_proxy',role='mechanism_proxy');interface('LiftBoomPivot',boom,post,pivot,.095)
    stay=beam('LiftBoomStay',(x,y,1.50),(-2.39,.41,2.89),.085,group='lifting_proxy',role='mechanism_proxy');interface('LiftStayPost',stay,post,(x,y,1.50),.095);interface('LiftStayBoom',stay,boom,(-2.39,.41,2.89),.075)
    line=beam('LiftLine',(-2.68,.28,3.03),(-2.68,.28,.79),.018,surface='cloth',stage='finish',group='lifting_proxy',role='mechanism_proxy');interface('LiftLineBoom',line,boom,tip,.035)
    # A ground-seated receiving tray avoids pretending a suspended load is animated.
    tray=B('LiftReceivingTray',(-2.68,.28,F+.055),(.67,.60,.11),'timber','finish','mechanism_proxy','lifting_proxy');contact('LiftTrayGround',tray,obj('EarthBed'))
    ANCHORS[CURRENT]['lift_proxy']={'upright_pivot':pivot,'boom_tip':tip,'line_end':[-2.68,.28,.79],'receiving_tray_top':F+.11,'native_binding':'Unbound static proxy. Native turn/tilt/stones/crate hierarchy and poses remain retained/deferred.'}

def props():
    for j,x in enumerate((-5.00,-3.63)):ore_bin('OreBin'+str(j),x,-3.48)
    top=trough();sorting=bench('DrySortBench',-.85,-2.01,1.30,.42,ANCHORS[CURRENT]['sorting_floor_top']+.68)
    for j in range(3):
        tray=B('SortTray'+str(j),(-1.23+j*.38,-2.01,ANCHORS[CURRENT]['sorting_floor_top']+.705),(.32,.31,.05),'timber','finish','props','sorting_bench');contact('SortTrayBed'+str(j),tray,sorting)
    lifting_proxy()
    # Two closed ore/tool chests on a masonry pallet beside the secure store.
    pallet=B('SecureOrePallet',(-3.07,1.67,F+.06),(.78,.80,.12),'stone','foundation','ground','secure_ore');contact('OrePalletBed',pallet,obj('EarthBed'))
    for j,y in enumerate((1.44,1.89)):
        chest=B('SecureOreChest'+str(j),(-3.07,y,F+.12+.21),(.63,.36,.42),'timber','finish','props','secure_ore');contact('OreChestPallet'+str(j),chest,pallet)
        for x in (-3.29,-2.85):B('ChestStrap'+str(j)+str(x),(x,y,F+.12+.425),(.055,.37,.01),'metal','finish','fittings','secure_ore')
    bracket=B('StoreOwnerBracket',(STORE_X-.52,STORE_Y-STORE_D/2-.025,P+1.72),(.35,.09,.06),'timber','finish','fittings','owner')
    cloth=B('StoreOwnerCloth',(STORE_X-.52,STORE_Y-STORE_D/2-.06,P+1.565),(.25,.025,.25),'owner','finish','owner','owner');contact('StoreClothBracket',cloth,bracket,'top-bottom')
    interface('StoreOwnerBracketWall',bracket,obj('StoreFrontArch'),(STORE_X-.52,STORE_Y-STORE_D/2+.01,P+1.72),.02)

def detail():
    # Local ore stains, threshold abrasion and sorting dust have fixed functional anchors.
    for j,x in enumerate((-5.00,-3.63)):B('BinDischargeWear'+str(j),(x,-4.06,F+.002),(.70,.33,.004),'grime','finish','wear','ore_bins')
    for j in range(3):B('StoreThresholdPaver'+str(j),(STORE_X,STORE_Y-STORE_D/2-.27-j*.29,F+.025),(.70,.26,.05),'stone','foundation','ground','store')
    B('SortingDust',(-.85,-2.39,ANCHORS[CURRENT]['sorting_floor_top']+.002),(.95,.20,.004),'earth','finish','wear','sorting_bench')
    # Short dry drain drops to a grounded sediment dish; no terrain cut or flowing effect.
    x=-.54;y=-1.54;floor=ANCHORS[CURRENT]['sorting_floor_top']
    channel=B('DryDrainBed',(x,y,floor+.025),(.15,.40,.05),'stone','finish','props','washing');contact('DryDrainApron',channel,obj('SortingApron'))
    outlet_top=ANCHORS[CURRENT]['wash_trough']['inner_floor_z']
    chute=beam('WashDrainChute',(x,-1.37,outlet_top),(x,y,floor+.05),.08,surface='stone',stage='finish',role='props',group='washing')
    interface('WashChuteUpperSeat',chute,obj('WashTroughFloor'),(x,-1.37,outlet_top),.02)
    interface('WashChuteLowerSeat',chute,channel,(x,y,floor+.05),.02)
    for side in (-1,1):beam('WashChuteRim'+str(side),(x+side*.052,-1.37,outlet_top+.025),(x+side*.052,y,floor+.075),.025,surface='stone',stage='finish',role='props',group='washing')
    for side in (-1,1):B('DryDrainSide'+str(side),(x+side*.095,y,floor+.07),(.04,.40,.09),'stone','finish','props','washing')
    dish=B('SedimentDish',(x,-1.81,floor+.02),(.34,.20,.04),'grime','finish','props','washing');contact('SedimentDishApron',dish,obj('SortingApron'))

def show(key='Shared',state='healthy',lod=0):
    activate();s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s

def build_body(key='Shared'):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_REQUIRES_PARENT_VERIFICATION',key)

def write_anchors():
    (ROOT/'evidence').mkdir(parents=True,exist_ok=True)
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n')
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n')


def build_lod(H,key,state,source,destination,lod,profile):
    from campus_lods import build_lod
    return build_lod(H,key,state,source,destination,lod,profile)
