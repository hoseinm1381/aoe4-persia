"""Unbuilt original Persian Madrasa, only the existing Abbasid-backed A4 body.

Quiet asymmetric study court; no landmark copy or native integration. Metadata
retains projected stamp/resource frames. Import never builds, resets or saves.
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
R.configure(ROOT,'madrasa')

F=.16
CURRENT='A4'
ANCHORS={}
CONTRACTS=[]
ASSEMBLIES={}
TEXTURE_INPUTS={k:str(ROOT/'textures'/(k+'.png')) for k in ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC={'resolution':[2048,2048],'original_pixels_required':True,'status':'paths only; parent generates original family atlas'}
ACTOR='ps_building_tech_university_control_sul'
VARIANT_EVIDENCE={'campaign':'existing_private_compiled_variant','default':'existing_private_compiled_variant',
 'cordoba':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
 'xp3':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant'}
STAMP_MATRIX=[[-2.220446049250313e-16,-1.,0.,-1.1182709932],[1.0000000000000002,-2.220446049250313e-16,0.,-.4334749877],[0.,0.,1.,0.],[0.,0.,0.,1.]]
STAMP_INVERSE=[[0.,1.,0.,.4334749877],[-1.,0.,0.,-1.1182709932],[0.,0.,1.,0.],[0.,0.,0.,1.]]
NATIVE={'A4':{
 'age':4,'triangles':109152,'budget_target':95017,'budget_cap':109152,
 'model':'art/civilizations/abbasids/structures/university/abb_university_control_age04/abb_university_control_age04.rgm',
 'model_sha256':'d99a1de7cf8a50a28b4998cf40aa769d586b6f6fd2f90c5ad524cd0fdf738011',
 'primary_resource_bounds':[[-5.640625,-7.015625,-1.599609375],[6.61328125,6.359375,9.2734375]],
 'primary_stamp_bounds':[[-7.4776459932,-6.0740999877,-1.599609375],[5.8973540068,6.1798062623,9.2734375]],
 'conditional_compound_bounds':[[-8.2097799331,-8.8567325543,-1.599609375],[6.8117914693,8.3497992246,9.2734375]],
}}
NATIVE['A4']['source_uses']=[dict(actor=ACTOR,variant=v,variant_evidence_class=e,
 attachment='attachments/attachment_lists/civilizations/abbasid/buildings/tech_university_abb/tier4_tech_university_control_abb',
 attachment_category='default',inventory_category='default',stamp='art/stamps/civ_abbasid/abb_university.bin',stamp_instance_index=0)
 for v,e in VARIANT_EVIDENCE.items()]
REVIEW_BOUNDS=[[-6.50,-5.50,-.06],[4.85,5.65,5.30]]
COURT=[[-3.65,-3.85],[2.45,3.20]]
PLANS={4:{'program':'inward study-cell court, offset teaching loggia, west library and east service room; no rear dome',
          'west_cells':[(-5.10,y,2.40,1.80) for y in (-2.95,-1.15,.65,2.45)],
          'east_cells':[(3.70,y,2.00,1.80) for y in (-2.95,-1.15,.65)],
          'teaching':(-.30,4.40,4.40,2.30,3.65)}}
NATIVE_STATE_CONTRACT={
 'life_cycle_values':['construct_'+str(i).zfill(2) for i in range(0,100,5)]+['healthy']+['damage_'+str(i) for i in range(1,6)]+['ruins','preview','targeting'],
 'conditional_properties':['has_collapsed_damage1','has_collapsed_damage2','has_collapsed_damage3','has_collapsed_damage4','has_collapsed_damage5','has_collapsed_ruins','life_cycle_state_previous','burn_state','jin_debuff','debug_static_rig_name'],
 'primary_skeleton_present':False,
 'native_actions':'Original RGO physics collapse/repair/static-rig actions exist; no new clips or physics playback authored.',
 'reference':'research/persia_buildings/inventory/FAMILY_NATIVE_STATE_CONTRACTS.json',
 'status':'Inventory only. Parent must retain exact additional component predicates/owners and map source states; no HP or new tier assumptions.',
}
NATIVE_DEPENDENCIES={
 'layout':'art/civilizations/common/layouts/archetypes/layout_university/layout_university.rgm',
 'layout_skeleton_present':True,'layout_marker_count':10,
 'existing_props':['stone_bench','tree_small_garden','wall_stone_high_post'],
 'marker_frame':'Bone-local until native skeleton/pose evaluation; no world-space socket claim.',
 'policy':'Preserve layout, original physics/repair/effect graphs and legal attachments. No new motion or rig.',
 'clearance_status':'Unqualified: static envelope fit is not footprint, native doorway, monk/unit exit, interaction marker or terrain-clearance proof.',
}


def age():return NATIVE[CURRENT]['age']


def root(key=None,state='healthy',lod=0):
    R.configure(ROOT,'madrasa');key=key or CURRENT
    if key not in NATIVE:raise ValueError('Only existing Madrasa A4 is admitted')
    return R.collection(R.PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)


def col(role):
    parent=root();return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,parent)


def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role;ob['draft_uninspected']=True
    ob['authored_coordinate_space']='projected stamp-space; inverse adapter pending'
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
    R.configure(ROOT,'madrasa');s=R.setup_scene()
    s['historical_basis']='Original Timurid-to-Safavid-informed teaching/student-cell court; not a Khargird reconstruction or Gundeshapur copy.'
    R.view(pos=(15,-20,17),center=(-.8,.1,2.),distance=22,solid=True)


def foundation(key='A4'):
    global CURRENT
    if key not in NATIVE:raise ValueError('Unknown measured body')
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body exists; explicit owned reset required')
    bed=B('StudyCourtEarthBed',(-.825,.075,.05),(11.35,11.15,.22),'earth','foundation','ground','court_ground')
    x0,y0=COURT[0];x1,y1=COURT[1]
    court=B('TeachingCourtPaving',((x0+x1)/2,(y0+y1)/2,F+.025),(x1-x0,y1-y0,.05),'stone','foundation','ground','court_ground')
    contact('CourtPavingGround',court,bed)
    lo,hi=NATIVE[key]['primary_stamp_bounds']
    margins=[REVIEW_BOUNDS[0][0]-lo[0],REVIEW_BOUNDS[0][1]-lo[1],hi[0]-REVIEW_BOUNDS[1][0],hi[1]-REVIEW_BOUNDS[1][1],hi[2]-REVIEW_BOUNDS[1][2]]
    if min(margins)<0:raise ValueError('Draft envelope exceeds primary healthy bounds')
    ANCHORS[key]=dict(ground_top=F,native_body_key=key,native_model=NATIVE[key]['model'],native_model_sha256=NATIVE[key]['model_sha256'],existing_visual_age=4,source_uses=NATIVE[key]['source_uses'],
      authoring_bounds_proposal=REVIEW_BOUNDS,native_primary_stamp_bounds=NATIVE[key]['primary_stamp_bounds'],conditional_compound_bounds=NATIVE[key]['conditional_compound_bounds'],envelope_proposal_margins=margins,
      projected_resource_to_stamp_matrix=STAMP_MATRIX,stamp_to_projected_resource_matrix=STAMP_INVERSE,
      authored_space='projected stamp-space; inverse returns projected resource frame, not raw native axes',
      court_bounds=COURT,entry=[-.70,-5.25,F],dependencies=NATIVE_DEPENDENCIES,native_states=NATIVE_STATE_CONTRACT,
      native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],visual_inspection='Not performed; parent serial build required')
    ASSEMBLIES[key]={'ground':bed,'court':court,'cells':[]}
    print('FOUNDATION_DRAFT',key,'one existing tier; quiet inward court within primary rest envelope')


def cell(index,side,spec):
    x,y,w,d=spec;bottom=F+.08;h=2.42;t=.18;g='study_cell_'+str(index)
    floor=B(g+'_Floor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',g)
    # The back lies outward from the teaching court; the real door faces inward.
    back=wall(g+'_Back',x+side*(w/2-t/2),y,t,d,h,bottom=bottom,group=g)
    for s in (-1,1):wall(g+'_PartyWall'+str(s),x,y+s*(d/2-t/2),w-.36,t,h,bottom=bottom,group=g)
    front=x-side*w/2
    arch=tag(R.archwall(CURRENT+'_'+g+'_DoorArch',y,front-.10,front+.10,bottom,d,h,.90,1.62,.32,'brick',col('architecture'),segments=16,transform=lambda u,v,z:(v,u,z)),'walls','architecture',g)
    contact(g+'_ArchFoot',arch,floor)
    # Recessed leaf is folded open into the room, rather than a dark rectangle
    # on an uncut solid wall. Static editable pose, not new hinge playback.
    door=B(g+'_OpenDoor',(front+side*.38,y+.50,bottom+.94),(.76,.045,1.88),'timber','finish','fittings',g)
    door['source_pose']='static open; native hinge/motion not authored'
    roof=B(g+'_Roof',(x,y,bottom+h+.085),(w+.04,d,.17),'roof','vaults','roofs',g)
    contact(g+'_RoofFront',roof,arch);contact(g+'_RoofBack',roof,back)
    ASSEMBLIES[CURRENT]['cells'].append(dict(index=index,side=side,x=x,y=y,w=w,d=d,h=h,bottom=bottom,front=front,floor=floor,arch=arch))


def first_room():
    cell(0,-1,PLANS[4]['west_cells'][0])
    print('FIRST_ROOM_DRAFT',CURRENT,'one complete inward-facing study cell; parent inspection pending')


def teaching_loggia():
    x,y,w,d,h=PLANS[4]['teaching'];bottom=F+.10;t=.24;g='teaching_loggia'
    floor=B('TeachingLoggiaFloor',(x,y,F+.05),(w,d,.10),'stone','foundation','ground',g)
    back=wall('TeachingLoggiaBack',x,y+d/2-t/2,w,t,h,bottom=bottom,group=g)
    sides=[]
    for s in (-1,1):sides.append(wall('TeachingLoggiaSide'+str(s),x+s*(w/2-t/2),y,t,d-.48,h,bottom=bottom,group=g))
    front=tag(R.archwall(CURRENT+'_TeachingLoggiaOpenArch',x,y-d/2,y-d/2+t,bottom,w,h,2.50,2.22,.72,'brick',col('architecture'),segments=24),'walls','architecture',g)
    contact('TeachingLoggiaArchFoot',front,floor)
    p=R.vault(CURRENT+'_TeachingLoggiaVault',x,y-d/2,y+d/2,bottom+h,(w-.24)/2,.60,.12,'roof',col('roofs'),segments=28,along=3,stage='vaults')
    tag(p,'vaults','roofs',g);contact('TeachingVaultFront',p,front);contact('TeachingVaultBack',p,back)
    ASSEMBLIES[CURRENT]['teaching']=dict(x=x,y=y,w=w,d=d,h=h,bottom=bottom,floor=floor,front=front)


def service_room(name,x,y,w,d,h,side):
    bottom=F+.08;t=.20
    floor=B(name+'_Floor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',name)
    back=wall(name+'_Back',x+side*(w/2-t/2),y,t,d,h,bottom=bottom,group=name)
    for s in (-1,1):wall(name+'_Side'+str(s),x,y+s*(d/2-t/2),w-.40,t,h,bottom=bottom,group=name)
    front=x-side*w/2
    arch=tag(R.archwall(CURRENT+'_'+name+'_InwardDoorArch',y,front-.10,front+.10,bottom,d,h,1.02,1.74,.34,'brick',col('architecture'),segments=18,transform=lambda u,v,z:(v,u,z)),'walls','architecture',name)
    contact(name+'_ArchFoot',arch,floor)
    roof=B(name+'_Roof',(x,y,bottom+h+.085),(w,d,.17),'roof','vaults','roofs',name)
    contact(name+'_RoofBack',roof,back);contact(name+'_RoofFront',roof,arch)
    ASSEMBLIES[CURRENT][name]=dict(x=x,y=y,w=w,d=d,h=h,bottom=bottom,floor=floor)


def entrance():
    x,y,w,d=-.70,-4.68,4.80,1.25;bottom=F+.08;h=2.60;opening=1.62;pw=(w-opening)/2;g='entrance'
    floor=B('EntranceThreshold',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',g)
    # Small two-shoulder entrance, not a monumental portal or fourth royal iwan.
    for side in (-1,1):
        roomx=x+side*(opening/2+pw/2)
        back=wall('EntryShoulderBack'+str(side),roomx,y+d/2-.09,pw,.18,h,bottom=bottom,group=g)
        wall('EntryShoulderFront'+str(side),roomx,y-d/2+.09,pw,.18,h,bottom=bottom,group=g)
        for sx in (-1,1):wall('EntryShoulderEnd'+str(side)+'_'+str(sx),roomx+sx*(pw/2-.09),y,.18,d-.36,h,bottom=bottom,group=g)
        roof=B('EntryShoulderRoof'+str(side),(roomx,y,bottom+h+.075),(pw,d,.15),'roof','vaults','roofs',g);contact('EntryShoulderRoofFoot'+str(side),roof,back)
    header=B('EntryTimberHeader',(x,y-d/2+.12,bottom+2.37),(opening+.22,.24,.18),'timber','walls','architecture',g)
    header['end_bearing_overlap']=.11
    ASSEMBLIES[CURRENT]['entrance_header']=header


def architecture():
    for i,spec in enumerate(PLANS[4]['west_cells'][1:],1):cell(i,-1,spec)
    for i,spec in enumerate(PLANS[4]['east_cells'],4):cell(i,1,spec)
    teaching_loggia()
    # West library directly abuts the cell-range north end; there is no tiny
    # inaccessible slit concealed by roof overhangs.
    service_room('library',-5.10,4.45,2.40,2.20,2.70,-1)
    service_room('writing_store',3.70,3.55,2.00,4.00,2.66,1)
    entrance()
    print('ARCHITECTURE_DRAFT',CURRENT,'seven inward study cells, offset teaching loggia and service rooms; no dome')


def reading_desk(name,x,y,floor,z0,w=.90,d=.48):
    top=z0+.47
    table=B(name+'_Top',(x,y,top-.04),(w,d,.08),'timber','finish','props','scholarly_work')
    for sx in (-1,1):
        for sy in (-1,1):
            leg=B(name+'_Leg'+str(sx)+str(sy),(x+sx*(w/2-.10),y+sy*(d/2-.08),(z0+top-.08)/2),(.065,.065,top-.08-z0),'timber','finish','props','scholarly_work')
            contact(name+'_LegTop'+str(sx)+str(sy),leg,table,'top-bottom');contact(name+'_LegFoot'+str(sx)+str(sy),leg,floor)
    sheet=B(name+'_WritingBoard',(x,y,top+.013),(.47,.30,.026),'paper','finish','props','scholarly_work')
    contact(name+'_BoardOnDesk',sheet,table)


def props():
    a=ASSEMBLIES[CURRENT]['teaching']
    for i in range(2):reading_desk('TeachingDesk'+str(i),a['x']+(i-.5)*1.25,a['y']+.16,a['floor'],a['bottom'])
    for s in ASSEMBLIES[CURRENT]['cells']:
        reading_desk('CellDesk'+str(s['index']),s['x']+s['side']*.25,s['y']-.30,s['floor'],s['bottom'],.80,.43)
        mat=B('CellReedMat'+str(s['index']),(s['x']-s['side']*.30,s['y']+.23,s['bottom']+.006),(.64,.66,.012),'cloth','finish','props','study_cell_'+str(s['index']))
        contact('CellMatFloor'+str(s['index']),mat,s['floor'])
    lib=ASSEMBLIES[CURRENT]['library']
    # A low shelf has grounded cheeks, measured shelf planes and bundled books.
    x,y,z0=lib['x'],lib['y']+.55,lib['bottom']
    cheeks=[]
    for side in (-1,1):
        q=wall('LibraryShelfCheek'+str(side),x+side*.72,y,.10,.42,1.18,'timber',z0,'library_furniture')
        contact('LibraryShelfCheekFoot'+str(side),q,lib['floor']);cheeks.append(q)
    for i in range(3):
        zz=z0+.10+i*.45
        shelf=B('LibraryShelf'+str(i),(x,y,zz+.035),(1.44,.42,.07),'timber','finish','props','library_furniture')
        shelf['horizontal_end_bearing_overlap']=.05
        for j in range(3):
            q=B('BundledBooks'+str(i)+'_'+str(j),(x-.46+j*.46,y,zz+.105),(.35,.28,.07),'paper','finish','props','library_furniture')
            contact('BooksOnShelf'+str(i)+'_'+str(j),q,shelf)
    print('PROPS_DRAFT',CURRENT,'supported low desks, mats and modest library bundles; no invented writing')


def detail():
    a=ASSEMBLIES[CURRENT]['teaching']
    cloth=B('TeachingExteriorOwnerCloth',(a['x'],a['y']-a['d']/2-.012,a['bottom']+a['h']-.13),(1.10,.024,.16),'owner','finish','owner','teaching_loggia');cloth['mounting_parent']=a['front'].name
    # One restrained geometric brick band is an authored trim proposal. No
    # fabricated calligraphy, medical apparatus or Wonder-scale tile field.
    for j in range(5):B('TeachingBrickAccent'+str(j),(a['x']-.80+j*.40,a['y']-a['d']/2-.015,a['bottom']+3.20),(.20,.03,.08),'brick','finish','fine_detail','teaching_loggia')
    for s in ASSEMBLIES[CURRENT]['cells']:
        B('CellThresholdWear'+str(s['index']),(s['front']-s['side']*.10,s['y'],F+.004),(.22,.50,.008),'grime','finish','wear','court_ground')
    print('DETAIL_DRAFT',CURRENT,'selective scholarly frontage and cell threshold wear')


def show(key='A4',state='healthy',lod=0):
    R.configure(ROOT,'madrasa')
    if key not in NATIVE:raise ValueError('Unknown measured body')
    s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s;R.view(pos=(15,-20,17),center=(-.8,.1,2.),distance=22,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    if key is not None and key not in NATIVE:raise ValueError('Unknown measured body')
    prefix='PSB_madrasa_'+(key+'_' if key else '')
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
    spec=importlib.util.spec_from_file_location("madrasa_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
