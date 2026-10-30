"""Bounded native source-mechanism inspection, for the parent's Blender session.

This module has NO import-time Blender operations, decode, save, cleanup or clip
creation. Functions are deliberately separate: catalog -> inspect_import_api ->
project_cached -> audit_import -> optional rigid_source_views -> pose_probe.

If cache hydration fails, use the actual installed public UI operators:
  bpy.ops.garrison.place_game_asset(asset_id=<card on current library page>)
  bpy.ops.garrison.decode_selected_static()
Record only the new import's IDs, then tag_public_import and audit it. These UI
operators may run a selective decode; this module never calls them or triggers it.

The installed public UI calls an internal compiled adapter. Its exact observed
call is _apply_decoded_static(proxy, complete_plan, create_controls=True). Cache
hydration of a bare owned Empty is an UNEXECUTED adapter probe, not a stable API
promise. No wrapper here overrides an importer failure or invents skin weights.
"""
from pathlib import Path
import hashlib
import inspect
import json
import math
import os
import sys
from collections import Counter

BUILDINGS = Path(__file__).resolve().parents[1]
TEMP = BUILDINGS.parents[2]
INVENTORY = TEMP / 'research/persia_buildings/inventory'
EXTENSION = Path(os.environ['APPDATA']) / 'Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'
CORE = EXTENSION / 'bin/core/garrison-core.exe'
KIT = Path(os.environ['LOCALAPPDATA']) / 'Garrison/Kit'
PREFIX = 'NSRC_'
TARGETS = {
    'mill': 'art/civilizations/chinese/structures/gristmill/chi_gristmill_control_age01/chi_gristmill_control_age01.rgm',
    'lumber_crane': 'art/civilizations/common/structures/lumber_camp/com_lumber_camp_crane_age01/com_lumber_camp_crane_age01.rgm',
    'mining_lift': 'art/civilizations/common/structures/mining_camp/com_mining_camp_combined/com_mining_camp_combined.rgm',
    'tc_bell_1': 'art/civilizations/mongols/structures/towncenter/mon_towncenter_bellarch_age01/mon_towncenter_bellarch_age01.rgm',
    'tc_bell_2': 'art/civilizations/mongols/structures/towncenter/mon_towncenter_bellarch_age02/mon_towncenter_bellarch_age02.rgm',
    'outpost_wood': 'art/civilizations/sultanate/structures/outpost/sul_outpost_control_age01/sul_outpost_control_age01.rgm',
    'outpost_fortified': 'art/civilizations/sultanate/structures/outpost/sul_outpost_control_age01_upgrade_stone/sul_outpost_control_age01_upgrade_stone.rgm',
    'outpost_cannon_child': 'art/civilizations/common/weapons/ranged/cannon_tower/cannon_tower.rgm',
    'blacksmith_layout': 'art/civilizations/common/layouts/archetypes/layout_blacksmith/layout_blacksmith.rgm',
    'blacksmith_bellows': 'art/civilizations/common/props/bellows/bellows.rgm',
}
CACHE_ROOTS = (
    INVENTORY / 'decode',
    TEMP / 'art/persia/gundeshapur/evidence/stock/decode',
    TEMP / 'research/persia_castle/evidence/stock/decode',
    TEMP / 'research/persia_imperial/evidence/stock/decode',
)


def _read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def _model(target):
    value = TARGETS.get(target, target)
    if value not in TARGETS.values():
        raise ValueError('Not an explicitly bounded mechanism target: ' + str(target))
    return value


def _bindings(model):
    rows = _read(INVENTORY / 'RIGID_MECHANISM_BINDINGS.json')['models']
    if model not in rows:
        raise RuntimeError('No qualified MSCL/SKLN binding inventory for this target; do not invent a rig')
    row = rows[model]
    if row.get('MSCL') and not row['MSCL'].get('valid_complete_binding_header_inventory'):
        raise RuntimeError('MSCL inventory quarantined; no usable partial records')
    return row


def _assert_plan_fingerprint(plan, binding):
    model_sha = (plan.get('skeleton') or {}).get('source_sha256')
    geometry_sha = plan.get('resources', {}).get('geometry', {}).get('sha256')
    if model_sha != binding['native_rgm_sha256']:
        raise RuntimeError('Public plan RGM hash does not match retained source binding inventory')
    expected_geometry = binding.get('native_rrgeom_sha256')
    if expected_geometry and geometry_sha != expected_geometry:
        raise RuntimeError('Public plan RRGeom hash does not match retained geometry snapshot')


def retained_plan(target, manifest_path=None):
    """Read only an exact retained public manifest; never run a decoder."""
    model = _model(target)
    token = hashlib.sha1(model.encode()).hexdigest()[:12]
    paths = [Path(manifest_path)] if manifest_path else [
        f for root in CACHE_ROOTS if (root / token).exists()
        for f in (root / token).rglob('decoded-static.json')]
    found = []
    for path in paths:
        data = _read(path)
        if data.get('provider_contract', {}).get('model', {}).get('logical_path', '').lower() == model:
            found.append((path, data))
    if len(found) != 1:
        raise RuntimeError('Need exactly one matching public plan; found ' + str(len(found)) +
                           '. Supply manifest_path explicitly or run one bounded decode later.')
    path, data = found[0]
    data['manifest_path'] = str(path.resolve())
    return data


def decode_command(target, output_root=None, animation_owner=None):
    """Return argv only. Installed CLI has NO skip-textures/geometry-only flag.

    Whole parent attachment decodes are unnecessary. Use one precise RGM, then
    reuse its content-addressed manifest. animation_owner must be an independently
    confirmed exact AttachmentList owner; leave it unset for reference-pose work.
    """
    model = _model(target)
    if target == 'blacksmith_layout' or model == TARGETS['blacksmith_layout']:
        raise RuntimeError('Layout-only model has no same-stem geometry; identify an actual moving dependency first')
    output = Path(output_root) if output_root else INVENTORY / 'decode' / hashlib.sha1(model.encode()).hexdigest()[:12]
    if not output.resolve().is_relative_to(TEMP.resolve()):
        raise ValueError('Decode output must remain inside the approved temporary workspace')
    argv = [str(CORE), 'convert', 'decode-static', '--logical-path', model,
            '--config', str(KIT / 'game-assets.local.json'), '--index', str(KIT / 'game-assets.sqlite3'),
            '--output-root', str(output)]
    if animation_owner is not None:
        argv.extend(['--animation-owner', str(animation_owner)])
    return argv


def catalog():
    """Cheap retained-input inventory, suitable outside Blender."""
    rig = _read(INVENTORY / 'RIGID_MECHANISM_BINDINGS.json')['models']
    geo = _read(INVENTORY / 'geometry-only-models.json')
    result = []
    for key, model in TARGETS.items():
        r, g = rig.get(model, {}), geo.get(model, {})
        try:
            plan = retained_plan(key)
            manifest, error = plan['manifest_path'], None
        except Exception as exc:
            manifest, error = None, str(exc)
        result.append(dict(target=key, model=model, manifest_path=manifest,
            cache_error=error, retained_native_rgm=g.get('native_rgm') or r.get('native_rgm_local_path'),
            qualified_binding_inventory=bool(r),
            bound_MSCL_sources=sum(bool(x.get('native_parent_bone'))
                for x in r.get('MSCL', {}).get('source_records', [])),
            notes=('One-bone layout is not evidence of an operating forge mechanism; no invented blocker/clip.'
                   if key == 'blacksmith_layout' else
                   'Retain original hierarchy/owners. Bone presence alone does not prove an operating clip.')))
    return result


def _projection_module():
    matches = [m for name, m in sys.modules.items()
               if (name == 'garrison.decode_projection' or name.endswith('.garrison.decode_projection')) and m is not None]
    if len(matches) != 1:
        raise RuntimeError('Expected one already loaded Garrison decode_projection module. Enable the installed extension; no guessed compiled import.')
    return matches[0]


def inspect_import_api():
    """Bounded metadata introspection; no pyd enumeration/reverse engineering."""
    module = _projection_module()
    result = {'module_file': str(getattr(module, '__file__', '')), 'callables': {}}
    for name in ('_apply_decoded_static', '_decoded_armature_bones'):
        fn = getattr(module, name, None)
        if fn is None:
            result['callables'][name] = {'present': False}
            continue
        try:
            signature = str(inspect.signature(fn))
        except (TypeError, ValueError) as exc:
            signature = 'Unavailable: ' + str(exc)
        result['callables'][name] = dict(present=True, signature=signature,
                                          doc=(inspect.getdoc(fn) or '')[:2500])
    result['observed_UI_call'] = '_apply_decoded_static(proxy, complete_plan, create_controls=True)'
    result['standalone_cache_hydration_qualified'] = False
    return result


def inspect_decoded_armature_bones(target, manifest_path=None):
    """Read-only call of the installed public reference-bone projector.

    Exact exposed signature confirmed by parent's actual probe:
    _decoded_armature_bones(skeleton: dict) -> list[dict]. No armature, scene,
    pose or weights are created. Preserve full bounded output for schema review.
    """
    plan = retained_plan(target, manifest_path)
    skeleton = plan.get('skeleton') or {}
    if int(skeleton.get('bone_count', 0)) > 256:
        raise RuntimeError('Outside bounded mechanism bone inspection')
    fn = getattr(_projection_module(), '_decoded_armature_bones', None)
    if not callable(fn):
        raise RuntimeError('Installed public bone projector unavailable')
    projected = fn(skeleton)
    def serial(value, depth=0):
        if depth > 10:
            raise RuntimeError('Unexpected projector result nesting')
        if value is None or isinstance(value, (str, bool, int, float)):
            return value
        if isinstance(value, dict):
            return {str(k): serial(v, depth + 1) for k, v in value.items()}
        try:
            items = list(value)
        except TypeError:
            return {'unserialized_type': type(value).__name__, 'repr': repr(value)[:500]}
        if len(items) > 1024:
            raise RuntimeError('Unexpected unbounded projector result')
        return [serial(v, depth + 1) for v in items]
    return dict(model=_model(target), public_projector_return_type=type(projected).__name__,
        public_projector_bones=serial(projected), native_skeleton_bone_count=skeleton.get('bone_count'),
        manifest_rest_pose=skeleton.get('rest_pose'),
        manifest_deform_layer=plan.get('animated_asset_import_plan', {}).get('layers', {}).get('deform'),
        manifest_rig_projection=plan.get('rig_projection'),
        standalone_armature_creation_qualified=False, native_world_pose_qualified=False)


def project_cached(target, manifest_path=None, collection_name=None):
    """Parent-only Blender mutation: project ONE cached model in an owned collection.

    Creates an identity proxy and calls the actual UI adapter. Keeps failures for
    inspection rather than deleting them. Does not touch/save existing sources.
    Importer may load the retained plan's materials/media; no decoder is invoked.
    """
    import bpy
    model = _model(target)
    plan = retained_plan(target, manifest_path)
    # Verify unchanged original native inputs where qualified snapshots exist.
    try:
        bindings = _bindings(model)
    except RuntimeError:
        bindings = None
    if bindings:
        _assert_plan_fingerprint(plan, bindings)
        for field in ('rgm', 'rrgeom'):
            path, expected = bindings.get('native_' + field + '_local_path'), bindings.get('native_' + field + '_sha256')
            if path and (not Path(path).is_file() or _sha(path) != expected):
                raise RuntimeError('Retained native input hash mismatch: ' + str(path))
    fn = getattr(_projection_module(), '_apply_decoded_static', None)
    if not callable(fn):
        raise RuntimeError('Installed UI projection adapter is unavailable')
    label = next(k for k, value in TARGETS.items() if value == model)
    name = collection_name or PREFIX + label
    if not name.startswith(PREFIX) or bpy.data.collections.get(name):
        raise ValueError('Require a new NSRC_ inspection collection; existing work is never reset')
    owner = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(owner)
    proxy = bpy.data.objects.new(name + '_Proxy', None)
    owner.objects.link(proxy)
    proxy_name = proxy.name
    owner_name = owner.name
    resource = plan.get('resources', {}).get('reference', {})
    for key, value in {
        'garrison_logical_path': model, 'garrison_source_card_path': model,
        'garrison_archive_path': resource.get('archive_path', ''), 'garrison_asset_kind': 'model',
        'garrison_source_asset_kind': 'model', 'garrison_display_name': model.rsplit('/', 1)[-1],
        'garrison_conversion_status': 'decoding', 'native_probe_scope': 'Raw source/reference inspection; all native state alternatives may be present',
    }.items():
        proxy[key] = value
    # The actual adapter may delete/replace the proxy. Never retain RNA handles
    # for post-call bookkeeping or restoration.
    before_pointers = {o.as_pointer() for o in bpy.data.objects}
    selection_names = [o.name for o in bpy.context.selected_objects]
    active_object = bpy.context.view_layer.objects.active
    active_name = active_object.name if active_object else None
    try:
        for selected_name in selection_names:
            selected = bpy.data.objects.get(selected_name)
            if selected is not None:
                selected.select_set(False)
        proxy.select_set(True)
        bpy.context.view_layer.objects.active = proxy
        # Exactly the call shape used by installed game_library._finish_decode.
        returned = fn(proxy, plan, create_controls=True)
        created = [o for o in bpy.data.objects if o.as_pointer() not in before_pointers]
        surviving_proxy = bpy.data.objects.get(proxy_name)
        if surviving_proxy is not None and all(o.as_pointer() != surviving_proxy.as_pointer() for o in created):
            created.insert(0, surviving_proxy)
        for o in created:
            o['native_probe_model'] = model
            o['native_probe_manifest'] = plan['manifest_path']
            o['native_probe_manifest_sha256'] = _sha(plan['manifest_path'])
            o['native_probe_owner'] = name
        return dict(model=model, collection=name, object_names=[o.name for o in created],
                    adapter_return_type=type(returned).__name__, adapter_return=repr(returned)[:1500],
                    source_pose_qualified=False)
    except Exception as exc:
        surviving_owner = bpy.data.collections.get(owner_name)
        if surviving_owner is not None:
            surviving_owner['native_probe_failure'] = str(exc)
            surviving_owner['native_probe_original_proxy_name'] = proxy_name
        raise
    finally:
        current_selection_names = [o.name for o in bpy.context.selected_objects]
        for selected_name in current_selection_names:
            selected = bpy.data.objects.get(selected_name)
            if selected is not None:
                selected.select_set(False)
        for selected_name in selection_names:
            selected = bpy.data.objects.get(selected_name)
            if selected is not None and bpy.context.view_layer.objects.get(selected_name) is not None:
                selected.select_set(True)
        restored_active = bpy.data.objects.get(active_name) if active_name else None
        if restored_active is not None and bpy.context.view_layer.objects.get(active_name) is not None:
            bpy.context.view_layer.objects.active = restored_active
        elif active_name is None:
            bpy.context.view_layer.objects.active = None


def _owned_objects(names):
    import bpy
    objects = [bpy.data.objects[n] for n in names]
    if not objects or any(not o.get('native_probe_owner', '').startswith(PREFIX) for o in objects):
        raise ValueError('Only explicitly owned NSRC_ imported objects may be inspected/mutated')
    return objects


def tag_public_import(target, newly_imported_object_names, owner_name):
    """Tag an explicitly selected NEW public-UI import for the same audit path.

    Parent must capture IDs created by its one public import. No mesh, parenting,
    selection or source metadata is changed here, and no geometry is inferred.
    """
    import bpy
    model = _model(target)
    if not owner_name.startswith(PREFIX):
        raise ValueError('Require an explicit NSRC_ evidence owner')
    objects = [bpy.data.objects[n] for n in newly_imported_object_names]
    if not any(o.get('garrison_logical_path', '').lower() == model for o in objects):
        raise ValueError('No exact public logical-path identity on the supplied new import')
    if any(o.get('native_probe_owner') not in (None, '', owner_name) for o in objects):
        raise ValueError('A supplied object already belongs to another probe')
    for o in objects:
        o['native_probe_owner'] = owner_name
        o['native_probe_model'] = model
    return [o.name for o in objects]


def audit_import(target, object_names, manifest_path=None):
    """Describe actual imported hierarchy/weights; never infer binding from counts."""
    model, rows = _model(target), []
    objects = _owned_objects(object_names)
    try:
        binding = _bindings(model)
    except RuntimeError:
        binding = None
    expected = [x for x in binding.get('MSCL', {}).get('source_records', [])
                if x.get('native_parent_bone')] if binding else []
    sources = {x['source_name']: x['native_parent_bone'] for x in expected}
    joins = {name: [] for name in sources}
    for o in objects:
        values = {str(o[k]) for k in o.keys() if isinstance(o[k], str)}
        for name in sources:
            if o.name == name or name in values:
                joins[name].append(o)
        row = dict(name=o.name, type=o.type, parent=o.parent.name if o.parent else None,
                   parent_type=o.parent_type, parent_bone=o.parent_bone,
                   matrix_local=[list(x) for x in o.matrix_local],
                   matrix_world_in_Blender_probe=[list(x) for x in o.matrix_world],
                   custom_property_names=list(o.keys()))
        row['bounded_garrison_projection_properties'] = {
            k: (o[k] if isinstance(o[k], (str, bool, int, float)) else str(o[k])[:1200])
            for k in o.keys() if k.startswith(('garrison_skipped_', 'garrison_rig_',
                'garrison_skin_', 'garrison_skeleton_', 'garrison_deform_',
                'garrison_animation_', 'garrison_conversion_'))}
        if o.type == 'ARMATURE':
            row['bones'] = [dict(name=b.name, parent=b.parent.name if b.parent else None,
                                matrix_local=[list(x) for x in b.matrix_local]) for b in o.data.bones]
        elif o.type == 'MESH':
            row['vertex_count'] = len(o.data.vertices)
            row['named_vertex_groups'] = [g.name for g in o.vertex_groups]
            row['weighted_vertex_count'] = sum(any(g.weight > 0 for g in v.groups) for v in o.data.vertices)
            row['armature_modifiers'] = [dict(name=m.name, armature=m.object.name if m.object else None)
                                        for m in o.modifiers if m.type == 'ARMATURE']
        rows.append(row)
    associations = []
    for name, bone in sources.items():
        matches = joins[name]
        direct = bool(matches) and all(o.parent and o.parent.type == 'ARMATURE' and
            o.parent_type == 'BONE' and o.parent_bone == bone for o in matches)
        associations.append(dict(source=name, expected_parent_bone=bone,
            exact_source_identity_matches=[o.name for o in matches],
            direct_native_bone_parent_confirmed=direct,
            status='Direct binding observed; pose/reference comparison still required' if direct else
                   'Unresolved source-node association; do not claim missing weights imply missing rigid binding'))
    return dict(model=model, actual_objects=rows, native_bound_source_audit=associations,
                world_pose_qualified=False, source_pose_qualified=False,
                no_skin_weights_is_not_itself_a_failure=True,
                skin_palette_contract=retained_plan(target, manifest_path).get('rig_palette_binding'))


def compare_public_reference_geometry(target, object_names, manifest_path=None, tolerance=.00001):
    """Exact quantized triangle multiset comparison in the owned Blender probe.

    Parent should pass only imported native source meshes, excluding control
    shapes. Report additional/missing triangles instead of silently ignoring them.
    UVs/normals/materials, poses and physical pivots remain separate checks.
    """
    import bpy
    objects = _owned_objects(object_names)
    plan = retained_plan(target, manifest_path)
    def point(p):
        return tuple(round(float(x) / tolerance) for x in p)
    def triangle(points):
        return tuple(sorted(point(p) for p in points))
    expected = Counter()
    projectable = Counter()
    repeated_index_faces = 0
    for g in plan['geometry']['groups']:
        for tri in g['triangles']:
            key = triangle(g['positions'][i] for i in tri)
            expected[key] += 1
            if len(set(tri)) < 3:
                repeated_index_faces += 1
            else:
                projectable[key] += 1
    actual = Counter()
    deps = bpy.context.evaluated_depsgraph_get()
    for o in objects:
        if o.type != 'MESH':
            continue
        evaluated = o.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            for tri in mesh.loop_triangles:
                actual[triangle(evaluated.matrix_world @ mesh.vertices[i].co for i in tri.vertices)] += 1
        finally:
            evaluated.to_mesh_clear()
    missing, additional = expected - actual, actual - expected
    projection_missing, projection_additional = projectable - actual, actual - projectable
    return dict(model=_model(target), coordinate_frame='Identity-placed Blender reference probe; not native world',
        quantization_metres=tolerance, expected_triangles=sum(expected.values()),
        imported_triangles=sum(actual.values()), missing_triangles=sum(missing.values()),
        additional_triangles=sum(additional.values()), exact_quantized_reference_match=not missing and not additional,
        raw_repeated_vertex_index_faces=repeated_index_faces,
        expected_triangles_after_repeated_index_filter=sum(projectable.values()),
        missing_nonrepeated_index_triangles=sum(projection_missing.values()),
        additional_against_repeated_index_filter=sum(projection_additional.values()),
        exact_projectable_reference_match=not projection_missing and not projection_additional,
        projection_filter_scope='Only repeated vertex INDEX faces excluded. Zero-area/coincident-position faces with distinct indices remain expected. Original raw manifest retained.',
        source_pose_qualified=False)


def _source_fragments(plan, binding):
    """Exact collection-local membership join. Refuse mixed/ambiguous triangles."""
    records = binding.get('MSCL', {}).get('source_records', [])
    if not records or not binding['MSCL'].get('valid_complete_binding_header_inventory'):
        raise RuntimeError('No complete usable MSCL source inventory')
    groups = plan.get('geometry', {}).get('groups', [])
    maps = plan.get('structure_collection_contract', {}).get('maps', [])
    if sum(int(m['geometry_group_span']) for m in maps) != len(groups):
        raise RuntimeError('Public geometry group spans do not join exact collection maps')
    cursor = 0
    for mapping in maps:
        source_to_local = mapping['source_to_local_bone']
        if len(source_to_local) != len(records):
            raise RuntimeError('Collection map/source count mismatch')
        inverse = {}
        for source_index, local in enumerate(source_to_local):
            if local >= 0:
                if local in inverse:
                    raise RuntimeError('Ambiguous collection-local source index')
                inverse[local] = source_index
        count = int(mapping['geometry_group_span'])
        for group in groups[cursor:cursor + count]:
            if group.get('skin_indices') or group.get('skin_weights'):
                raise RuntimeError('This group has native vertex skin; retain/import exact palette/weights separately, never replace with rigid weights')
            local_ids = group.get('collection_bone_indices', [])
            if len(local_ids) != len(group['positions']):
                raise RuntimeError('Collection vertex membership missing')
            buckets = {}
            for tri in group['triangles']:
                ids = {local_ids[i] for i in tri}
                if len(ids) != 1 or next(iter(ids)) not in inverse:
                    raise RuntimeError('Mixed or unresolved native source triangle')
                source_index = inverse[next(iter(ids))]
                buckets.setdefault(source_index, []).append(tri)
            for source_index, triangles in buckets.items():
                used = sorted({i for t in triangles for i in t})
                remap = {old: new for new, old in enumerate(used)}
                yield records[source_index], group, used, [[remap[i] for i in t] for t in triangles]
        cursor += count


def reference_projection_contract(target, manifest_path=None, tolerance=.00001):
    """Pure-data preflight for an exact, bounded reference-only skeleton.

    Requires complete native SKLN records, complete MSCL binding headers, every
    nonempty source parent resolved, and ALL inverse-reference checks recomputed.
    No operator, guessed bone length, skin weight or runtime pivot is involved.
    """
    model = _model(target)
    binding = _bindings(model)
    plan = retained_plan(target, manifest_path)
    _assert_plan_fingerprint(plan, binding)
    for kind in ('rgm', 'rrgeom'):
        path = binding.get('native_' + kind + '_local_path')
        expected = binding.get('native_' + kind + '_sha256')
        if path and (not Path(path).is_file() or _sha(path) != expected):
            raise RuntimeError('Native input changed before reference projection: ' + str(path))
    skln, mscl = binding.get('SKLN', {}), binding.get('MSCL', {})
    bones, sources = skln.get('bones', []), mscl.get('source_records', [])
    if not skln.get('valid_complete_parse') or not skln.get('payload_bytes_fully_accounted'):
        raise RuntimeError('Complete byte-accounted SKLN reference inventory required')
    if not 0 < len(bones) <= 256 or len(bones) != skln.get('bone_count'):
        raise RuntimeError('Missing or out-of-bounds native bone count')
    if [b.get('index') for b in bones] != list(range(len(bones))):
        raise RuntimeError('Native SKLN indices must be exact and complete')
    if len({b['name'] for b in bones}) != len(bones):
        raise RuntimeError('Duplicate native bone names')
    if not mscl.get('valid_complete_binding_header_inventory') or len(sources) != mscl.get('source_object_count'):
        raise RuntimeError('Complete MSCL header inventory required')
    if not all(s.get('valid_complete_binding_header') for s in sources):
        raise RuntimeError('Quarantined/partial MSCL header prevents reference armature creation')
    bound = [s for s in sources if s.get('native_parent_bone')]
    if not bound or not mscl.get('bound_headers_inverse_reference_crosscheck_passed'):
        raise RuntimeError('Nonempty, fully crosschecked native rigid parent references required')

    def matrix(value):
        if len(value) != 4 or any(len(row) != 4 for row in value):
            raise RuntimeError('Invalid native matrix dimensions')
        if not all(math.isfinite(float(x)) for row in value for x in row):
            raise RuntimeError('Nonfinite native reference matrix')
        return [[float(x) for x in row] for row in value]
    def multiply(a, b):
        return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]
    def error(a, b):
        return max(abs(a[r][c]-b[r][c]) for r in range(4) for c in range(4))
    def raw_trs(values):
        if len(values) != 10 or not all(math.isfinite(float(x)) for x in values):
            raise RuntimeError('Incomplete/nonfinite native TRS')
        x,y,z,w,tx,ty,tz,sx,sy,sz = values
        length = math.sqrt(x*x+y*y+z*z+w*w)
        if length < .000001:
            raise RuntimeError('Invalid native quaternion')
        x,y,z,w = (v/length for v in (x,y,z,w))
        return [[(1-2*(y*y+z*z))*sx, 2*(x*y-z*w)*sy, 2*(x*z+y*w)*sz, tx],
                [2*(x*y+z*w)*sx, (1-2*(x*x+z*z))*sy, 2*(y*z-x*w)*sz, ty],
                [2*(x*z-y*w)*sx, 2*(y*z+x*w)*sy, (1-2*(x*x+y*y))*sz, tz],
                [0,0,0,1]]
    identity = [[float(r == c) for c in range(4)] for r in range(4)]
    B = [[-1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]]
    K = [[0,1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]]
    globals_, visiting = {}, set()
    def resolve(index):
        if index in globals_:
            return globals_[index]
        if index in visiting or not 0 <= index < len(bones):
            raise RuntimeError('Invalid/cyclic native hierarchy')
        visiting.add(index)
        record = bones[index]
        if not record.get('record_fully_consumed') or not record.get('record_sha256'):
            raise RuntimeError('Incomplete native SKLN record')
        local = raw_trs(record['raw_local_reference_trs_xyzw_translation_scale'])
        if error(local, matrix(record['matrix_from_raw_TRS_row_major'])) > tolerance:
            raise RuntimeError('SKLN raw TRS/matrix disagreement')
        parent = record['parent_index']
        if parent < -1 or parent >= len(bones):
            raise RuntimeError('Invalid native parent index')
        result = local if parent == -1 else multiply(resolve(parent), local)
        if error(result, matrix(record['candidate_model_relative_global_reference_matrix_row_major'])) > tolerance:
            raise RuntimeError('Native local/global reference disagreement')
        globals_[index] = result
        visiting.remove(index)
        return result
    for index in range(len(bones)):
        resolve(index)
    by_name = {b['name']: b for b in bones}
    maximum_inverse_error = 0
    for source in bound:
        if source.get('parent_bone_resolves_in_this_SKLN') is not True or not source.get('inverse_parent_reference_crosscheck_passed'):
            raise RuntimeError('Unresolved or unqualified MSCL inverse reference')
        parent = by_name.get(source['native_parent_bone'])
        if parent is None:
            raise RuntimeError('MSCL parent is absent from exact native SKLN')
        local = raw_trs(source['raw_reference_trs_xyzw_translation_scale'])
        if error(local, matrix(source['matrix_from_raw_TRS_row_major'])) > tolerance:
            raise RuntimeError('MSCL raw TRS/matrix disagreement')
        residual = error(multiply(globals_[parent['index']], local), identity)
        maximum_inverse_error = max(maximum_inverse_error, residual)
        if residual > tolerance:
            raise RuntimeError('Native inverse-reference relation failed')
    projected = []
    for record in bones:
        expected = multiply(multiply(B, globals_[record['index']]), K)
        a,b,c = (expected[r][:3] for r in range(3))
        determinant = a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
        if abs(determinant-1) > tolerance:
            raise RuntimeError('Projected reference basis is not a proper unit bone orientation')
        for i in range(3):
            for j in range(3):
                dot = sum(expected[r][i]*expected[r][j] for r in range(3))
                if abs(dot-float(i == j)) > tolerance:
                    raise RuntimeError('Nonunit/sheared reference basis cannot be silently flattened into EditBone')
        projected.append(dict(name=record['name'], native_index=record['index'],
            parent_index=record['parent_index'],
            parent_name=None if record['parent_index'] == -1 else bones[record['parent_index']]['name'],
            expected_reference_matrix_row_major=expected,
            raw_local_reference_trs_xyzw_translation_scale=record['raw_local_reference_trs_xyzw_translation_scale'],
            SKLN_record_sha256=record['record_sha256']))
    return dict(model=model, bone_count=len(bones), bones=projected,
        native_rgm_sha256=binding['native_rgm_sha256'], SKLN_payload_sha256=skln['payload_sha256'],
        MSCL_payload_sha256=mscl['payload_sha256'], checked_bound_source_count=len(bound),
        maximum_inverse_reference_error=maximum_inverse_error,
        formula='B * native_global_reference * K; parent globals recomputed from exact raw local TRS',
        qualification='Exact native reference hierarchy and inverse-reference numeric relation; not engine physical-pivot or animation proof')


def reference_armature_views(target, collection_name=None, manifest_path=None, display_length=.16):
    """Create an editable, exact reference-only hierarchy in a NEW owned collection.

    The display tail length is an explicit visual guide, never a native bone
    length. Bones carry original raw TRS and hashes; no Actions, weights, clips,
    controls, native marker transforms or source geometry are invented. Parent
    may append returned object_names to its public-import IDs for rigid views.
    """
    contract = reference_projection_contract(target, manifest_path)
    if not .03 <= display_length <= .5:
        raise ValueError('Display-only guide tail length must be bounded and explicit')
    import bpy
    from mathutils import Matrix
    if bpy.context.mode != 'OBJECT':
        raise RuntimeError('Reference projection requires Object mode; never interrupt external edit/pose work')
    label = next(k for k, value in TARGETS.items() if value == contract['model'])
    name = collection_name or PREFIX + label + '_ReferenceHierarchy'
    if not name.startswith(PREFIX) or bpy.data.collections.get(name):
        raise ValueError('Require a new owned reference collection; never reset an existing rig')
    selected_names = [o.name for o in bpy.context.selected_objects]
    active = bpy.context.view_layer.objects.active
    active_name = active.name if active else None
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    data = bpy.data.armatures.new(name + '_data')
    arm = bpy.data.objects.new(name + '_Armature', data)
    collection.objects.link(arm)
    arm_name = arm.name
    arm['native_probe_owner'] = name
    arm['native_probe_model'] = contract['model']
    arm['native_reference_only_projection'] = True
    arm['native_reference_projection_formula'] = contract['formula']
    arm['native_rgm_sha256'] = contract['native_rgm_sha256']
    arm['native_SKLN_payload_sha256'] = contract['SKLN_payload_sha256']
    arm['native_MSCL_payload_sha256'] = contract['MSCL_payload_sha256']
    arm['native_display_tail_length_is_visual_guide_only'] = True
    arm['native_display_tail_length_metres'] = display_length
    arm['native_engine_physical_pivots_qualified'] = False
    arm['native_world_pose_qualified'] = False
    arm.show_in_front = True
    data.display_type = 'STICK'
    try:
        for selected_name in selected_names:
            ob = bpy.data.objects.get(selected_name)
            if ob is not None:
                ob.select_set(False)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='EDIT')
        for row in contract['bones']:
            bone = data.edit_bones.new(row['name'])
            bone.head = (0,0,0)
            bone.tail = (0,display_length,0)
            bone.matrix = Matrix(row['expected_reference_matrix_row_major'])
            bone.length = display_length
            bone.use_connect = False
        for row in contract['bones']:
            if row['parent_name'] is not None:
                data.edit_bones[row['name']].parent = data.edit_bones[row['parent_name']]
        bpy.ops.object.mode_set(mode='OBJECT')
        for row in contract['bones']:
            bone = data.bones[row['name']]
            bone.use_deform = False  # rigid bone parenting works without invented skin groups
            bone['native_raw_local_reference_TRS_json'] = json.dumps(row['raw_local_reference_trs_xyzw_translation_scale'])
            bone['native_SKLN_record_sha256'] = row['SKLN_record_sha256']
            bone['native_SKLN_payload_sha256'] = contract['SKLN_payload_sha256']
            bone['native_parent_index'] = row['parent_index']
            bone['native_reference_matrix_json'] = json.dumps(row['expected_reference_matrix_row_major'])
            bone['display_tail_length_is_visual_guide_only'] = True
            bone['native_engine_physical_pivot_qualified'] = False
        bpy.context.view_layer.update()
        audit = audit_reference_bones(target, arm_name)
        if any(not row['public_reference_projection_matches'] or
               row['actual_parent'] != row['expected_parent'] for row in audit['bones']):
            raise RuntimeError('Generated reference hierarchy disagrees numerically with exact native reference matrices')
        arm['native_reference_hierarchy_numeric_check_passed'] = True
        return dict(model=contract['model'], collection=name, armature=arm_name,
            object_names=[arm_name], bone_count=contract['bone_count'], reference_bone_audit=audit,
            inverse_reference_contract=contract, display_tail_length_metres=display_length,
            reference_projection_only=True, native_engine_physical_pivots_qualified=False,
            source_pose_qualified=False,
            next_step='Append object_names to exact public import IDs, then rigid_source_views and reversible pose/static-partition checks')
    except Exception as exc:
        owner = bpy.data.collections.get(name)
        if owner is not None:
            owner['native_reference_projection_failure'] = str(exc)
            owner['native_reference_hierarchy_quarantined'] = True
        raise
    finally:
        existing = bpy.data.objects.get(arm_name)
        if existing is not None and bpy.context.mode == 'EDIT_ARMATURE':
            bpy.context.view_layer.objects.active = existing
            bpy.ops.object.mode_set(mode='OBJECT')
        for ob in list(bpy.context.selected_objects):
            ob.select_set(False)
        for selected_name in selected_names:
            ob = bpy.data.objects.get(selected_name)
            if ob is not None and bpy.context.view_layer.objects.get(selected_name) is not None:
                ob.select_set(True)
        old_active = bpy.data.objects.get(active_name) if active_name else None
        bpy.context.view_layer.objects.active = old_active if old_active is not None and bpy.context.view_layer.objects.get(active_name) is not None else None


def rigid_source_views(target, imported_object_names, collection_name=None, manifest_path=None):
    """Parent-only optional rigid inspection views; no weights invented.

    Splits public projected reference geometry by exact MSCL collection mapping,
    parents each complete bound source to its original imported bone, and checks
    that evaluated reference vertices remain unchanged. Native source tails and
    SKMS are never guessed. Original importer output and binaries stay intact.
    This tests rigid inspectability, not the physical meaning of a native pivot.
    """
    import bpy
    from mathutils import Matrix, Vector
    model = _model(target)
    binding, plan = _bindings(model), retained_plan(target, manifest_path)
    _assert_plan_fingerprint(plan, binding)
    objects = _owned_objects(imported_object_names)
    native_bones = {b['name'] for b in binding.get('SKLN', {}).get('bones', [])}
    arms = [o for o in objects if o.type == 'ARMATURE' and native_bones and
            native_bones.issubset({b.name for b in o.data.bones})]
    if len(arms) != 1:
        raise RuntimeError('Need exactly one imported armature with the complete exact native hierarchy')
    arm = arms[0]
    if any((arm.matrix_world - Matrix.Identity(4))[r][c] != 0 for r in range(4) for c in range(4)):
        raise RuntimeError('Reference probe requires identity model placement; do not fold a stamp into bone local space')
    fragments = list(_source_fragments(plan, binding))  # validate ALL joins before creating views
    label = next(k for k, value in TARGETS.items() if value == model)
    name = collection_name or PREFIX + label + '_RigidSources'
    if not name.startswith(PREFIX) or bpy.data.collections.get(name):
        raise ValueError('Require a new owned inspection collection')
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    created = []
    for index, (record, group, used, triangles) in enumerate(fragments):
        source = record['source_name']
        data = bpy.data.meshes.new(name + '_' + str(index) + '_mesh')
        vertices = [group['positions'][i] for i in used]
        data.from_pydata(vertices, [], triangles)
        data.update()
        o = bpy.data.objects.new(name + '_' + str(index), data)
        collection.objects.link(o)
        o['native_probe_owner'] = name
        o['native_probe_model'] = model
        o['native_source_name'] = source
        o['native_source_binding_sha256'] = record['binding_header_sha256']
        o['native_mesh_index'] = group['mesh_index']
        o['native_group_index'] = group['group_index']
        o['native_source_vertex_indices_json'] = json.dumps(used)
        o['native_source_numeric_frame'] = 'Public projected cooked reference coordinates; native raw TRS retained separately'
        o['native_source_parent_bone'] = record['native_parent_bone']
        o['native_reference_TRS_json'] = json.dumps(record['raw_reference_trs_xyzw_translation_scale'])
        o['native_reference_pose_qualified'] = False
        # Preserve vertex UVs and source normals as inspectable attributes.
        layers = group.get('uv_layers', {})
        if not isinstance(layers, dict):
            raise RuntimeError('Unexpected public UV shape; retain created view as diagnostic only')
        for uv_name, uv_values in layers.items():
            layer = data.uv_layers.new(name=uv_name)
            for loop in data.loops:
                layer.data[loop.index].uv = uv_values[used[loop.vertex_index]]
        normals = group.get('normals', [])
        if len(normals) == len(group['positions']):
            normal_attribute = data.attributes.new('native_reference_normal', 'FLOAT_VECTOR', 'POINT')
            for value, old_index in zip(normal_attribute.data, used):
                value.vector = normals[old_index]
        if record['native_parent_bone']:
            o.parent = arm
            o.parent_type = 'BONE'
            o.parent_bone = record['native_parent_bone']
            bpy.context.view_layer.update()
            # Let Blender solve its own bone-parent matrix, including tail offset;
            # do not guess or hand-apply MSCL inverse reference as ordinary TRS.
            o.matrix_world = Matrix.Identity(4)
            bpy.context.view_layer.update()
        evaluated = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            error = max(((evaluated.matrix_world @ v.co) - Vector(expected)).length
                        for v, expected in zip(mesh.vertices, vertices)) if vertices else 0
        finally:
            evaluated.to_mesh_clear()
        o['native_reference_numeric_error'] = error
        o['native_reference_geometry_preserved'] = error <= .0001
        if error > .0001:
            raise RuntimeError('Reference bone parenting changed source geometry; retain failed view as quarantined diagnostic')
        created.append(o.name)
    return dict(model=model, source_view_objects=created, armature=arm.name,
                reference_geometry_preserved=True, source_pose_qualified=False,
                warning='Rigid inspection reconstruction only; bone rest matrices/pivots and exact native motion still need comparison')


def pose_probe(armature_name, bone_name, object_names, radians=.035):
    """Small reversible Blender pose test. No Action/keyframes/clips are created.

    Report Blender-scene vertex displacement and restore every pose basis in a
    finally block. This establishes responsiveness/restoration only, never native
    motion limits, engine world coordinates or a stock clip's playback.
    """
    import bpy
    from mathutils import Matrix
    objects = _owned_objects(object_names)
    arm = bpy.data.objects[armature_name]
    if arm.type != 'ARMATURE' or not arm.get('native_probe_owner', '').startswith(PREFIX):
        raise ValueError('Armature is not an owned native inspection input')
    if bone_name not in arm.pose.bones or not 0 < abs(radians) <= .1:
        raise ValueError('Require an exact native bone and a small reversible angle')
    saved = {b.name: b.matrix_basis.copy() for b in arm.pose.bones}
    frame = bpy.context.scene.frame_current
    def sample():
        bpy.context.view_layer.update()
        deps = bpy.context.evaluated_depsgraph_get()
        points = {}
        for o in objects:
            if o.type != 'MESH':
                continue
            evaluated = o.evaluated_get(deps)
            mesh = evaluated.to_mesh()
            try:
                points[o.name] = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            finally:
                evaluated.to_mesh_clear()
        return points
    baseline = sample()
    result = {}
    try:
        arm.pose.bones[bone_name].matrix_basis = saved[bone_name] @ Matrix.Rotation(radians, 4, 'Z')
        posed = sample()
        for name, before in baseline.items():
            after = posed[name]
            if len(before) != len(after):
                raise RuntimeError('Pose altered evaluated topology')
            result[name] = max(((a - b).length for a, b in zip(before, after)), default=0)
    finally:
        for name, matrix in saved.items():
            arm.pose.bones[name].matrix_basis = matrix
        bpy.context.view_layer.update()
    restored = sample()
    restore_error = max(((a - b).length for name in baseline
                         for a, b in zip(baseline[name], restored[name])), default=0)
    if bpy.context.scene.frame_current != frame:
        raise RuntimeError('Unexpected frame change during pose-only probe')
    descendants = {bone_name} | {b.name for b in arm.data.bones[bone_name].children_recursive}
    expected_rigid_movement = []
    for o in objects:
        if 'native_source_parent_bone' in o and o.type == 'MESH':
            expected_move = o['native_source_parent_bone'] in descendants
            moved = result.get(o.name, 0) > .0000001
            expected_rigid_movement.append(dict(object=o.name,
                expected_move_from_exact_native_parent=expected_move, observed_move=moved,
                movement_partition_matches=expected_move == moved))
    return dict(bone=bone_name, probe_radians=radians, max_Blender_scene_displacement_by_object=result,
                restored_reference_max_error=restore_error, reference_restored=restore_error <= .0001,
                rigid_movement_partition=expected_rigid_movement,
                keyframes_created=False, native_world_pose_qualified=False,
                qualification='Reversible source-pose responsiveness only; verify expected bound/static source partition and physical pivot separately')


def audit_reference_bones(target, armature_name):
    """Compare actual imported bone references to the public projector formula.

    Agreement qualifies consistency with the retained reference projection only;
    raw SKLN reference semantics and an engine motion pivot are not thereby proved.
    """
    import bpy
    from mathutils import Matrix
    arm = bpy.data.objects[armature_name]
    if arm.type != 'ARMATURE' or not arm.get('native_probe_owner', '').startswith(PREFIX):
        raise ValueError('Not an owned inspection armature')
    binding = _bindings(_model(target))
    bones = binding.get('SKLN', {}).get('bones', [])
    if not binding.get('SKLN', {}).get('valid_complete_parse'):
        raise RuntimeError('No complete qualified SKLN parse')
    B = Matrix(((-1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    K = Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    result = []
    for record in bones:
        actual = arm.data.bones.get(record['name'])
        expected_parent = None if record['parent_index'] < 0 else bones[record['parent_index']]['name']
        native = Matrix(record['candidate_model_relative_global_reference_matrix_row_major'])
        expected = B @ native @ K
        error = max(abs(actual.matrix_local[r][c] - expected[r][c])
                    for r in range(4) for c in range(4)) if actual else None
        result.append(dict(name=record['name'], present=bool(actual),
            expected_parent=expected_parent,
            actual_parent=actual.parent.name if actual and actual.parent else None,
            maximum_matrix_residual=error,
            public_reference_projection_matches=error is not None and error <= .0001))
    return dict(model=_model(target), bones=result,
                frame='Armature-local reference comparison; not native world pose',
                source_pose_qualified=False)


def socket_views(target, collection_name=None):
    """Preserve validated raw sockets and inspect model-root markers only.

    Bone-local markers remain explicit metadata-only quarantined objects until
    the parent's exact native reference/bone-axis source gate is qualified. They
    are not placed at zero and presented as valid socket positions.
    """
    import bpy
    from mathutils import Matrix, Quaternion, Vector
    model = _model(target)
    row = _read(INVENTORY / 'geometry-only-models.json').get(model, {})
    contract = row.get('native_markers', {})
    if not contract.get('valid'):
        raise RuntimeError('No complete valid marker parse; no partial socket list is usable')
    label = next(k for k, value in TARGETS.items() if value == model)
    name = collection_name or PREFIX + label + '_Sockets'
    if not name.startswith(PREFIX) or bpy.data.collections.get(name):
        raise ValueError('Require a new owned socket collection')
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    B = Matrix(((-1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    result = []
    for index, marker in enumerate(contract.get('markers', [])):
        root_local = marker['native_frame_flag'] == 0 and not marker['parent_bone']
        o = bpy.data.objects.new(name + '_' + str(index), None)
        collection.objects.link(o)
        o['native_probe_owner'] = name
        o['native_marker_name'] = marker['name']
        o['native_marker_raw_record_json'] = json.dumps(marker)
        o['native_MRKS_payload_sha256'] = contract['payload_sha256']
        o['native_world_pose_qualified'] = False
        o['native_marker_transform_usable'] = root_local
        o.empty_display_type = 'ARROWS'
        o.empty_display_size = .15
        if root_local:
            x, y, z, w = marker['quaternion_xyzw']
            native = Matrix.LocRotScale(Vector(marker['translation']), Quaternion((w, x, y, z)), Vector(marker['scale']))
            o.matrix_world = B @ native @ B.inverted()
            o['native_numeric_frame'] = 'Projected model-root reference; no actor/stamp/world placement applied'
        else:
            o.hide_viewport = True
            o.hide_render = True
            o['native_numeric_frame'] = 'QUARANTINED raw bone-local record only; visible transform not usable'
        result.append(dict(object=o.name, native_name=marker['name'],
                           root_local_projection_only=root_local,
                           bone_local_transform_quarantined=not root_local))
    return dict(model=model, marker_records=result, native_world_pose_qualified=False)


def write_report(path, report):
    """Explicit parent evidence write, never automatic or outside the owned temp."""
    path = Path(path).resolve()
    if not path.is_relative_to(BUILDINGS.resolve()):
        raise ValueError('Reports must stay under temporary Persian building source evidence')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return str(path)
