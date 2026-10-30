"""Unbuilt original civil Divan source, one existing resource-age A1 body.

The resource age does not establish availability or historical construction date.
Institution-led interpretation; projected stamp frame; no integration or playback.
"""
from pathlib import Path
import sys
import json
import bpy

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'divan_commerce')
F=.16
CURRENT='A1'
ANCHORS={}
CONTRACTS=[]
ASSEMBLIES={}
TEXTURE_INPUTS={k:str(ROOT/'textures'/(k+'.png')) for k in ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC={'resolution':[2048,2048],'original_pixels_required':True,'status':'paths only; parent supplies original atlas'}
FAMILY_INVENTORY_KEY='divan_economy'
ACTOR='ps_building_divan_economy_persia'
VARIANT_EVIDENCE={'campaign':'existing_private_compiled_variant','default':'existing_private_compiled_variant','hre_brawl':'existing_private_compiled_variant',
 'cordoba':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
 'xp3':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant'}
STAMP_MATRIX=[[-1.,0.,0.,-.05000000074505806],[0.,-1.,0.,-.6434699892997742],[0.,0.,1.,0.],[0.,0.,0.,1.]]
NATIVE={'A1':{
 'resource_age_label':1,'resource_age_is_not_availability':True,
 'model':'art/civilizations/sultanate/structures/wonder_great_mosque_of_delhi/sul_great_mosque_of_delhi_control_age01/sul_great_mosque_of_delhi_control_age01.rgm',
 'model_sha256':'1090b91f30a87fb8c4a568d9138d97f0bd4ed5a9d4118af725d74397eff5ef20','triangles':69870,
 'budget_target':59652,'budget_cap':208161,
 'primary_resource_bounds':[[-7.17578125,-8.1328125,-1.599609375],[7.17578125,7.60546875,10.25]],
 'primary_stamp_bounds':[[-7.2257812507,-8.2489387393,-1.599609375],[7.1257812493,7.4893425107,10.25]],
 'conditional_compound_bounds':[[-10.2494230362,-9.8506014777,-1.599609375],[9.7970504069,10.1686149675,10.25]],
}}
NATIVE['A1']['source_uses']=[dict(actor=ACTOR,variant=v,variant_evidence_class=e,
 attachment='attachments/attachment_lists/civilizations/sultanate/buildings/landmark_quwwat_ul_islam_sul/landmark_quwwat_ul_islam_control_sul',
 attachment_category='default',inventory_category='default',stamp='art/stamps/civ_sul/sul_wonder_quwwat_ul_islam.bin',stamp_instance_index=0)
 for v,e in VARIANT_EVIDENCE.items()]
REVIEW_BOUNDS=[[-6.60,-6.00,-.06],[6.50,6.50,5.50]]
PLANS={1:{'program':'broad public assessment/clerks range, protected northeast archive and side delivery porch',
          'main':(-1.30,3.20,9.00,3.80,3.30),'archive':(4.65,4.10,2.90,4.00,4.20)}}
NATIVE_STATE_CONTRACT={
 'life_cycle_values':['construct_'+str(i).zfill(2) for i in range(0,100,5)]+['healthy']+['damage_'+str(i) for i in range(1,6)]+['ruins','preview','targeting'],
 'conditional_properties':['has_collapsed_damage1','has_collapsed_damage2','has_collapsed_damage3','has_collapsed_damage4','has_collapsed_damage5','has_collapsed_ruins','life_cycle_state_previous','burn_state','jin_debuff','debug_static_rig_name'],
 'native_primary_skeleton_present':False,'actions':'15 original collapse/repair/static-rig references; no new clips or playback.',
 'reference':'research/persia_buildings/inventory/FAMILY_NATIVE_STATE_CONTRACTS.json',
 'status':'Inventory only; native component/effect and repair mappings remain parent work. No HP or gameplay-age assumptions.',
}
NATIVE_DEPENDENCIES={
 'layout':'art/civilizations/common/layouts/archetypes/layout_market/layout_market.rgm',
 'layout_skeleton_present':True,'layout_marker_count':11,'existing_props':['stone_bench','sagebush_row'],
 'marker_frame':'Bone-local until native skeleton/pose evaluation, not world-space sockets.',
 'policy':'Retain original layout, physics/repair/auxiliary effect owners and exact native bindings; no new motion.',
 'clearance_status':'Unqualified: source rest envelope is not native footprint, interaction/production route or terrain clearance.',
}


def age():return NATIVE[CURRENT]['resource_age_label']


def root(key=None,state='healthy',lod=0):
    R.configure(ROOT,'divan_commerce');key=key or CURRENT
    if key not in NATIVE:raise ValueError('Only the existing Divan Commerce resource A1 is admitted')
    return R.collection(R.PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)


def col(role):
    parent=root();return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,parent)


def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role;ob['draft_uninspected']=True
    ob['authored_coordinate_space']='projected stamp frame; inverse adapter pending'
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
    R.configure(ROOT,'divan_commerce');s=R.setup_scene()
    s['historical_basis']='Original fiscal/chancery interpretation from Divan, Daftar and royal-secretariat research; not a surviving named monument reconstruction.'
    s['chronology_limit']='A1 is a resource label only. No Dark Age availability or exact medieval office elevation is inferred. No 1643-44 royal talar copy.'
    R.view(pos=(17,-22,18),center=(-.2,.3,2.3),distance=23,solid=True)


def foundation(key='A1'):
    global CURRENT
    if key not in NATIVE:raise ValueError('Unknown existing body')
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body exists; explicit owned reset required')
    ground=B('CivilOfficeEarthBed',(-.05,.25,.05),(13.10,12.50,.22),'earth','foundation','ground','court_ground')
    court=B('PublicAssessmentCourt',(-1.50,-1.35,F+.025),(8.60,5.30,.05),'stone','foundation','ground','public_court')
    contact('PublicCourtGround',court,ground)
    lo,hi=NATIVE[key]['primary_stamp_bounds']
    margins=[REVIEW_BOUNDS[0][0]-lo[0],REVIEW_BOUNDS[0][1]-lo[1],hi[0]-REVIEW_BOUNDS[1][0],hi[1]-REVIEW_BOUNDS[1][1],hi[2]-REVIEW_BOUNDS[1][2]]
    if min(margins)<0:raise ValueError('Draft proposal exceeds measured primary rest envelope')
    ANCHORS[key]=dict(ground_top=F,native_body_key=key,native_model=NATIVE[key]['model'],native_model_sha256=NATIVE[key]['model_sha256'],
      resource_age_label=1,availability='Unchanged and not inferred from resource age',source_uses=NATIVE[key]['source_uses'],family_inventory_key=FAMILY_INVENTORY_KEY,
      authoring_bounds_proposal=REVIEW_BOUNDS,native_primary_stamp_bounds=NATIVE[key]['primary_stamp_bounds'],conditional_compound_bounds=NATIVE[key]['conditional_compound_bounds'],envelope_proposal_margins=margins,
      projected_resource_to_stamp_matrix=STAMP_MATRIX,stamp_to_projected_resource_matrix=STAMP_MATRIX,
      authored_space='projected stamp coordinates; translated half-turn is its own inverse',
      public_route=[[-1.30,-4.85,F],[-1.30,1.30,F]],service_route=[[4.65,-2.0,F],[4.65,2.10,F]],
      historical_claim='Original institution-led composition, not the recovered historical Divan of Commerce',
      dependencies=NATIVE_DEPENDENCIES,native_states=NATIVE_STATE_CONTRACT,native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],visual_inspection='Not performed; parent serial build required')
    ASSEMBLIES[key]={'ground':ground,'court':court}
    print('FOUNDATION_DRAFT',key,'civil office programme; resource age does not assign availability')


def first_room():
    x,y,w,d,h=PLANS[1]['main'];bottom=F+.10;t=.24;g='clerks_range'
    floor=B('ClerksRangeFloor',(x,y,F+.05),(w,d,.10),'stone','foundation','ground',g)
    back=wall('ClerksBack',x,y+d/2-t/2,w,t,h,bottom=bottom,group=g)
    for side in (-1,1):wall('ClerksSide'+str(side),x+side*(w/2-t/2),y,t,d-.48,h,bottom=bottom,group=g)
    arches=[]
    for i in range(3):
        xx=x-w/2+(i+.5)*w/3;opening=2.20 if i==1 else 1.08
        p=tag(R.archwall(CURRENT+'_CivilReceptionArch'+str(i),xx,y-d/2,y-d/2+t,bottom,w/3,h,opening,2.05,.50,'brick',col('architecture'),segments=20),'walls','architecture',g)
        contact('CivilArchFoot'+str(i),p,floor);arches.append(p)
        if i!=1:
            q=B('ClerksRecessedDoor'+str(i),(xx,y-d/2+.18,bottom+.95),(.98,.045,1.90),'timber','finish','fittings',g);contact('ClerksDoorFoot'+str(i),q,floor)
    ASSEMBLIES[CURRENT]['main']=dict(x=x,y=y,w=w,d=d,h=h,bottom=bottom,top=bottom+h,floor=floor,back=back,arches=arches)
    print('FIRST_ROOM_DRAFT',CURRENT,'one public reception recess, controlled side doors and broad office range')


def main_roof():
    a=ASSEMBLIES[CURRENT]['main'];x,y,w,d,z=a['x'],a['y'],a['w'],a['d'],a['top'];bay=w/3
    for i in range(3):
        xx=x-w/2+(i+.5)*bay
        p=R.vault(CURRENT+'_ClerksVault'+str(i),xx,y-d/2,y+d/2,z,(bay-.24)/2,.52,.12,'roof',col('roofs'),segments=24,along=4,stage='vaults')
        tag(p,'vaults','roofs','clerks_range');contact('ClerksVaultFront'+str(i),p,a['arches'][i]);contact('ClerksVaultBack'+str(i),p,a['back'])


def archive_room():
    x,y,w,d,h=PLANS[1]['archive'];bottom=F+.10;t=.24;g='protected_archive'
    floor=B('ArchiveFloor',(x,y,F+.05),(w,d,.10),'stone','foundation','ground',g)
    back=wall('ArchiveBack',x,y+d/2-t/2,w,t,h,bottom=bottom,group=g)
    wall('ArchiveWest',x-w/2+t/2,y,t,d-.48,h,bottom=bottom,group=g)
    # A true high east window ventilates protected stores, not an invented
    # additional occupied floor or a texture rectangle on solid masonry.
    low,winh,ww=2.70,.70,.74
    wall('ArchiveEastLower',x+w/2-t/2,y,t,d-.48,low,bottom=bottom,group=g)
    wall('ArchiveEastHead',x+w/2-t/2,y,t,d-.48,h-low-winh,bottom=bottom+low+winh,group=g)
    for side in (-1,1):wall('ArchiveWindowPier'+str(side),x+w/2-t/2,y+side*(d-.48+ww)/4,t,(d-.48-ww)/2,winh,bottom=bottom+low,group=g)
    B('ArchiveRecessedShutter',(x+w/2-.20,y,bottom+low+winh/2),(.04,.64,.60),'timber','finish','fittings',g)
    opening=1.06;pw=(w-opening)/2
    for side in (-1,1):wall('ArchiveDoorPier'+str(side),x+side*(opening/2+pw/2),y-d/2+t/2,pw,t,h,bottom=bottom,group=g)
    wall('ArchiveDoorHead',x,y-d/2+t/2,opening,t,h-2.02,bottom=bottom+2.02,group=g)
    door=B('ArchiveSecureDoor',(x,y-d/2+.18,bottom+.98),(.96,.055,1.96),'timber','finish','fittings',g);contact('ArchiveDoorFoot',door,floor)
    roof=B('ArchiveRoof',(x,y,bottom+h+.10),(w,d,.20),'roof','vaults','roofs',g);contact('ArchiveRoofBearing',roof,back)
    ASSEMBLIES[CURRENT]['archive']=dict(x=x,y=y,floor=floor,bottom=bottom)


def porch(label,x,y,w,d,top):
    floor=B(label+'_Floor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',label)
    posts=[]
    for sx in (-1,1):
        for j in range(4 if w>5 else 2):
            count=4 if w>5 else 2;xx=x-w/2+.14+j*(w-.28)/(count-1)
            yy=y+sx*(d/2-.14)
            p=wall(label+'_Post'+str(sx)+'_'+str(j),xx,yy,.16,.16,top-F-.08,'timber',F+.08,label)
            contact(label+'_PostFoot'+str(sx)+'_'+str(j),p,floor);posts.append((sx,j,p))
        beam=B(label+'_Beam'+str(sx),(x,y+sx*(d/2-.14),top+.09),(w,.22,.18),'timber','vaults','architecture',label)
        for s,j,p in posts:
            if s==sx:contact(label+'_BeamBearing'+str(sx)+'_'+str(j),beam,p)
    roof=B(label+'_Roof',(x,y,top+.27),(w+.06,d+.06,.18),'roof','vaults','roofs',label)
    for side in (-1,1):contact(label+'_RoofBeam'+str(side),roof,bpy.data.objects[R.PREFIX+CURRENT+'_'+label+'_Beam'+str(side)])
    return floor


def public_gate():
    x,y,w,opening=-1.30,-4.55,8.60,1.50;h=.65
    for side in (-1,1):
        pw=(w-opening)/2
        wall('PublicBoundary'+str(side),x+side*(opening/2+pw/2),y,pw,.20,h,group='public_gate')
        p=wall('CivilGatePost'+str(side),x+side*(opening/2+.09),y,.18,.24,2.45,'timber',F,'public_gate')
        contact('CivilGatePostGround'+str(side),p,ASSEMBLIES[CURRENT]['ground'])
    beam=B('CivilGateHeader',(x,y,F+2.54),(opening+.36,.24,.18),'timber','walls','architecture','public_gate')
    for side in (-1,1):contact('CivilGateHeaderBearing'+str(side),beam,bpy.data.objects[R.PREFIX+CURRENT+'_CivilGatePost'+str(side)])


def architecture():
    main_roof();archive_room()
    ASSEMBLIES[CURRENT]['clerks_porch_floor']=porch('public_clerks_porch',-1.30,.65,9.00,1.30,F+2.72)
    ASSEMBLIES[CURRENT]['delivery_floor']=porch('document_delivery',4.65,-.10,2.90,4.40,F+2.48)
    public_gate()
    print('ARCHITECTURE_DRAFT',CURRENT,'broad civil facade, higher archive and separate service delivery')


def desk(name,x,y,floor,z0,w=1.65):
    top=z0+.66
    table=B(name+'_Top',(x,y,top-.05),(w,.68,.10),'timber','finish','props','records_work')
    for sx in (-1,1):
        for sy in (-1,1):
            q=B(name+'_Leg'+str(sx)+str(sy),(x+sx*(w/2-.12),y+sy*.22,(z0+top-.10)/2),(.085,.085,top-.10-z0),'timber','finish','props','records_work')
            contact(name+'_LegTop'+str(sx)+str(sy),q,table,'top-bottom');contact(name+'_LegFoot'+str(sx)+str(sy),q,floor)
    return table,top


def props():
    a=ASSEMBLIES[CURRENT]['main'];table,top=desk('AssessmentDesk',-1.30,3.85,a['floor'],a['bottom'])
    for j in range(3):
        q=B('SealedDocumentBundle'+str(j),(-1.75+j*.44,3.85,top+.035),(.34,.26,.07),'paper','finish','props','records_work');contact('DocumentOnDesk'+str(j),q,table)
    arc=ASSEMBLIES[CURRENT]['archive']
    for j in range(2):
        q=B('ArchiveChest'+str(j),(4.15+j*.95,5.40,arc['bottom']+.27),(.78,.62,.54),'timber','finish','props','protected_archive');contact('ArchiveChestFloor'+str(j),q,arc['floor'])
        B('ArchiveChestLid'+str(j),(4.15+j*.95,5.40,arc['bottom']+.57),(.81,.65,.06),'timber','finish','props','protected_archive')
    p,z=desk('DeliveryWeightsTable',5.25,-.50,ASSEMBLIES[CURRENT]['delivery_floor'],F+.08,1.10)
    for j in range(3):
        q=R.lathe(CURRENT+'_MeasurementWeight'+str(j),(4.95+j*.25,-.50,z),[(.07,0),(.07,.10),(.04,.14)],'metal',col('props'),sides=8,role='props')
        tag(q,'finish','props','records_work');contact('WeightOnTable'+str(j),q,p)
    print('PROPS_DRAFT',CURRENT,'protected documents/chests and measured delivery; no coin-pile identity')


def detail():
    a=ASSEMBLIES[CURRENT]['main']
    q=B('CivilReceptionOwnerCloth',(-1.30,a['y']-a['d']/2-.012,a['top']-.12),(1.25,.024,.16),'owner','finish','owner','clerks_range');q['mounting_parent']=a['arches'][1].name
    for j in range(4):B('CivilBrickFraming'+str(j),(-1.90+j*.40,1.285,a['top']-.23),(.22,.03,.09),'carving','finish','fine_detail','clerks_range')
    for j in range(3):B('DeliveryThresholdWear'+str(j),(4.40+j*.18,1.84,F+.084),(.25,.32,.008),'grime','finish','wear','document_delivery')
    print('DETAIL_DRAFT',CURRENT,'restrained administrative frame and localized delivery wear')


def show(key='A1',state='healthy',lod=0):
    R.configure(ROOT,'divan_commerce')
    if key not in NATIVE:raise ValueError('Unknown existing body')
    s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s;R.view(pos=(17,-22,18),center=(-.2,.3,2.3),distance=23,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    if key is not None and key not in NATIVE:raise ValueError('Unknown existing body')
    prefix='PSB_divan_commerce_'+(key+'_' if key else '')
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
    spec=importlib.util.spec_from_file_location("divan_commerce_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
