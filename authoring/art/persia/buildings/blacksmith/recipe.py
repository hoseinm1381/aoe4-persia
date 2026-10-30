"""DRAFT original Persian blacksmith source; no Blender run or native changes.

Only measured A2/A3/A4 bodies are admitted. Architecture is authored in the
projected healthy stamp frame; native body matrices and bellows frame are
recorded, never applied here. Import does not build, reset, save or cook.
"""
from pathlib import Path
import sys
import json
import math
import bpy

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / '_shared'
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
import source_runner as R
R.configure(ROOT, 'blacksmith')

F = .16
CURRENT = 'A2'
ANCHORS = {}
CONTRACTS = []
ASSEMBLIES = {}
TEXTURE_INPUTS = {k: str(ROOT / 'textures' / (k + '.png')) for k in
                  ('albedo', 'normal', 'roughness', 'metalness', 'owner_mask')}
TEXTURE_SPEC = {'resolution': [2048, 2048], 'original_pixels_required': True,
                'status': 'paths only; parent generates original family atlas'}
ACTOR = 'ps_building_tech_unit_infantry_control_sul'
VARIANT_EVIDENCE = {
    'campaign': 'existing_private_compiled_variant',
    'default': 'existing_private_compiled_variant',
    'cordoba': 'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
    'xp3': 'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
}
MODEL_STEM = 'art/civilizations/sultanate/structures/blacksmith/'
NATIVE = {
    'A2': {'age': 2, 'triangles': 15231, 'stamp_translation': [-1.7000000477, -1.75, 0.],
           'primary_stamp_bounds': [[-6.2976562977, -7.4453125, -1.599609375], [2.6984374523, 2.74609375, 6.640625]],
           'possible_compound_bounds': [[-7.9835351764, -7.8833437292, -1.599609375], [6.5847394551, 5.9872415972, 6.640625]],
           'bellows_instance_index': 3},
    'A3': {'age': 3, 'triangles': 15465, 'stamp_translation': [-1.7050629854, -1.3669509888, 0.],
           'primary_stamp_bounds': [[-6.3027192354, -7.0622634888, -1.599609375], [2.6933745146, 3.1291427612, 6.640625]],
           'possible_compound_bounds': [[-7.9835351764, -7.8833437292, -1.599609375], [7.1413099729, 5.7874169693, 6.640625]],
           'bellows_instance_index': 33},
    'A4': {'age': 4, 'triangles': 22172, 'stamp_translation': [-1.7050629854, -1.3669509888, 0.],
           'primary_stamp_bounds': [[-6.1855317354, -6.6911697388, -1.599609375], [2.7168120146, 3.2971115112, 6.671875]],
           'possible_compound_bounds': [[-7.9835351764, -7.8833437292, -1.599609375], [7.1413099729, 5.7874169693, 6.671875]],
           'bellows_instance_index': 37},
}
for _key, _row in NATIVE.items():
    _n = str(_row['age']).zfill(2)
    _row['model'] = MODEL_STEM + 'sul_blacksmith_control_age' + _n + '/sul_blacksmith_control_age' + _n + '.rgm'
    _row['source_uses'] = [dict(actor=ACTOR, variant=v, variant_evidence_class=e,
                              attachment='attachments/attachment_lists/civilizations/sultanate/buildings/tech_unit_melee_sul/tier' + str(_row['age']) + '_tech_unit_melee_control_sul',
                              attachment_category='default', inventory_category='default',
                              stamp='art/stamps/civ_sul/sul_blacksmith_age_' + _n + '.bin', stamp_instance_index=0)
                           for v, e in VARIANT_EVIDENCE.items()]

REVIEW_BOUNDS = [[-6.05, -6.20, -.06], [4.85, 4.65, 5.40]]
PLANS = {
    2: {'program': 'brick fire chamber, deep open timber handling porch, low fuel bay',
        'porch': (-1.55, -2.15, 7.50, 3.45, 2.62), 'flue_height': 1.35,
        'store': (-5.20, 1.55, 1.45, 3.40, 2.10)},
    3: {'program': 'divided hot/cold work, enclosed west tool store and shallow north handling roof',
        'porch': (-1.55, -2.15, 7.50, 3.45, 2.78), 'flue_height': 1.70,
        'store': (-5.10, 1.65, 1.65, 3.60, 2.65)},
    4: {'program': 'larger fitted tool store, second cool finishing bay, raised supported smoke flue',
        'porch': (-1.55, -2.15, 7.50, 3.45, 2.90), 'flue_height': 2.05,
        'store': (-5.00, 1.65, 1.85, 3.60, 3.25)},
}
BELLOWS = {
    'model': 'art/civilizations/common/props/bellows/bellows.rgm',
    'stamp_matrix': [[-.5297451045, -.8447244385, -.0762282577, 1.5762100220],
                     [.8481446287, -.5280770416, -.0422531301, 1.9819070101],
                     [-.0045621412, -.0870359762, .9961947228, 0.], [0., 0., 0., 1.]],
    'possible_rest_bounds': [[-.3181049645, .6392442321, -.1254559184], [2.7892333510, 3.1139238299, 2.3499984206]],
    'reserved_review_box': [[-.45, .50, -.15], [2.92, 3.25, 2.50]],
    'frame_limit': 'Measured stamp rest frame, not a nozzle socket or animated swept volume. Native rig/graph and playback must be inventoried by parent; no replacement bellows is authored.',
}
NATIVE_DEPENDENCIES = {
    'layout': 'art/civilizations/common/layouts/archetypes/layout_blacksmith/layout_blacksmith.rgm',
    'bellows': BELLOWS,
    'other_existing_props': ['blacksmith_anvil_stump', 'wood_piles_stacked', 'wood_pile_heap', 'water_bucket', 'cart_2_wheeled'],
    'policy': 'Keep existing native owners, graphs, transforms and markers. Proposed custom static tools are review sources, not permission to duplicate/replace native attachments.',
    'clearance_status': 'Unqualified: source envelope is conditional compound evidence, not footprint, unit-exit, nozzle contact or motion clearance.',
}


def age():
    return NATIVE[CURRENT]['age']


def root(key=None, state='healthy', lod=0):
    R.configure(ROOT, 'blacksmith')
    key = key or CURRENT
    if key not in NATIVE:
        raise ValueError('Only native Blacksmith A2/A3/A4 are admitted')
    return R.collection(R.PREFIX + key + '_' + state + '_LOD' + str(lod), R.setup_scene().collection)


def col(role):
    parent = root()
    return R.collection(R.PREFIX + CURRENT + '_healthy_' + role, parent)


def tag(ob, stage, role, group=''):
    ob['body_key'] = CURRENT
    ob['construction_stage'] = stage
    ob['role'] = role
    ob['draft_uninspected'] = True
    ob['authored_coordinate_space'] = 'projected stamp-space; adapter pending'
    if group:
        ob['structural_group'] = group
    return ob


def B(name, center, size, surface='plaster', stage='walls', role='architecture', group=''):
    if any(v <= 0 for v in size):
        raise ValueError('Nonpositive part: ' + name)
    return tag(R.block(CURRENT + '_' + name, center, size, surface, col(role), stage, role), stage, role, group)


def wall(name, x, y, w, d, h, surface='plaster', bottom=F, group=''):
    return B(name, (x, y, bottom+h/2), (w, d, h), surface, 'walls', 'architecture', group)


def contact(name, child, parent, axis='bottom-top', target=0., tolerance=.003):
    CONTRACTS.append(dict(body=CURRENT, name=name, a=child.name, b=parent.name,
                          axis=axis, target=target, tolerance=tolerance))


def setup():
    R.configure(ROOT, 'blacksmith')
    scene = R.setup_scene()
    scene['historical_basis'] = 'Original hot-work court informed by Iranica Ahan and Met Nishapur metalwork; see README.'
    R.view(pos=(14, -18, 14), center=(-1., -.3, 2.), distance=18, solid=True)


def foundation(key='A2'):
    global CURRENT
    if key not in NATIVE:
        raise ValueError('Unknown measured native key')
    CURRENT = key
    setup()
    if root().all_objects:
        raise ValueError('Owned body exists; explicit owned reset required')
    lo,hi=NATIVE[key]['primary_stamp_bounds'];xa,xb=lo[0]+.02,hi[0]-.02;ya,yb=-6.20,hi[1]-.02
    bed = B('EarthWorkCourt', ((xa+xb)/2,(ya+yb)/2,.05), (xb-xa,yb-ya,.22), 'earth', 'foundation', 'ground', 'court_ground')
    for i in range(5):
        p = B('EntryPaver' + str(i), (-.65, -5.70+i*.43, F+.025), (.85, .36, .05), 'stone', 'foundation', 'ground', 'entry_path')
        contact('PaverGround' + str(i), p, bed)
    n = NATIVE[key]
    tx, ty, tz = n['stamp_translation']
    ANCHORS[key] = dict(ground_top=F, native_body_key=key, native_model=n['model'],
                        existing_visual_age=age(), source_uses=n['source_uses'],
                        authoring_bounds_proposal=[[xa,ya,-.06],[xb,yb,5.40]],
                        native_primary_stamp_bounds=n['primary_stamp_bounds'],
                        conditional_compound_bounds=n['possible_compound_bounds'],
                        authored_space='projected stamp-space, not raw native/model-root coordinates',
                        projected_resource_to_stamp_matrix=[[1,0,0,tx],[0,1,0,ty],[0,0,1,tz],[0,0,0,1]],
                        stamp_to_projected_resource_matrix=[[1,0,0,-tx],[0,1,0,-ty],[0,0,1,-tz],[0,0,0,1]],
                        entry=[-.65,-6.0,F], forge_front=[-1.60,.80,F+.65],
                        dependencies=NATIVE_DEPENDENCIES,
                        native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],
                        visual_inspection='Not performed; parent must build and inspect serially')
    ANCHORS[key]['source_primary_revision']={'basis':'Exact native primary body, no conditional prop envelope override',
        'ground_bounds':[[xa,ya,-.06],[xb,yb,F]],
        'store_front_retained':-.15,'finishing_bay_relocated_to_south_forecourt':age()==4,
        'native_markers_and_stamp_frames':'Retained; native actor/route/playback gates remain deferred'}
    ASSEMBLIES[key] = {'ground': bed}
    print('FOUNDATION_DRAFT', key, 'conditional compound envelope; no footprint claim')


def first_room():
    """Heavy fire chamber with actual mouth and an open smoke path above it."""
    x, y, w, d = -1.60, 1.90, 1.80, 2.20
    if age()==2:
        # Keep the working mouth/front fixed; shorten only the rear fire chamber.
        front=.80;rear=NATIVE[CURRENT]['primary_stamp_bounds'][1][1]-.05
        d=rear-front;y=(front+rear)/2
    bottom = F+.65
    height = 1.85
    base = B('ForgeHearthBase', (x,y,F+.325), (w,d,.65), 'brick', 'foundation', 'architecture', 'forge')
    contact('ForgeBaseGround', base, ASSEMBLIES[CURRENT]['ground'])
    walls = []
    for side in (-1, 1):
        q = wall('ForgeSide' + str(side), x+side*(w/2-.13), y, .26, d, height, 'brick', bottom, 'forge')
        contact('ForgeSideFoot' + str(side), q, base)
        walls.append(q)
    back = wall('ForgeBack', x, y+d/2-.13, w-.52, .26, height, 'brick', bottom, 'forge')
    contact('ForgeBackFoot', back, base)
    front = tag(R.archwall(CURRENT+'_ForgeMouthArch', x, y-d/2, y-d/2+.26,
                           bottom, w-.52, height, .98, .78, .46,
                           'brick', col('architecture'), segments=16), 'walls', 'architecture', 'forge')
    contact('ForgeMouthFoot', front, base)
    ASSEMBLIES[CURRENT]['forge'] = dict(x=x,y=y,w=w,d=d,top=bottom+height,base=base,walls=walls+[back,front])
    print('FIRST_ROOM_DRAFT', CURRENT, 'open fire mouth, masonry bearings; no effects')


def forge_hood():
    a = ASSEMBLIES[CURRENT]['forge']
    x,y,w,d,z = a['x'],a['y'],a['w'],a['d'],a['top']
    # Four solid roof panels leave a continuous square smoke passage. The flue
    # itself comprises four closed wall meshes, rather than a capped solid box.
    cx,cy,hole,t = x,y+.40,.62,.15
    x0,x1,y0,y1 = x-w/2,x+w/2,y-d/2,y+d/2
    pieces = [('West',x0,cx-hole/2,y0,y1),('East',cx+hole/2,x1,y0,y1),
              ('Front',cx-hole/2,cx+hole/2,y0,cy-hole/2),('Back',cx-hole/2,cx+hole/2,cy+hole/2,y1)]
    roof = {}
    for label,xa,xb,ya,yb in pieces:
        roof[label] = B('HoodRing'+label, ((xa+xb)/2,(ya+yb)/2,z+.09), (xb-xa,yb-ya,.18), 'brick', 'vaults', 'roofs', 'forge')
    for i, support in enumerate(a['walls'][:2]):
        contact('HoodSideBearing'+str(i), roof['West' if i==0 else 'East'], support)
    bottom = z+.18
    h = PLANS[age()]['flue_height']
    for label,xx,yy,ww,dd in [('West',cx-hole/2-t/2,cy,t,hole+2*t),
                              ('East',cx+hole/2+t/2,cy,t,hole+2*t),
                              ('Front',cx,cy-hole/2-t/2,hole,t),
                              ('Back',cx,cy+hole/2+t/2,hole,t)]:
        p = B('OpenFlue'+label,(xx,yy,bottom+h/2),(ww,dd,h),'brick','vaults','architecture','forge')
        contact('FlueBearing'+label,p,roof[label])
    ANCHORS[CURRENT]['flue_opening'] = dict(center=[cx,cy,bottom+h],clear_width=hole,source_open=True)


def work_porch():
    x,y,w,d,h = PLANS[age()]['porch']
    floor = B('WorkPorchBeddedFloor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground','hot_work')
    beam_bottom = F+h
    posts=[]
    for side in (-1,1):
        for j in range(3):
            xx=x-w/2+.16+j*(w-.32)/2
            q=B('WorkPost'+str(side)+'_'+str(j),(xx,y+side*(d/2-.16),(F+.08+beam_bottom)/2),
                (.18,.18,beam_bottom-F-.08),'timber','walls','architecture','hot_work')
            contact('WorkPostFoot'+str(side)+'_'+str(j),q,floor)
            posts.append((side,j,q))
        beam=B('WorkBearingBeam'+str(side),(x,y+side*(d/2-.16),beam_bottom+.10),(w,.24,.20),'timber','vaults','architecture','hot_work')
        for s,j,q in posts:
            if s==side:contact('WorkBeamBearing'+str(side)+'_'+str(j),beam,q)
    # A continuous roof bed bears on joists; its visible clay surface remains
    # quiet instead of a repeated modern-looking stripe grid.
    for j in range(11):
        xx=x-w/2+.14+j*(w-.28)/10
        q=B('WorkRoofJoist'+str(j),(xx,y,beam_bottom+.27),(.12,d,.14),'timber','vaults','fittings','hot_work')
        for side in (-1,1):
            beam=bpy.data.objects[R.PREFIX+CURRENT+'_WorkBearingBeam'+str(side)]
            contact('WorkJoistBearing'+str(j)+'_'+str(side),q,beam)
    roof=B('WorkClayRoof',(x,y,beam_bottom+.42),(w+.12,d+.12,.16),'roof','vaults','roofs','hot_work')
    q=bpy.data.objects[R.PREFIX+CURRENT+'_WorkRoofJoist0']
    contact('WorkRoofOnJoist',roof,q)
    ASSEMBLIES[CURRENT]['porch_floor']=floor


def store():
    x,y,w,d,h = PLANS[age()]['store']
    # Preserve the entrance and the gap behind the hot-work porch. Moving the
    # whole room south would collide with that porch; shorten its rear instead.
    front=y-d/2;rear=NATIVE[CURRENT]['primary_stamp_bounds'][1][1]-.05-.02
    d=rear-front;y=(front+rear)/2
    t=.20
    floor=B('StoreFloor',(x,y,F+.035),(w,d,.07),'stone','foundation','ground','tool_store')
    back=wall('StoreBack',x,y+d/2-t/2,w,t,h,bottom=F+.07,group='tool_store')
    for side in (-1,1):
        wall('StoreSide'+str(side),x+side*(w/2-t/2),y,t,d-.40,h,bottom=F+.07,group='tool_store')
    opening=.88
    pier=(w-opening)/2
    for side in (-1,1):
        wall('StoreFrontPier'+str(side),x+side*(opening/2+pier/2),y-d/2+t/2,pier,t,h,bottom=F+.07,group='tool_store')
    wall('StoreDoorHead',x,y-d/2+t/2,opening,t,h-1.90,bottom=F+.07+1.90,group='tool_store')
    roof=B('StoreRoof',(x,y,F+.07+h+.09),(w+.04,d+.04,.18),'roof','vaults','roofs','tool_store')
    contact('StoreRoofBearing',roof,back)
    door=B('StoreRecessedDoor',(x,y-d/2+.16,F+.07+.91),(.78,.05,1.82),'timber','finish','fittings','tool_store')
    contact('StoreDoorFoot',door,floor)


def cool_finishing_bay():
    if age()<4:
        return
    # The former east shoulder was outside the verified primary body. A compact
    # south bay leaves the existing entry pavers and central approach open.
    x,y,w,d = .80,-5.10,1.95,1.75
    floor=B('FinishingFloor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground','cool_work')
    top=F+2.70
    posts=[]
    for sx in (-1,1):
        for sy in (-1,1):
            p=B('FinishingPost'+str(sx)+str(sy),(x+sx*(w/2-.10),y+sy*(d/2-.10),(F+.08+top)/2),(.16,.16,top-F-.08),'timber','walls','architecture','cool_work')
            contact('FinishingPostFoot'+str(sx)+str(sy),p,floor)
            posts.append(p)
    roof=B('FinishingRoof',(x,y,top+.10),(w+.10,d+.10,.20),'roof','vaults','roofs','cool_work')
    for i,p in enumerate(posts):contact('FinishingRoofFoot'+str(i),roof,p)
    ANCHORS[CURRENT]['cool_finishing_source_bounds']=[[-.225,-6.025,F],[1.825,-4.175,top+.20]]


def architecture():
    forge_hood()
    work_porch()
    store()
    cool_finishing_bay()
    print('ARCHITECTURE_DRAFT',CURRENT,'one supported open flue, timber handling and separate storage')


def bench(name,x,y,w=1.75,d=.62,top=.96,group='hot_work'):
    floor=ASSEMBLIES[CURRENT]['porch_floor']
    z0=F+.08
    table=B(name+'Top',(x,y,top-.05),(w,d,.10),'timber','finish','props',group)
    for sx in (-1,1):
        for sy in (-1,1):
            leg=B(name+'Leg'+str(sx)+str(sy),(x+sx*(w/2-.13),y+sy*(d/2-.10),(z0+top-.10)/2),(.10,.10,top-.10-z0),'timber','finish','props',group)
            contact(name+'LegTop'+str(sx)+str(sy),leg,table,'top-bottom')
            contact(name+'LegGround'+str(sx)+str(sy),leg,floor)
    return table


def props():
    table=bench('ColdToolBench',-3.65,-1.55,1.65,.64,1.02)
    # Original static anvil is a closed stepped section on a grounded stump.
    # This does not authorize replacement of the separately owned stock anvil.
    stump=tag(R.lathe(CURRENT+'_AnvilStump',(-.70,-1.70,F+.08),[(.32,0),(.34,.08),(.29,.62)],'timber',col('props'),sides=12,role='props'), 'finish','props','hot_work')
    profile=[(-.43,0),(.28,0),(.28,.12),(.50,.22),(.65,.23),(.42,.34),(-.45,.34),(-.48,.22),(-.17,.18),(-.17,.10),(-.43,.10)]
    anvil=tag(R.extrude_xz(CURRENT+'_OriginalAnvil',[(u-.70,z+F+.70) for u,z in profile],-1.86,-1.54,'metal',col('props'),'finish',role='props'),'finish','props','hot_work')
    contact('AnvilOnStump',anvil,stump)
    # Low iron bars and a compact tool tray seat on the actual bench top.
    for j in range(5):
        q=B('IronBar'+str(j),(-4.05+j*.15,-1.55,1.02+.025),(.09,.46,.05),'metal','finish','props','hot_work')
        contact('IronBarOnBench'+str(j),q,table)
    for j in range(4):
        B('FuelLog'+str(j),(-5.20+(j%2)*.22,.40+(j//2)*.19,F+.045),(.44,.16,.09),'timber','finish','props','fuel')
    # The fire bed is matte charcoal source geometry; no glow/smoke is claimed.
    for j in range(7):
        B('HearthCharcoal'+str(j),(-1.90+(j%4)*.18,1.35+(j//4)*.22,F+.69),(.14,.14,.08),'ink','finish','props','forge')
    tag(R.lathe(CURRENT+'_QuenchTub',(-2.55,-2.95,F+.08),[(.34,0),(.40,.53),(.35,.53),(.29,.08)],'timber',col('props'),sides=16,role='props'),'finish','props','hot_work')
    if age()>=3:
        bench('RearInspectionBench',-3.55,-3.08,1.65,.60,1.02)
    print('PROPS_DRAFT',CURRENT,'supported anvil/benches, fuel, quench and iron stock; bellows reserved')


def detail():
    x,y,w,d,h=PLANS[age()]['porch']
    # Supported textile ties family identity to a working frontage, not a palace.
    beam=bpy.data.objects[R.PREFIX+CURRENT+'_WorkBearingBeam-1']
    band=B('WorkOwnerTextile',(x,y-d/2+.0275,F+h+.08),(1.20,.025,.16),'owner','finish','owner','hot_work')
    # Back of cloth lies against the front bearing face; role records this
    # intentional horizontal mounting, not an invented vertical contact.
    band['mounting_parent']=beam.name
    band['mounting_relation']='thin cloth on the front bearing beam face'
    for j in range(4):
        B('SootAtMouth'+str(j),(-1.92+j*.21,.796,F+2.20),(.15,.008,.21),'grime','finish','wear','forge')
    # Localized workshop traffic; no random all-over exposed-brick damage.
    for j in range(3):
        B('HearthTrafficWear'+str(j),(-1.50+j*.25,-.65,F+.084),(.42,.35,.008),'grime','finish','wear','hot_work')
    print('DETAIL_DRAFT',CURRENT,'owner textile, local soot and purposeful traffic wear')


def show(key='A2',state='healthy',lod=0):
    R.configure(ROOT,'blacksmith')
    if key not in NATIVE:raise ValueError('Unknown body key')
    scene=bpy.data.scenes[R.SCENE]
    for c in scene.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=scene
    R.view(pos=(14,-18,14),center=(-1.,-.3,2.),distance=18,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    """Explicit owned removal only; import/build never calls this."""
    if key is not None and key not in NATIVE:raise ValueError('Unknown body key')
    prefix='PSB_blacksmith_'+(key+'_' if key else '')
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
    spec=importlib.util.spec_from_file_location("blacksmith_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
