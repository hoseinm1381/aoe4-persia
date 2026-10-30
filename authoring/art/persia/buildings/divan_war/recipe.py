"""Unbuilt original Divan of War, preserving two DIFFERENT native branches.

A3 is the default Sultanate arsenal resource; A4 is the campaign/hre_brawl
Ottoman military-school resource. Resource ages do not define an age-up chain.
"""
from pathlib import Path
import sys
import json
import bpy

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'divan_war')
F=.16
CURRENT='A3'
ANCHORS={}
CONTRACTS=[]
ASSEMBLIES={}
TEXTURE_INPUTS={k:str(ROOT/'textures'/(k+'.png')) for k in ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC={'resolution':[2048,2048],'original_pixels_required':True,'status':'paths only; parent generates original atlas'}
FAMILY_INVENTORY_KEY='divan_military'
ACTOR='ps_building_divan_military_persia'
NATIVE={
 'A3':{'resource_age_label':3,'model':'art/civilizations/sultanate/structures/arsenal/sul_arsenal_control_age03/sul_arsenal_control_age03.rgm',
 'model_sha256':'85e9cb03e8d11e2a1a948a046643a108b481552bde5882829bfcbe1277309138','triangles':32075,'budget_target':55112,'budget_cap':96840,
 'primary_resource_bounds':[[-6.2890625,-5.92578125,-1.599609375],[5.90625,5.4453125,4.6640625]],
 'primary_stamp_bounds':[[-5.90625,-6.4453125,-1.599609375],[6.2890625,4.92578125,4.6640625]],
 'conditional_compound_bounds':[[-7.6878341514,-8.3690498081,-1.599609375],[6.8992946928,6.5843862787,4.6640625]],
 'stamp_matrix':[[-1.,0.,0.,0.],[0.,-1.,0.,-1.],[0.,0.,1.,0.],[0.,0.,0.,1.]],
 'stamp_inverse':[[-1.,0.,0.,0.],[0.,-1.,0.,-1.],[0.,0.,1.,0.],[0.,0.,0.,1.]],
 'source_uses':[dict(actor=ACTOR,variant=v,variant_evidence_class=e,
   attachment='attachments/attachment_lists/civilizations/sultanate/buildings/tech_unit_ranged_sul/tier3_tech_unit_ranged_control_sul',
   attachment_category='default',inventory_category='default',stamp='art/stamps/civ_sul/sul_arsenal_03.bin',stamp_instance_index=0)
   for v,e in [('default','existing_private_compiled_variant'),('cordoba','official_parent_inheritance_candidate_not_a_separately_serialized_private_variant'),('xp3','official_parent_inheritance_candidate_not_a_separately_serialized_private_variant')]]},
 'A4':{'resource_age_label':4,'model':'art/civilizations/ottoman/structures/military_academy/ott_military_academy_control_age04/ott_military_academy_control_age04.rgm',
 'model_sha256':'80dfd9482362b286e1b87ee7bdf6513e974158660b278a40ae9898319d39c888','triangles':129648,'budget_target':52048,'budget_cap':86329,
 'primary_resource_bounds':[[-6.22265625,-6.25390625,-1.6171875],[5.8515625,6.81640625,7.8515625]],
 'primary_stamp_bounds':[[-6.6164062470,-6.1226562485,-1.6171875],[6.4539062530,5.9515625015,7.8515625]],
 'conditional_compound_bounds':[[-9.2112478148,-8.0086053680,-2.2587890027],[8.9741058350,7.9602437019,7.8515625]],
 'stamp_matrix':[[-2.220446049250313e-16,-1.0000000000000002,0.,.20000000298023224],[1.0000000000000002,-2.220446049250313e-16,0.,.10000000149011612],[0.,0.,1.,0.],[0.,0.,0.,1.]],
 'stamp_inverse':[[0.,1.,0.,-.10000000149011612],[-1.,0.,0.,.20000000298023224],[0.,0.,1.,0.],[0.,0.,0.,1.]],
 'source_uses':[dict(actor=ACTOR,variant=v,variant_evidence_class='existing_private_compiled_variant',
   attachment='attachments/attachment_lists/civilizations/ottoman/buildings/building_military_school_ott/tier4_military_school_control_ott',
   attachment_category='default',inventory_category='default',stamp='art/stamps/civ_ott/ott_military_school_age_04.bin',stamp_instance_index=0)
   for v in ('campaign','hre_brawl')]},
}
PLANS={
 3:{'program':'low dispatch office, two broad inspection bays and rear records range around an open muster court',
    'bounds':[[-5.60,-5.90,-.06],[5.80,4.60,4.55]],'court':(.80,-1.35,7.40,6.90),
    'register':(.25,3.35,10.50,2.50,2.42),'porch':(-4.45,.10,2.20,4.00,2.30),'office_height':3.05,'upper_office':False},
 4:{'program':'occupied upper dispatch room, longer inspection porch and deeper court-led administrative range',
    'bounds':[[-5.90,-5.80,-.06],[6.00,5.60,6.30]],'court':(.80,-.85,7.40,7.90),
    'register':(.25,4.30,10.50,2.40,2.85),'porch':(-4.45,.55,2.20,5.10,2.48),'office_height':4.60,'upper_office':True},
}
NATIVE_STATE_CONTRACT={
 'life_cycle_values':['construct_'+str(i).zfill(2) for i in range(0,100,5)]+['healthy']+['damage_'+str(i) for i in range(1,6)]+['ruins','preview','targeting'],
 'conditional_properties':['has_collapsed_damage1','has_collapsed_damage2','has_collapsed_damage3','has_collapsed_damage4','has_collapsed_damage5','has_collapsed_ruins','life_cycle_state_previous','burn_state','jin_debuff','debug_static_rig_name'],
 'native_primary_skeleton_present':False,'native_actions':'15 original collapse/repair/static-rig references per primary body; no new clip/playback.',
 'reference':'research/persia_buildings/inventory/FAMILY_NATIVE_STATE_CONTRACTS.json',
 'status':'Inventory only; preserve branch-specific physics/visibility/effect owners and exact mappings; no HP, age admission or new variant inference.',
}
NATIVE_DEPENDENCIES={
 'layout':'art/civilizations/common/layouts/archetypes/layout_market/layout_market.rgm','layout_skeleton_present':True,'layout_marker_count':11,
 'other_existing_owners':['wood_pieces','banner_barracks','banner_archery','banner_stables'],
 'branch_difference':'Default arsenal props and campaign military-school props differ; retain actual branch legal membership, never merge them.',
 'marker_frame':'Bone-local until native skeleton/pose evaluation; no world-space socket claim.',
 'policy':'Preserve native layout, branch-specific graphs, markers and legal attachments. No new moving rig, troops or animals.',
 'clearance_status':'Unqualified: static fit and source open lane do not establish footprint, courier/horse route, native exit or terrain clearance.',
}


def age():return NATIVE[CURRENT]['resource_age_label']


def root(key=None,state='healthy',lod=0):
    R.configure(ROOT,'divan_war');key=key or CURRENT
    if key not in NATIVE:raise ValueError('Only the two existing War Divan branch resources A3/A4 are admitted')
    return R.collection(R.PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)


def col(role):
    parent=root();return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,parent)


def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role;ob['draft_uninspected']=True
    ob['authored_coordinate_space']='projected stamp-space; branch-specific inverse adapter pending'
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
    R.configure(ROOT,'divan_war');s=R.setup_scene()
    s['historical_basis']='Original divan-e arz muster, pay/register and dispatch composition; no surviving exact War Divan plan is claimed.'
    s['branch_warning']='A3/default and A4/campaign-hre_brawl are alternative native branches, not a proven age-up sequence.'
    R.view(pos=(16,-21,17),center=(0.,-.3,2.),distance=23,solid=True)


def foundation(key='A3'):
    global CURRENT
    if key not in NATIVE:raise ValueError('Unknown existing branch body')
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body exists; explicit owned reset required')
    bounds=PLANS[age()]['bounds'];(x0,y0,z0),(x1,y1,z1)=bounds
    ground=B('MilitaryOfficeEarthBed',((x0+x1)/2,(y0+y1)/2,.05),(x1-x0,y1-y0,.22),'earth','foundation','ground','court_ground')
    x,y,w,d=PLANS[age()]['court'];court=B('MusterReviewPaving',(x,y,F+.025),(w,d,.05),'stone','foundation','ground','muster_court');contact('MusterPavingGround',court,ground)
    lo,hi=NATIVE[key]['primary_stamp_bounds']
    margins=[x0-lo[0],y0-lo[1],hi[0]-x1,hi[1]-y1,hi[2]-z1]
    if min(margins)<0:raise ValueError('Draft bounds exceed the current branch primary rest envelope')
    ANCHORS[key]=dict(ground_top=F,native_body_key=key,native_model=NATIVE[key]['model'],native_model_sha256=NATIVE[key]['model_sha256'],
      resource_age_label=age(),availability='Unchanged; resource label is not an age-up chain',source_uses=NATIVE[key]['source_uses'],family_inventory_key=FAMILY_INVENTORY_KEY,
      authoring_bounds_proposal=bounds,native_primary_stamp_bounds=NATIVE[key]['primary_stamp_bounds'],conditional_compound_bounds=NATIVE[key]['conditional_compound_bounds'],envelope_proposal_margins=margins,
      projected_resource_to_stamp_matrix=NATIVE[key]['stamp_matrix'],stamp_to_projected_resource_matrix=NATIVE[key]['stamp_inverse'],
      authored_space='projected stamp-space; inverse returns projected resource frame',review_lane=[[-.80,-4.90,F],[-.80,1.65 if age()==3 else 2.65,F]],
      historical_claim='Original military administration interpretation; no standing troop diorama or recovered historical office',
      dependencies=NATIVE_DEPENDENCIES,native_states=NATIVE_STATE_CONTRACT,native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],visual_inspection='Not performed; parent serial build required')
    ASSEMBLIES[key]={'ground':ground,'court':court}
    print('FOUNDATION_DRAFT',key,'court-led military administration; preserve native branch split')


def first_room():
    x,y,w,d=-4.10,-3.65,2.70,3.30;bottom=F+.10;h=PLANS[age()]['office_height'];t=.24;g='dispatch_office'
    floor=B('DispatchGroundFloor',(x,y,F+.05),(w,d,.10),'stone','foundation','ground',g)
    back=wall('DispatchWest',x-w/2+t/2,y,t,d,h,bottom=bottom,group=g)
    for s in (-1,1):wall('DispatchEnd'+str(s),x,y+s*(d/2-t/2),w-.48,t,h,bottom=bottom,group=g)
    front=x+w/2;lowh=2.45 if age()==4 else h
    arch=tag(R.archwall(CURRENT+'_DispatchDoorArch',y,front-t,front,bottom,d-.48,lowh,1.12,1.75,.42,'brick',col('architecture'),segments=18,transform=lambda u,v,z:(v,u,z)),'walls','architecture',g)
    contact('DispatchArchFoot',arch,floor)
    if age()==4:
        upper=bottom+2.45;wb=upper+.75;wh=.75;wy=y+.30;ww=.78;ymin=y-d/2+t;ymax=y+d/2-t
        wall('UpperDispatchLower',front-t/2,(ymin+ymax)/2,t,ymax-ymin,.75,bottom=upper,group=g)
        wall('UpperDispatchHead',front-t/2,(ymin+ymax)/2,t,ymax-ymin,h-2.45-1.50,bottom=wb+wh,group=g)
        for label,ya,yb in [('Front',ymin,wy-ww/2),('Rear',wy+ww/2,ymax)]:wall('UpperDispatchWindowPier'+label,front-t/2,(ya+yb)/2,t,yb-ya,wh,bottom=wb,group=g)
        B('UpperDispatchRecessedShutter',(front-.18,wy,wb+wh/2),(.04,.66,.65),'timber','finish','fittings',g)
    roof=B('DispatchRoof',(x,y,bottom+h+.09),(w,d,.18),'roof','vaults','roofs',g);contact('DispatchRoofWest',roof,back)
    ASSEMBLIES[CURRENT]['office']=dict(x=x,y=y,w=w,d=d,h=h,bottom=bottom,floor=floor,front=front)
    print('FIRST_ROOM_DRAFT',CURRENT,'occupied office with genuine courtyard-facing entrance/window')


def upper_office_access():
    if age()<4:return
    a=ASSEMBLIES[CURRENT]['office'];z0=a['bottom'];upper=z0+2.45;g='dispatch_stair'
    ix0,ix1,iy0,iy1=-5.21,-2.99,-5.06,-2.24
    hx0,hx1,hy0,hy1=-5.18,-4.48,-4.88,-2.80
    panels=[('East',hx1,ix1,iy0,iy1),('WestLedger',ix0,hx0,iy0,iy1),('Front',hx0,hx1,iy0,hy0),('Landing',hx0,hx1,hy1,iy1)]
    for label,xa,xb,ya,yb in panels:
        B('DispatchUpperFloor'+label,((xa+xb)/2,(ya+yb)/2,upper-.06),(xb-xa,yb-ya,.12),'timber','walls','architecture','dispatch_office')
    for j in range(13):
        height=(j+1)*2.45/13
        step=B('DispatchStair'+str(j),(-4.85,hy0+(j+.5)*.16,z0+height/2),(.62,.16,height),'stone','walls','architecture',g)
        if j==12:step['landing_interface']='Rear face y=-2.80; walking top z=2.71 exactly meets landing front/top.'
    ANCHORS[CURRENT]['upper_stair']=dict(hole_bounds=[[hx0,hy0],[hx1,hy1]],walking_top=upper,last_rear_y=hy1,landing_front_y=hy1,landing_depth=iy1-hy1,
      status='Analytic source interfaces only; parent must inspect real tread/landing/headroom and accessibility.')


def register_range():
    x,y,w,d,h=PLANS[age()]['register'];bottom=F+.10;t=.22;g='pay_register'
    floor=B('RegisterFloor',(x,y,F+.05),(w,d,.10),'stone','foundation','ground',g)
    back=wall('RegisterBack',x,y+d/2-t/2,w,t,h,bottom=bottom,group=g)
    for side in (-1,1):wall('RegisterEnd'+str(side),x+side*(w/2-t/2),y,t,d-.44,h,bottom=bottom,group=g)
    for i in range(3):
        xx=x-w/2+(i+.5)*w/3
        p=tag(R.archwall(CURRENT+'_RegisterDoorArch'+str(i),xx,y-d/2,y-d/2+t,bottom,w/3,h,1.12,1.70,.35,'brick',col('architecture'),segments=16),'walls','architecture',g)
        contact('RegisterArchFoot'+str(i),p,floor)
        if i!=1:
            q=B('RegisterClosedDoor'+str(i),(xx,y-d/2+.16,bottom+.94),(1.00,.045,1.88),'timber','finish','fittings',g);contact('RegisterDoorFoot'+str(i),q,floor)
    roof=B('RegisterQuietRoof',(x,y,bottom+h+.085),(w,d,.17),'roof','vaults','roofs',g);contact('RegisterRoofBack',roof,back)
    ASSEMBLIES[CURRENT]['register']=dict(x=x,y=y,w=w,d=d,h=h,bottom=bottom,floor=floor)


def inspection_porch():
    x,y,w,d,h=PLANS[age()]['porch'];bottom=F+.08;g='inspection_porch'
    floor=B('InspectionFloor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',g)
    outer=wall('InspectionOuter',x-w/2+.11,y,.22,d,h,bottom=bottom,group=g)
    bays=2 if age()==3 else 3
    for i in range(bays):
        yy=y-d/2+(i+.5)*d/bays;front=x+w/2
        opening=d/bays-.35
        p=tag(R.archwall(CURRENT+'_InspectionArch'+str(i),yy,front-.22,front,bottom,d/bays,h,opening,1.56,.35,'brick',col('architecture'),segments=16,transform=lambda u,v,z:(v,u,z)),'walls','architecture',g)
        contact('InspectionArchFoot'+str(i),p,floor)
        slab=B('InspectionRoof'+str(i),(x,yy,bottom+h+.08),(w,d/bays,.16),'roof','vaults','roofs',g)
        contact('InspectionRoofArch'+str(i),slab,p);contact('InspectionRoofOuter'+str(i),slab,outer)
    ASSEMBLIES[CURRENT]['inspection']=dict(x=x,y=y,floor=floor,bottom=bottom)


def controlled_gate():
    x,y,w,h=-.80,-5.10,2.60,(2.65 if age()==3 else 2.95);opening=1.70;g='controlled_gate'
    arch=tag(R.archwall(CURRENT+'_ControlledGateArch',x,y-.12,y+.12,F,w,h,opening,1.80,.45,'brick',col('architecture'),segments=20),'walls','architecture',g)
    contact('ControlledGateFoot',arch,ASSEMBLIES[CURRENT]['ground'])
    cap=B('ControlledGateCap',(x,y,F+h+.075),(w+.06,.30,.15),'roof','vaults','roofs',g);contact('ControlledGateCapFoot',cap,arch)
    for label,xa,xb in [('West',-5.45,x-w/2),('East',x+w/2,5.30)]:wall('LowFrontBoundary'+label,(xa+xb)/2,y,xb-xa,.18,.64,group=g)
    ANCHORS[CURRENT]['gate_opening']=dict(center=[x,y,F],clear_width=opening,arch_spring=1.80,arch_rise=.45,native_mounted_clearance='Unverified')


def architecture():
    upper_office_access();register_range();inspection_porch();controlled_gate()
    print('ARCHITECTURE_DRAFT',CURRENT,'muster court, inspection porch, register office; no keep/barracks copy')


def desk(name,x,y,floor,z0,w=1.50):
    top=z0+.65
    p=B(name+'_Top',(x,y,top-.05),(w,.64,.10),'timber','finish','props','register_work')
    for sx in (-1,1):
        for sy in (-1,1):
            q=B(name+'_Leg'+str(sx)+str(sy),(x+sx*(w/2-.12),y+sy*.21,(z0+top-.10)/2),(.08,.08,top-.10-z0),'timber','finish','props','register_work')
            contact(name+'_LegTop'+str(sx)+str(sy),q,p,'top-bottom');contact(name+'_LegFloor'+str(sx)+str(sy),q,floor)
    return p,top


def props():
    a=ASSEMBLIES[CURRENT]['register'];p,z=desk('PayRegisterDesk',.25,a['y']+.30,a['floor'],a['bottom'])
    for j in range(2):
        q=B('MilitaryRegisterBundle'+str(j),(-.10+j*.65,a['y']+.30,z+.035),(.45,.28,.07),'paper','finish','props','register_work');contact('RegisterBundleOnDesk'+str(j),q,p)
    for j in range(2):
        q=B('PayRecordChest'+str(j),(3.70+j*.95,a['y']+.35,a['bottom']+.25),(.78,.62,.50),'timber','finish','props','pay_register');contact('PayChestFloor'+str(j),q,a['floor'])
    inspect=ASSEMBLIES[CURRENT]['inspection'];p,z=desk('InspectionBench',inspect['x']-.20,.30,inspect['floor'],inspect['bottom'],1.20)
    q=B('InspectionFoldedCloth',(inspect['x']-.20,.30,z+.06),(.76,.44,.12),'cloth','finish','props','inspection_porch');contact('InspectionBundleOnBench',q,p)
    # No static soldiers, sleeping bays, hay pile or arsenal wall of weapons.
    for j in range(2):
        q=wall('CourierTetherPost'+str(j),4.70,-3.25+j*1.25,.15,.15,1.12,'timber',F,'dispatch_court');contact('CourierPostGround'+str(j),q,ASSEMBLIES[CURRENT]['ground'])
    # A low review platform is an architectural cue, not an impassable parade
    # diorama. Its bed rests on the actual court paving.
    court=ASSEMBLIES[CURRENT]['court'];bottom=F+.05
    base=B('ReviewPlatformBase',(3.25,1.10,bottom+.10),(1.90,1.20,.20),'stone','foundation','architecture','review_platform');contact('ReviewPlatformCourt',base,court)
    for j in range(2):B('ReviewApproachStep'+str(j),(3.25,.20+j*.20,bottom+(j+1)*.05),(1.90,.20,(j+1)*.10),'stone','walls','architecture','review_platform')
    print('PROPS_DRAFT',CURRENT,'records/pay/inspection and a clear central review lane; no permanent troops')


def detail():
    a=ASSEMBLIES[CURRENT]['register'];y=a['y']-a['d']/2
    q=B('RegisterAdministrativeOwnerCloth',(.25,y-.012,a['bottom']+a['h']-.10),(1.12,.024,.14),'owner','finish','owner','pay_register')
    q['mounting_relation']='exterior register-office header above the real central opening'
    for j in range(3):B('GateHandlingWear'+str(j),(-1.20+j*.30,-4.90,F+.004),(.24,.30,.008),'grime','finish','wear','court_ground')
    print('DETAIL_DRAFT',CURRENT,'restrained office identity and practical gate handling wear')


def show(key='A3',state='healthy',lod=0):
    R.configure(ROOT,'divan_war')
    if key not in NATIVE:raise ValueError('Unknown existing branch')
    s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s;R.view(pos=(16,-21,17),center=(0.,-.3,2.),distance=23,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    if key is not None and key not in NATIVE:raise ValueError('Unknown existing branch')
    prefix='PSB_divan_war_'+(key+'_' if key else '')
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):
            data=ob.data if ob.type=='MESH' else None;bpy.data.objects.remove(ob,do_unlink=True)
            if data and not data.users:bpy.data.meshes.remove(data)
    for c in list(bpy.data.collections):
        if c.name.startswith(prefix):bpy.data.collections.remove(c)
    if key:
        ANCHORS.pop(key,None);ASSEMBLIES.pop(key,None);CONTRACTS[:]=[c for c in CONTRACTS if c['body']!=key]
    else:ANCHORS.clear();ASSEMBLIES.clear();CONTRACTS.clear()


def build_lod(H,key,state,source,destination,level,profile):
    """Parent-only family LOD source adapter; no healthy mesh mutation."""
    import importlib.util
    spec=importlib.util.spec_from_file_location("divan_war_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
