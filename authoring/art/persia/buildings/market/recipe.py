"""Unbuilt original Persian Market draft; only existing A2/A3/A4 bodies.

Authored in projected stamp coordinates. Retained matrices are metadata, not an
implicit integration. No native motion/state wiring, save, reset or build on import.
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
R.configure(ROOT,'market')

F=.16
CURRENT='A2'
ANCHORS={}
CONTRACTS=[]
ASSEMBLIES={}
TEXTURE_INPUTS={k:str(ROOT/'textures'/(k+'.png')) for k in ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC={'resolution':[2048,2048],'original_pixels_required':True,'status':'paths only; parent generates original family atlas'}
ACTOR='ps_building_econ_market_control_sul'
VARIANT_EVIDENCE={'campaign':'existing_private_compiled_variant','default':'existing_private_compiled_variant',
 'cordoba':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
 'xp3':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant'}
STAMP_MATRIX=[[-2.220446049250313e-16,-1.0000000000000002,0.,0.],[1.,0.,0.,-4.1999998093],[0.,0.,1.,0.],[0.,0.,0.,1.]]
STAMP_INVERSE=[[0.,1.,0.,4.1999998093],[-1.,0.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
NATIVE={
 'A2':{'age':2,'triangles':22607,'budget_target':35260,'budget_cap':38208,
       'primary_resource_bounds':[[-4.421875,-2.955078125,-1.599609375],[2.796875,2.97265625,5.54296875]],
       'primary_stamp_bounds':[[-2.97265625,-8.6218748093,-1.599609375],[2.955078125,-1.4031248093,5.54296875]],
       'conditional_compound_bounds':[[-7.7481794357,-8.6218748093,-1.599609375],[8.2651555734,7.6802797577,5.54296875]]},
 'A3':{'age':3,'triangles':23206,'budget_target':34974,'budget_cap':35106,
       'primary_resource_bounds':[[-4.421875,-2.955078125,-1.599609375],[2.796875,2.97265625,5.54296875]],
       'primary_stamp_bounds':[[-2.97265625,-8.6218748093,-1.599609375],[2.955078125,-1.4031248093,5.54296875]],
       'conditional_compound_bounds':[[-8.2836378599,-8.6218748093,-1.599609375],[8.2651555734,7.6802797577,5.54296875]]},
 'A4':{'age':4,'triangles':38036,'budget_target':38461,'budget_cap':59563,
       'primary_resource_bounds':[[-4.421875,-2.970703125,-1.5517578125],[3.220703125,2.974609375,5.49609375]],
       'primary_stamp_bounds':[[-2.974609375,-8.6218748093,-1.5517578125],[2.970703125,-.9792966843,5.49609375]],
       'conditional_compound_bounds':[[-8.2836378599,-8.6218748093,-1.5517578125],[8.2651555734,7.6802797577,5.49609375]]},
}
for _k,_n in NATIVE.items():
    _a=str(_n['age']).zfill(2)
    _n['model']='art/civilizations/sultanate/structures/market/sul_market_control_age'+_a+'/sul_market_control_age'+_a+'.rgm'
    _n['source_uses']=[dict(actor=ACTOR,variant=v,variant_evidence_class=e,
      attachment='attachments/attachment_lists/civilizations/sultanate/buildings/econ_market_sul/tier'+str(_n['age'])+'_econ_market_control_sul',
      attachment_category='default',inventory_category='default',stamp='art/stamps/civ_sul/sul_market_age_'+_a+'.bin',stamp_instance_index=0)
      for v,e in VARIANT_EVIDENCE.items()]
REVIEW_BOUNDS=[[-4.20,-8.20,-.06],[4.20,2.45,4.60]]
PLANS={
 2:{'program':'three asymmetric brick/timber shops and a partial timber-covered trading lane',
    'shops':[(-1,-6.70),(-1,-4.55),(1,-3.45)],'roof':'flat','store':(-1.25,.35,2.80,3.25,2.25)},
 3:{'program':'four vaulted shops, a short open cross-lane and divided goods store',
    'shops':[(-1,-6.70),(-1,-4.55),(-1,-2.40),(1,-4.55)],'roof':'vault','store':(.10,.65,4.80,2.90,2.70)},
 4:{'program':'six regular brick shop bays, a higher open lane shade and two small service stores',
    'shops':[(s,y) for s in (-1,1) for y in (-6.70,-4.55,-2.40)],'roof':'parapet','store':(-1.35,.65,2.30,2.90,3.05)},
}
NATIVE_STATE_CONTRACT={
 'life_cycle_values':['construct_'+str(i).zfill(2) for i in range(0,100,5)]+['healthy']+['damage_'+str(i) for i in range(1,6)]+['ruins','preview','targeting'],
 'geometry_condition':'has_collapsed_ruins=false appears in component predicates; source aliases are not new lifecycle names',
 'primary_graph_properties':['preview','life_cycle_state','has_collapsed_damage1','has_collapsed_damage2','has_collapsed_damage3','has_collapsed_damage4','has_collapsed_damage5','has_collapsed_ruins','life_cycle_state_previous','burn_state','jin_debuff','debug_static_rig_name'],
 'physics_actions':'Native collapse/repair/static-rig actions exist in the original RGO; they are not newly authored animation clips.',
 'primary_skeleton_present':False,
 'inventory_reference':'research/persia_buildings/inventory/FAMILY_NATIVE_STATE_CONTRACTS.json',
 'status':'Inventory only. Additional native contexts, component mapping, effects and transitions require parent adapter review; no HP thresholds or playback claims.',
}
NATIVE_DEPENDENCIES={
 'layout':'art/civilizations/common/layouts/archetypes/layout_market/layout_market.rgm',
 'native_layout_skeleton':True,'layout_markers':11,
 'marker_frame':'Bone-local until native skeleton/pose evaluation; not world-space exits.',
 'policy':'Preserve native layout, physics/repair graphs, markers and existing legal prop/animal owners; no new moving rig.',
 'clearance_status':'Unqualified: conditional whole-compound rest bounds do not prove footprint, trader route, stock prop overlap or runtime swept clearance.',
}


def age():return NATIVE[CURRENT]['age']


def root(key=None,state='healthy',lod=0):
    R.configure(ROOT,'market');key=key or CURRENT
    if key not in NATIVE:raise ValueError('Only measured Market A2/A3/A4 are admitted')
    return R.collection(R.PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)


def col(role):
    parent=root();return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,parent)


def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role;ob['draft_uninspected']=True
    ob['authored_coordinate_space']='projected stamp-space; adapter pending'
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
    R.configure(ROOT,'market');s=R.setup_scene()
    s['historical_basis']='Original local trading lane and shop programme; Iranica bazaar studies, not a miniature named landmark.'
    R.view(pos=(14,-20,16),center=(0.,-3.,1.8),distance=20,solid=True)


def foundation(key='A2'):
    global CURRENT
    if key not in NATIVE:raise ValueError('Unknown measured body')
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body exists; explicit owned reset required')
    lo,hi=NATIVE[key]['primary_stamp_bounds'];xa,xb=lo[0]+.01,hi[0]-.01;ya,yb=-8.20,hi[1]-.01
    bed=B('MarketEarthBed',((xa+xb)/2,(ya+yb)/2,.05),(xb-xa,yb-ya,.22),'earth','foundation','ground','court_ground')
    lane=B('TradingLane',(0.,-5.15,F+.025),(1.80,6.10,.05),'stone','foundation','ground','public_lane')
    contact('LaneGround',lane,bed)
    ANCHORS[key]=dict(ground_top=F,native_body_key=key,native_model=NATIVE[key]['model'],source_uses=NATIVE[key]['source_uses'],existing_visual_age=age(),
      authored_space='projected stamp frame; inverse below targets projected resource coordinates, not raw native axes',
      projected_resource_to_stamp_matrix=STAMP_MATRIX,stamp_to_projected_resource_matrix=STAMP_INVERSE,
      native_primary_stamp_bounds=NATIVE[key]['primary_stamp_bounds'],conditional_compound_bounds=NATIVE[key]['conditional_compound_bounds'],
      authoring_bounds_proposal=[[xa,ya,-.06],[xb,yb,4.60]],entry=[0.,-8.05,F],lane_clear_width=1.80,
      dependencies=NATIVE_DEPENDENCIES,native_states=NATIVE_STATE_CONTRACT,
      native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],visual_inspection='Not performed; parent builds and reviews serially')
    ANCHORS[key]['source_primary_revision']={'ground_bounds':[[xa,ya,-.06],[xb,yb,F]],
      'storage':'Supported cabinets inside merchant bays replace the excluded north store compounds',
      'merchant_standing_rectangle_per_bay':'Counter rear to back wall: .72m; central unobstructed length .80m, storage kept at one end',
      'native_route_status':'Original markers/branches unchanged; source lane 1.80m wide, native route clearance deferred'}
    ASSEMBLIES[key]={'ground':bed,'lane':lane,'shops':[]}
    print('FOUNDATION_DRAFT',key,'linear market, conditional full-compound envelope')


def shop(index,side,y):
    x=side*1.95;w,d,h=1.50,1.95,(2.35 if age()==2 else 2.55 if age()==3 else 2.75)
    group='shop_'+str(index);bottom=F+.08;t=.18
    floor=B(group+'_Floor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',group)
    back=wall(group+'_Back',x+side*(w/2-t/2),y,t,d,h,'brick',bottom,group)
    sides=[]
    for s in (-1,1):sides.append(wall(group+'_Side'+str(s),x,y+s*(d/2-t/2),w-.36,t,h,bottom=bottom,group=group))
    front=x-side*w/2
    if age()==2:
        posts=[]
        for s in (-1,1):
            p=wall(group+'_FrontPost'+str(s),front+side*.08,y+s*(d/2-.12),.16,.16,h-.16,'timber',bottom,group)
            contact(group+'_PostFoot'+str(s),p,floor);posts.append(p)
        beam=B(group+'_FrontBeam',(front+side*.08,y,bottom+h-.08),(.20,d,.16),'timber','vaults','architecture',group)
        for i,p in enumerate(posts):contact(group+'_BeamBearing'+str(i),beam,p)
        front_support=beam
    else:
        front_support=tag(R.archwall(CURRENT+'_'+group+'_OpenArch',y,front-.10,front+.10,bottom,d,h,1.28,1.78,.45,
          'brick',col('architecture'),segments=16,transform=lambda u,v,z:(v,u,z)),'walls','architecture',group)
        contact(group+'_ArchFoot',front_support,floor)
    ASSEMBLIES[CURRENT]['shops'].append(dict(group=group,index=index,x=x,y=y,w=w,d=d,h=h,bottom=bottom,side=side,front=front,floor=floor,back=back,front_support=front_support))


def first_room():
    # Build one complete module first; parent inspects it before adding the rest.
    side,y=PLANS[age()]['shops'][0];shop(0,side,y)
    print('FIRST_ROOM_DRAFT',CURRENT,'one actual open merchant bay; inspection pending')


def shop_roof(s):
    group=s['group'];x,y,w,d,z=s['x'],s['y'],s['w'],s['d'],s['bottom']+s['h']
    if PLANS[age()]['roof']=='vault':
        p=R.vault(CURRENT+'_'+group+'_Vault',y,x-w/2,x+w/2,z,(d-.24)/2,.35,.12,'roof',col('roofs'),segments=18,along=3,transform=lambda u,v,zz:(v,u,zz),stage='vaults')
        tag(p,'vaults','roofs',group)
        contact(group+'_VaultFront',p,s['front_support']);contact(group+'_VaultBack',p,s['back'])
    else:
        roof=B(group+'_ClayRoof',(x,y,z+.085),(w+.04,d+.04,.17),'roof','vaults','roofs',group)
        contact(group+'_RoofFront',roof,s['front_support']);contact(group+'_RoofBack',roof,s['back'])
        if age()==4:
            # Low perimeter, not an ornamental palace parapet.
            B(group+'_BackCoping',(x+s['side']*(w/2-.06),y,z+.25),(.12,d,.16),'brick','vaults','roofs',group)
    # Shutters are folded against the front jambs, not pasted over an uncut wall.
    if age()>=3:
        for sign in (-1,1):
            q=B(group+'_OpenShutter'+str(sign),(s['front']+s['side']*.32,y+sign*.66,s['bottom']+.98),(.64,.045,1.96),'timber','finish','fittings',group)
            q['source_pose']='static open leaf turned into shop; no new animation clip or hinge playback'


def lane_shade():
    x,y,w,d=0.,-5.20,1.90,4.20
    top=F+(2.72 if age()==2 else 3.15 if age()==3 else 3.48)
    for side in (-1,1):
        posts=[]
        for j in range(3):
            yy=y-d/2+.12+j*(d-.24)/2
            p=wall('LanePost'+str(side)+'_'+str(j),side*(w/2-.08),yy,.14,.14,top-F,'timber',F,'lane_shade')
            contact('LanePostGround'+str(side)+'_'+str(j),p,ASSEMBLIES[CURRENT]['ground']);posts.append(p)
        beam=B('LaneBeam'+str(side),(side*(w/2-.08),y,top+.09),(.18,d,.18),'timber','vaults','architecture','lane_shade')
        for j,p in enumerate(posts):contact('LaneBeamBearing'+str(side)+'_'+str(j),beam,p)
    for j in range(7):
        yy=y-d/2+.10+j*(d-.20)/6
        joist=B('LaneRoofJoist'+str(j),(0.,yy,top+.225),(w,.10,.09),'timber','vaults','fittings','lane_shade')
        for side in (-1,1):contact('LaneJoistBearing'+str(side)+'_'+str(j),joist,bpy.data.objects[R.PREFIX+CURRENT+'_LaneBeam'+str(side)])
    roof=B('LaneShadeRoof',(0.,y,top+.325),(w+.08,d+.08,.11),'roof','vaults','roofs','lane_shade')
    contact('LaneRoofOnJoist',roof,bpy.data.objects[R.PREFIX+CURRENT+'_LaneRoofJoist0'])


def store(label,spec):
    x,y,w,d,h=spec;t=.20;bottom=F+.08
    floor=B(label+'_Floor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',label)
    back=wall(label+'_Back',x,y+d/2-t/2,w,t,h,bottom=bottom,group=label)
    for side in (-1,1):wall(label+'_Side'+str(side),x+side*(w/2-t/2),y,t,d-.40,h,bottom=bottom,group=label)
    opening=1.03;dh=1.98;pw=(w-opening)/2
    for side in (-1,1):wall(label+'_FrontPier'+str(side),x+side*(opening/2+pw/2),y-d/2+t/2,pw,t,h,bottom=bottom,group=label)
    wall(label+'_DoorHead',x,y-d/2+t/2,opening,t,h-dh,bottom=bottom+dh,group=label)
    door=B(label+'_RecessedDoor',(x,y-d/2+.15,bottom+.96),(.92,.045,1.92),'timber','finish','fittings',label)
    contact(label+'_DoorFoot',door,floor)
    roof=B(label+'_Roof',(x,y,bottom+h+.09),(w+.06,d+.06,.18),'roof','vaults','roofs',label)
    contact(label+'_RoofBearing',roof,back)


def architecture():
    for i,(side,y) in enumerate(PLANS[age()]['shops'][1:],1):shop(i,side,y)
    for s in ASSEMBLIES[CURRENT]['shops']:shop_roof(s)
    lane_shade()
    # All shops already fit the primary body. The former north stores did not;
    # useful goods storage now lives inside their actual merchant bays.
    print('ARCHITECTURE_DRAFT',CURRENT,'short linear shops and partial covered lane; no central dome/four arms')


def counter(s):
    x=s['front']+s['side']*.30;y=s['y'];z0=s['bottom'];top=z0+.82
    s['counter_x']=x
    table=B(s['group']+'_Counter',(x,y,top-.05),(.60,.80,.10),'timber','finish','props',s['group'])
    for sx in (-1,1):
        for sy in (-1,1):
            leg=B(s['group']+'_CounterLeg'+str(sx)+str(sy),(x+sx*.20,y+sy*.29,(z0+top-.10)/2),(.08,.08,top-.10-z0),'timber','finish','props',s['group'])
            contact(s['group']+'_CounterLegTop'+str(sx)+str(sy),leg,table,'top-bottom')
            contact(s['group']+'_CounterLegFoot'+str(sx)+str(sy),leg,s['floor'])
    return table,top


def controlled_storage(s):
    """A supported shop cabinet at one side, clear of the merchant stance."""
    x=s['x'];y=s['y']+.61;z=s['bottom'];group='GoodsStore'
    name=s['group']+'_StockCabinet';w,d=.90,.30
    base=B(name+'Base',(x,y,z+.04),(w,d,.08),'timber','finish','props',group)
    contact(name+'Floor',base,s['floor'])
    sides=[]
    for side in (-1,1):
        p=B(name+'Side'+str(side),(x+side*(w/2-.035),y,z+.66),(.07,d,1.16),'timber','finish','props',group)
        contact(name+'SideFoot'+str(side),p,base);sides.append(p)
    for j in range(3):
        shelf=B(name+'Shelf'+str(j),(x,y,z+.36+j*.36),(w-.14,d,.06),'timber','finish','props',group)
        shelf['mounting_parent']=sides[0].name;shelf['mounting_relation']='Shelf ends seat in the two cabinet side panels'
        # Intentional horizontal supported join, recorded against actual panels.
        contact(name+'ShelfLeft'+str(j),shelf,sides[0],'left-right')
        contact(name+'ShelfRight'+str(j),shelf,sides[1],'right-left')
        goods=B(name+'FoldedStock'+str(j),(x,y,z+.435+j*.36),(.50,.22,.09),'cloth','finish','props',group)
        contact(name+'StockOnShelf'+str(j),goods,shelf)
    top=B(name+'Top',(x,y,z+1.28),(w,d,.08),'timber','finish','props',group)
    for i,p in enumerate(sides):contact(name+'TopBearing'+str(i),top,p)


def props():
    for s in ASSEMBLIES[CURRENT]['shops']:
        table,top=counter(s);x,y=s['counter_x'],s['y'];kind=s['index']%3
        if kind==0:
            for j in range(3):
                q=B(s['group']+'_FoldedCloth'+str(j),(x,y-.25+j*.25,top+.045),(.50,.22,.09),'cloth','finish','props',s['group'])
                contact(s['group']+'_ClothOnCounter'+str(j),q,table)
        elif kind==1:
            for j in range(3):
                q=R.lathe(CURRENT+'_'+s['group']+'_Pot'+str(j),(x,y-.24+j*.24,top),[(.09,0),(.12,.12),(.10,.26),(.06,.31),(.045,.31),(.045,.25)],'pottery',col('props'),sides=12,role='props')
                tag(q,'finish','props',s['group']);contact(s['group']+'_PotOnCounter'+str(j),q,table)
        else:
            for j in range(5):
                q=R.lathe(CURRENT+'_'+s['group']+'_Weight'+str(j),(x+(j%2)*.20-.10,y+(j//2)*.24-.24,top),[(.07,0),(.07,.09),(.035,.12)],'metal',col('props'),sides=8,role='props')
                tag(q,'finish','props',s['group']);contact(s['group']+'_WeightOnCounter'+str(j),q,table)
        controlled_storage(s)
    # Goods remain grouped inside shop floors; no arbitrary obstruction across
    # the public lane, and no fabricated trade-cart/animal motion.
    print('PROPS_DRAFT',CURRENT,'distinct cloth, pottery and weights in supported merchant groups')


def detail():
    for s in ASSEMBLIES[CURRENT]['shops']:
        z=s['bottom']+s['h']-.08
        face_offset=.032 if age()==2 else .112
        q=B(s['group']+'_OwnerTextile',(s['front']-s['side']*face_offset,s['y'],z),(.024,.70,.13),'owner','finish','owner',s['group'])
        q['mounting_parent']=s['front_support'].name
        for j in range(2):B(s['group']+'_ThresholdWear'+str(j),(s['front']-s['side']*(.12+j*.14),s['y'],F+.004),(.16,.48,.008),'grime','finish','wear','court_ground')
    print('DETAIL_DRAFT',CURRENT,'restrained merchant identity, shutter wear and traffic')


def show(key='A2',state='healthy',lod=0):
    R.configure(ROOT,'market')
    if key not in NATIVE:raise ValueError('Unknown body')
    scene=bpy.data.scenes[R.SCENE]
    for c in scene.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=scene;R.view(pos=(14,-20,16),center=(0.,-3.,1.8),distance=20,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    if key is not None and key not in NATIVE:raise ValueError('Unknown body')
    prefix='PSB_market_'+(key+'_' if key else '')
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
    spec=importlib.util.spec_from_file_location("market_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
