"""Fail-closed full source builder; no native export, cook or integration.

Blender --background --factory-startup --python-exit-code 1 --python THIS -- SLUG
Use --probe for an unsaved full-family qualification. Never run in a live file.
The shared state recipe provides 31 compositions per existing native body.
"""
from pathlib import Path
import sys, json, hashlib, importlib.util, re, traceback, math, os
import bpy
from mathutils import Matrix, Vector

ART = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ART / '_shared'))
import mesh_checks as C
import family_states as S

STAGES = ('foundation', 'walls', 'vaults', 'finish')
NATIVE_GATES = 'Deferred: native export/cook, bindings, placement, owner rendering, mechanisms/animation, lifecycle transitions, destruction/repair, import and multiplayer.'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def family_root(slug):
    if not re.fullmatch(r'[a-z][a-z0-9_]*', slug) or slug == 'house':
        raise ValueError('Select one non-House family slug')
    root = ART / slug
    if not root.is_dir():
        raise ValueError('Missing prepared family: ' + slug)
    return root


def factory_guard():
    if not bpy.app.background or bpy.data.filepath or '--factory-startup' not in sys.argv:
        raise RuntimeError('Requires a new background --factory-startup process with no open file')
    if set(s.name for s in bpy.data.scenes) != {'Scene'} or any(o.name not in {'Cube', 'Camera', 'Light'} for o in bpy.data.objects):
        raise RuntimeError('Factory scene contains unexpected user/source data; refusing generation')


def load_recipe(root):
    spec = importlib.util.spec_from_file_location('recipe', root / 'recipe.py')
    H = importlib.util.module_from_spec(spec)
    sys.modules['recipe'] = H
    spec.loader.exec_module(H)
    return H


def inputs(root):
    """Retained authoring inputs, not generated anchors/manifests/receipts.

    Additional family dependencies must be enumerated in retained_input_paths.
    Compact native contracts retain donor hashes; this does not reread/cache
    native game media that the original geometry recipe does not consume.
    """
    required = [root / n for n in ('recipe.py', 'family.json', 'native-contracts.json', 'state-profiles.json', 'evidence/stock-budgets.json')]
    generated_json = {'anchors.json', 'state-manifest.json'}
    shared_inputs=[ART/'_shared'/name for name in ('source_runner.py','mesh_checks.py','state_geometry.py','family_states.py','build_family.py','verify_family.py','atlas_source.py','make_original_atlas.py')]
    paths = set(required + list(root.glob('*.py')) + [p for p in root.glob('*.json') if p.name not in generated_json] + shared_inputs + list((root / 'textures').rglob('*')))
    family = json.loads((root / 'family.json').read_text())
    native = json.loads((root / 'native-contracts.json').read_text())
    inventory = ART.parents[2] / 'research/persia_buildings/inventory'
    for name, expected in native.get('input_contract_sha256', {}).items():
        p = inventory / name
        if not p.is_file() or sha(p) != expected:
            raise RuntimeError('Compact native contract provenance is stale/missing: ' + str(p))
        paths.add(p)
    for name in family.get('retained_input_paths', []):
        p = Path(name)
        paths.add(p if p.is_absolute() else (root / p).resolve())
    for p in required:
        if not p.is_file():
            raise RuntimeError('Missing retained input: ' + str(p))
    if any(not p.exists() for p in paths):
        raise RuntimeError('A declared retained input is missing')
    expanded = set()
    for p in paths:
        expanded.update(x.resolve() for x in p.rglob('*') if x.is_file()) if p.is_dir() else expanded.add(p.resolve())
    return sorted(expanded, key=str)


def fingerprints(root):
    return {os.path.relpath(p, ART): sha(p) for p in inputs(root)}


def source_contracts(root):
    family = json.loads((root / 'family.json').read_text())
    native = json.loads((root / 'native-contracts.json').read_text())
    profiles = json.loads((root / 'state-profiles.json').read_text())
    keys = family['expected_body_keys']
    if not keys or len(keys) != len(set(keys)) or any(not re.fullmatch(r'[A-Za-z0-9_]+', k) for k in keys):
        raise RuntimeError('Invalid/duplicate expected native body keys')
    if set(keys) != set(native['bodies']) or set(keys) != set(profiles['bodies']):
        raise RuntimeError('Family/native/profile body coverage differs')
    if profiles.get('native_hp_thresholds') is not None:
        raise RuntimeError('Source profile must not infer native HP thresholds')
    return family, native, profiles, keys


def expected_names(prefix, keys):
    return {prefix + k + '_' + state + '_LOD' + str(lod) for k in keys for state in S.STATES for lod in (0, 1, 2)} | {prefix + k + '_construct_' + stage for k in keys for stage in STAGES}


def meshes(col):
    return [o for o in col.all_objects if o.type == 'MESH']


def identity(ob):
    return ob.get('healthy_source', ob.name)


def shape_digest(ob):
    """World-space oriented geometry only: UV/debris changes cannot fake damage."""
    def q(x): return round(float(x), 5) or 0.0
    vs = [tuple(q(v) for v in p) for p in C.world_points(ob)]
    fs = []
    for f in ob.data.polygons:
        row = [vs[i] for i in f.vertices]
        fs.append(min(tuple(row[j:] + row[:j]) for j in range(len(row))))
    return hashlib.sha256(json.dumps([sorted(vs), sorted(fs)], separators=(',', ':')).encode()).hexdigest()


def part_record(ob):
    return {'name': ob.name, 'healthy_source': identity(ob), 'role': ob.get('role'), 'group': ob.get('structural_group'),
            'stage': ob.get('construction_stage'), 'triangles': C.triangles([ob]), 'geometry_uv_digest_q5': C.digest(ob),
            'world_geometry_digest_q5': shape_digest(ob), 'matrix_world': [list(row) for row in ob.matrix_world]}


def collection_map(col, geometry=False, architecture=False):
    out = {}
    for ob in meshes(col):
        if architecture and ob.get('role') not in ('architecture', 'roofs'):
            continue
        key = identity(ob)
        if key in out:
            raise RuntimeError('Duplicate source identity in ' + col.name + ': ' + key)
        out[key] = shape_digest(ob) if geometry else C.digest(ob)
    return out


def native_frame(anchor, body):
    if 'authored_space' not in anchor:
        raise RuntimeError('Recipe must explicitly declare ANCHORS[key].authored_space')
    authored = str(anchor['authored_space']).lower()
    if 'stamp' in authored and not authored.startswith('model'):
        stamps = body['stamp_contracts']
        matrices = {json.dumps(s['blender_matrix_row_major']) for s in stamps}
        if len(matrices) != 1:
            raise RuntimeError('Multiple/missing stamp frames need an explicit per-consumer adapter')
        frame = Matrix(stamps[0]['blender_matrix_row_major']).inverted()
    elif authored.startswith('model') or authored.startswith('resource'):
        frame = Matrix.Identity(4)
    else:
        raise RuntimeError('Unrecognized authored coordinate space: ' + authored)
    if frame.determinant() <= 0 or any(abs(frame[2][i]) > 1e-7 or abs(frame[i][2]) > 1e-7 for i in (0, 1)):
        raise RuntimeError('Reflected/tilted frame needs a reviewed contact/winding adapter')
    return frame


def project_contact(contract, frame):
    """Project a signed scalar face-to-face joint into the saved resource frame.

    A half-turn reverses the measured gap and swaps the extrema pair. A
    quarter-turn also changes the axis. Sheared/oblique joints require a real
    numerical interface rather than a guessed axis-aligned AABB contact.
    """
    axes = {'bottom-top': (2, False), 'top-bottom': (2, True),
            'right-left': (0, True), 'left-right': (0, False),
            'front-back': (1, False), 'back-front': (1, True)}
    axis = contract.get('axis', 'bottom-top')
    if axis not in axes:
        raise RuntimeError('Unsupported scalar contact axis: ' + axis)
    direction, reverse = axes[axis]
    column = [float(frame[i][direction]) for i in range(3)]
    dest = max(range(3), key=lambda i: abs(column[i]))
    coefficient = column[dest]
    if abs(coefficient) < 1e-9 or any(abs(column[i]) > 1e-7 for i in range(3) if i != dest):
        raise RuntimeError('Oblique scalar contact needs a measured numerical interface: ' + contract['name'])
    # Other input axes must not shear into the measured destination direction.
    if any(abs(frame[dest][i]) > 1e-7 for i in range(3) if i != direction):
        raise RuntimeError('Sheared scalar contact needs a measured numerical interface: ' + contract['name'])
    if coefficient < 0:
        reverse = not reverse
    saved_axis = next(name for name, value in axes.items() if value == (dest, reverse))
    return {**contract, 'axis': saved_axis, 'target': contract.get('target', 0) * coefficient,
            'tolerance': contract.get('tolerance', .003) * abs(coefficient),
            'authored_axis': axis, 'projection_signed_axis_scale': coefficient}


def apply_frame(H, key, frame):
    cols = [bpy.data.collections[n] for n in sorted(expected_names(H.R.PREFIX, [key]))]
    obs = {o for c in cols for o in meshes(c)}
    for ob in obs:
        if ob.get('source_resource_frame_applied'):
            raise RuntimeError('Refusing a second authored-to-resource inverse: ' + ob.name)
        if ob.parent or any(m.type == 'ARMATURE' for m in ob.modifiers):
            if all(abs(frame[r][c]-float(r==c))<=1e-9 for r in range(4) for c in range(4)):
                # Model-space authoring needs no coordinate projection. Baking
                # an identity through an existing rig would needlessly alter its
                # local bind data; keep the complete parent/modifier graph.
                ob['source_resource_frame_applied']=True
                ob['source_resource_frame_policy']='Identity projection: local vertices, parent, bind matrices and modifiers preserved verbatim'
                continue
            raise RuntimeError('Live parent/rig needs a preserved dependency adapter, not mesh-only inverse: ' + ob.name)
        world = ob.matrix_world.copy()
        for vertex in ob.data.vertices:
            vertex.co = frame @ (world @ vertex.co)
        ob.matrix_world = Matrix.Identity(4)
        ob.data.update()
        ob['source_resource_frame_applied'] = True
    H.ANCHORS[key]['source_checkpoint_frame'] = {'authored_space': H.ANCHORS[key]['authored_space'],
        'saved_space': 'projected native resource space', 'authored_to_resource_matrix': [list(row) for row in frame],
        'native_actor_stamp_markers_changed': False}


def budget_for(root, body, profile=None):
    budgets = json.loads((root / 'evidence/stock-budgets.json').read_text())['budgets_by_age']
    resource_age = body['native_age_label_from_resource_name']
    if resource_age is None:
        choice = (profile or {}).get('comparison_budget')
        if not choice or not choice.get('basis'):
            raise RuntimeError('Shared native body needs an explicit comparison_budget age/basis; do not invent a resource age')
        age = str(choice['age'])
    else:
        age = str(resource_age)
    if age not in budgets:
        raise RuntimeError('Missing exact resource-age budget: ' + age)
    row = budgets[age]
    if row.get('sample_count', 0) < 3 or row.get('cap_guaranteed_native_maximum_triangles', 0) <= 0:
        raise RuntimeError('Unqualified three-sample conservative stock budget')
    return row


def state_envelope(body, profile, state, root):
    override = profile.get('verified_resource_state_envelopes', {}).get(state)
    if override:
        evidence = override.get('retained_evidence_file')
        declared = set(fingerprints(root))
        p = (root / evidence).resolve() if evidence else None
        if not p or os.path.relpath(p, ART) not in declared or not override.get('basis'):
            raise RuntimeError('State envelope override needs pinned retained evidence and a stated basis')
        return override['bounds'], 'family measured state envelope; ' + override['basis']
    return body['healthy_definite_rest_bounds'], 'Conservative healthy definite primary-resource rest envelope applied to this source state; native per-state/compound envelope is not qualified.'


def texture_checks(H, root):
    rows = []
    for name in ('albedo', 'normal', 'roughness', 'metalness', 'owner_mask'):
        path = (root / 'textures' / (name + '.png')).resolve()
        if not path.is_file():
            raise RuntimeError('Missing original family atlas: ' + str(path))
        image = bpy.data.images.load(str(path), check_existing=True)
        rows.append({'map': name, 'path': str(path), 'sha256': sha(path), 'size': list(image.size), 'passed': tuple(image.size) == (2048, 2048)})
    for ob in bpy.data.scenes[H.R.SCENE].objects:
        if ob.type != 'MESH' or ob.get('retained_native_dependency'):
            continue
        for slot in ob.material_slots:
            mat = slot.material
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        p = Path(bpy.path.abspath(node.image.filepath)).resolve()
                        if p.parent != (root / 'textures').resolve() or p.stem not in ('albedo', 'normal', 'roughness', 'metalness', 'owner_mask'):
                            raise RuntimeError('Authored material refers outside original family atlas: ' + str(p))
        if not ob.material_slots or any(slot.material is None for slot in ob.material_slots):
            raise RuntimeError('Authored mesh has an unresolved material: ' + ob.name)
    return rows


def remap_contact(contract, lookup):
    return {**contract, 'a': lookup[contract['a']].name, 'b': lookup[contract['b']].name}


def assess(H, root, native, profiles, keys, contacts, interfaces):
    errors, reports, compositions = [], [], {}
    scene = bpy.data.scenes.get(H.R.SCENE)
    names = expected_names(H.R.PREFIX, keys)
    actual = {c.name for c in scene.collection.children if c.name.startswith(H.R.PREFIX)} if scene else set()
    if actual != names:
        errors.append({'coverage_missing': sorted(names - actual), 'coverage_extra': sorted(actual - names)})
    for key in keys:
        body, profile = native['bodies'][key], profiles['bodies'][key]
        budget = budget_for(root, body, profile)
        known = set(S.STATES)
        unknown = [v for v in body['actual_geometry_lifecycle_values'] if v not in known and not re.fullmatch(r'construct_\d+', v)]
        if unknown:
            errors.append({'body': key, 'unmapped_native_additional_states_require_adapter': unknown})
        rows = []
        for name in sorted(expected_names(H.R.PREFIX, [key])):
            col = bpy.data.collections.get(name)
            if col is None:
                continue
            state = name[len(H.R.PREFIX + key + '_'):].split('_LOD')[0]
            envelope, basis = state_envelope(body, profile, state, root)
            row = C.composition_report(col, envelope, budget['cap_guaranteed_native_maximum_triangles'])
            row['envelope_basis'] = basis
            row['triangle_cap_scope'] = 'Actual generated source composition only; uncounted retained native extras are not assumed to be zero.'
            row['compound_budget_qualified'] = False
            row['mesh_checks'] = [C.mesh_report(o) for o in meshes(col)]
            for ob, check in zip(meshes(col), row['mesh_checks']):
                if any(not math.isfinite(v) for vertex in ob.data.vertices for v in vertex.co):
                    check['errors'].append('nonfinite mesh coordinate')
                if ob.get('retained_native_dependency') and hasattr(H,'qualify_native_mesh'):
                    try:
                        qualification=H.qualify_native_mesh(ob)
                        check['native_mesh_adapter']=qualification
                        if not qualification.get('passed'):
                            check['errors'].append('explicit native mesh adapter failed')
                    except Exception as exc:
                        check['errors'].append('native source mesh qualification: '+str(exc))
                if ob.modifiers:
                    adapter = getattr(H, 'qualify_native_modifier', None)
                    if adapter is None:
                        check['errors'].append('unapplied modifier requires an explicit evaluated/native adapter')
                    else:
                        try:
                            qualification = adapter(ob)
                            check['native_modifier_adapter'] = qualification
                            if not qualification.get('passed'):
                                check['errors'].append('explicit native modifier adapter failed')
                        except Exception as exc:
                            check['errors'].append('native modifier qualification: ' + str(exc))
                check['passed'] = not check['errors']
            if not row['passed'] or any(not r['passed'] for r in row['mesh_checks']):
                errors.append({'body': key, 'composition': name, 'bounds_or_cap': row['errors'], 'mesh_errors': [r for r in row['mesh_checks'] if not r['passed']]})
            compositions[name] = {'body': key, 'state': state, 'parts': [part_record(o) for o in sorted(meshes(col), key=lambda o: o.name)]}
            rows.append(row)
        def coll(state, lod=0):
            return bpy.data.collections.get(H.R.PREFIX + key + '_' + state + '_LOD' + str(lod))
        healthy = coll('healthy')
        if healthy is None or any(coll(s, l) is None for s in S.STATES for l in (0, 1, 2)):
            continue
        for ob in meshes(healthy):
            if ob.get('construction_stage') not in STAGES:
                errors.append({'body': key, 'missing_or_invalid_construction_stage': ob.name})
            if ob.get('role') in ('architecture', 'roofs') and not ob.get('structural_group'):
                errors.append({'body': key, 'major_structure_without_group': ob.name})
        bearing_checks = []
        for suffix in ['healthy_LOD0'] + ['construct_' + stage for stage in STAGES]:
            col = bpy.data.collections.get(H.R.PREFIX + key + '_' + suffix)
            if col is None:
                continue
            lookup = {identity(o): o for o in meshes(col)}
            for contract in contacts[key]:
                a, b = contract['a'] in lookup, contract['b'] in lookup
                # Vertical bearings carry gravity. Horizontal adjacency alone
                # never establishes which member supports the other.
                axis = contract.get('axis', 'bottom-top')
                if axis in ('bottom-top', 'top-bottom'):
                    dependent_present = a if axis == 'bottom-top' else b
                    support_present = b if axis == 'bottom-top' else a
                    if dependent_present and not support_present:
                        errors.append({'body': key, 'assembly': suffix, 'missing_bearing_support': contract})
                if a and b:
                    check = C.contact_report(remap_contact(contract, lookup)); check['assembly'] = suffix
                    bearing_checks.append(check)
                    if not check['passed']:
                        errors.append({'body': key, 'contact': check})
            for contract in interfaces[key]:
                if contract['a'] in lookup and contract['b'] in lookup:
                    check = C.interface_report(remap_contact(contract, lookup)); check['assembly'] = suffix
                    bearing_checks.append(check)
                    if not check['passed']:
                        errors.append({'body': key, 'interface': check})
        finish = bpy.data.collections.get(H.R.PREFIX + key + '_construct_finish')
        if finish is None or collection_map(finish) != collection_map(healthy):
            errors.append({'body': key, 'construction_finish_not_exact_healthy': True})
        for lod in (0, 1, 2):
            wanted = collection_map(coll('healthy', lod))
            if collection_map(coll('preview', lod)) != wanted:
                errors.append({'body': key, 'preview_differs_from_healthy_lod': lod})
            wanted = {n: v for n, v in wanted.items() if not any(t in n for t in profile['targeting_omit_name_fragments'])}
            if collection_map(coll('targeting', lod)) != wanted:
                errors.append({'body': key, 'targeting_differs_from_mapped_omissions_lod': lod})
        progression = []
        previous = collection_map(healthy, geometry=True, architecture=True)
        for level in range(1, 6):
            now = collection_map(coll('damage_' + str(level)), geometry=True, architecture=True)
            changed = sorted(n for n in set(previous) | set(now) if previous.get(n) != now.get(n))
            progression.append({'level': level, 'changed_architecture_parts': changed, 'passed': bool(changed)})
            if not changed:
                errors.append({'body': key, 'damage_level_without_architectural_progression': level})
            previous = now
        debris_checks = []
        for state in [*[f'damage_{n}' for n in range(1, 6)], 'ruins']:
            frame = Matrix(H.ANCHORS[key]['source_checkpoint_frame']['authored_to_resource_matrix'])
            ground = profile['ruins' if state == 'ruins' else 'damage']['debris_ground_z']
            resource_ground = (frame @ Vector((0, 0, ground))).z
            debris = [o for o in meshes(coll(state)) if o.get('role') == 'debris']
            grounded=[];support_checks=[]
            for ob in debris:
                low,high=C.bounds(ob);support_name=ob.get('ground_support_healthy_source')
                if not support_name:
                    grounded.append(abs(low[2]-resource_ground)<=.02);continue
                supports=[o for o in meshes(coll(state)) if identity(o)==support_name and o.get('role')=='ground']
                valid=False;gap=None
                if len(supports)==1:
                    slo,shi=C.bounds(supports[0]);gap=low[2]-shi[2]
                    valid=abs(gap)<=.004 and all(low[i]>=slo[i]-.004 and high[i]<=shi[i]+.004 for i in (0,1))
                support_checks.append({'object':ob.name,'named_surviving_support':support_name,'matching_supports':len(supports),'actual_gap':gap,'passed':valid})
                grounded.append(valid)
            check = {'state': state, 'debris_count': len(debris), 'resource_ground_z': resource_ground, 'named_support_checks':support_checks,'passed': bool(debris) and all(grounded)}
            debris_checks.append(check)
            if not check['passed']:
                errors.append({'body': key, 'missing_or_ungrounded_debris': check})
        lod_checks = []
        for state in S.STATES:
            base = C.composition_report(coll(state)); base_arch = [o for o in meshes(coll(state)) if o.get('role') in ('architecture', 'roofs')]
            for lod, target in ((1, .5), (2, .25)):
                reduced = coll(state, lod); ratio = C.triangles(meshes(reduced)) / max(1, base['triangles'])
                arch = [o for o in meshes(reduced) if o.get('role') in ('architecture', 'roofs')]
                groups = {o.get('structural_group') for o in base_arch if o.get('structural_group')}
                retained = {o.get('structural_group') for o in arch if o.get('structural_group')}
                sizes = []
                for obs in (base_arch, arch):
                    pts = [p for o in obs for p in C.world_points(o)]
                    sizes.append([max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)] if pts else [0, 0, 0])
                silhouette = bool(arch) and groups <= retained and all(a > 1e-5 and .85 <= b / a <= 1.05 for a, b in zip(*sizes))
                passed = abs(ratio - target) <= .1000001 and silhouette
                check = {'state': state, 'lod': lod, 'actual_ratio': ratio, 'target': target, 'tolerance': .10, 'structural_groups_and_bounds_preserved': silhouette, 'visual_readability_review': 'required; structural bounds/groups are a fail-closed proxy, not a visual acceptance claim', 'passed': passed}
                lod_checks.append(check)
                if not passed:
                    errors.append({'body': key, 'lod_needs_authored_reduction_or_readability_repair': check})
        reports.append({'body': key, 'compositions': rows, 'resource_bearing_checks': bearing_checks, 'damage_progression': progression, 'debris_grounding': debris_checks, 'lod_checks': lod_checks,
                        'native_model_sha256': body['native_model_sha256'], 'source_uses': body['source_uses'], 'native_lifecycle_values': body['actual_geometry_lifecycle_values']})
    texture_rows = texture_checks(H, root)
    if any(not row['passed'] for row in texture_rows):
        errors.append({'invalid_atlas_resolution': texture_rows})
    return {'passed': not errors, 'errors': errors, 'bodies': reports, 'textures': texture_rows,
            'triangle_cap_scope': 'Generated source geometry only', 'compound_budget_qualified': False,
            'declared_native_dependency_models': sorted(native.get('mechanism_dependencies', {})),
            'compound_budget_pending': 'Acceptance requires exact simultaneously visible dependency quantities/states represented in the inspectable source manifest and counted against the stock compound cap. Neither absent geometry nor a deferred native gate proves zero overhead.'}, compositions


def generate(root):
    family, native, profiles, keys = source_contracts(root)
    H = load_recipe(root)
    contacts, interfaces, authored_reports = {}, {}, []
    for key in keys:
        H.build_body(key)
        contacts[key] = [dict(c) for c in H.CONTRACTS if c['body'] == key]
        interfaces[key] = [dict(c) for c in H.ANCHORS[key].get('numerical_interfaces', [])]
        rows = [C.mesh_report(o) for o in meshes(H.root(key))] + [C.contact_report(c) for c in contacts[key]] + [C.interface_report(c) for c in interfaces[key]]
        if any(not r['passed'] for r in rows):
            raise RuntimeError('Authored healthy geometry/contacts failed ' + key + ': ' + str([r for r in rows if not r['passed']][:8]))
        authored_reports.append({'body': key, 'checks': rows})
        S.build(H, key, profiles['bodies'][key])
        frame = native_frame(H.ANCHORS[key], native['bodies'][key])
        apply_frame(H, key, frame)
        contacts[key] = [project_contact(c, frame) for c in contacts[key]]
        for c in interfaces[key]:
            c['authored_contact_point'] = list(frame @ Vector(c['authored_contact_point']))
        print('SOURCE_FAMILY_BODY', root.name, key, flush=True)
    report, compositions = assess(H, root, native, profiles, keys, contacts, interfaces)
    report['authored_frame_checks'] = authored_reports
    manifest = {'schema': 'persia-family-source-state-manifest/1', 'family': root.name, 'source_art_only': True,
        'expected_body_keys': keys, 'expected_compositions_per_body': 31, 'native_hp_thresholds': None,
        'native_construction_wiring': 'Deferred; four source assembly stages are not native progress thresholds.',
        'digest_method': 'Q5 canonical oriented polygon surfaces and every UV layer; world geometry and matrix also retained. Winding, duplicate counts and identity matter.',
        'resource_contact_contracts': contacts, 'resource_interface_contracts': interfaces, 'source_anchors': H.ANCHORS,
        'native_source_uses': {k: native['bodies'][k]['source_uses'] for k in keys},
        'native_lifecycle_values': {k: native['bodies'][k]['actual_geometry_lifecycle_values'] for k in keys},
        'compositions': compositions, 'compound_budget_qualified': False,
        'declared_native_dependency_models': sorted(native.get('mechanism_dependencies', {})),
        'triangle_cap_scope': 'Generated source geometry only; complete visible dependency count remains an acceptance requirement.', 'native_gates': NATIVE_GATES}
    return H, report, manifest


def master_guard(root):
    master = root / (root.name + '.blend')
    current = sha(master) if master.exists() else None
    if current:
        receipts = [root / 'evidence' / n for n in ('healthy-build-receipt.json', 'build-receipt.json')]
        rows = [json.loads(p.read_text()) for p in receipts if p.exists()]
        known = [r.get('saved_file_sha256') for r in rows if r.get('passed') or r.get('healthy_checkpoint_passed')]
        if current not in known:
            raise RuntimeError('Manual/external master edit detected; preserve and reconcile before rebuilding')
    return master, current


def main(slug, probe=False):
    factory_guard()
    root = family_root(slug)
    master, before = master_guard(root)
    pinned = fingerprints(root)
    H, report, manifest = generate(root)
    report.update({'family': slug, 'complete_compositions': len(manifest['compositions']), 'geometry_input_sha256': pinned, 'native_gates': NATIVE_GATES, 'family_accepted': False, 'visual_review_required': 'All healthy bodies, state/LOD coverage, compound dependencies and the task rubric require actual rendered critique after source checks.'})
    if report['complete_compositions'] != 31 * len(manifest['expected_body_keys']):
        report['passed'] = False; report['errors'].append('Expected exactly 31 compositions per native body')
    write(root / 'evidence/full-source-checks.json', report)
    if not report['passed']:
        raise RuntimeError('Source checks failed; no master saved: ' + str(report['errors'][:8]))
    if fingerprints(root) != pinned or (sha(master) if master.exists() else None) != before:
        raise RuntimeError('Retained input/master changed during generation; save aborted')
    if probe:
        print('FULL_SOURCE_UNSAVED_PROBE_PASS', slug, report['complete_compositions'], flush=True)
        return report
    H.write_anchors(); H.show(manifest['expected_body_keys'][0])
    for image in bpy.data.images:
        if image.name.startswith(H.R.PREFIX):
            image.filepath = '//textures/' + Path(image.filepath).name
    # Check again immediately before the only saved-master mutation.
    if fingerprints(root) != pinned or (sha(master) if master.exists() else None) != before:
        raise RuntimeError('Retained input/master changed before save; save aborted')
    H.R.save()
    manifest['saved_file_sha256'] = sha(master)
    manifest['geometry_input_sha256'] = pinned
    write(root / 'state-manifest.json', manifest)
    report.update({'saved_file_sha256': sha(master), 'state_manifest_sha256': sha(root / 'state-manifest.json')})
    write(root / 'evidence/build-receipt.json', report)
    print('FULL_SOURCE_SAVED', slug, report['complete_compositions'], flush=True)
    return report


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    try:
        if not args: raise ValueError('Expected family slug')
        main(args[0], '--probe' in args)
    except Exception:
        if args and re.fullmatch(r'[a-z][a-z0-9_]*', args[0]) and (ART / args[0] / 'evidence').is_dir():
            (ART / args[0] / 'evidence/full-build-error.txt').write_text(traceback.format_exc())
        raise
