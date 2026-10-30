"""DRAFT original Persian stable, authored in projected stamp coordinates.

The native primary range is shallow and rotated. Its measured frame is retained;
the larger animal court is a conditional compound proposal, not a footprint.
No Blender execution, native resource replacement, motion or state wiring occurs.
"""
from pathlib import Path
import sys
import json
import math
import bpy

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'stable')

F=.16
CURRENT='A2'
ANCHORS={}
CONTRACTS=[]
ASSEMBLIES={}
TEXTURE_INPUTS={k:str(ROOT/'textures'/(k+'.png')) for k in ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC={'resolution':[2048,2048],'original_pixels_required':True,'status':'paths only; parent generates original atlas'}
ACTOR='ps_building_unit_cavalry_control_sul'
VARIANT_EVIDENCE={
    'campaign':'existing_private_compiled_variant',
    'default':'existing_private_compiled_variant',
    'cordoba':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
    'xp3':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
}
STABLE_MATRIX=[[0.,1.,0.,-3.9000000954],[-1.,-2.220446049250313e-16,0.,-1.6000000238],[0.,0.,1.,0.],[0.,0.,0.,1.]]
STABLE_INVERSE=[[0.,-1.,0.,-1.6000000238],[1.,0.,0.,3.9000000954],[0.,0.,1.,0.],[0.,0.,0.,1.]]
NATIVE={
    'A2':{'age':2,'triangles':21823,
          'primary_resource_bounds':[[-3.44921875,-1.6005859375,-1.19921875],[3.654296875,1.6044921875,5.09765625]],
          'primary_stamp_bounds':[[-5.5005860329,-5.2542968988,-1.19921875],[-2.2955079079,1.8492187262,5.09765625]],
          'possible_compound_bounds':[[-7.1989036750,-6.9868024581,-2.509765625],[5.6818187784,5.7236703596,5.09765625]]},
    'A3':{'age':3,'triangles':22156,
          'primary_resource_bounds':[[-3.44921875,-1.6005859375,-1.19921875],[3.654296875,1.6044921875,5.09765625]],
          'primary_stamp_bounds':[[-5.5005860329,-5.2542968988,-1.19921875],[-2.2955079079,1.8492187262,5.09765625]],
          'possible_compound_bounds':[[-7.1989036750,-6.9868024581,-2.509765625],[5.2985798877,5.5381137889,5.09765625]]},
    'A4':{'age':4,'triangles':25874,
          'primary_resource_bounds':[[-3.60546875,-1.583984375,-1.19921875],[3.609375,1.6044921875,5.171875]],
          'primary_stamp_bounds':[[-5.4839844704,-5.2093750238,-1.19921875],[-2.2955079079,2.0054687262,5.171875]],
          'possible_compound_bounds':[[-7.1989036750,-6.9868024581,-2.509765625],[5.2985798877,5.5381137889,5.171875]]},
}
for _key,_n in NATIVE.items():
    _a=str(_n['age']).zfill(2)
    _n['model']='art/civilizations/sultanate/structures/stable/sul_stable_control_age'+_a+'/sul_stable_control_age'+_a+'.rgm'
    _n['source_uses']=[dict(actor=ACTOR,variant=v,variant_evidence_class=e,
                           attachment='attachments/attachment_lists/civilizations/sultanate/buildings/unit_cavalry_sul/tier'+str(_n['age'])+'_unit_cavalry_control_sul',
                           attachment_category='default',inventory_category='default',stamp='art/stamps/civ_sul/sul_stable_age_'+_a+'.bin',stamp_instance_index=0)
                        for v,e in VARIANT_EVIDENCE.items()]

ORIGINAL_REVIEW_BOUNDS=[[-6.60,-6.30,-.06],[4.60,5.00,4.70]]
# Narrow visual-only boundary revision. These are exact-joined, non-debris
# reference coordinates; prop-specific native healthy activation is still
# unqualified (evidence/visual-envelope-contract.json). Never use destruction
# debris to enlarge an ordinary healthy plot or change a native footprint.
SOURCE_FRONT=-5.627689449559207+.05
SOURCE_EAST=4.60
SOURCE_NORTH=5.00
REVIEW_BOUNDS=[[-5.455,SOURCE_FRONT,-.06],[SOURCE_EAST,SOURCE_NORTH,4.70]]


def source_west(key):
    return NATIVE[key]['primary_stamp_bounds'][0][0]+.05


def source_bounds(key):
    # Retain the original functional A2/A3 vault overhang: it remains 44.586mm
    # inside the measured reference even though it is 4.414mm short of the
    # preferred 50mm margin. No architecture is scaled/moved for that margin.
    lo,hi=NATIVE[key]['primary_stamp_bounds']
    return [[lo[0]+.01,lo[1]+.01,-.06],[hi[0]-.01,hi[1]-.01,4.70]]
PLANS={
    2:{'program':'two animal stalls and open end handling bay under timber roof; internal tack/feed/water stations',
       'wall_height':2.63,'roof':'flat','feed_store':False,'wash_bay':False,'supervisor':False},
    3:{'program':'two stalls and handling court with three ventilated vaults; compact feed and tack preparation',
       'wall_height':2.72,'roof':'three_vaults','feed_store':True,'wash_bay':True,'supervisor':False},
    4:{'program':'two vaulted animal stalls and a raised open handling clerestory; fitted feed/tack and supervisor ledger',
       'wall_height':2.90,'roof':'three_vaults','feed_store':True,'wash_bay':True,'supervisor':True},
}
NATIVE_DEPENDENCIES={
    'layout':'art/civilizations/common/layouts/archetypes/layout_stable/layout_stable.rgm',
    'existing_props':['stable_horserun','hayshack_a','stable_saddle','rope_coil','sack_single','rectangular_woodwater_trough','water_bucket'],
    'banner':'art/civilizations/common/banners/banner_stables/banner_stables.rgm',
    'policy':'Retain original native layout, graph/rig owners, markers and legal attachments. No animal mesh or new animation is authored.',
    'marker_frame':'Layout markers are native bone-local until skeleton/pose evaluation; no recorded marker is asserted to be a world-space socket.',
    'clearance_status':'Unqualified: conditional compound proposal is not native footprint, horse exit, posed animal size or moving swept volume.',
}


def age():return NATIVE[CURRENT]['age']


def root(key=None,state='healthy',lod=0):
    R.configure(ROOT,'stable')
    key=key or CURRENT
    if key not in NATIVE:raise ValueError('Only measured Stable A2/A3/A4 are admitted')
    return R.collection(R.PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)


def col(role):
    parent=root()
    return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,parent)


def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role
    ob['draft_uninspected']=True
    ob['authored_coordinate_space']='projected stamp-space; inverse resource adapter pending'
    if group:ob['structural_group']=group
    return ob


def B(name,center,size,surface='plaster',stage='walls',role='architecture',group=''):
    if any(v<=0 for v in size):raise ValueError('Nonpositive part: '+name)
    return tag(R.block(CURRENT+'_'+name,center,size,surface,col(role),stage,role),stage,role,group)


def wall(name,x,y,w,d,h,surface='plaster',bottom=F,group=''):
    return B(name,(x,y,bottom+h/2),(w,d,h),surface,'walls','architecture',group)


def contact(name,child,parent,axis='bottom-top',target=0.,tolerance=.003):
    CONTRACTS.append(dict(body=CURRENT,name=name,a=child.name,b=parent.name,axis=axis,target=target,tolerance=tolerance))


def setup():
    R.configure(ROOT,'stable');s=R.setup_scene()
    s['historical_basis']='Original animal/service court with Persian caravanserai practical accommodation comparisons; see README.'
    R.view(pos=(15,-19,15),center=(-.5,-.4,1.8),distance=20,solid=True)


def foundation(key='A2'):
    global CURRENT
    if key not in NATIVE:raise ValueError('Unknown measured native key')
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body exists; explicit owned reset required')
    lo,hi=source_bounds(key);west,front=lo[:2];east,north=hi[:2]
    bed=B('AnimalCourtBed',((west+east)/2,(front+north)/2,.05),
          (east-west,north-front,.22),'earth','foundation','ground','court_ground')
    # A shallow drain has a genuine recessed channel between its side stones;
    # the channel is source geometry, never terrain excavation or native routing.
    drain=B('DrainBed',(-2.37,-1.70,F+.025),(.08,6.40,.05),'stone','foundation','ground','drain')
    contact('DrainOnGround',drain,bed)
    for s in (-1,1):B('DrainSide'+str(s),(-2.37+s*.05,-1.70,F+.06),(.02,6.40,.12),'stone','foundation','ground','drain')
    n=NATIVE[key]
    ANCHORS[key]=dict(ground_top=F,native_body_key=key,native_model=n['model'],existing_visual_age=age(),source_uses=n['source_uses'],
                      authoring_bounds_proposal=source_bounds(key),native_primary_resource_bounds=n['primary_resource_bounds'],
                      native_primary_stamp_bounds=n['primary_stamp_bounds'],conditional_compound_bounds=n['possible_compound_bounds'],
                      authored_space='projected stamp-space; compact stable bounded by measured primary body, no conditional prop union',
                      projected_resource_to_stamp_matrix=STABLE_MATRIX,stamp_to_projected_resource_matrix=STABLE_INVERSE,
                      entry=[1.65,-6.10,F],animal_court=[-3.65,-4.1,F+.10],
                      dependencies=NATIVE_DEPENDENCIES,native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],
                      visual_inspection='Not performed; serial parent build and inspection required')
    ANCHORS[key]['source_boundary_revision']={
        'scope':'Compact authored stable redesign within verified primary; native footprint/stamps/markers remain unchanged',
        'original_earth_bounds':[[-6.60,-6.30],[4.60,5.00]],
        'revised_earth_bounds':[[west,front],[east,north]],
        'original_entry_anchor_retained':[1.65,-6.10,F],
        'visual_entry_edge':[-3.90,-5.14,F+.10],
        'handling_bay':'South bay is an open handling court under the range roof; the two north bays remain stalls',
        'handling_clear_rectangle':[[-4.84,-4.85],[-2.51,-3.30]],
        'source_headroom':'Every animal opening has 1.97m spring + .43m rise; actual native horse pose/turning/route qualification remains deferred',
        'service_functions':'Supported tack preparation, feed bins and water trough inside handling bay; no excluded north rooms/east sheds',
        'qualification':'Verified primary-body bounded source architecture; no prop healthy activation inference'}
    ASSEMBLIES[key]={'ground':bed,'stalls':[]}
    print('FOUNDATION_DRAFT',key,'primary is narrow; whole court uses conditional compound proposal')


def first_room():
    """West range: large east-facing animal openings, actual partitions and air gaps."""
    x,w,y0,y1=-3.90,2.90,-5.05,1.70
    h=PLANS[age()]['wall_height'];t=.22
    floor=B('StallRangeFloor',(x,(y0+y1)/2,F+.05),(w,y1-y0+.18,.10),'earth','foundation','ground','stall_range')
    # Back wall has a real high ventilation band: continuous lower wall,
    # intermittent load-bearing piers and a top ring, never painted apertures.
    lowh=h-.48
    back=wall('StallBackLower',x-w/2+t/2,(y0+y1)/2,t,y1-y0,lowh,bottom=F+.10,group='stall_range')
    top=F+.10+h
    cap=B('StallBackTopRing',(x-w/2+t/2,(y0+y1)/2,top-.08),(t,y1-y0,.16),'brick','walls','architecture','stall_range')
    for j in range(7):
        yy=y0+.11+j*(y1-y0-.22)/6
        pier=wall('BackVentPier'+str(j),x-w/2+t/2,yy,t,.18,.32,bottom=F+.10+lowh,group='stall_range')
        contact('BackVentFoot'+str(j),pier,back)
        contact('BackVentHead'+str(j),pier,cap,'top-bottom')
    bay=(y1-y0)/3
    for i in range(3):
        yy=y0+(i+.5)*bay
        front=x+w/2-t/2
        arch=tag(R.archwall(CURRENT+'_AnimalBayArch'+str(i),yy,front-t/2,front+t/2,F+.10,
                            bay,h,1.84,1.97,.43,'brick',col('architecture'),segments=16,
                            transform=lambda u,v,z:(v,u,z)),'walls','architecture','stall_'+str(i))
        contact('BayArchFoot'+str(i),arch,floor)
        ASSEMBLIES[CURRENT]['stalls'].append(dict(index=i,y=yy,bay=bay,arch=arch))
    for i in range(4):
        yy=y0+i*bay
        # Full-height end walls, lower internal dividers retain ventilation.
        if i==0:
            p=tag(R.archwall(CURRENT+'_HandlingEndArch',x,yy-.09,yy+.09,F+.10,w-.44,h,1.84,1.97,.43,
                'brick',col('architecture'),segments=16),'walls','architecture','stall_range')
            contact('HandlingEndArchFoot',p,floor)
            continue
        ph=h if i==3 else 1.35
        p=wall('StallPartition'+str(i),x,yy,w-.44,.18,ph,'brick',F+.10,'stall_range')
        contact('StallPartitionFoot'+str(i),p,floor)
    ASSEMBLIES[CURRENT].update(range=dict(x=x,w=w,y0=y0,y1=y1,h=h,top=top,back=back,cap=cap,floor=floor))
    ANCHORS[CURRENT]['proposed_animal_openings']=[dict(center=[x+w/2,s['y'],F+.10],clear_width=1.84,arch_spring_height=1.97,arch_rise=.43) for s in ASSEMBLIES[CURRENT]['stalls']]
    print('FIRST_ROOM_DRAFT',CURRENT,'three real animal openings and ventilated back range')


def range_roof():
    a=ASSEMBLIES[CURRENT]['range'];x,w,y0,y1,top=a['x'],a['w'],a['y0'],a['y1'],a['top']
    if PLANS[age()]['roof']=='flat':
        roof=B('StallTimberClayRoof',(x,(y0+y1)/2,top+.10),(w+.08,y1-y0+.08,.20),'roof','vaults','roofs','stall_range')
        contact('StallRoofBackRing',roof,a['cap'])
        for s in ASSEMBLIES[CURRENT]['stalls']:contact('StallRoofArch'+str(s['index']),roof,s['arch'])
        for j in range(9):
            yy=y0+.15+j*(y1-y0-.30)/8
            B('StallRoofJoist'+str(j),(x,yy,top-.04),(w,.10,.08),'timber','vaults','fittings','stall_range')
    else:
        for s in ASSEMBLIES[CURRENT]['stalls']:
            i,yy,bay=s['index'],s['y'],s['bay']
            if age()==4 and i==0:
                # The later handling bay has a raised, genuinely ventilated
                # timber clerestory; the two animal stalls retain vaults.
                posts=[]
                for sx in (-1,1):
                    for sy in (-1,1):
                        q=B('HandlingClerestoryPost'+str(sx)+str(sy),(x+sx*(w/2-.10),yy+sy*(bay/2-.12),top+.22),
                            (.16,.16,.44),'timber','vaults','architecture','stall_0')
                        contact('ClerestoryFoot'+str(sx)+str(sy),q,s['arch'] if sx==1 else a['cap']);posts.append(q)
                roof=B('HandlingClerestoryRoof',(x,yy,top+.52),(w+.05,bay-.10,.16),'roof','vaults','roofs','stall_0')
                for j,q in enumerate(posts):contact('ClerestoryRoofBearing'+str(j),roof,q)
                continue
            # Three barrel shells run across the narrow west range. The open
            # lunette above each animal arch is purposeful high ventilation.
            p=R.vault(CURRENT+'_StallVault'+str(i),yy,x-w/2,x+w/2,top,(bay-.24)/2,.40 if age()==3 else .55,.12,
                      'roof',col('roofs'),segments=20,along=3,transform=lambda u,v,z:(v,u,z),stage='vaults')
            tag(p,'vaults','roofs','stall_'+str(i))
            # Bounds meet the front/back wall tops at the spring line; parent
            # must inspect the actual bearing area, not infer it from AABBs.
            contact('VaultFrontBearing'+str(i),p,s['arch'])
            contact('VaultBackBearing'+str(i),p,a['cap'])


def service_room(name,x,y,w,d,h,vault=False,window=False):
    t=.20;bottom=F+.08
    floor=B(name+'Floor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',name)
    back=wall(name+'Back',x,y+d/2-t/2,w,t,h,bottom=bottom,group=name)
    wall(name+'West',x-w/2+t/2,y,t,d-.40,h,bottom=bottom,group=name)
    if window:
        # True split wall and recessed shutter at the occupied service level.
        wall(name+'EastLower',x+w/2-t/2,y,t,d-.40,1.60,bottom=bottom,group=name)
        wall(name+'EastHead',x+w/2-t/2,y,t,d-.40,h-2.25,bottom=bottom+2.25,group=name)
        for side in (-1,1):wall(name+'WindowPier'+str(side),x+w/2-t/2,y+side*(d-.40+.65)/4,t,(d-.40-.65)/2,.65,bottom=bottom+1.60,group=name)
        B(name+'RecessedShutter',(x+w/2-.18,y,bottom+1.925),(.04,.54,.55),'timber','finish','fittings',name)
    else:wall(name+'East',x+w/2-t/2,y,t,d-.40,h,bottom=bottom,group=name)
    opening=.98;dh=2.05;piece=(w-opening)/2
    for side in (-1,1):wall(name+'FrontPier'+str(side),x+side*(opening/2+piece/2),y-d/2+t/2,piece,t,h,bottom=bottom,group=name)
    wall(name+'DoorHead',x,y-d/2+t/2,opening,t,h-dh,bottom=bottom+dh,group=name)
    leaf=B(name+'RecessedDoor',(x,y-d/2+.16,bottom+.98),(.86,.04,1.96),'timber','finish','fittings',name)
    contact(name+'DoorFoot',leaf,floor)
    if vault:
        p=R.vault(CURRENT+'_'+name+'Vault',x,y-d/2,y+d/2,bottom+h,(w-.08)/2,.42,.12,'roof',col('roofs'),segments=18,along=3,stage='vaults')
        tag(p,'vaults','roofs',name);contact(name+'VaultBack',p,back)
    else:
        p=B(name+'Roof',(x,y,bottom+h+.09),(w+.05,d+.05,.18),'roof','vaults','roofs',name)
        contact(name+'RoofBack',p,back)
    return floor


def handling_shade():
    if not PLANS[age()]['wash_bay']:return
    x,y,w,d=2.50,-3.75,3.00,2.10
    floor=B('HandlingBeddedFloor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground','handling')
    top=F+2.50;posts=[]
    for sx in (-1,1):
        for sy in (-1,1):
            q=B('HandlingPost'+str(sx)+str(sy),(x+sx*(w/2-.12),y+sy*(d/2-.12),(F+.08+top)/2),(.16,.16,top-F-.08),'timber','walls','architecture','handling')
            contact('HandlingPostFoot'+str(sx)+str(sy),q,floor);posts.append(q)
    roof=B('HandlingRoof',(x,y,top+.09),(w+.10,d+.10,.18),'roof','vaults','roofs','handling')
    for i,p in enumerate(posts):contact('HandlingRoofPost'+str(i),roof,p)


def architecture():
    range_roof()
    # Service rooms sit north of the animal range. They never close the main
    # east-facing animal mouths or the deliberately open south court entrance.
    # Service functions are fitted within the south handling bay by props().
    # Excluded north rooms and east court shade are not regenerated elsewhere.
    print('ARCHITECTURE_DRAFT',CURRENT,'animal bays, separate tack/feed/service and clear court entrance')


def trough(name,x,y,w,d=.58,bottom=None,support=None):
    bottom=F if bottom is None else bottom
    support=ASSEMBLIES[CURRENT]['ground'] if support is None else support
    base=B(name+'Base',(x,y,bottom+.05),(w,d,.10),'timber','finish','props','animal_care')
    contact(name+'Ground',base,support)
    z=bottom+.10+.18
    for side in (-1,1):B(name+'Side'+str(side),(x,y+side*(d/2-.045),z),(w,.09,.36),'timber','finish','props','animal_care')
    for side in (-1,1):B(name+'End'+str(side),(x+side*(w/2-.045),y,z),(.09,d-.18,.36),'timber','finish','props','animal_care')
    # Recessed interior remains visible; no solid blue cap pretending water.


def tack_stand(name,x,y):
    # Grounded timber trestle and separately editable folded cloth/saddle pad.
    top=F+1.05
    cross=B(name+'Cross',(x,y,top-.055),(1.20,.18,.11),'timber','finish','props','tack')
    for side in (-1,1):
        p=B(name+'Leg'+str(side),(x+side*.44,y,(F+top-.11)/2),(.12,.38,top-.11-F),'timber','finish','props','tack')
        contact(name+'LegTop'+str(side),p,cross,'top-bottom')
        contact(name+'LegGround'+str(side),p,ASSEMBLIES[CURRENT]['ground'])
    blanket=B(name+'FoldedPad',(x,y,top+.055),(.72,.46,.11),'cloth','finish','props','tack')
    contact(name+'PadOnCross',blanket,cross)


def props():
    floor=ASSEMBLIES[CURRENT]['range']['floor'];z0=F+.10
    # An open trough sits against the west handling wall, leaving the recorded
    # central handling rectangle and both real animal openings free.
    base=B('WaterTroughBase',(-4.99,-4.15,z0+.05),(.28,1.00,.10),'timber','finish','props','animal_care')
    contact('CompactTroughFoot',base,floor)
    for sx in (-1,1):B('WaterTroughSide'+str(sx),(-4.99+sx*.115,-4.15,z0+.23),(.05,1.00,.26),'timber','finish','props','animal_care')
    for sy in (-1,1):B('WaterTroughEnd'+str(sy),(-4.99,-4.15+sy*.475,z0+.23),(.18,.05,.26),'timber','finish','props','animal_care')
    # Every member of the small tack-preparation bench is separately editable.
    top=z0+.82
    bench=B('TackPrepCross',(-4.72,-3.13,top-.05),(.80,.28,.10),'timber','finish','props','tack')
    for sx in (-1,1):
        leg=B('TackPrepLeg'+str(sx),(-4.72+sx*.29,-3.13,(z0+top-.10)/2),(.09,.22,top-.10-z0),'timber','finish','props','tack')
        contact('CompactTackFoot'+str(sx),leg,floor);contact('CompactTackTop'+str(sx),bench,leg)
    pad=B('TackPrepFoldedPad',(-4.72,-3.13,top+.055),(.58,.24,.11),'cloth','finish','props','tack')
    contact('CompactPadOnBench',pad,bench)
    # Feed bundles have a deliberately faceted, closed section and stay well
    # clear of the stall mouths. They are original static art, not stock media.
    for j in range(2 if age()>2 else 1):
        x=-3.92+j*.50;y=-3.09;bottom=z0
        tag(R.lathe(CURRENT+'_FeedSack'+str(j),(x,y,bottom),[(.15,0),(.18,.12),(.17,.49),(.10,.57),(.05,.58)],'cloth',col('props'),sides=12,role='props'),'finish','props','feed')
    for i in (1,2):
        yy=ASSEMBLIES[CURRENT]['stalls'][i]['y']
        B('StallBedding'+str(i),(-4.15,yy,F+.108),(1.45,1.55,.016),'cloth','finish','wear','stall_'+str(i))
    # Short solid timber tether posts use no improvised rope animation.
    if age()==4:
        ledger=B('SupervisorRegister',(-4.72,-3.13,top+.13),(.35,.20,.04),'paper','finish','props','tack')
        contact('SupervisorRegisterOnPad',ledger,pad)
    print('PROPS_DRAFT',CURRENT,'recessed troughs, feed, grounded tack preparation and tether space')


def detail():
    a=ASSEMBLIES[CURRENT]['range'];xfront=a['x']+a['w']/2
    for i,s in enumerate(ASSEMBLIES[CURRENT]['stalls']):
        # Short high owner cloth is mounted to real masonry above the opening.
        z=F+.10+PLANS[age()]['wall_height']-.09
        q=B('AnimalBayOwner'+str(i),(xfront+.012,s['y'],z),(.024,.82,.14),'owner','finish','owner','stall_'+str(i))
        q['mounting_parent']=s['arch'].name
        B('MouthTraffic'+str(i),(-2.40,s['y'],F+.004),(.10,.85,.008),'grime','finish','wear','court_ground')
    for j in range(3):
        B('CourtApproachPaver'+str(j),(-3.90,NATIVE[CURRENT]['primary_stamp_bounds'][0][1]+.035+j*.035,F+.025),(.95,.03,.05),'stone','foundation','ground','entry_path')
    print('DETAIL_DRAFT',CURRENT,'masonry-mounted owner textile, local animal traffic and drain')


def show(key='A2',state='healthy',lod=0):
    R.configure(ROOT,'stable')
    if key not in NATIVE:raise ValueError('Unknown body key')
    scene=bpy.data.scenes[R.SCENE]
    for c in scene.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=scene
    R.view(pos=(15,-19,15),center=(-.5,-.4,1.8),distance=20,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    if key is not None and key not in NATIVE:raise ValueError('Unknown body key')
    prefix='PSB_stable_'+(key+'_' if key else '')
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):
            data=ob.data if ob.type=='MESH' else None
            bpy.data.objects.remove(ob,do_unlink=True)
            if data and not data.users:bpy.data.meshes.remove(data)
    for c in list(bpy.data.collections):
        if c.name.startswith(prefix):bpy.data.collections.remove(c)
    if key:
        ANCHORS.pop(key,None);ASSEMBLIES.pop(key,None)
        CONTRACTS[:]=[c for c in CONTRACTS if c['body']!=key]
    else:ANCHORS.clear();ASSEMBLIES.clear();CONTRACTS.clear()


def build_lod(H,key,state,source,destination,level,profile):
    """Parent-only family LOD source adapter; no healthy mesh mutation."""
    import importlib.util
    spec=importlib.util.spec_from_file_location("stable_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
