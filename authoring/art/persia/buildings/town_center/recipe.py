"""DRAFT original Persian civic Town Centers; no native edits or new motion.

Four measured shared native bodies, not separate invented capital tiers.
Authored in measured STAMP-space for review. A future adapter must apply the
recorded inverse stamp matrix to resource-space geometry exactly once.
Import configures only the owned family; it never builds, saves or resets.
"""
from pathlib import Path
import sys
import math
import json
import bpy

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / '_shared'
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
import source_runner as R
R.configure(ROOT, 'town_center')

F = .16
CURRENT = 'A1'
ANCHORS = {}
CONTRACTS = []
ASSEMBLIES = {}
LOD_CAP_HEIGHT = .055
TEXTURE_INPUTS = {k: str(ROOT / 'textures' / (k + '.png')) for k in
                  ('albedo', 'normal', 'roughness', 'metalness', 'owner_mask')}
TEXTURE_SPEC = {'resolution': [2048, 2048], 'original_pixels_required': True,
                'status': 'paths only; parent generates original family atlas'}
ACTORS = ('ps_building_town_center_capital_sul', 'ps_building_town_center_sul')
HANDOFF = ROOT.parents[3] / 'research/persia_buildings/inventory/PRIMARY_BODY_HANDOFF.json'
MODEL_STEM = 'art/civilizations/sultanate/structures/towncenter/'
NATIVE = {
    'A1': {'age': 1, 'model': MODEL_STEM + 'sul_towncenter_combined_age01/sul_towncenter_combined_age01.rgm',
           'stamp_bounds': [[-7.9914062023, -7.5636720657, -1.61328125], [7.8562500477, 8.0046873093, 5.796875]],
           'stamp_translation': [-2.2999999523, -5.3000001907, 0.], 'body_triangles': 43003},
    'A2': {'age': 2, 'model': MODEL_STEM + 'sul_towncenter_combined_age02/sul_towncenter_combined_age02.rgm',
           'stamp_bounds': [[-7.9093749523, -7.7785158157, -1.599609375], [7.7546875477, 8.0984373093, 6.7578125]],
           'stamp_translation': [-2.2999999523, -5.3000001907, 0.], 'body_triangles': 43877},
    'A3': {'age': 3, 'model': MODEL_STEM + 'sul_towncenter_combined_age03/sul_towncenter_combined_age03.rgm',
           'stamp_bounds': [[-7.9093749523, -7.7785158157, -1.599609375], [7.7546875477, 8.0984373093, 6.7578125]],
           'stamp_translation': [-2.2999999523, -5.3000001907, 0.], 'body_triangles': 45718},
    'A4': {'age': 4, 'model': MODEL_STEM + 'sul_towncenter_combined_age04/sul_towncenter_combined_age04.rgm',
           'stamp_bounds': [[-7.9416539669, -7.6992797852, -1.599609375], [7.8630335331, 8.0292358398, 9.4609375]],
           'stamp_translation': [-2.3166539669, -5.2207641602, 0.], 'body_triangles': 55886},
}
# Horizontal review envelope is deliberately a subset of every measured healthy
# primary-body stamp bound. It is NOT an engine collision/placement measurement.
REVIEW_BOUNDS = [[-6.85, -6.55, -.08], [6.85, 6.45, 8.35]]
PLANS = {
    1: {'program': 'open timber civic meeting hall + west store + east water shelter',
        'hall': (.4, 3.45, 8.4, 3.9, 3.00), 'bays': 3, 'roof': 'timber_flat',
        'utility': [(-5.0, .35, 2.4, 4.9, 2.45), (5.45, 2.95, 1.7, 3.6, 2.25)],
        'court': (.3, -2.1), 'height_cap': 5.30},
    2: {'program': 'three-bay vaulted civic range + deeper public court + offset store',
        'hall': (0., 3.35, 8.8, 3.9, 3.15), 'bays': 3, 'roof': 'three_vaults',
        'utility': [(-5.35, -.1, 1.9, 4.8, 2.65), (5.35, 3.0, 1.9, 3.6, 2.45)],
        'court': (.5, -2.0), 'height_cap': 6.20},
    3: {'program': 'arched public hall + offset inhabited upper office + west stair',
        'hall': (.55, 3.35, 8.7, 3.9, 3.12), 'bays': 3, 'roof': 'office_expansion',
        'utility': [(-5.35, -3.05, 1.9, 3.8, 2.55), (5.6, 2.9, 1.4, 4.0, 2.45)],
        'court': (.7, -2.3), 'height_cap': 6.30},
    4: {'program': 'broad upper civic porch + occupied rear council hall + low service wing',
        'hall': (0., 3.50, 9.8, 3.8, 3.12), 'bays': 3, 'roof': 'broad_upper_porch',
        'utility': [(-6.10, -1.7, 1.2, 4.2, 2.65), (5.65, 3.1, 1.3, 3.6, 2.5)],
        'court': (.4, -2.7), 'height_cap': 8.35},
}
NATIVE_DEPENDENCIES = {
    'base_layout': 'art/civilizations/common/layouts/archetypes/layout_towncenter/layout_towncenter.rgm',
    'bell_attachment': 'attachments/attachment_lists/civilizations/common/buildings/building_town_center_bell_arch',
    'outskirts_early': 'attachments/attachment_lists/civilizations/sultanate/outskirts/general/sul_towncenter_01',
    'outskirts_late': 'attachments/attachment_lists/civilizations/sultanate/outskirts/general/sul_towncenter_03',
    'motion_policy': 'Preserve every existing bell/rig/graph/marker dependency; no new bell geometry or animation.',
    'clearance_status': 'Unqualified: bell pivot, moving swept volume, unit exits and native selection markers require parent adapter inventory.',
}


def age():
    return NATIVE[CURRENT]['age']


def consumer_evidence(key):
    """Preserve evidence classes; never promote official candidates to consumers."""
    handoff=json.loads(HANDOFF.read_text(encoding='utf-8'))
    body=next(b for b in handoff['families']['town_center']['bodies'] if b['model']==NATIVE[key]['model'])
    uses=body['source_uses']
    return {'source_uses': uses,
            'private_compiled_source_uses': [u for u in uses if u['variant_evidence_class']=='existing_private_compiled_variant'],
            'official_parent_candidate_source_uses': [u for u in uses if u['variant_evidence_class']!='existing_private_compiled_variant'],
            'admission_note': 'Private/default/campaign and any separately evidenced native branches require parent consumer contract; candidate names do not authorize runtime scope.'}


def root(key=None, state='healthy', lod=0):
    if R.ROOT != ROOT or R.SLUG != 'town_center':
        R.configure(ROOT, 'town_center')
    key = key or CURRENT
    if key not in NATIVE:
        raise ValueError('Only measured Town Center keys A1/A2/A3/A4 are admitted')
    return R.collection(R.PREFIX + key + '_' + state + '_LOD' + str(lod), R.setup_scene().collection)


def col(role):
    return R.collection(R.PREFIX + CURRENT + '_healthy_' + role, root())


def tag(ob, stage, role, group=''):
    ob['body_key'] = CURRENT
    ob['construction_stage'] = stage
    ob['role'] = role
    ob['draft_uninspected'] = True
    ob['authored_coordinate_space'] = 'qualified healthy-body stamp projection; inverse pending'
    if group:
        ob['structural_group'] = group
    return ob


def B(name, center, size, surface='plaster', stage='walls', role='architecture', group=''):
    if any(v <= 0 for v in size):
        raise ValueError('Nonpositive part dimension: ' + name)
    return tag(R.block(CURRENT + '_' + name, center, size, surface, col(role), stage, role), stage, role, group)


def wall(name, x, y, w, d, h, surface='plaster', bottom=F, group=''):
    return B(name, (x, y, bottom + h / 2), (w, d, h), surface, 'walls', 'architecture', group)


def contact(name, child, parent, axis, target=0., tolerance=.003):
    CONTRACTS.append({'body': CURRENT, 'name': name, 'a': child.name, 'b': parent.name,
                      'axis': axis, 'target': target, 'tolerance': tolerance})


def setup():
    R.configure(ROOT, 'town_center')
    scene = R.setup_scene()
    scene['historical_basis'] = 'Original Persian civic court, institutional hall and service wings; see town_center/README.md.'
    scene['later_comparator_qualifier'] = 'Broad late timber porch uses later Safavid comparisons; not an exact pre-1629 Ali Qapu reconstruction.'
    R.view(pos=(18, -22, 17), center=(0., .2, 2.8), distance=23, solid=True)


def foundation(key='A1'):
    global CURRENT
    if key not in NATIVE:
        raise ValueError('Unknown native body key: ' + str(key))
    CURRENT = key
    setup()
    if root().all_objects:
        raise ValueError('Owned body exists; explicitly reset that body before rebuilding')
    x0, y0, _ = REVIEW_BOUNDS[0]
    x1, y1, _ = REVIEW_BOUNDS[1]
    ground = B('EarthCourtBed', (0., -.05, .04), (13.7, 13.0, .24), 'earth', 'foundation', 'ground', 'court_ground')
    # Continuous top is a source bearing plane; restrained apron does not authorize
    # any native footprint, grass clearing or placement-grid changes.
    apron = B('PublicApron', (.35, -2.5, F + .025), (7.4, 6.3, .05),
              'earth', 'foundation', 'ground', 'court_ground')
    contact('ApronOnGround', apron, ground, 'bottom-top')
    native = NATIVE[key]
    low, high = native['stamp_bounds']
    envelope = [[x0, y0, -.08], [x1, y1, PLANS[age()]['height_cap']]]
    margins = {'west': x0-low[0], 'east': high[0]-x1, 'front': y0-low[1],
               'back': high[1]-y1, 'top': high[2]-envelope[1][2]}
    if min(margins.values()) < 0:
        raise ValueError('Proposed conservative envelope exceeds measured healthy body')
    tx, ty, tz = native['stamp_translation']
    ANCHORS[key] = {
        'ground_top': F, 'native_body_key': key, 'native_model': native['model'],
        'actors_sharing_body': list(ACTORS), 'consumer_evidence': consumer_evidence(key),
        'existing_visual_age': age(), 'authoring_bounds_proposal': envelope,
        'chosen_horizontal_bounds': [[x0,y0],[x1,y1]],
        'native_healthy_stamp_bounds': native['stamp_bounds'],
        'envelope_proposal_margins': margins, 'entry': [0., -6.15, F],
        'court': list(PLANS[age()]['court']),
        'height_cap': PLANS[age()]['height_cap'],
        'planned_highest_z': {1:3.615,2:4.07,3:6.295,4:6.775}[age()],
        'planned_height_basis': 'Analytic draft geometry; parent must replace with actual built bounds receipt',
        'authored_space': 'stamp-space; identity object transforms; not native resource space',
        'native_resource_to_stamp_matrix': [[-1, 0, 0, tx], [0, -1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]],
        'stamp_to_native_resource_matrix': [[-1, 0, 0, tx], [0, -1, 0, ty], [0, 0, 1, -tz], [0, 0, 0, 1]],
        'dependencies': NATIVE_DEPENDENCIES,
        'doorway_measurement_status': 'All proposed openings are original art dimensions, not measured stock doorways.',
        'clearance_status': NATIVE_DEPENDENCIES['clearance_status'],
        'visual_inspection': 'Not performed; serial parent build and stage review required',
    }
    ASSEMBLIES[key] = {'ground': ground, 'apron': apron, 'rooms': {}}
    print('FOUNDATION_DRAFT', key, 'measured-envelope margins', margins)


def rectangular_front(name, x, y, w, h, opening, door_h, bottom=F, thickness=.28, group=''):
    """Three actual wall parts around a gap, never a door plaque on solid wall."""
    pier = (w - opening) / 2
    parts = [wall(name + '_Pier' + str(s), x+s*(opening/2+pier/2), y,
                  pier, thickness, h, bottom=bottom, group=group) for s in (-1, 1)]
    parts.append(wall(name + '_Head', x, y, opening, thickness, h-door_h,
                      bottom=bottom+door_h, group=group))
    return parts


def coping_run(name,center,length,width,z,axis,group,surface='stone',parent=None):
    count=max(1,math.ceil(length/.30));unit=length/count
    for i in range(count):
        xyz=list(center);xyz[axis]=center[axis]-length/2+(i+.5)*unit;xyz[2]=z+LOD_CAP_HEIGHT/2
        size=[width,width,LOD_CAP_HEIGHT];size[axis]=unit-.008 if count>1 else unit
        ob=B(name+'_Unit'+str(i),tuple(xyz),tuple(size),surface,'vaults','roofs',group)
        if parent is not None:contact(name+'_CopingSeat'+str(i),ob,parent,'bottom-top')
        ob['lod_cap_run']=CURRENT+'_'+name;ob['lod_cap_axis']=axis
        ob['lod_cap_mortar_gap']=.008;ob['lod_cap_course_bottom']=z
        ob['lod_cap_role']='weathering coping course; coarsen only continuous surviving units'


def flat_roof(name, x, y, w, d, wall_top, bearings, parapet=True, group='',omit_rear_interval=None):
    roof = B(name + '_RoofBed', (x, y, wall_top+.10), (w, d, .20),
             'roof', 'vaults', 'roofs', group)
    for i,bearing in enumerate(bearings):contact(name+'_RoofBearing'+str(i),roof,bearing,'bottom-top')
    if parapet:
        for side in (-1,1):
            px=x+side*(w/2-.09)
            para=B(name+'_SideParapet'+str(side),(px,y,wall_top+.30),(.18,d,.20),
                   'plaster','vaults','roofs',group)
            contact(name+'_SideParapetSeat'+str(side),para,roof,'bottom-top')
            coping_run(name+'_CopingSide'+str(side),(px,y,0),d,.22,wall_top+.40,1,group,'earth' if age()==1 else 'stone',parent=para)
        for side in (-1,1):
            yy=y+side*(d/2-.09);segments=[(x-w/2+.18,x+w/2-.18)]
            if side==1 and omit_rear_interval:
                a,b=segments[0];u,v=omit_rear_interval
                segments=[(a,min(b,u)),(max(a,v),b)]
            for j,(a,b) in enumerate(segments):
                if b-a<.01:continue
                para=B(name+'_EndParapet'+str(side)+'_'+str(j),((a+b)/2,yy,wall_top+.30),
                       (b-a,.18,.20),'plaster','vaults','roofs',group)
                contact(name+'_EndParapetSeat'+str(side)+'_'+str(j),para,roof,'bottom-top')
                coping_run(name+'_CopingEnd'+str(side)+'_'+str(j),((a+b)/2,yy,0),max(.01,b-a-.04),.22,wall_top+.40,0,group,
                           'earth' if age()==1 else 'stone',parent=para)
    return roof


def window_wall(name,x,y,length,thickness,height,windows,bottom,group,axis=0):
    """Actual wall openings with separately editable jambs, sill, head and trim."""
    parts=[];cursor=-length/2
    def segment(label,lo,hi,z,h):
        if hi-lo<1e-6 or h<1e-6:return None
        center=(x+(lo+hi)/2,y,z+h/2) if axis==0 else (x,y+(lo+hi)/2,z+h/2)
        size=(hi-lo,thickness,h) if axis==0 else (thickness,hi-lo,h)
        q=B(name+'_'+label,center,size,'plaster','walls','architecture',group);parts.append(q);return q
    for i,(offset,ow,sill,clear) in enumerate(sorted(windows)):
        lo,hi=offset-ow/2,offset+ow/2
        if lo<cursor-1e-6 or hi>length/2:raise ValueError('Window does not fit '+name)
        segment('Pier'+str(i),cursor,lo,bottom,height)
        sillpart=segment('SillWall'+str(i),lo,hi,bottom,sill)
        segment('Head'+str(i),lo,hi,bottom+sill+clear,height-sill-clear)
        cx,cy=(x+offset,y) if axis==0 else (x,y+offset)
        # Projected stone sill rests on real sill masonry, not across open air.
        silltrim=B(name+'_StoneSill'+str(i),(cx,cy,bottom+sill+.035),
              (ow+.12,thickness+.12,.07) if axis==0 else (thickness+.12,ow+.12,.07),
              'stone','finish','fine_detail',group)
        contact(name+'_SillTrimSeat'+str(i),silltrim,sillpart,'bottom-top')
        # Trim occupies the reveal edge; horizontal pieces butt to the verticals.
        for side in (-1,1):
            px,py=(cx+side*(ow/2-.035),cy) if axis==0 else (cx,cy+side*(ow/2-.035))
            B(name+'_Reveal'+str(i)+'_'+str(side),(px,py,bottom+sill+.07+(clear-.07)/2),
              (.07,thickness+.02,clear-.07) if axis==0 else (thickness+.02,.07,clear-.07),
              'timber','finish','fine_detail',group)
        B(name+'_LintelTrim'+str(i),(cx,cy,bottom+sill+clear-.035),
          (ow-.14,thickness+.02,.07) if axis==0 else (thickness+.02,ow-.14,.07),
          'timber','finish','fine_detail',group)
        cursor=hi
    segment('EndPier',cursor,length/2,bottom,height)
    return parts


def capital(name,post,beam,width,depth,height=.12):
    lo,hi=R.bounds(post);center=((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,hi[2]-height/2)
    ob=B(name,center,(width,depth,height),'timber','finish','fine_detail',post.get('structural_group','public_hall'))
    contact(name+'_BeamSeat',ob,beam,'top-bottom')
    return ob


def utility_room(label, spec):
    x, y, w, d, h = spec
    group = label
    t = .24
    back = wall(label+'_Back', x, y+d/2-t/2, w, t, h, group=group)
    sides = [wall(label+'_Side'+str(s), x+s*(w/2-t/2), y, t, d-.48, h, group=group) for s in (-1, 1)]
    ow = min(.95, w*.52)
    dh = min(2.05, h-.30)
    rectangular_front(label+'_Front', x, y-d/2+t/2, w, h, ow, dh, thickness=t, group=group)
    sill = B(label+'_Sill', (x, y-d/2, F+.035), (ow+.16, .42, .07), 'stone', 'foundation', 'ground', group)
    leaf = B(label+'_RecessedDoor', (x, y-d/2+t*.85, F+.07+(dh-.07)/2),
             (ow*.88, .055, dh-.07), 'timber', 'finish', 'fittings', group)
    contact(label+'_DoorOnSill', leaf, sill, 'bottom-top')
    roof = flat_roof(label, x, y, w, d, F+h, [back]+sides, group=group)
    ASSEMBLIES[CURRENT]['rooms'][label] = {'spec': spec, 'roof': roof, 'back': back}


def hall_walls():
    x, y, w, d, h = PLANS[age()]['hall']
    t = .30
    group = 'public_hall'
    back = wall('Hall_Back', x, y+d/2-t/2, w, t, h, group=group)
    sides = [wall('Hall_Side'+str(s), x+s*(w/2-t/2), y, t, d-.60, h, group=group) for s in (-1, 1)]
    floor = B('Hall_Floor', (x, y, F+.07), (w-.30, d-.30, .14),
              'stone', 'foundation', 'architecture', group)
    # The hall itself is civic open-front space. Its small service rooms are
    # separate from this repeated covered assembly, never a scaled house shell.
    ASSEMBLIES[CURRENT]['hall'] = {'spec': (x,y,w,d,h), 'back': back, 'sides': sides, 'floor': floor}


def hall_front_and_roof():
    a = ASSEMBLIES[CURRENT]['hall']
    x, y, w, d, h = a['spec']
    front = y-d/2+.15
    supports = [a['back']]+a['sides']
    n = PLANS[age()]['bays']
    bay = w/n
    if age() == 1:
        # Open timber meeting frontage: posts -> beam -> joists -> earthen bed.
        beam_h, joist_h = .22, .16
        post_top = F+h-beam_h-joist_h
        for i in range(n+1):
            xx = x-w/2+.15+i*(w-.30)/n
            post = B('Hall_FrontPost'+str(i), (xx, front, (F+.14+post_top)/2),
                     (.20,.20,post_top-F-.14), 'timber', 'walls', 'architecture', 'public_hall')
            contact('HallPostFoot'+str(i), post, a['floor'], 'bottom-top')
            supports.append(post)
        beam = B('Hall_FrontBeam',(x,front,post_top+beam_h/2),(w,.30,beam_h),'timber','vaults','architecture','public_hall')
        for i, post in enumerate(supports[3:]):
            contact('HallFrontBeamBearing'+str(i),beam,post,'bottom-top')
            capital('Hall_TimberCapital'+str(i),post,beam,.34,.38)
        for i in range(11):
            xx=x-w/2+.20+i*(w-.40)/10
            joist=B('Hall_Joist'+str(i),(xx,y,F+h-joist_h/2),(.14,d,joist_h),'timber','vaults','architecture','public_hall')
            joist['lod_joist_run']='hall_roof';joist['lod_joist_index']=i;joist['lod_joist_count']=11
            contact('HallJoistOnBeam'+str(i),joist,beam,'bottom-top')
        # Rear and side wall tops continue to the roof underside; joists terminate
        # inside these bearing walls by design. Only front post/beam is exposed.
        flat_roof('Hall',x,y,w,d,F+h,[a['back']]+a['sides'],group='public_hall')
    else:
        # Each arcade bay is one editable closed masonry arch mesh with a REAL
        # opening. Independent bays avoid fake texture doors or linked duplicates.
        for i in range(n):
            cx=x-w/2+bay*(i+.5)
            arch=tag(R.archwall(CURRENT+'_Hall_Arcade'+str(i),cx,front-.15,front+.15,F,
                               bay,h,bay-.46,2.18,.56,'plaster',col('architecture'),segments=16),
                     'walls','architecture','public_hall')
            arch['lod_arch_spec']=json.dumps({'cx':cx,'y0':front-.15,'y1':front+.15,'z0':F,'outer_w':bay,'height':h,
                'inner_w':bay-.46,'spring':2.18,'rise':.56,'surface':'plaster'})
            supports.append(arch)
        if age()==2:
            for i in range(n):
                cx=x-w/2+bay*(i+.5)
                if i:
                    wall('Hall_VaultBearing'+str(i),x-w/2+bay*i,y,.25,d-.60,h,
                         group='public_hall')
                roof=tag(R.vault(CURRENT+'_Hall_Vault'+str(i),cx,y-d/2,y+d/2,F+h,
                                  (bay-.24)/2,.63,.13,'roof',col('roofs'),segments=20,along=3),
                         'vaults','roofs','public_hall')
                roof['lod_vault_spec']=json.dumps({'cx':cx,'y0':y-d/2,'y1':y+d/2,'z0':F+h,
                    'rx':(bay-.24)/2,'rz':.63,'thickness':.13,'surface':'roof'})
                for end in (-1,1):
                    outline=[(cx-(bay-.24)/2,F+h),(cx+(bay-.24)/2,F+h)]
                    outline += [(cx+(bay-.24)/2*math.cos(j*math.pi/20),F+h+.63*math.sin(j*math.pi/20)) for j in range(1,20)]
                    yy=y+end*d/2
                    endcap=tag(R.extrude_xz(CURRENT+'_Hall_VaultEnd'+str(i)+'_'+str(end),outline,
                                     yy-.06,yy+.06,'plaster',col('roofs'),'vaults'),
                        'vaults','roofs','public_hall')
                    endcap['lod_vault_end']=json.dumps({'cx':cx,'y0':yy-.06,'y1':yy+.06,'z0':F+h,'rx':(bay-.24)/2,'rz':.63,'surface':'plaster'})
                contact('VaultSpringOnArcade'+str(i),roof,supports[3+i],'bottom-top')
        else:
            a['roof']=flat_roof('Hall',x,y,w,d,F+h,supports,parapet=(age()==3),group='public_hall',
                   omit_rear_interval=(-2.95,2.25) if age()==3 else None)
    # An intentionally wide raised civic threshold rather than a residential door.
    threshold=B('Hall_PublicThreshold',(x,front-.24,F+.07),(w-.30,.48,.14),
                'stone','foundation','architecture','public_hall')
    contact('ThresholdOnGround',threshold,ASSEMBLIES[CURRENT]['ground'],'bottom-top')


def upper_office_age3():
    """Broader occupied office; existing west wall/landing remains anchored."""
    x,y,w,d=-.35,3.65,5.20,3.30
    bottom=F+3.44;h=2.24;group='upper_office'
    floor=B('Office_Floor',(x,y,bottom-.06),(w,d,.12),'timber','walls','architecture',group)
    contact('UpperOfficeFloorOnHallRoof',floor,ASSEMBLIES[CURRENT]['hall']['roof'],'bottom-top')
    back=wall('Office_Back',x,y+d/2-.13,w,.26,h,bottom=bottom,group=group)
    east=wall('Office_East',x+w/2-.13,y,.26,d-.52,h,bottom=bottom,group=group)
    frontparts=window_wall('Office_ReceptionWindows',x,2.13,w,.26,h,
                          [(-1.30,1.25,.62,1.15),(1.30,1.25,.62,1.15)],bottom,group)
    westx=x-w/2+.13;opening=.98;clear=1.98;west=[]
    for side in (-1,1):
        segment=(d-opening)/2
        west.append(wall('Office_WestPier'+str(side),westx,y+side*(opening/2+segment/2),.26,segment,h,bottom=bottom,group=group))
    head=wall('Office_WestDoorHead',westx,y,.26,opening,h-clear,bottom=bottom+clear,group=group)
    sill=B('Office_WestDoorSill',(-2.95,y,bottom+.035),(.40,opening+.12,.07),'stone','walls','architecture',group)
    door=B('Office_RecessedWestDoor',(westx+.08,y,bottom+.07+(clear-.07)/2),(.06,opening*.88,clear-.07),
           'timber','finish','fittings',group)
    contact('OfficeDoorOnSill',door,sill,'bottom-top')
    bearings=[back,east,head]+west+[p for p in frontparts if 'SillWall' not in p.name]
    flat_roof('Office',x,y,w,d,bottom+h,bearings,group=group)
    landing=B('Office_StairLanding',(-3.90,3.60,(F+bottom)/2),(1.90,1.30,bottom-F),
              'plaster','walls','architecture','office_access')
    contact('OfficeLandingMeetsWestWall',landing,west[0],'right-left')
    stairs('Office_Stair',-4.35,-1.0,2.95,1.0,bottom-F,22,'office_access')
    # An open reception window and one partially shuttered office window show
    # occupied administration; both remain real openings with useful reveals.
    shutter=B('Office_PartialShutter',(-1.91,2.15,bottom+1.195),(.56,.06,1.01),'timber','finish','fittings',group)
    CONTRACTS.append({'body':CURRENT,'name':'OfficePartialShutterSill','a':shutter.name,
       'b':R.PREFIX+CURRENT+'_Office_ReceptionWindows_StoneSill0','axis':'bottom-top','target':0.,'tolerance':.003})
    for i,cx in enumerate((-1.65,.95)):
        for side in (-1,1):
            B('Office_WindowMullion'+str(i)+'_'+str(side),(cx+side*.20,2.15,bottom+1.195),(.035,.04,1.08),
              'timber','finish','fine_detail',group)
    # Closed triangular timber brackets visibly bear a shallow continuous hood.
    hood_bottom=bottom+1.92
    brackets=[]
    for i,xx in enumerate((-2.45,-.85,.15,1.75)):
        outline=[(1.47,hood_bottom),(2.0,hood_bottom-.38),(2.0,hood_bottom)]
        ob=tag(R.extrude_xz(CURRENT+'_Office_HoodBracket'+str(i),outline,xx-.055,xx+.055,'timber',
                col('architecture'),'vaults',lambda u,v,z:(v,u,z)),'vaults','architecture',group);brackets.append(ob)
    hood=B('Office_ReceptionHood',(x,1.745,hood_bottom+.04),(5.40,.55,.08),'timber','vaults','roofs',group)
    for i,bracket in enumerate(brackets):contact('OfficeHoodBearing'+str(i),hood,bracket,'bottom-top')
    # A low writing counter is seen through the open eastern reception window.
    desk=B('Office_ReceptionCounter',(.95,2.52,bottom+.59),(1.12,.55,.10),'timber','finish','props',group)
    for i,xx in enumerate((.52,1.38)):
        leg=B('Office_CounterLeg'+str(i),(xx,2.52,bottom+.27),(.09,.42,.54),'timber','finish','props',group)
        contact('OfficeCounterLegFloor'+str(i),leg,floor,'bottom-top')
        contact('OfficeCounterSeat'+str(i),desk,leg,'bottom-top')
    ANCHORS[CURRENT]['office_programme']={'west_face_fixed_x':-2.95,'east_expanded_x':2.25,
        'reception_windows':2,'stair_start_y':-1.0,'service_wing_forward_shift':'clears lengthened stair; unchanged native bounds'}


def stairs(label,x,y0,y1,width,rise,count,group):
    run=(y1-y0)/count
    for j in range(count):
        height=rise*(j+1)/count
        step=B(label+str(j),(x,y0+(j+.5)*run,F+height/2),(width,run,height),'stone','walls','architecture',group)
        contact(label+'_Ground'+str(j),step,ASSEMBLIES[CURRENT]['ground'],'bottom-top')
        step['lod_stair_group']=CURRENT+'_'+label;step['lod_stair_index']=j;step['lod_stair_count']=count
        step['lod_stair_spec']=json.dumps({'x':x,'y0':y0,'y1':y1,'width':width,'bottom':F,'rise':rise,'group':group})


def upper_civic_age4():
    floor_top=F+3.44;x,y,w,d=0.,3.70,9.20,3.40;h=2.72;group='upper_council'
    floor=B('Council_Floor',(x,y,floor_top-.06),(w,d,.12),'timber','walls','architecture',group)
    contact('CouncilFloorOnHallRoof',floor,ASSEMBLIES[CURRENT]['hall']['roof'],'bottom-top')
    back=window_wall('Council_BackWindows',0.,5.26,w,.28,h,
                     [(-2.50,1.20,1.10,1.00),(2.50,1.20,1.10,1.00)],floor_top,group)
    sides=[]
    for sign in (-1,1):
        sides+=window_wall('Council_SideWindows'+str(sign),sign*4.46,y,d-.56,.28,h,
                      [(-.70,.65,1.10,1.00),(.70,.65,1.10,1.00)],floor_top,group,axis=1)
    fronts=[];module=w/3
    for i in range(3):
        cx=-w/2+(i+.5)*module
        fronts+=rectangular_front('CouncilFront'+str(i),cx,2.14,module,h,1.46,2.18,
                                   bottom=floor_top,thickness=.28,group=group)
        sill=B('Council_DoorSill'+str(i),(cx,2.0,floor_top+.035),(1.58,.40,.07),'stone','walls','architecture',group)
        if i!=1:
            leaf=B('Council_Shutter'+str(i),(cx,2.22,floor_top+.07+(2.18-.07)/2),(1.28,.06,2.18-.07),
                   'timber','finish','fittings',group)
            contact('CouncilShutterOnSill'+str(i),leaf,sill,'bottom-top')
    bearings=[q for q in back+sides+fronts if 'SillWall' not in q.name]
    ASSEMBLIES[CURRENT]['council_roof']=flat_roof('Council',0.,y,w,d,floor_top+h,bearings,group=group)
    # Four supports derive from the actual three-bay public arcade piers. Both
    # floors keep the center entrance clear; matched upper supports transmit load.
    hall_w=PLANS[4]['hall'][2];bay=hall_w/3
    postxs=[-hall_w/2+.115,-hall_w/2+bay,-hall_w/2+2*bay,hall_w/2-.115]
    porch_y,porch_w,porch_d=1.30,9.80,1.40
    deck_th=.12;joist_h=.18;beam_h=.24
    beam_top=floor_top-deck_th-joist_h;beam_bottom=beam_top-beam_h;front_y=.70
    posts=[]
    for i,xx in enumerate(postxs):
        post=B('Porch_LowerPost'+str(i),(xx,front_y,(F+beam_bottom)/2),(.22,.22,beam_bottom-F),
               'timber','walls','architecture','porch_support')
        contact('PorchLowerPostOnGround'+str(i),post,ASSEMBLIES[CURRENT]['ground'],'bottom-top');posts.append(post)
    beam=B('Porch_LowerFrontBeam',(0.,front_y,beam_bottom+beam_h/2),(porch_w,.28,beam_h),
           'timber','walls','architecture','porch_support')
    for i,post in enumerate(posts):
        contact('PorchBeamOnPost'+str(i),beam,post,'bottom-top');capital('Porch_LowerCapital'+str(i),post,beam,.34,.34)
    ledger=B('Porch_LowerWallLedger',(0.,2.0,beam_bottom+beam_h/2),(porch_w,.26,beam_h),
             'timber','walls','architecture','porch_support')
    contact('PorchLedgerIntoHallRoof',ledger,ASSEMBLIES[CURRENT]['hall']['roof'],'top-bottom',target=.02)
    # A real west turn landing butts to a notched deck; no overlapping flat
    # floor faces, tiny corner-only connection or doorway through a solid wall.
    landing=B('Council_Landing',(-5.0,1.60,(F+floor_top)/2),(.90,.80,floor_top-F),
              'plaster','walls','architecture','council_access')
    contact('CouncilLandingGround',landing,ASSEMBLIES[CURRENT]['ground'],'bottom-top')
    outline=[(-4.9,.6),(4.9,.6),(4.9,2.0),(-4.55,2.0),(-4.55,1.2),(-4.9,1.2)]
    vertices=[(xx,yy,zz) for zz in (floor_top-deck_th,floor_top) for xx,yy in outline]
    faces=[(5,4,3,2,1,0),(6,7,8,9,10,11)]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
    deck=tag(R.mesh(CURRENT+'_Porch_Deck',vertices,faces,'timber',col('architecture'),'vaults','architecture'),
             'vaults','architecture','porch_support')
    ANCHORS[CURRENT].setdefault('numerical_interfaces',[]).append({
      'body':CURRENT,'name':'CouncilLandingToNotchedDeck','a':landing.name,'b':deck.name,
      'authored_contact_point':[-4.55,1.60,floor_top-.06],
      'intentional_socket_overlap_metres':0.0,'tolerance':.003,
      'basis':'Actual rear-notch vertical faces meet atX-4.55; bbox extrema alone do not represent this joint.'})

    for i in range(17):
        xx=-4.70+i*9.40/16
        jy,jd=(.90,.60) if i==0 else (porch_y,porch_d)
        q=B('Porch_FloorJoist'+str(i),(xx,jy,beam_top+joist_h/2),(.12,jd,joist_h),
            'timber','walls','architecture','porch_support')
        q['lod_joist_run']='porch_floor';q['lod_joist_index']=i;q['lod_joist_count']=17
        contact('PorchJoistOnBeam'+str(i),q,beam,'bottom-top')
        if i==0:contact('PorchLeftJoistIntoLanding',q,landing,'back-front')
        else:contact('PorchJoistOnLedger'+str(i),q,ledger,'bottom-top')
        contact('PorchDeckOnJoist'+str(i),deck,q,'bottom-top')
    roof_post_top=floor_top+2.65;upper=[]
    for i,xx in enumerate(postxs):
        q=B('Porch_UpperPost'+str(i),(xx,front_y,floor_top+2.65/2),(.16,.16,2.65),
            'timber','vaults','architecture','upper_porch')
        contact('PorchUpperPostOnDeck'+str(i),q,deck,'bottom-top');upper.append(q)
    upperbeam=B('Porch_RoofBeam',(0.,front_y,roof_post_top+.09),(10.0,.22,.18),
                'timber','vaults','architecture','upper_porch')
    ASSEMBLIES[CURRENT]['owner_beam']=upperbeam
    for i,post in enumerate(upper):
        contact('PorchRoofBeamOnPost'+str(i),upperbeam,post,'bottom-top');capital('Porch_UpperCapital'+str(i),post,upperbeam,.28,.30,.11)
    roofledger=B('Porch_RearRoofLedger',(0.,2.02,roof_post_top+.09),(10.0,.22,.18),'timber','vaults','architecture','upper_porch')
    # .11 intentional embed into the occupied hall roof/header, not a gap.
    contact('PorchRearLedgerIntoCouncilRoof',roofledger,ASSEMBLIES[CURRENT]['council_roof'],'top-bottom',target=.11)
    rafters=[]
    for i in range(17):
        q=B('Porch_RoofRafter'+str(i),(-4.75+i*9.50/16,1.30,roof_post_top+.23),(.09,1.65,.10),
            'timber','vaults','fittings','upper_porch')
        q['lod_joist_run']='porch_roof';q['lod_joist_index']=i;q['lod_joist_count']=17
        contact('PorchRafterOnRoofBeam'+str(i),q,upperbeam,'bottom-top')
        contact('PorchRafterOnRearLedger'+str(i),q,roofledger,'bottom-top');rafters.append(q)
    shade=B('Porch_ShadeRoof',(0.,1.30,roof_post_top+.35),(10.05,1.70,.14),'roof','vaults','roofs','upper_porch')
    for i,q in enumerate(rafters):contact('PorchShadeOnRafter'+str(i),shade,q,'bottom-top')
    stairs('Council_WestStair',-5.0,-2.80,1.20,.90,floor_top-F,22,'council_access')
    ANCHORS[CURRENT]['council_access']={'stair_bounds_x':[-5.45,-4.55],'stair_y':[-2.80,1.20],
       'landing_bounds_xy':[[-5.45,1.20],[-4.55,2.0]],'deck_notch':[[-4.90,1.20],[-4.55,2.0]],
       'actual_join_plane':{'axis':'x','landing_right':-4.55,'deck_rear_notch_left':-4.55,'gap':0.0},
       'status':'original source geometry, not native travel-path clearance'}
    ANCHORS[CURRENT]['porch_supports']={'x':postxs,'count':4,'main_axis_clear_x':[-1.45,1.45],
        'derivation':'actual ground arcade pier axes, matched upper/lower load paths; native exits unqualified'}


def first_room():
    hall_walls()
    print('FIRST_ROOM_DRAFT',CURRENT,'rear/side masonry and civic floor; front openings/roof await next stage')


def architecture():
    hall_front_and_roof()
    for i,spec in enumerate(PLANS[age()]['utility']):
        utility_room('ServiceWing'+str(i),spec)
    if age()==3:upper_office_age3()
    if age()==4:upper_civic_age4()
    # The front is intentionally public and broad: unlike House/Caravanserai,
    # it is not a tiny door through an enclosing wall. Two low walls mark edges.
    for i,(x,w) in enumerate([(-4.85,3.4),(4.85,3.4)]):
        wall('CivicBoundary'+str(i),x,-5.9,w,.28,.72,group='court_boundary')
    intervals=[(-5.75,-1.95)]
    for sx,sy,sw,sd,sh in PLANS[age()]['utility']:
        if min(-6.27,sx+sw/2)-max(-6.53,sx-sw/2)<=0:continue
        fresh=[]
        for a,b in intervals:
            lo,hi=sy-sd/2,sy+sd/2
            if min(b,hi)<=max(a,lo):fresh.append((a,b))
            else:
                if lo>a:fresh.append((a,lo))
                if hi<b:fresh.append((hi,b))
        intervals=fresh
    for i,(a,b) in enumerate(intervals):
        wall('WestCourtReturn'+str(i),-6.4,(a+b)/2,.26,b-a,.72,group='court_boundary')
    print('ARCHITECTURE_DRAFT',CURRENT,PLANS[age()]['program'])


def props():
    # Civic public programme: protected writing/notice station, water provision
    # and limited received supplies. No market stalls or residential pot clutter.
    x,y,w,d,h=PLANS[age()]['hall']
    front=y-d/2
    platform=B('Civic_AssessmentPlatform',(x+1.9,front+.7,F+.18),(1.9,1.1,.36),
               'stone','foundation','architecture','civic_props')
    desk_top=F+.95
    desk=B('Civic_ClerkDesk',(x+1.9,front+.7,desk_top-.045),(1.60,.65,.09),
           'timber','finish','props','civic_props')
    for i,sx in enumerate((-.48,.48)):
        leg=B('ClerkDeskLeg'+str(i),(x+1.9+sx,front+.7,(F+.36+desk_top-.09)/2),
              (.10,.44,desk_top-.09-F-.36),'timber','finish','props','civic_props')
        contact('DeskLegOnPlatform'+str(i),leg,platform,'bottom-top')
        contact('DeskOnLeg'+str(i),desk,leg,'bottom-top')
    book=B('Civic_ClosedRegister',(x+1.72,front+.7,desk_top+.035),(.44,.30,.07),
           'cloth','finish','props','civic_props')
    contact('RegisterOnDesk',book,desk,'bottom-top')
    inkwell=tag(R.lathe(CURRENT+'_ClerkInkpot',(x+2.35,front+.70,desk_top),[(.055,0),(.07,.07),(.05,.12)],
                    'ink',col('props'),sides=12,stage='finish'),'finish','props','civic_props')
    contact('InkpotOnDesk',inkwell,desk,'bottom-top')
    chest=B('Civic_RegisterChest',(x+2.25,front+.85,F+.54),(.54,.40,.36),'timber','finish','props','civic_props')
    contact('RegisterChestPlatform',chest,platform,'bottom-top')
    paper=B('ClerkOpenSheet',(x+1.45,front+.65,desk_top+.012),(.30,.25,.024),'paper','finish','props','civic_props')
    contact('ClerkSheetOnDesk',paper,desk,'bottom-top')
    # Water jar and broad low basin sit to one side, leaving civic center empty.
    tag(R.lathe(CURRENT+'_WaterJar',(4.25,-3.5,F),[(.26,0),(.43,.20),(.45,.66),(.28,.86),(.25,.92)],
                'pottery',col('props'),sides=16,stage='finish'), 'finish','props','water_station')
    tag(R.lathe(CURRENT+'_WaterBasin',(3.25,-3.45,F),[(.46,0),(.52,.28),(.47,.33),(.36,.14)],
                'stone',col('props'),sides=16,stage='finish'), 'finish','props','water_station')
    for i in range(3):
        B('ReceivedSupply'+str(i),(-3.35+i*.55,-3.6,F+.22),(.46,.55,.44),
          'cloth','finish','props','received_supplies')
    # A supported public notice board with framed paper, not invented calligraphy.
    for i,xx in enumerate((-2.4,-1.5)):
        post=B('NoticePost'+str(i),(xx,-4.1,F+.78),(.10,.12,1.56),
               'timber','finish','fittings','public_notice')
    board=B('NoticeBoard',(-1.95,-4.1,F+1.28),(1.04,.10,.70),
            'timber','finish','props','public_notice')
    B('NoticePaper',(-1.95,-4.16,F+1.28),(.72,.02,.46),'paper','finish','props','public_notice')
    # Geometric seal marks, not fabricated historical lettering.
    for i,cx in enumerate((-2.12,-1.80)):
        B('NoticeSeal'+str(i),(cx,-4.175,F+1.28),(.13,.015,.13),'ink','finish','fine_detail','public_notice')
    for i,xx in enumerate((-2.43,-1.47)):
        B('NoticeSideFrame'+str(i),(xx,-4.18,F+1.28),(.08,.08,.70),'timber','finish','fittings','public_notice')
    # No new bell: the pre-existing native dependency is separately preserved.
    print('PROPS_DRAFT',CURRENT,'clerk/water/notice programme; central approach kept visually clear')


def _arcade_ring(name,cx,y,rx,spring,rz,group):
    # Real individually editable brick voussoirs sit against the actual arch face.
    for i in range(12):
        a=i*math.pi/12+.006;b=(i+1)*math.pi/12-.006
        outline=[(cx+rx*math.cos(a),spring+rz*math.sin(a)),
                 (cx+(rx+.11)*math.cos(a),spring+(rz+.11)*math.sin(a)),
                 (cx+(rx+.11)*math.cos(b),spring+(rz+.11)*math.sin(b)),
                 (cx+rx*math.cos(b),spring+rz*math.sin(b))]
        ob=tag(R.extrude_xz(CURRENT+'_'+name+'_Voussoir'+str(i),outline,y-.035,y,'brick',
                 col('details'),'finish'),'finish','fine_detail',group)
        ob['detail_basis']='Original brick ring on real civic arch, not copied texture or floating plaque'


def detail():
    x,y,w,d,h=PLANS[age()]['hall']
    if age()==4:
        # Visible front of upper beam; the earlier ground-hall cloth was hidden.
        support=B('OwnerTextileSupport',(0.,.555,F+6.17),(2.10,.09,.09),
                  'timber','finish','fittings','upper_porch')
        cloth=B('OwnerCivicTextile',(0.,.495,F+5.91),(1.85,.025,.43),
                'owner','finish','owner','upper_porch')
        contact('OwnerClothSuspended',cloth,support,'top-bottom')
        # The beam support overlaps the actual exposed front beam intentionally.
        contact('OwnerSupportIntoRoofBeam',support,ASSEMBLIES[CURRENT]['owner_beam'],'back-front',target=.01)
    else:
        support=B('OwnerTextileSupport',(x,y-d/2-.04,F+h-.30),(2.30,.08,.09),
                  'timber','finish','fittings','owner_identity')
        cloth=B('OwnerCivicTextile',(x,y-d/2-.095,F+h-.56),(1.86,.025,.43),
                'owner','finish','owner','owner_identity')
        contact('OwnerClothSuspended',cloth,support,'top-bottom')
    if age()>=2:
        bay=w/3
        for i in range(3):_arcade_ring('HallBrickRing'+str(i),x-w/2+(i+.5)*bay,y-d/2,(bay-.46)/2,F+2.18,.56,'public_hall')
    if age()==4:
        B('CouncilGeometricTileBand',(0.,1.985,F+5.93),(3.10,.045,.17),'carving','finish','fine_detail','upper_council')
    for i in range(9):
        B('ApproachPaver'+str(i),(.30,-5.2+i*.61,F+.067),(1.12,.53,.084),'stone','foundation','ground','court_path')
    # Local handling and rain patterns explain wear rather than randomly exposing
    # masonry. They sit slightly above the existing source surface, not in air.
    for i in range(5):
        B('CivicTrafficWear'+str(i),(.30,-4.65+i*.90,F+.052),(.90,.52,.006),
          'grime','finish','wear','court_wear')
    for i,room in enumerate(PLANS[age()]['utility']):
        xx,yy,ww,dd,hh=room
        B('ServiceThresholdWear'+str(i),(xx,yy-dd/2-.25,F+.004),(.75,.36,.008),
          'grime','finish','wear','service_wear')
    print('DETAIL_DRAFT',CURRENT,'visible civic owner; seated coping, brick rings, capitals and purposeful wear')


def build_lod(H,key,state,source,destination,level,profile):
    """Family hook; parent family_states invokes this after LOD0 composition."""
    import importlib.util
    spec=importlib.util.spec_from_file_location('persia_tc_lods',ROOT/'lods.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)


def show(key='A1', state='healthy', lod=0):
    R.configure(ROOT,'town_center')
    scene=bpy.data.scenes[R.SCENE]
    for collection in scene.collection.children:
        if collection.name.startswith(R.PREFIX):
            collection.hide_render=collection.hide_viewport=(collection.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod))
    bpy.context.window.scene=scene
    R.view(pos=(18,-22,17),center=(0.,.2,2.8),distance=23,solid=True)


def build_body(key):
    foundation(key)
    first_room()
    architecture()
    props()
    detail()
    show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    """Explicit removal of this family/body only; never called on import."""
    # Never trust mutable shared-runner PREFIX here: another family can have
    # configured the shared module since import. Cleanup ownership is literal.
    prefix='PSB_town_center_'+(key+'_' if key else '')
    if key is not None and key not in NATIVE:
        raise ValueError('Unknown body key')
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):
            data=ob.data if ob.type=='MESH' else None
            bpy.data.objects.remove(ob,do_unlink=True)
            if data and not data.users:bpy.data.meshes.remove(data)
    for collection in list(bpy.data.collections):
        if collection.name.startswith(prefix):bpy.data.collections.remove(collection)
    if key:
        ANCHORS.pop(key,None)
        ASSEMBLIES.pop(key,None)
        CONTRACTS[:]=[c for c in CONTRACTS if c['body']!=key]
    else:
        ANCHORS.clear(); ASSEMBLIES.clear(); CONTRACTS.clear()
