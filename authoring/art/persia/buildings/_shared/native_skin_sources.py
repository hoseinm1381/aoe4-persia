"""Bounded Lumber native skin + rigid source views; parent-only Blender calls.

No import-time Blender operations, decode, clips, automatic weights or cleanup.
The original public plan/binaries/import stay intact. This is a reference-source
projection, not a claim about engine physical pivots or stock animation playback.
"""
import hashlib
import json
import math
from collections import Counter

import native_mechanisms as N

TARGET = 'lumber_crane'
RGM_SHA = '55ad1d5227fc5d14355e6439b6bbf91695fbf1de913f6241b50b087f3997834b'
SKIN_NAME = 'geo_sel_construct_80__sel_ruins_disappear_002'


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _require(condition, message):
    if not condition:
        raise RuntimeError(message)


def _mul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def _error(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))


def _trs(record):
    values = record['quaternion_xyzw'] + record['translation_xyz'] + record['scale_xyz']
    _require(len(values) == 10 and all(math.isfinite(x) for x in values), 'Invalid palette TRS')
    x,y,z,w,tx,ty,tz,sx,sy,sz = values
    norm = math.sqrt(x*x+y*y+z*z+w*w)
    _require(abs(norm-1) < .00001, 'Nonunit palette quaternion')
    x,y,z,w = [v/norm for v in (x,y,z,w)]
    return [[(1-2*(y*y+z*z))*sx,2*(x*y-z*w)*sy,2*(x*z+y*w)*sz,tx],
            [2*(x*y+z*w)*sx,(1-2*(x*x+z*z))*sy,2*(y*z-x*w)*sz,ty],
            [2*(x*z-y*w)*sx,2*(y*z+x*w)*sy,(1-2*(x*x+y*y))*sz,tz], [0,0,0,1]]


def _inputs(target=TARGET, manifest_path=None):
    _require(target == TARGET, 'Only the exact audited Lumber target is admitted')
    binding = N._bindings(N._model(target))
    plan = N.retained_plan(target, manifest_path)
    N._assert_plan_fingerprint(plan, binding)
    _require(binding['native_rgm_sha256'] == RGM_SHA, 'Lumber source changed; requalify instead of guessing')
    return binding, plan


def _collection_subset(plan, binding):
    """Join by unique exact native effect/stream, never by cyclic material guess.

    The full public manifest has partition_bound=false because it also contains
    SKMS. This derived inspection subset is not written back or called a public
    bound partition. Both unique effects and all vertex local IDs must agree.
    """
    groups = plan['geometry']['groups']
    maps = plan['structure_collection_contract']['maps']
    _require(len(groups) == 3 and len(maps) == 2, 'Unexpected mixed model layout')
    expected = [('structure_collection', 'StructureCollectionPositionDataStream', 10),
                ('object_layered_collection', 'ObjectLayeredCollectionPositionDataStream', 1)]
    selected, proof = [], []
    for mapping, (effect, stream, count) in zip(maps, expected):
        matches = [g for g in groups if g['effect'] == effect and g['stream'] == stream]
        _require(len(matches) == 1 and mapping['effect'] == effect and
                 mapping['geometry_group_span'] == 1, 'Ambiguous effect/stream collection join')
        g = matches[0]
        _require(not g['skin_indices'] and not g['skin_weights'], 'Native skin cannot become rigid weights')
        _require(mapping['active_object_count'] == count and g['collection_bone_index_count'] == count,
                 'Collection active source count disagreement')
        ids = g['collection_bone_indices']
        _require(len(ids) == len(g['positions']) and set(ids) == set(range(count)),
                 'Incomplete collection-local vertex membership')
        _require(len(mapping['source_to_local_bone']) == len(binding['MSCL']['source_records']),
                 'MSCL source map count mismatch')
        selected.append(g)
        proof.append(dict(group=g['name'], mesh_index=g['mesh_index'], collection=mapping['collection'],
                          effect=effect, stream=stream, active_source_count=count,
                          vertex_membership_sha256=_digest(ids)))
    _require(len({id(g) for g in selected}) == 2 and
             set(id(g) for g in groups if g['collection_bone_indices']) == set(id(g) for g in selected),
             'Unaccounted native collection geometry')
    subset = dict(plan, geometry=dict(plan['geometry'], groups=selected))
    # Existing strict triangle/source-map join provides a second independent gate.
    fragments = list(N._source_fragments(subset, binding))
    _require(len(fragments) == 11, 'Expected exact eleven nonempty MSCL source views')
    return subset, fragments, proof


def skin_source_contract(target=TARGET, manifest_path=None):
    """Pure-data admission; imports no bpy and creates/writes nothing."""
    binding, plan = _inputs(target, manifest_path)
    reference = N.reference_projection_contract(target, manifest_path)
    skeleton = plan['skeleton']
    rest = skeleton['rest_pose']
    _require(rest['semantic'] == 'bind_pose' and rest['semantic_confidence'] == 'confirmed' and
             rest['status'] == 'local_bind_transforms_decoded', 'Bind reference semantics unqualified')
    _require(plan['rig_palette_binding']['status'] == 'complete' and
             plan['rig_palette_binding']['bound_group_count'] == 1 and
             plan['rig_palette_binding']['unbound_group_count'] == 0, 'Partial native skin binding')
    groups = [g for g in plan['geometry']['groups'] if g['skin_weights']]
    _require(len(groups) == 1 and groups[0]['name'] == SKIN_NAME and
             binding['direct_SKMS_names'] == [SKIN_NAME], 'Unexpected SKMS identity')
    group = groups[0]
    rig, encoding = group['rig_projection'], group['skin_projection']
    _require(rig['status'] == 'decoded' and rig['index_space'] == 'SKIN_after_LOD_remap' and
             rig['binding_kind'] == 'skinned_lod_palette' and rig['skin_weights_decoded'] and
             rig['skeleton_binding_decoded'], 'Decoded native SKIN index space not qualified')
    _require(encoding['index_encoding'] == 'uint8x4' and encoding['weight_encoding'] == 'unorm8x4' and
             encoding['weight_byte_sum'] == 255, 'Unexpected native influence encoding')
    palettes = skeleton['skin_palettes']
    _require(len(palettes) == 1 and rig['palette_index'] == 0, 'Unexpected palette selection')
    palette = palettes[0]
    _require(palette['name'] == SKIN_NAME and palette['status'] == 'bind_palette_decoded' and
             palette['bone_count'] == 3 and palette['inverse_bind_validation']['status'] == 'matched' and
             palette['skln_crosscheck']['status'] == 'matched', 'Palette incomplete or not crosschecked')
    native = binding['SKLN']['bones']
    identity = [[float(r == c) for c in range(4)] for r in range(4)]
    inverse_error, skeleton_error = 0, 0
    for i, bone in enumerate(palette['bones']):
        index = bone['skeleton_index']
        _require(bone['palette_index'] == i and 0 <= index < len(native) and
                 native[index]['name'] == bone['name'], 'Palette/SKLN name-index mismatch')
        global_ = _trs(bone['global_reference_transform'])
        inverse_error = max(inverse_error, _error(_mul(global_, _trs(bone['inverse_bind_transform'])), identity))
        skeleton_error = max(skeleton_error, _error(global_, native[index]['candidate_model_relative_global_reference_matrix_row_major']))
    _require(max(inverse_error, skeleton_error) < .00001, 'Numeric native palette inverse/SKLN mismatch')
    count = len(group['positions'])
    _require(count == group['vertex_count'] == 297 and len(group['triangles']) == 352 and
             len(group['skin_indices']) == len(group['skin_weights']) == len(group['skin_indices_raw_lod']) == count,
             'Native skin vertex/influence/triangle counts changed')
    lod = rig['lod_palette']['skin_indices']
    _require(lod == [1,2], 'Unexpected exact native LOD palette')
    weighted_counts = Counter()
    for indices, raw, weights in zip(group['skin_indices'], group['skin_indices_raw_lod'], group['skin_weights']):
        _require(len(indices) == len(raw) == len(weights) == 4 and all(math.isfinite(w) and 0 <= w <= 1 for w in weights),
                 'Invalid native influence tuple')
        _require(abs(sum(weights)-1) < .000001 and sum(round(w*255) for w in weights) == 255 and
                 all(abs(w*255-round(w*255)) < .00001 for w in weights), 'Non-exact unorm8 native weights')
        for index, raw_index, weight in zip(indices, raw, weights):
            _require(isinstance(index, int) and 0 <= index < len(palette['bones']), 'Invalid SKIN index')
            if weight:
                _require(0 <= raw_index < len(lod) and index == lod[raw_index], 'LOD remap disagreement')
                weighted_counts[palette['bones'][index]['name']] += 1
    _require(dict(weighted_counts) == {'bone_wheel_base':39, 'bone_cable_twist':258}, 'Native weighted partition changed')
    for g in plan['geometry']['groups']:
        _require(all(len(v) == 3 and all(math.isfinite(x) for x in v) for v in g['positions']), 'Invalid native position')
        _require(all(len(t) == 3 and all(isinstance(i,int) and 0 <= i < len(g['positions']) for i in t) for t in g['triangles']), 'Invalid native triangle')
        _require(isinstance(g['uv_layers'],dict) and all(len(v) == len(g['positions']) for v in g['uv_layers'].values()), 'Invalid native UV layer')
    _, fragments, proof = _collection_subset(plan, binding)
    return dict(model=N._model(target), native_rgm_sha256=RGM_SHA, manifest_path=plan['manifest_path'],
        reference_contract=reference, skin_group=SKIN_NAME, vertex_count=count,
        raw_triangles=352, projectable_triangles=sum(len(set(t)) == 3 for t in group['triangles']),
        palette=palette, native_rest_pose=rest, weighted_vertex_counts=dict(weighted_counts),
        influence_index_space='SKIN_after_LOD_remap', lod_remapped_again=False,
        influences_sha256=_digest([group['skin_indices'],group['skin_weights'],group['skin_indices_raw_lod']]),
        maximum_palette_inverse_error=inverse_error, maximum_palette_SKLN_error=skeleton_error,
        collection_join=proof, rigid_source_count=len(fragments), public_partition_bound=bool(plan.get('structure_collection_partition_bound')),
        collection_join_qualification='Derived unique effect/stream + exact source/local-ID + homogeneous triangle join; original public plan unchanged',
        native_world_pose_qualified=False, engine_physical_pivots_qualified=False, clips_created=False)


def _mesh_data(bpy, name, group, used, triangles):
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata([group['positions'][i] for i in used], [], triangles)
    mesh.update()
    for uv_name, values in group['uv_layers'].items():
        uv = mesh.uv_layers.new(name=uv_name)
        for loop in mesh.loops:
            uv.data[loop.index].uv = values[used[loop.vertex_index]]
    normals = group.get('normals', [])
    if len(normals) == len(group['positions']):
        attr = mesh.attributes.new('native_reference_normal', 'FLOAT_VECTOR', 'POINT')
        for entry, index in zip(attr.data, used):
            entry.vector = normals[index]
    return mesh


def _reference_error(bpy, obj, expected):
    from mathutils import Vector
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        _require(len(mesh.vertices) == len(expected), 'Unexpected evaluated vertex count')
        return max(((evaluated.matrix_world @ v.co)-Vector(p)).length for v,p in zip(mesh.vertices,expected))
    finally:
        evaluated.to_mesh_clear()


def source_views(target, armature_name, collection_name=None, manifest_path=None):
    """Create editable exact native skin and collection-rigid views, explicitly.

    Use N.reference_armature_views first and pass its exact armature name. Only
    this owned new reference armature may have its native weighted bones enabled.
    Original import IDs and controls are never selected by a heuristic or edited.
    """
    import bpy
    from mathutils import Matrix
    contract = skin_source_contract(target, manifest_path)
    binding, plan = _inputs(target, manifest_path)
    arm = bpy.data.objects.get(armature_name)
    _require(arm is not None and arm.type == 'ARMATURE' and
             arm.get('native_probe_owner','').startswith(N.PREFIX) and
             arm.get('native_probe_model') == N._model(target) and
             arm.get('native_reference_only_projection'), 'Need explicitly owned exact reference armature')
    _require(_error(arm.matrix_world,Matrix.Identity(4)) < 1e-8 and
             not arm.animation_data and not any(b.constraints for b in arm.pose.bones) and
             all(_error(b.matrix_basis,Matrix.Identity(4)) < 1e-8 for b in arm.pose.bones), 'Reference armature must be unposed, unconstrained and at identity')
    audit = N.audit_reference_bones(target,arm.name)
    _require(all(r['public_reference_projection_matches'] and r['actual_parent']==r['expected_parent'] for r in audit['bones']), 'Reference bones fail exact native audit')
    _, fragments, _ = _collection_subset(plan,binding)
    name = collection_name or N.PREFIX+'lumber_crane_NativeSkinAndRigidSources'
    _require(name.startswith(N.PREFIX) and bpy.data.collections.get(name) is None, 'Require new owned source collection')
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    collection['native_contract_json'] = json.dumps(contract)
    collection['native_reference_projection_only'] = True
    created, rigid = [], []
    try:
        group = next(g for g in plan['geometry']['groups'] if g['name'] == SKIN_NAME)
        used = list(range(len(group['positions'])))
        triangles = [t for t in group['triangles'] if len(set(t)) == 3]
        data = _mesh_data(bpy,name+'_SKMS',group,used,triangles)
        skin = bpy.data.objects.new(name+'_SKMS',data)
        collection.objects.link(skin)
        skin['native_probe_owner'] = name
        skin['native_probe_model'] = N._model(target)
        skin['native_SKMS_name'] = SKIN_NAME
        skin['native_mesh_index'] = group['mesh_index']
        skin['native_group_index'] = group['group_index']
        skin['native_source_vertex_indices_json'] = json.dumps(used)
        skin['native_SKMS_palette_json'] = json.dumps(contract['palette'])
        skin['native_raw_influences_json'] = json.dumps(dict(indices=group['skin_indices'],raw_lod_indices=group['skin_indices_raw_lod'],weights=group['skin_weights']))
        skin['native_influences_sha256'] = contract['influences_sha256']
        skin['native_reference_numeric_frame'] = 'Public projected model reference; no stamp/world placement'
        skin['garrison_skin_index_space'] = 'SKIN_after_LOD_remap'
        skin['native_source_geometry_group_json'] = json.dumps(dict(name=group['name'],mesh_index=group['mesh_index'],group_index=group['group_index'],source_contract=group['source_contract'],material=group['material'],effect=group['effect']))
        for bone in contract['palette']['bones']:
            skin.vertex_groups.new(name=bone['name'])
        for vertex,(indices,weights) in enumerate(zip(group['skin_indices'],group['skin_weights'])):
            for index,weight in zip(indices,weights):
                if weight:
                    skin.vertex_groups[contract['palette']['bones'][index]['name']].add([vertex],weight,'REPLACE')
        for bone_name in contract['weighted_vertex_counts']:
            arm.data.bones[bone_name].use_deform = True
            arm.data.bones[bone_name]['native_deform_enabled_from_exact_SKMS_weights'] = True
        modifier = skin.modifiers.new('Exact native SKMS palette weights','ARMATURE')
        modifier.object = arm
        modifier.use_deform_preserve_volume = False
        modifier.use_vertex_groups = True
        modifier.use_bone_envelopes = False
        error = _reference_error(bpy,skin,group['positions'])
        _require(error < .0001,'Exact native skin changed reference geometry')
        skin['native_reference_numeric_error'] = error
        skin['native_reference_geometry_preserved'] = True
        skin['native_weight_audit_json'] = json.dumps(audit_skin_weights(skin.name,contract))
        created.append(skin.name)
        for index,(record,g,used,triangles) in enumerate(fragments):
            triangles = [t for t in triangles if len(set(t)) == 3]
            mesh = _mesh_data(bpy,name+'_MSCL_'+str(index),g,used,triangles)
            obj = bpy.data.objects.new(name+'_MSCL_'+str(index),mesh)
            collection.objects.link(obj)
            obj['native_probe_owner'] = name
            obj['native_probe_model'] = N._model(target)
            obj['native_source_name'] = record['source_name']
            obj['native_mesh_index'] = g['mesh_index']
            obj['native_group_index'] = g['group_index']
            obj['native_source_vertex_indices_json'] = json.dumps(used)
            obj['native_source_parent_bone'] = record['native_parent_bone']
            obj['native_source_binding_sha256'] = record['binding_header_sha256']
            obj['native_reference_TRS_json'] = json.dumps(record['raw_reference_trs_xyzw_translation_scale'])
            obj['native_source_numeric_frame'] = 'Public projected model reference; raw local TRS retained separately'
            if record['native_parent_bone']:
                obj.parent, obj.parent_type, obj.parent_bone = arm,'BONE',record['native_parent_bone']
                bpy.context.view_layer.update()
                obj.matrix_world = Matrix.Identity(4)
            error = _reference_error(bpy,obj,[g['positions'][i] for i in used])
            _require(error < .0001,'Rigid native collection view changed reference geometry')
            obj['native_reference_numeric_error'] = error
            obj['native_reference_geometry_preserved'] = True
            rigid.append(obj.name)
            created.append(obj.name)
        return dict(armature=arm.name,collection=name,skin_object=skin.name,rigid_objects=rigid,
                    object_names=created,contract=contract,reference_geometry_preserved=True,
                    source_pose_qualified=False,clips_created=False,
                    material_projection='Exact UVs/native material references retained; view material slots unassigned. Original public import preserved.',
                    next_step='skin_pose_probe for cable twist and wheel base; N.pose_probe for rigid source partition; compare total geometry with original public import')
    except Exception as exc:
        collection['native_source_quarantined'] = True
        collection['native_source_failure'] = str(exc)
        for obj in collection.objects:
            obj['native_source_quarantined'] = True
        raise


def audit_skin_weights(object_name, contract=None):
    """Compare every actual editable vertex group weight to exact native data."""
    import bpy
    contract = contract or skin_source_contract()
    obj = N._owned_objects([object_name])[0]
    _require(obj.type == 'MESH' and obj.get('native_SKMS_name') == SKIN_NAME,'Not exact owned SKMS view')
    _, plan = _inputs()
    group = next(g for g in plan['geometry']['groups'] if g['name'] == SKIN_NAME)
    _require(len(obj.data.vertices) == len(group['positions']), 'Editable skin vertex count mismatch')
    residual = 0
    for vertex,indices,weights in zip(obj.data.vertices,group['skin_indices'],group['skin_weights']):
        actual = {obj.vertex_groups[e.group].name:e.weight for e in vertex.groups if e.weight}
        expected = {contract['palette']['bones'][i]['name']:w for i,w in zip(indices,weights) if w}
        _require(set(actual)==set(expected),'Native named weight membership changed')
        residual=max(residual,max((abs(actual[k]-v) for k,v in expected.items()),default=0))
    _require(residual < 1e-7,'Native per-vertex weights changed')
    return dict(vertices_checked=len(group['positions']),maximum_weight_error=residual,
                exact_native_named_weights_preserved=True,automatic_weights=False,LOD_remapped_again=False)


def skin_pose_probe(object_name, armature_name, bone_name='bone_cable_twist', radians=.035):
    """Reversible source pose; compare each evaluated vertex with exact native LBS.

    Establishes Blender inspectability/restoration and native influence partition;
    never adds an Action or claims an engine clip/physical pivot was reproduced.
    """
    import bpy
    from mathutils import Matrix,Vector
    audit_skin_weights(object_name)
    skin = bpy.data.objects[object_name]
    arm = N._owned_objects([armature_name])[0]
    _require(arm.type=='ARMATURE' and bone_name in arm.pose.bones and 0 < abs(radians) <= .1,'Invalid bounded native bone pose')
    _require(len(skin.modifiers)==1 and skin.modifiers[0].type=='ARMATURE' and skin.modifiers[0].object==arm,
             'Pose probe requires exact single native skin modifier')
    _require(_error(skin.matrix_world,Matrix.Identity(4)) < 1e-8 and _error(arm.matrix_world,Matrix.Identity(4)) < 1e-8,'Model-reference identity placement required')
    saved={b.name:b.matrix_basis.copy() for b in arm.pose.bones}
    frame=bpy.context.scene.frame_current
    def sample():
        bpy.context.view_layer.update()
        ev=skin.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
        try:return [(ev.matrix_world@v.co).copy() for v in mesh.vertices]
        finally:ev.to_mesh_clear()
    baseline=sample()
    try:
        arm.pose.bones[bone_name].matrix_basis=saved[bone_name]@Matrix.Rotation(radians,4,'Z')
        posed=sample()
        matrices={b.name:b.matrix@arm.data.bones[b.name].matrix_local.inverted() for b in arm.pose.bones}
        predicted=[]
        for vertex in skin.data.vertices:
            point=Vector((0,0,0))
            for entry in vertex.groups:
                point+=(matrices[skin.vertex_groups[entry.group].name]@vertex.co)*entry.weight
            predicted.append(point)
        lbs_error=max(((a-b).length for a,b in zip(posed,predicted)),default=0)
        descendants={bone_name}
        pending=list(arm.data.bones[bone_name].children)
        while pending:
            child=pending.pop()
            descendants.add(child.name)
            pending.extend(child.children)
        # Per-vertex partition allows immobility on the rotation axis.
        weighted=[any(skin.vertex_groups[e.group].name in descendants and e.weight for e in v.groups) for v in skin.data.vertices]
        moved=[(a-b).length for a,b in zip(posed,baseline)]
        static_error=max((d for d,w in zip(moved,weighted) if not w),default=0)
        maximum=max(moved,default=0)
    finally:
        for name,matrix in saved.items():arm.pose.bones[name].matrix_basis=matrix
        bpy.context.view_layer.update()
    restored=sample()
    restore_error=max(((a-b).length for a,b in zip(baseline,restored)),default=0)
    _require(bpy.context.scene.frame_current==frame,'Frame changed in bounded pose probe')
    passed=lbs_error<=.0001 and static_error<=.0001 and restore_error<=.0001 and maximum>1e-7
    return dict(bone=bone_name,radians=radians,exact_native_weighted_vertex_count=sum(weighted),
        maximum_Blender_scene_displacement=maximum,maximum_exact_weight_LBS_error=lbs_error,
        unweighted_partition_maximum_displacement=static_error,restored_reference_maximum_error=restore_error,
        reversible_source_pose_passed=passed,clips_created=False,native_world_pose_qualified=False,
        engine_physical_pivot_qualified=False,qualification='Reference-source pose/LBS consistency only; actual parent probe required')
