"""Original Persian Outpost architecture drafts; no native weapon substitutes.

Run only in the parent's serialized source-art pipeline. Geometry is unbuilt here.
configuration.json preserves native evidence and the eight standard configurations.
"""
from pathlib import Path
import sys, math, json
import bpy

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / '_shared'
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
import source_runner as R

BODY_KEYS = ('A1Basic', 'A1Fortified')
NATIVE_CHOICES = {'A1Basic': 'wood', 'A1Fortified': 'fortified'}
CURRENT = 'A1Basic'
ANCHORS = {}
CONTRACTS = []
F = .12
PARAMS = {
    'wood': dict(floor=.28, shaft_top=3.26, outer_bottom=1.65,
                 outer_top=1.48, inner_bottom=1.17, inner_top=1.12,
                 gallery_floor=3.40, gallery_head=5.50, upper_floor=5.78,
                 overall_top=8.52),
    'fortified': dict(floor=.36, shaft_top=5.38, outer_bottom=1.58,
                      outer_top=1.32, inner_bottom=1.02, inner_top=.99,
                      gallery_floor=5.52, gallery_head=7.84, upper_floor=8.18,
                      overall_top=9.14),
}


def activate():
    R.configure(ROOT, 'outpost')


def root(key=None, state='healthy', lod=0):
    activate()
    return R.collection(R.PREFIX + (key or CURRENT) + '_' + state + '_LOD' + str(lod),
                        R.setup_scene().collection)


def col(role):
    return R.collection(R.PREFIX + CURRENT + '_healthy_' + role, root())


def tag(o, stage, role, group):
    o['body_key'] = CURRENT
    o['construction_stage'] = stage
    o['role'] = role
    o['structural_group'] = group
    o['draft_status'] = 'Unbuilt source architecture; mechanism compound pending'
    return o


def B(name, center, size, surface='brick', stage='walls', role='architecture', group='shaft'):
    activate()
    return tag(R.block(CURRENT + '_' + name, center, size, surface, col(role), stage, role),
               stage, role, group)


def obj(name):
    return bpy.data.objects[R.PREFIX + CURRENT + '_' + name]


def contact(name, a, b, target=0, tolerance=.003):
    CONTRACTS.append(dict(body=CURRENT, name=name, a=a.name, b=b.name,
                          axis='bottom-top', target=target, tolerance=tolerance))


def interface(name, a, b, point, description, intentional_socket_overlap_metres=0):
    row = dict(
        name=name, a=a.name, b=b.name, authored_contact_point=list(point),
        authored_space='model-space', relation=description,
        verification='Contact plan; inspect generated faces before acceptance.')
    if intentional_socket_overlap_metres:
        row['intentional_socket_overlap_metres'] = intentional_socket_overlap_metres
    ANCHORS[CURRENT]['numerical_interfaces'].append(row)


def plan():
    return PARAMS[NATIVE_CHOICES[CURRENT]]


def halves(z):
    p = plan()
    t = (z - p['floor']) / (p['shaft_top'] - p['floor'])
    return (p['outer_bottom'] + t * (p['outer_top'] - p['outer_bottom']),
            p['inner_bottom'] + t * (p['inner_top'] - p['inner_bottom']))


def rotate_side(face, u, v, z):
    return ((u, -v, z), (v, u, z), (-u, v, z), (-v, -u, z))[face]


def panel(name, face, u0, u1, z0, z1, surface='plaster', inner_u0=None, inner_u1=None):
    """One closed tapered masonry panel, mitered at tower corners.

    None u endpoints follow outer/inner corner edges. Fixed endpoints form a
    real aperture; separate inner endpoints provide a genuine splayed reveal.
    """
    vs = []
    for z in (z0, z1):
        outer, inner = halves(z)
        oa, ob = (-outer if u0 is None else u0), (outer if u1 is None else u1)
        ia = -inner if u0 is None else (u0 if inner_u0 is None else inner_u0)
        ib = inner if u1 is None else (u1 if inner_u1 is None else inner_u1)
        vs.extend(rotate_side(face, u, v, z)
                  for u, v in [(oa, outer), (ob, outer), (ib, inner), (ia, inner)])
    o = tag(R.mesh(CURRENT + '_' + name, vs,
                  [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                   (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
                  surface, col('architecture'), 'walls', 'architecture'),
            'walls', 'architecture', 'shaft')
    if abs(z0 - plan()['floor']) < .0001:
        contact(name + 'PlinthBearing', o, obj('Plinth'))
    return o


def opening_band(face, z0, z1, outer_width, inner_width, label):
    a = panel(label + 'PierL', face, None, -outer_width / 2, z0, z1,
              inner_u1=-inner_width / 2)
    b = panel(label + 'PierR', face, outer_width / 2, None, z0, z1,
              inner_u0=inner_width / 2)
    ANCHORS[CURRENT]['openings'].append(dict(
        name=label, face=face, outer_clear_width=outer_width,
        inner_clear_width=inner_width, z_interval=[z0, z1],
        purpose='Authored opening; native muzzle/sweep compatibility must be inspected.'))
    return a, b


def hatch_deck(name, z0, z1, half, surface, stage='vaults', group='floor'):
    # Closed, non-overlapping pieces around a real .62 x .70 access hatch.
    xa, xb, ya, yb = -.99, -.37, -.99, -.29
    boxes = [('West', -half, xa, -half, half), ('East', xb, half, -half, half),
             ('South', xa, xb, -half, ya), ('North', xa, xb, yb, half)]
    out = []
    for suffix, x0, x1, y0, y1 in boxes:
        if x1 <= x0 or y1 <= y0:
            raise ValueError('Deck hatch exceeds slab')
        out.append(B(name + suffix, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                     (x1 - x0, y1 - y0, z1 - z0), surface, stage, 'architecture', group))
    ANCHORS[CURRENT]['hatches'].append(dict(name=name, x=[xa, xb], y=[ya, yb], z=z1))
    return out


def ladder(name, z0, z1, x=-.68, y=-.62):
    # Fixed straight timber ladder, not a motion asset or pretend mechanism.
    rails = []
    for side in (-1, 1):
        rails.append(B(name + 'Rail' + str(side), (x + side * .245, y, (z0 + z1) / 2),
                       (.07, .09, z1 - z0), 'timber', 'walls', 'architecture', 'access'))
    count = max(2, int((z1 - z0) / .27))
    for j in range(1, count):
        z = z0 + (z1 - z0) * j / count
        rung = B(name + 'Rung' + str(j), (x, y - .015, z), (.56, .07, .065),
                 'timber', 'walls', 'architecture', 'access')
        for side, rail in zip((-1, 1), rails):
            interface(name + 'RungSeat' + str(j) + str(side), rung, rail,
                      (x + side * .245, y - .015, z),
                      'Rung ends enter side rails by .035m; fixed joinery.',
                      intentional_socket_overlap_metres=.035)
    ANCHORS[CURRENT]['access'].append(dict(name=name, z_interval=[z0, z1],
                                          clear_width=.42, hatch_axis=[x, y]))
    return rails


def foundation(key='A1Basic'):
    global CURRENT
    if key not in BODY_KEYS:
        raise ValueError('Only native wood/default and fortified/stone_upgrade bodies exist')
    CURRENT = key
    activate()
    R.setup_scene()
    if root().all_objects:
        raise ValueError('Owned body exists; parent must inspect before explicit reset')
    p = plan()
    cfg = json.loads((ROOT / 'configuration.json').read_text(encoding='utf-8'))
    ANCHORS[key] = dict(body_key=key, front_direction='-Y', ground_top=F,
        work_floor_top=p['floor'], numerical_interfaces=[], openings=[], hatches=[], access=[],
        authored_space='model-space', authored_coordinate_projection='Blender=(-native.x,-native.z,native.y)',
        native_body_choice=NATIVE_CHOICES[key], native_body=cfg['bodies'][NATIVE_CHOICES[key]], gameplay_footprint=cfg['exact_gameplay_footprint_scale'],
        source_to_native_stamp='Apply the retained 180-degree stamp matrix once after source fit; do not bake it twice.',
        retained_native_mechanisms=False, motion_sweep_qualified=False,
        authored_architecture_top=p['overall_top'],
        source_acceptance_gap='Inspect retained native body members, hierarchy/pivots and cannon child against this original shell. No compound clearance is claimed.')
    xmin, xmax, ymin, ymax = (-1.98, 1.98, -1.98, 1.98) if NATIVE_CHOICES[key] == 'wood' else (-1.66, 1.66, -3.20, 1.66)
    bed = B('EarthBed', ((xmin + xmax) / 2, (ymin + ymax) / 2, (F - .03) / 2),
            (xmax - xmin, ymax - ymin, F + .03), 'earth', 'foundation', 'ground', 'plot')
    half = p['outer_bottom'] + .035
    plinth = B('Plinth', (0, 0, (F + p['floor']) / 2),
               (2 * half, 2 * half, p['floor'] - F), 'stone', 'foundation', 'ground', 'foundation')
    contact('PlinthEarthBearing', plinth, bed)
    # Three low approach treads on fortified body; two on basic body.
    n = 2 if NATIVE_CHOICES[key] == 'wood' else 3
    depth = .14 if NATIVE_CHOICES[key] == 'wood' else .34
    outer = p['outer_bottom']
    for j in range(n):
        top = F + (p['floor'] - F) * (j + 1) / n
        step = B('EntryStep' + str(j), (0, -outer - depth * (n - j - .5), (F + top) / 2),
                 (.97, depth, top - F), 'stone', 'foundation', 'ground', 'entry')
        contact('EntryStepEarth' + str(j), step, bed)
    ANCHORS[key]['entry_approach'] = dict(width=.97, tread_depth=depth, step_count=n,
                                         ground_z=F, landing_z=p['floor'])


def first_room():
    p = plan()
    z0, z1 = p['floor'], p['shaft_top']
    # Protected entry and real interior. All slit bands are genuine voids.
    door_top = z0 + 2.12
    opening_band(0, z0, door_top, .91, 1.01, 'Entry')
    panel('EntryHead', 0, None, None, door_top, z1, 'brick')
    for side in (1, 2, 3):
        slit0, slit1 = (2.38, 3.06) if NATIVE_CHOICES[CURRENT] == 'wood' else (2.58, 3.30)
        panel('Side' + str(side) + 'BelowSlit', side, None, None, z0, slit0)
        opening_band(side, slit0, slit1, .14, .48, 'ArrowSlit' + str(side))
        if NATIVE_CHOICES[CURRENT] == 'fortified':
            panel('Side' + str(side) + 'BetweenPorts', side, None, None, slit1, 4.10)
            opening_band(side, 4.10, 4.96, .82, 1.02, 'LowerEmbrasure' + str(side))
            panel('Side' + str(side) + 'UpperBearing', side, None, None, 4.96, z1)
        else:
            panel('Side' + str(side) + 'OverSlit', side, None, None, slit1, z1)
    # Fixed shaped timber leaf, recessed behind the masonry throat.
    front = -p['outer_bottom']
    outline = [(-.405, z0 + .06), (.405, z0 + .06)]
    outline += [(.405 * math.cos(j * math.pi / 14), z0 + 1.66 + .42 * math.sin(j * math.pi / 14))
                for j in range(15)]
    leaf = tag(R.extrude_xz(CURRENT + '_EntryLeaf', outline, front + .11, front + .165,
                           'timber', col('fittings'), 'finish', role='fittings'),
               'finish', 'fittings', 'entry')
    sill = B('EntrySill', (0, front + .055, z0 + .03), (1.05, .32, .06),
             'stone', 'foundation', 'ground', 'entry')
    contact('EntryLeafSill', leaf, sill)
    contact('EntrySillPlinth', sill, obj('Plinth'))
    for z in (z0 + .40, z0 + 1.46):
        B('DoorRail' + str(z), (0, front + .085, z), (.79, .035, .065),
          'timber', 'finish', 'fittings', 'entry')
    # Floor access stays visible/editable through open hatches in the source.
    ladder('LowerAccess', z0, p['gallery_floor'])
    ANCHORS[CURRENT]['entry_clearance'] = dict(width=.91, height=2.12,
        leaf='Closed static healthy leaf; no opening animation authored',
        protected_by='Tapered thick jambs and masonry head; splayed interior throat')


def architecture():
    p = plan()
    z0, z1 = p['shaft_top'], p['gallery_floor']
    deck = hatch_deck('GalleryDeck', z0, z1, 1.88 if NATIVE_CHOICES[CURRENT] == 'wood' else 1.51,
                       'timber', group='fighting_gallery')
    shaft_seat = (p['outer_top'] + p['inner_top']) / 2
    side_head = 'OverSlit' if NATIVE_CHOICES[CURRENT] == 'wood' else 'UpperBearing'
    # Each hatch slab names its actual wall head and its own shared bearing
    # point. A single south-wall point cannot describe all four deck pieces.
    seats = [('Side3' + side_head, (-shaft_seat, 0, z0)),
             ('Side1' + side_head, (shaft_seat, 0, z0)),
             ('EntryHead', (-.68, -shaft_seat, z0)),
             ('Side2' + side_head, (-.68, shaft_seat, z0))]
    for slab, (support, point) in zip(deck, seats):
        interface('GalleryDeckWallSeat' + slab.name, slab, obj(support), point,
                  'Slab bottom seats on this tapered masonry head at the shared z datum; hatch remains internal.')
    if NATIVE_CHOICES[CURRENT] == 'wood':
        # Open lower machinery gallery; corners lie outside measured springald
        # source rest-union in XY. This is not a sampled moving-sweep claim.
        pos, width = 1.76, .15
        head = p['gallery_head']
        for x in (-pos, pos):
            for y in (-pos, pos):
                post = B('GalleryPost' + str(x) + str(y), (x, y, (z1 + head) / 2),
                         (width, width, head - z1), 'timber', group='fighting_gallery')
                contact('GalleryPostDeck' + str(x) + str(y), post,
                        obj('GalleryDeckWest' if x < 0 else 'GalleryDeckEast'))
        # Paired bearing rails and perpendicular joists carry the upper lookout.
        for y in (-pos, pos):
            rail = B('GalleryBearing' + str(y), (0, y, head + .07),
                     (3.67, .20, .14), 'timber', 'vaults', group='fighting_gallery')
            for x in (-pos, pos):
                contact('GalleryBearingPost' + str(x) + str(y), rail,
                        obj('GalleryPost' + str(x) + str(y)))
        upper = hatch_deck('LookoutFloor', head + .14, head + .28, 1.88, 'timber',
                            group='lookout')
        # Floor datum follows actual deck thickness, not a decorative floating slab.
        upper_top = head + .28
        for slab in upper:
            bearer_y = pos if slab.name.endswith('North') else -pos
            contact('LookoutFloorBearing' + slab.name, slab, obj('GalleryBearing' + str(bearer_y)))
        for x in (-pos, pos):
            for y in (-pos, pos):
                post = B('LookoutPost' + str(x) + str(y), (x, y, (upper_top + 8.17) / 2),
                         (.15, .15, 8.17 - upper_top), 'timber', group='lookout')
                contact('LookoutPostFloor' + str(x) + str(y), post,
                        obj('LookoutFloorWest' if x < 0 else 'LookoutFloorEast'))
        for face in range(4):
            for sign in (-1, 1):
                x, y, z = rotate_side(face, sign * .94, pos, (upper_top + 6.65) / 2)
                size = (1.70, .10, 6.65 - upper_top) if face % 2 == 0 else (.10, 1.70, 6.65 - upper_top)
                B('LookoutBreastwork' + str(face) + str(sign), (x, y, z), size,
                  'timber', group='lookout')
        for y in (-pos, pos):
            rail = B('RoofBearing' + str(y), (0, y, 8.23), (3.78, .18, .12),
                     'timber', 'vaults', group='roof')
            for x in (-pos, pos):
                contact('RoofBearingPost' + str(x) + str(y), rail,
                        obj('LookoutPost' + str(x) + str(y)))
        for j, x in enumerate((-1.58, -.95, -.32, .32, .95, 1.58)):
            joist = B('RoofJoist' + str(j), (x, 0, 8.34), (.11, 3.78, .10),
                      'timber', 'vaults', group='roof')
            for y in (-pos, pos):
                contact('RoofJoistBearing' + str(j) + str(y), joist,
                        obj('RoofBearing' + str(y)))
        roof = B('ClayWatchRoof', (0, 0, (8.39 + 8.52) / 2), (3.88, 3.88, .13),
                 'roof', 'vaults', 'roofs', 'roof')
        for j in range(6):
            contact('RoofBearing' + str(j), roof, obj('RoofJoist' + str(j)))
        ladder('GalleryAccess', z1, upper_top + .12)
        ANCHORS[CURRENT]['lookout_floor_actual_top'] = upper_top
    else:
        # Fortified mass is masonry, not a third age tier. Broad intermediate
        # openings reserve donor reference regions without inventing weapons.
        pos, width, head = 1.28, .34, p['gallery_head']
        for x in (-pos, pos):
            for y in (-pos, pos):
                pier = B('GalleryPier' + str(x) + str(y), (x, y, (z1 + head) / 2),
                         (width, width, head - z1), 'brick', group='fighting_gallery')
                contact('GalleryPierDeck' + str(x) + str(y), pier,
                        obj('GalleryDeckWest' if x < 0 else 'GalleryDeckEast'))
        for y in (-pos, pos):
            rail = B('UpperBearing' + str(y), (0, y, head + .09), (2.94, .24, .18),
                     'timber', 'vaults', group='upper_platform')
            for x in (-pos, pos):
                contact('UpperBearingPier' + str(x) + str(y), rail,
                        obj('GalleryPier' + str(x) + str(y)))
        upper = hatch_deck('UpperPlatform', head + .18, head + .34, 1.55,
                            'timber', group='upper_platform')
        for slab in upper:
            bearer_y = pos if slab.name.endswith('North') else -pos
            contact('UpperPlatformBearing' + slab.name, slab, obj('UpperBearing' + str(bearer_y)))
        top = head + .34
        for face in range(4):
            # Butt-connected straight parapet pieces. Corner end lengths differ
            # on EW faces, so exterior walls never share coplanar strips.
            length = 3.10 if face % 2 == 0 else 2.66
            center = rotate_side(face, 0, 1.44, top + .26)
            size = (length, .22, .52) if face % 2 == 0 else (.22, length, .52)
            wall = B('Parapet' + str(face), center, size, 'brick', group='parapet')
            support = ('UpperPlatformSouth', 'UpperPlatformEast',
                       'UpperPlatformNorth', 'UpperPlatformWest')[face]
            contact('ParapetFloor' + str(face), wall, obj(support))
            for j, u in enumerate((-.98, 0, .98)):
                center = rotate_side(face, u, 1.44, (top + .52 + 9.14) / 2)
                size = (.48, .22, 9.14 - top - .52) if face % 2 == 0 else (.22, .48, 9.14 - top - .52)
                tooth = B('Merlon' + str(face) + str(j), center, size, 'brick', group='parapet')
                contact('MerlonParapet' + str(face) + str(j), tooth, wall)
        ladder('UpperAccess', z1, top + .12)
        ANCHORS[CURRENT]['upper_platform_actual_top'] = top
    ANCHORS[CURRENT]['open_fighting_gallery_z'] = [z1, p['gallery_head']]


def props():
    # Useful, restrained fixed supplies, never an archer, launcher or cannon proxy.
    z = plan()['floor']
    box = B('WatchSupplies', (.72, .54, z + .19), (.42, .46, .38),
            'timber', 'finish', 'props', 'supplies')
    contact('SupplyBoxFloor', box, obj('Plinth'))
    jar = tag(R.lathe(CURRENT + '_WaterJar', (-.72, .52, z),
                     [(.14, 0), (.21, .08), (.23, .32), (.13, .43), (.14, .47)],
                     'pottery', col('props'), sides=16, stage='finish', role='props'),
              'finish', 'props', 'supplies')
    contact('WaterJarFloor', jar, obj('Plinth'))


def detail():
    p = plan()
    # Original regional brick/earth language: restrained course collars and no
    # mosque gallery, borrowed Sultanate dome, ornamental portal or fantasy crown.
    if NATIVE_CHOICES[CURRENT] == 'wood':
        z = 8.22
        fascia = B('OwnerFascia', (0, -1.855, z), (1.15, .025, .13),
                   'owner', 'finish', 'owner', 'owner')
        interface('OwnerFasciaBeamSeat', fascia, obj('RoofBearing' + str(-1.76)),
                  (0, -1.85, z), 'Fascia back embeds .0075m into front bearing face; preview owner mask only.',
                  intentional_socket_overlap_metres=.0075)
    else:
        B('OwnerPlaque', (.71, -1.558, 8.42), (.42, .025, .22),
          'owner', 'finish', 'owner', 'owner')
    ANCHORS[CURRENT]['material_contract'] = dict(
        original_atlas_size=[2048, 2048], texture_files=[str(ROOT / 'textures' / (n + '.png'))
        for n in ('albedo', 'normal', 'roughness', 'metalness', 'owner_mask')],
        status='Pending original painting by parent; existing material helper expects these files.',
        wear='Local entry rub, damp plinth and roof-edge runoff only; no random all-over damage.')


def write_anchors():
    activate()
    path = ROOT / 'anchors.json'
    path.write_text(json.dumps(ANCHORS, indent=2) + '\n', encoding='utf-8')
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')
    return path


def show(key='A1Basic',state='healthy',lod=0):
    activate();scene=bpy.data.scenes[R.SCENE]
    for collection in scene.collection.children:
        if collection.name.startswith(R.PREFIX):
            collection.hide_render=collection.hide_viewport=(collection.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod))
    bpy.context.window.scene=scene


def build_body(key='A1Basic'):
    foundation(key)
    first_room()
    architecture()
    props()
    detail()
    return root(key)


def preview_configuration(configuration_id):
    """Return a composition proposal only; never invent or auto-import a weapon."""
    activate()
    data = json.loads((ROOT / 'configuration.json').read_text(encoding='utf-8'))
    row = next(x for x in data['configurations'] if x['id'] == configuration_id)
    return dict(row, architecture_collection=R.PREFIX + row['body_key'] + '_healthy_LOD0',
                assembly_status='Parent must retain and qualify native mechanism before this preview is complete')


activate()
