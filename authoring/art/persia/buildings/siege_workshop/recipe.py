"""Unbuilt ordinary Persian Siege Workshop draft, exact existing A3/A4 bodies.

Projected stamp frame; no native integration, saved master, new clip or playback.
The functional design is timber fabrication/assembly, not the Factory landmark.
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
R.configure(ROOT,'siege_workshop')

F=.16
CURRENT='A3'
ANCHORS={}
CONTRACTS=[]
ASSEMBLIES={}
TEXTURE_INPUTS={k:str(ROOT/'textures'/(k+'.png')) for k in ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC={'resolution':[2048,2048],'original_pixels_required':True,'status':'paths only; parent generates original family atlas'}
ACTOR='ps_building_unit_siege_control_sul'
VARIANT_EVIDENCE={'campaign':'existing_private_compiled_variant','default':'existing_private_compiled_variant',
 'cordoba':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
 'xp3':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant'}
STAMP_MATRIX=[[-2.220446049250313e-16,-1.0000000000000002,0.,-.6000000238],[1.0000000000000002,-2.220446049250313e-16,0.,-.9499999881],[0.,0.,1.,0.],[0.,0.,0.,1.]]
STAMP_INVERSE=[[0.,1.,0.,.9499999881],[-1.,0.,0.,-.6000000238],[0.,0.,1.,0.],[0.,0.,0.,1.]]
NATIVE={
 'A3':{'age':3,'triangles':23257,'budget_target':31724,'budget_cap':112347,
 'model_sha256':'f360aeffb19a05c8af1b513d6af2002e5a45d9788a0511e524b4469377184150',
 'primary_resource_bounds':[[-4.30859375,-4.546875,-1.19921875],[3.54296875,4.46484375,5.09765625]],
 'primary_stamp_bounds':[[-5.0648437738,-5.2585937381,-1.19921875],[3.9468749762,2.5929687619,5.09765625]]},
 'A4':{'age':4,'triangles':35206,'budget_target':58130,'budget_cap':113798,
 'model_sha256':'39d119ff8657f79350e2dae37d402dfb2b542692a6bf8779bfb9cf201ef4776e',
 'primary_resource_bounds':[[-4.38671875,-4.546875,-1.19921875],[3.59375,4.5390625,5.84765625]],
 'primary_stamp_bounds':[[-5.1390625238,-5.3367187381,-1.19921875],[3.9468749762,2.6437500119,5.84765625]]},
}
for _key,_n in NATIVE.items():
    _a=str(_n['age']).zfill(2)
    _n['model']='art/civilizations/sultanate/structures/siege_workshop/sul_siege_workshop_control_age'+_a+'/sul_siege_workshop_control_age'+_a+'.rgm'
    _n['conditional_compound_bounds']=[[-6.8502757862,-7.0539476206,-1.19921875],[5.1936451844,5.3194412165,5.09765625 if _n['age']==3 else 5.84765625]]
    _n['source_uses']=[dict(actor=ACTOR,variant=v,variant_evidence_class=e,
      attachment='attachments/attachment_lists/civilizations/sultanate/buildings/unit_siege_sul/tier'+str(_n['age'])+'_unit_siege_control_sul',
      attachment_category='default',inventory_category='default',stamp='art/stamps/civ_sul/sul_siege_workshop_age_'+_a+'.bin',stamp_instance_index=0)
      for v,e in VARIANT_EVIDENCE.items()]
PLANS={
 3:{'program':'two unequal open fabrication bays and loose wheel/long-stock court',
    'main':(-2.65,.25,4.40,4.40,3.30,3.40),'side':(1.40,.55,3.70,3.60,2.45,2.35),'roof_rise':.48,'height_cap':4.85},
 4:{'program':'unified braced assembly hall, internal guarded tool store and covered long-stock side bay',
    'main':(-.80,.25,8.10,4.40,3.90,3.50),'side':None,'roof_rise':.80,'height_cap':5.55},
}
# Source-only crop to current exact-joined, non-debris reference coordinates.
# Healthy native prop-state activation is still unqualified; this is not an
# enlarged footprint or permission to borrow destruction debris space.
SOURCE_EAST=3.9468749762-.05


def source_front():
    return NATIVE[CURRENT]['primary_stamp_bounds'][0][1]+.05


def source_bounds():
    lo,hi=NATIVE[CURRENT]['primary_stamp_bounds']
    return [[lo[0]+.05,source_front(),-.06],[SOURCE_EAST,hi[1]-.05,PLANS[age()]['height_cap']]]
NATIVE_STATE_CONTRACT={
 'life_cycle_values':['construct_'+str(i).zfill(2) for i in range(0,100,5)]+['healthy']+['damage_'+str(i) for i in range(1,6)]+['ruins','preview','targeting'],
 'conditional_properties':['has_collapsed_damage1','has_collapsed_damage2','has_collapsed_damage3','has_collapsed_damage4','has_collapsed_damage5','has_collapsed_ruins','life_cycle_state_previous','burn_state','jin_debuff','debug_static_rig_name'],
 'native_primary_skeleton_present':False,
 'actions':'Original RGO physics collapse, repair and static-rig actions remain owners; not newly authored clips.',
 'reference':'research/persia_buildings/inventory/FAMILY_NATIVE_STATE_CONTRACTS.json',
 'status':'Inventory only; component visibility/physics, repair transitions and additional contexts require parent mapping. No HP thresholds or playback claim.',
}
NATIVE_DEPENDENCIES={
 'layout':'art/civilizations/common/layouts/archetypes/layout_siegeworkshop/layout_siegeworkshop.rgm',
 'layout_skeleton_present':True,'layout_marker_count':9,
 'banner':'art/civilizations/common/banners/banner_siege/banner_siege.rgm',
 'other_owners':['wood_pieces','wall_stone_high_post','wall_stone_high_segment','wall_stone_high_segment_half'],
 'marker_frame':'Bone-local until native skeleton/pose evaluation; not world-space sockets.',
 'motion_policy':'No new rig/clip. Static original lifting tackle is source art, not a replacement for an inventoried moving native mechanism.',
 'clearance_status':'Unqualified: conditional compound rest envelope is not native footprint, siege-unit exit or moving swept-volume proof.',
}


def age():return NATIVE[CURRENT]['age']


def root(key=None,state='healthy',lod=0):
    R.configure(ROOT,'siege_workshop');key=key or CURRENT
    if key not in NATIVE:raise ValueError('Only existing Siege Workshop A3/A4 are admitted')
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
    R.configure(ROOT,'siege_workshop');s=R.setup_scene()
    s['historical_basis']='Original Persian-material timber fabrication yard; no exact medieval workshop plan or cannon-production chronology is asserted.'
    R.view(pos=(15,-19,15),center=(-.4,-.7,2.),distance=20,solid=True)


def foundation(key='A3'):
    global CURRENT
    if key not in NATIVE:raise ValueError('Unknown measured body')
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body exists; explicit owned reset required')
    bounds=source_bounds()
    west,front=bounds[0][:2];east,north=bounds[1][:2]
    ground=B('AssemblyEarthBed',((west+east)/2,(front+north)/2,.05),
             (east-west,north-front,.22),'earth','foundation','ground','court_ground')
    ANCHORS[key]=dict(ground_top=F,native_body_key=key,native_model=NATIVE[key]['model'],native_model_sha256=NATIVE[key]['model_sha256'],existing_visual_age=age(),source_uses=NATIVE[key]['source_uses'],
      authoring_bounds_proposal=bounds,native_primary_stamp_bounds=NATIVE[key]['primary_stamp_bounds'],conditional_compound_bounds=NATIVE[key]['conditional_compound_bounds'],
      authored_space='projected stamp-space; source bed and all authored geometry bounded by verified primary body',
      projected_resource_to_stamp_matrix=STAMP_MATRIX,stamp_to_projected_resource_matrix=STAMP_INVERSE,
      vehicle_route_proposal={'x_interval':[-4.15,-1.15] if age()==3 else [-2.40,.80],'y_interval':[-6.25,.85],
                              'status':'Source negative space only; native moving-unit/marker clearance unqualified'},
      dependencies=NATIVE_DEPENDENCIES,native_states=NATIVE_STATE_CONTRACT,
      native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],visual_inspection='Not performed; parent serial build required')
    ANCHORS[key]['source_boundary_revision']={
      'scope':'Original visual bed and isolated loose-part/stock-shade revisions; native footprint, transforms and reserved assembly lane unchanged',
      'original_earth_bounds':[[-5.80,-6.50],[4.80,4.80]],
      'revised_earth_bounds':[[west,front],[east,north]],
      'loose_wheel_original_center':[-5.20,-3.50,F+.50],
      'loose_wheel_revised_center':[2.75,-2.90,F+.50],
      'wheel_source_route_clearance_x':3.40 if age()==3 else 1.45,
      'route_clearance_limit':'Axis-aligned original source-art gap only; not a posed moving-unit/native clearance qualification',
      'qualification':'Verified primary-body envelope; no prop healthy selector inference or footprint change'}
    ASSEMBLIES[key]={'ground':ground,'bays':{}}
    print('FOUNDATION_DRAFT',key,'open source assembly route, no native footprint claim')


def bay_walls(label,spec):
    x,y,w,d,h,opening=spec;bottom=F+.12;t=.24
    floor=B(label+'_Floor',(x,y,F+.06),(w,d,.12),'earth','foundation','ground',label)
    back=wall(label+'_Back',x,y+d/2-t/2,w,t,h,bottom=bottom,group=label)
    sides=[]
    for side in (-1,1):sides.append(wall(label+'_Side'+str(side),x+side*(w/2-t/2),y,t,d-.48,h,bottom=bottom,group=label))
    pier=(w-opening)/2;door_h=h-.32
    for side in (-1,1):wall(label+'_FrontPier'+str(side),x+side*(opening/2+pier/2),y-d/2+t/2,pier,t,h,bottom=bottom,group=label)
    lintel=B(label+'_WideTimberLintel',(x,y-d/2+t/2,bottom+h-.16),(opening+.24,.28,.32),'timber','walls','architecture',label)
    # Jambs are integral to the masonry piers; lintel bearings overlap them by
    # .12 each. Parent must inspect actual end bearing, not just AABB height.
    lintel['end_bearing_overlap']=.12
    ASSEMBLIES[CURRENT]['bays'][label]=dict(spec=spec,bottom=bottom,top=bottom+h,floor=floor,back=back,sides=sides,lintel=lintel)
    ANCHORS[CURRENT].setdefault('assembly_openings',{})[label]=dict(center=[x,y-d/2,bottom],clear_width=opening,clear_height=door_h)


def first_room():
    bay_walls('main_assembly',PLANS[age()]['main'])
    print('FIRST_ROOM_DRAFT',CURRENT,'genuine wide assembly mouth and masonry/timber bearings')


def gabled_roof(label,a,rise):
    x,y,w,d,h,_=a['spec'];z=a['top'];thick=.16
    # Each roof half is one closed prism with real thickness. No paper cards.
    for side in (-1,1):
        xe=x+side*w/2;xr=x
        verts=[(xe,yy,z+zz) for zz in (0,thick) for yy in (y-d/2,y+d/2)]
        verts +=[(xr,yy,z+rise+zz) for zz in (0,thick) for yy in (y-d/2,y+d/2)]
        faces=[(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6),(0,4,6,2),(1,3,7,5)]
        roof=tag(R.mesh(CURRENT+'_'+label+'_RoofHalf'+str(side),verts,faces,'roof',col('roofs'),'vaults','roofs'),'vaults','roofs',label)
        contact(label+'_RoofEave'+str(side),roof,a['sides'][0 if side==-1 else 1])
    # Full front/rear gable spandrels carry end roofing and close false gaps.
    for end in (-1,1):
        yy=y+end*(d/2-.12)
        p=R.extrude_xz(CURRENT+'_'+label+'_Gable'+str(end),[(x-w/2,z),(x+w/2,z),(x,z+rise)],yy-.12,yy+.12,'brick',col('architecture'),'vaults',role='architecture')
        tag(p,'vaults','architecture',label)
        contact(label+'_GableBearing'+str(end),p,a['back'] if end==1 else a['lintel'])
    # Explicit tie/king-post system reads as timber construction. No unheld
    # rig or moving truss is created. Its direct interfaces are recorded.
    for j in range(3):
        yy=y-d/2+.35+j*(d-.70)/2
        tie=B(label+'_TieBeam'+str(j),(x,yy,z-.10),(w,.18,.20),'timber','vaults','architecture',label)
        king=wall(label+'_KingPost'+str(j),x,yy,.16,.16,rise,'timber',z,label)
        contact(label+'_KingOnTie'+str(j),king,tie)
        for side in (-1,1):
            q=R.beam(CURRENT+'_'+label+'_RoofBrace'+str(j)+'_'+str(side),(x+side*(w/2-.15),yy,z-.02),(x,yy,z+rise-.12),.13,'timber',col('fittings'),'vaults','fittings')
            tag(q,'vaults','fittings',label)


def tool_store():
    if age()<4:return
    x,y,w,d,h=-3.72,1.20,1.68,2.05,2.32;bottom=F+.12;g='tool_store'
    floor=ASSEMBLIES[CURRENT]['bays']['main_assembly']['floor']
    back=wall('ToolStoreBack',x,y+d/2-.10,w,.20,h,bottom=bottom,group=g)
    for side in (-1,1):wall('ToolStoreSide'+str(side),x+side*(w/2-.10),y,.20,d-.40,h,bottom=bottom,group=g)
    opening=.88;pw=(w-opening)/2
    for side in (-1,1):wall('ToolStoreFrontPier'+str(side),x+side*(opening/2+pw/2),y-d/2+.10,pw,.20,h,bottom=bottom,group=g)
    wall('ToolStoreDoorHead',x,y-d/2+.10,opening,.20,h-1.90,bottom=bottom+1.90,group=g)
    q=B('ToolStoreRecessedDoor',(x,y-d/2+.15,bottom+.91),(.78,.04,1.82),'timber','finish','fittings',g);contact('ToolStoreDoorFoot',q,floor)
    roof=B('ToolStoreRoof',(x,y,bottom+h+.08),(w,d,.16),'roof','vaults','roofs',g);contact('ToolStoreRoofBearing',roof,back)


def long_stock_shelter():
    if age()<4:return
    # Keep the west roof edge and west posts exactly where authored; shorten
    # only the east roof/frame by 254.0078735mm. Main vehicle lane is unchanged.
    roof_west=3.425
    x,y,w,d=(roof_west+SOURCE_EAST)/2,-.45,SOURCE_EAST-roof_west-.06,4.50
    top=F+2.42;posts=[]
    for sx in (-1,1):
        for sy in (-1,1):
            p=wall('LongStockPost'+str(sx)+str(sy),x+sx*(w/2-.08),y+sy*(d/2-.10),.14,.14,top-F,'timber',F,'long_stock')
            contact('LongStockFoot'+str(sx)+str(sy),p,ASSEMBLIES[CURRENT]['ground']);posts.append(p)
    roof=B('LongStockRoof',(x,y,top+.09),(w+.06,d+.06,.18),'roof','vaults','roofs','long_stock')
    for j,p in enumerate(posts):contact('LongStockRoofPost'+str(j),roof,p)
    # Original timber-stock positions remain covered by the narrowed roof.
    for j in range(4):B('LongStockTimber'+str(j),(3.55+(j%2)*.20,y,F+.065+(j//2)*.13),(.16,3.65,.13),'timber','finish','props','long_stock')
    ANCHORS[CURRENT]['source_boundary_revision']['long_stock']={
      'original_roof_x_interval':[3.425,4.635],
      'revised_roof_x_interval':[roof_west,SOURCE_EAST],
      'west_post_center_x_unchanged':3.535,'east_trim_metres':4.635-SOURCE_EAST,
      'stock_centers_unchanged':False,'stock_column_centers':[3.55,3.75],
      'qualification':'Primary-body bounded authored stock recess; no conditional prop union',
      'support_contracts':'Rebuilt from actual revised post/roof meshes by existing contact() calls'}


def architecture():
    if PLANS[age()]['side']:bay_walls('parts_bay',PLANS[age()]['side'])
    for label,a in ASSEMBLIES[CURRENT]['bays'].items():gabled_roof(label,a,PLANS[age()]['roof_rise'] if label=='main_assembly' else .30)
    tool_store();long_stock_shelter()
    print('ARCHITECTURE_DRAFT',CURRENT,'ordinary fabrication programme; no furnace/casting/gun landmark copy')


def bench(name,x,y,w=1.50,d=.70):
    floor=ASSEMBLIES[CURRENT]['bays']['main_assembly']['floor'];z0=F+.12;top=z0+.78
    p=B(name+'Top',(x,y,top-.06),(w,d,.12),'timber','finish','props','fabrication')
    for sx in (-1,1):
        for sy in (-1,1):
            q=B(name+'Leg'+str(sx)+str(sy),(x+sx*(w/2-.13),y+sy*(d/2-.12),(z0+top-.12)/2),(.10,.10,top-.12-z0),'timber','finish','props','fabrication')
            contact(name+'LegTop'+str(sx)+str(sy),q,p,'top-bottom');contact(name+'LegFoot'+str(sx)+str(sy),q,floor)
    return p,top


def loose_wheel():
    # Complete wheel, hub, spokes and both chocks share this one translated
    # source origin. Radius/pose/ground contact remain unchanged.
    x,y,z=2.75,-2.90,F+.50;n=16;ro,ri,thick=.50,.40,.09;verts=[]
    for yy in (y-thick/2,y+thick/2):
        for r in (ro,ri):
            for i in range(n):
                a=2*math.pi*i/n;verts.append((x+r*math.cos(a),yy,z+r*math.sin(a)))
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    rim=tag(R.mesh(CURRENT+'_LooseWheelRim',verts,faces,'timber',col('props'),'finish','props'),'finish','props','loose_parts')
    contact('LooseWheelGround',rim,ASSEMBLIES[CURRENT]['ground'])
    for side in (-1,1):
        chock=B('LooseWheelChock'+str(side),(x,y+side*.115,F+.06),(.30,.14,.12),'timber','finish','props','loose_parts')
        contact('WheelChockGround'+str(side),chock,ASSEMBLIES[CURRENT]['ground'])
    B('WheelHub',(x,y,z),(.18,.22,.18),'timber','finish','props','loose_parts')
    for i in range(8):
        a=2*math.pi*i/8
        q=R.beam(CURRENT+'_WheelSpoke'+str(i),(x+.07*math.cos(a),y,z+.07*math.sin(a)),(x+.43*math.cos(a),y,z+.43*math.sin(a)),.065,'timber',col('props'),'finish','props')
        tag(q,'finish','props','loose_parts')
    ANCHORS[CURRENT]['loose_wheel_source_relocation']={'center':[x,y,z],
        'basis':'Whole wheel/hub/spokes/chocks moved to east forecourt inside verified primary, clear of central assembly mouth and yard-plank ends',
        'native_route_clearance':'Not asserted; native actor/pose/route gates remain deferred'}


def static_tackle():
    if age()<4:return
    floor=ASSEMBLIES[CURRENT]['bays']['main_assembly']['floor'];z0=F+.12;top=3.45;posts=[]
    for j,x in enumerate((-2.50,.90)):
        p=wall('TacklePost'+str(j),x,1.10,.18,.24,top-z0,'timber',z0,'tackle')
        contact('TacklePostFoot'+str(j),p,floor);posts.append(p)
    beam=B('TackleCrossBeam',(-.80,1.10,top+.09),(3.58,.26,.18),'timber','finish','architecture','tackle')
    for j,p in enumerate(posts):contact('TackleBeamBearing'+str(j),beam,p)
    rope=R.lathe(CURRENT+'_TackleStaticRope',(-.80,1.10,2.75),[(.024,0),(.024,.70)],'cloth',col('props'),sides=8,role='props')
    tag(rope,'finish','props','tackle');contact('StaticRopeTop',rope,beam,'top-bottom')
    block=B('StaticTackleBlock',(-.80,1.10,2.67),(.18,.14,.16),'timber','finish','props','tackle')
    contact('TackleBlockToRope',block,rope,'top-bottom')
    block['motion_status']='Original static source pose; no clip, motor, native socket or lifting playback.'


def props():
    x,y=(-3.72,1.60) if age()==3 else (1.95,.40)
    p,top=bench('CarpenterBench',x,y)
    ASSEMBLIES[CURRENT]['bench_position']=[x,y]
    for j in range(3):
        q=B('Workpiece'+str(j),(x-.25+j*.25,y,top+.035),(.18,.48,.07),'timber','finish','props','fabrication');contact('WorkpieceOnBench'+str(j),q,p)
    loose_wheel();static_tackle()
    # Loose material stays to the court edge. No complete unselectable siege
    # unit or weapon is placed in the proposed assembly exit route.
    for j in range(4):B('YardPlank'+str(j),(2.70+(j%2)*.24,-4.30,F+.045+(j//2)*.09),(.20,1.65,.09),'timber','finish','props','loose_parts')
    print('PROPS_DRAFT',CURRENT,'supported fabrication bench, loose wheel/stock and static tackle')


def detail():
    a=ASSEMBLIES[CURRENT]['bays']['main_assembly'];x,y,w,d,h,_=a['spec']
    q=B('AssemblyOwnerCloth',(x,y-d/2-.032,a['top']-.16),(1.20,.024,.18),'owner','finish','owner','main_assembly');q['mounting_parent']=a['lintel'].name
    for j in range(5):B('ThresholdBeddedStone'+str(j),(x-1.20+j*.60,y-d/2-.20,F+.03),(.53,.34,.06),'stone','foundation','ground','assembly_approach')
    bx,by=ASSEMBLIES[CURRENT]['bench_position']
    for j in range(3):B('BenchTrafficWear'+str(j),(bx+.20,by-.62+j*.12,F+.124),(.32,.25,.008),'grime','finish','wear','main_assembly')
    print('DETAIL_DRAFT',CURRENT,'plain owner cloth and practical threshold/bench wear')


def show(key='A3',state='healthy',lod=0):
    R.configure(ROOT,'siege_workshop')
    if key not in NATIVE:raise ValueError('Unknown measured body')
    s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s;R.view(pos=(15,-19,15),center=(-.4,-.7,2.),distance=20,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    if key is not None and key not in NATIVE:raise ValueError('Unknown measured body')
    prefix='PSB_siege_workshop_'+(key+'_' if key else '')
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
    spec=importlib.util.spec_from_file_location("siege_workshop_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
