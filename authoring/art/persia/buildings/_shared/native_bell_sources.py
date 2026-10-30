"""Exact healthy TC bell-only subset. No import-time Blender operations.

Native healthy bell geometry is unbound; its damaged helper is not silently
assigned to it. Category admission and fit in a Persian TC remain explicit.
"""
import collections
import json
from pathlib import Path
import native_mechanisms as N
import native_skin_sources as S


def qualified_subset(target):
    """Pure exact source proof: all212 oriented damaged bell triangles in healthy."""
    if target not in ('tc_bell_1','tc_bell_2'):raise ValueError('Only retained TC bell candidates')
    plan=N.retained_plan(target);binding=N._bindings(N._model(target))
    N._assert_plan_fingerprint(plan,binding)
    fragments=list(N._source_fragments(plan,binding))
    healthy=next(f for f in fragments if f[0]['source_name']=='eng_towncenter_bellarch_base_age01')
    bell=next(f for f in fragments if f[0]['source_name']=='main_dest_bell_01')
    if healthy[0]['native_parent_bone']:raise RuntimeError('Native healthy parent semantics changed')
    def oriented(t,g):
        p=tuple(tuple(g['positions'][i]) for i in t)
        return min(p,p[1:]+p[:1],p[2:]+p[:2])
    wanted=collections.Counter(oriented([bell[2][i] for i in t],bell[1]) for t in bell[3])
    triangles=[];indices=[]
    for index,t in enumerate(healthy[3]):
        original=[healthy[2][i] for i in t];key=oriented(original,healthy[1])
        if wanted[key]:triangles.append(original);indices.append(index);wanted[key]-=1
    if len(triangles)!=212 or any(wanted.values()):raise RuntimeError('Exact oriented bell subset no longer qualified')
    used=sorted({i for t in triangles for i in t});remap={old:new for new,old in enumerate(used)}
    return dict(target=target,model=N._model(target),plan=plan,group=healthy[1],used=used,
        triangles=[[remap[i] for i in t] for t in triangles],
        healthy_source_triangle_indices=indices,original_group_vertex_triangles=triangles,
        native_healthy_source=healthy[0],native_damaged_source=bell[0],
        damaged_group=bell[1],damaged_used=bell[2],damaged_triangles=bell[3],
        proof='212 oriented triangle positions match native damaged bell exactly; healthy source UVs/normals/indices retained; remaining252 arch/base triangles excluded')


def healthy_bell_view(target, public_object_names, inventory_category=None, collection_name=None):
    """Parent-run visible editable source subset, with optional exact stamp.

    inventory_category=None retains model-reference space. A named category is
    resolved only from the retained native family manifest; its transform is
    applied once for stamp-space source review. This is a chosen candidate,
    not evidence that Persia's dynamic category selection activates it.
    """
    import bpy
    from mathutils import Matrix
    import native_source_appearance as A
    subset=qualified_subset(target)
    manifest_path=N.INVENTORY/'mechanism-composition/town_center.json'
    document=json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest=next(t for t in document['targets'] if t['target']==target)
    if manifest['native_rgm_sha256']!=subset['plan']['skeleton']['source_sha256'] or manifest['public_plan_sha256']!=N._sha(subset['plan']['manifest_path']):
        raise RuntimeError('Declared family dependency manifest is stale')
    placement=None
    if inventory_category is not None:
        choices=[u for u in manifest['source_uses'] if u['inventory_category']==inventory_category]
        unique={json.dumps(u['projected_model_to_stamp_matrix_row_major']):u for u in choices}
        if len(unique)!=1:raise RuntimeError('Need one exact native category/stamp placement, not an inferred TC bell position')
        placement=next(iter(unique.values()))
    name=collection_name or N.PREFIX+target+'_HealthyBellOnly'
    if not name.startswith(N.PREFIX) or bpy.data.collections.get(name):raise ValueError('Require new owned bell source collection')
    owner=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(owner)
    mesh=S._mesh_data(bpy,name,subset['group'],subset['used'],subset['triangles'])
    obj=bpy.data.objects.new(name+'_Bell',mesh);owner.objects.link(obj)
    obj['native_probe_owner']=name;obj['native_probe_model']=subset['model']
    obj['native_source_name']=subset['native_healthy_source']['source_name']
    obj['native_exact_bell_healthy_subset']=True
    obj['native_source_parent_bone']=''  # exact original healthy source is unbound
    obj['native_source_binding_sha256']=subset['native_healthy_source']['binding_header_sha256']
    obj['native_mesh_index']=subset['group']['mesh_index'];obj['native_group_index']=subset['group']['group_index']
    obj['native_source_vertex_indices_json']=json.dumps(subset['used'])
    obj['native_healthy_source_triangle_indices_json']=json.dumps(subset['healthy_source_triangle_indices'])
    obj['native_subset_proof']=subset['proof']
    obj['native_dependency_manifest']=str(manifest_path)
    obj['native_dependency_manifest_sha256']=N._sha(manifest_path)
    obj['native_geometry_numeric_frame']='Public cooked model reference; healthy source unbound'
    obj['native_category_activation_proven_for_Persia']=False
    obj['native_new_clips_created']=False
    obj['retained_native_dependency']=True
    try:
        appearance=A.preserve(target,public_object_names,[obj.name])
        error=S._reference_error(bpy,obj,[subset['group']['positions'][i] for i in subset['used']])
        if error>.0001:raise RuntimeError('Healthy subset changed native reference geometry')
        if placement:
            obj.matrix_world=Matrix(placement['projected_model_to_stamp_matrix_row_major'])
            obj['native_geometry_numeric_frame']='Exact retained category stamp reference; not runtime actor world space'
            obj['native_selected_category']=inventory_category
            obj['native_selected_stamp']=placement['stamp']
            obj['native_model_to_stamp_matrix_json']=json.dumps(placement['projected_model_to_stamp_matrix_row_major'])
        owner['native_declared_dependencies_json']=json.dumps(dict(model=manifest['model'],native_rgm_path=manifest['native_rgm_path'],native_rgm_sha256=manifest['native_rgm_sha256'],
            native_rrgeom_path=manifest['native_rrgeom_path'],native_rrgeom_sha256=manifest['native_rrgeom_sha256'],source_library=manifest['qualified_source_library'],
            source_probe=manifest['actual_probe_path'],native_owner_graphs=manifest['native_owner_graphs'],native_selectors=manifest['native_selectors'],
            retained_reference_hierarchy=manifest['reference_hierarchy'],category_placement=placement))
        return dict(target=target,collection=name,object_names=[obj.name],triangles=212,
            native_reference_geometry_maximum_error=error,appearance=appearance,
            selected_inventory_category=inventory_category,category_placement=placement,
            native_healthy_parent_preserved='unbound',native_damaged_bell_parent=subset['native_damaged_source']['native_parent_bone'],
            active_source_subset_created=True,Persia_dynamic_category_activation_proven=False,
            native_ringing_clip_proven=False,source_fit_inspection_pending=True,clips_created=False)
    except Exception as exc:
        owner['native_source_quarantined']=True;owner['native_source_failure']=str(exc)
        obj['native_source_quarantined']=True
        raise


def family_attachment_plan(body_key):
    """Pure approved source coordinates and ALL retained category alternatives."""
    if body_key not in ('A1','A2','A3','A4'):raise ValueError('Only four existing TC bodies')
    path=N.INVENTORY/'mechanism-composition/town_center.json'
    document=json.loads(path.read_text(encoding='utf-8'))
    alternatives=[]
    for target in document['targets']:
        for category in sorted({u['inventory_category'] for u in target['source_uses']}):
            uses=[u for u in target['source_uses'] if u['inventory_category']==category]
            alternatives.append(dict(target=target['target'],inventory_category=category,
                native_source_uses=uses,native_source_predicates=target['native_selectors'],
                applicability='Supplied alternative in shared TC attachment inventory; dynamic Persia selection/age admission unproved'))
    assert {(a['target'],a['inventory_category']) for a in alternatives}=={
        ('tc_bell_1','chi_bell_arch_age_01'),('tc_bell_1','mon_bell_arch_age_01'),('tc_bell_2','mon_bell_arch_age_02')}
    # Same original call-frame at all four authored body courts. This is an
    # approved SOURCE placement, not the native inventory stamp or runtime gate.
    matrix=[[0,-1,0,2.10],[1,0,0,-4.698760986328125],
            [0,0,1,.35078125],[0,0,0,1]]
    subset=qualified_subset('tc_bell_1')
    def transform(p):return [sum(matrix[r][c]*p[c] for c in range(3))+matrix[r][3] for r in range(3)]
    points=[transform(subset['group']['positions'][i]) for i in subset['used']]
    top=max((subset['group']['positions'][i] for i in subset['used']),key=lambda p:p[2])
    native_bone=next(b for b in N.reference_projection_contract('tc_bell_1')['bones'] if b['name']=='hlp_main_dest_bell_01')
    pivot=[native_bone['expected_reference_matrix_row_major'][r][3] for r in range(3)]
    return dict(body_key=body_key,authored_space='TC stamp-space',
        all_retained_candidate_alternatives=alternatives,
        native_default_category_has_geometry=False,mandatory_bell_for_Persia_proven=False,
        exact_source_whole_model_transform_row_major=matrix,
        matrix_scope='Approved original source assembly placement; whole native model/root transformed once, original vertex/pivot/bone-local data untouched. Do not apply the native candidate stamp in addition.',
        native_bell_reference_bounds={'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]},
        native_geometric_hanging_contact=transform(top),
        hanging_contact_semantics='Exact highest native healthy-bell geometry vertex on new lintel underside; requires visual hardware inspection, not an asserted engine physical pivot',
        native_damaged_reference_pivot=transform(pivot),native_reference_pivot_is_separate=True,
        frame={'feet':[{'name':'NativeBellFootLeft','center':[1.10,-4.75,.26],'size':[.32,.76,.10]},
                       {'name':'NativeBellFootRight','center':[3.10,-4.75,.26],'size':[.32,.76,.10]}],
               'posts':[{'name':'NativeBellPostLeft','center':[1.10,-4.75,1.43],'size':[.16,.24,2.24]},
                        {'name':'NativeBellPostRight','center':[3.10,-4.75,1.43],'size':[.16,.24,2.24]}],
               'lintel':{'name':'NativeBellLintel','center':[2.10,-4.75,2.64],'size':[2.20,.44,.18]}},
        analytical_contacts={'apron_top_and_foot_bottom':.21,'foot_top_and_post_bottom':.31,'post_top_and_lintel_bottom':2.55,
            'bell_top_and_lintel_bottom':2.55,'main_paver_east_to_foot_west_gap':.08,'water_basin_front_to_foot_rear_gap':.40},
        analytical_visible_triangles={'native_healthy_bell':212,'five_original_closed_box_frame_members':60,'total':272},
        original_materials={'native_bell':'Exact public native material datablock via native_source_appearance',
            'new_frame':'Current Town Center original timber/stone atlas materials via family recipe API'},
        source_state_contract={'healthy':'Chosen candidate212-triangle native healthy subset active with original unbound semantics.',
            'construction':'Bell/frame finish-stage source assembly only. Native numeric build gating preserved raw, not reinterpreted as a progress threshold.',
            'native_dmg_01_and_dead':'Same212-triangle native bell fragment retained with original hlp_main_dest_bell_01 parent in separate inspectable alternative. Native numeric gates retained; no invented mapping to authored damage1..5.',
            'poses':'Reference rest plus reversible source pose response on original damaged-bell bone; no operating/ringing or collapse clip is fabricated.',
            'ruins':'Native dead/collapse source and graphs retained. Physical collapse/world orientation not inferred from a static source pose.'},
        nonselected_arch_reference_policy='Original public/raw donor arch sources retained separately; degenerate arch normal failures are quarantined nonselected references and do not qualify or block the exact bell-only input.',
        source_acceptance_remaining=['Actual generated member contacts and bell hardware/support visual inspection',
            'Actual visible family rest bounds and geometry/normal/material readback','Per-source alternative selection and damaged-bell pose test',
            'Preserve all declared native graphs/raw hierarchy/markers; no world socket inference'])


def attach_call_frame(H, body_key, target, inventory_category, public_object_names,
                      reference_armature_name, prepared_inputs=None):
    """Parent-run family assembly; caller explicitly selects a source candidate.

    No recipe file is edited. Existing healthy family must be built and active.
    Alternative category inventory is retained for every body without guessing
    an age→category runtime mapping. Original reference import stays untouched.
    """
    import bpy
    from mathutils import Matrix,Vector
    import native_source_appearance as A
    plan=family_attachment_plan(body_key)
    if H.CURRENT!=body_key or body_key not in H.ANCHORS or 'stamp-space' not in H.ANCHORS[body_key].get('authored_space',''):
        raise RuntimeError('Need active, built Town Center healthy source in explicitly declared stamp-space')
    if not any(a['target']==target and a['inventory_category']==inventory_category for a in plan['all_retained_candidate_alternatives']):
        raise RuntimeError('Explicit candidate/category is not in retained TC inventory')
    if H.ANCHORS[body_key].get('native_bell_source_attachment'):
        raise RuntimeError('Existing bell assembly; do not append a second simultaneous alternative')
    arm=N._owned_objects([reference_armature_name])[0]
    if arm.type!='ARMATURE' or arm.get('native_probe_model')!=N._model(target) or not arm.get('native_reference_only_projection'):
        raise RuntimeError('Require explicitly supplied exact native reference armature, not a guessed control rig')
    audit=N.audit_reference_bones(target,arm.name)
    if any(not r['public_reference_projection_matches'] or r['actual_parent']!=r['expected_parent'] for r in audit['bones']):
        raise RuntimeError('Native reference hierarchy failed numerical audit')
    if arm.animation_data or any(b.constraints or any(abs(b.matrix_basis[r][c]-float(r==c))>1e-7 for r in range(4) for c in range(4)) for b in arm.pose.bones):
        raise RuntimeError('Only unposed exact reference hierarchy is admitted; no stock clip/control assumption')
    subset=qualified_subset(target)
    base=N.PREFIX+'TC_'+body_key+'_'+inventory_category
    healthy=(prepared_inputs['healthy_view'] if prepared_inputs is not None else
             healthy_bell_view(target,public_object_names,collection_name=base+'_Healthy'))
    healthy_obj=bpy.data.objects[healthy['object_names'][0]]
    healthy_collection=bpy.data.collections[healthy['collection']]
    family=H.root(body_key)
    family.children.link(healthy_collection)
    if healthy_collection in list(bpy.context.scene.collection.children):
        bpy.context.scene.collection.children.unlink(healthy_collection)
    H.tag(healthy_obj,'finish','native_mechanism','native_bell')
    assembly=bpy.data.objects.new(base+'_WholeModelPlacement',None);family.objects.link(assembly)
    assembly['native_probe_owner']=base;assembly['native_probe_model']=N._model(target)
    assembly['native_whole_model_transform_json']=json.dumps(plan['exact_source_whole_model_transform_row_major'])
    assembly['native_vertices_and_raw_pivots_unchanged']=True
    healthy_obj.parent=assembly;healthy_obj.matrix_parent_inverse=Matrix.Identity(4);healthy_obj.matrix_basis=Matrix.Identity(4)
    reference_name=(prepared_inputs['reference_collection'] if prepared_inputs is not None else base+'_InspectableNativeAlternatives')
    if prepared_inputs is not None:
        reference=bpy.data.collections[reference_name];ref_arm=arm
    else:
        if bpy.data.collections.get(reference_name):raise RuntimeError('Owned reference alternative collection exists')
        reference=bpy.data.collections.new(reference_name);bpy.context.scene.collection.children.link(reference)
        ref_arm=arm.copy();ref_arm.data=arm.data.copy();ref_arm.name=base+'_NativeReferenceHierarchy'
        reference.objects.link(ref_arm);ref_arm['native_probe_owner']=reference_name
    ref_arm.parent=assembly;ref_arm.matrix_parent_inverse=Matrix.Identity(4);ref_arm.matrix_basis=Matrix.Identity(4)
    if prepared_inputs is not None:
        damaged=bpy.data.objects[prepared_inputs['damaged_bell_object']]
    else:
        data=S._mesh_data(bpy,base+'_NativeDamagedBell',subset['damaged_group'],subset['damaged_used'],subset['damaged_triangles'])
        damaged=bpy.data.objects.new(base+'_NativeDamagedBell',data);reference.objects.link(damaged)
    damaged['native_probe_owner']=reference_name;damaged['native_probe_model']=N._model(target)
    damaged['native_source_name']='main_dest_bell_01'
    damaged['retained_native_dependency']=True
    damaged['native_source_parent_bone']=subset['native_damaged_source']['native_parent_bone']
    damaged['native_source_binding_sha256']=subset['native_damaged_source']['binding_header_sha256']
    damaged['native_reference_TRS_json']=json.dumps(subset['native_damaged_source']['raw_reference_trs_xyzw_translation_scale'])
    damaged.parent=ref_arm;damaged.parent_type='BONE';damaged.parent_bone=damaged['native_source_parent_bone']
    bpy.context.view_layer.update();damaged.matrix_world=Matrix.Identity(4)
    damaged_appearance=(prepared_inputs['appearance_contract'] if prepared_inputs is not None else
                        A.preserve(target,public_object_names,[damaged.name]))
    error=S._reference_error(bpy,damaged,[subset['damaged_group']['positions'][i] for i in subset['damaged_used']])
    if error>.0001:raise RuntimeError('Original damaged bell parenting changed reference geometry')
    assembly.matrix_world=Matrix(plan['exact_source_whole_model_transform_row_major'])
    feet=[];posts=[]
    apron=bpy.data.objects.get(H.R.PREFIX+body_key+'_PublicApron')
    if apron is None:raise RuntimeError('Actual named TC PublicApron support missing')
    for row in plan['frame']['feet']:
        part=H.B(row['name'],row['center'],row['size'],'stone','finish','architecture','native_bell_support');feet.append(part)
        H.contact(row['name']+'OnPublicApron',part,apron,'bottom-top')
    for row,foot in zip(plan['frame']['posts'],feet):
        part=H.B(row['name'],row['center'],row['size'],'timber','finish','architecture','native_bell_support');posts.append(part)
        H.contact(row['name']+'OnStoneFoot',part,foot,'bottom-top')
    row=plan['frame']['lintel']
    lintel=H.B(row['name'],row['center'],row['size'],'timber','finish','architecture','native_bell_support')
    for post in posts:H.contact('NativeBellLintelOn'+post.name,lintel,post,'bottom-top')
    H.ANCHORS[body_key].setdefault('numerical_interfaces',[]).append(dict(
        body=body_key,name='NativeBellGeometricTopToLintelUnderside',a=healthy_obj.name,b=lintel.name,
        authored_contact_point=plan['native_geometric_hanging_contact'],authored_space='stamp-space',
        intentional_socket_overlap_metres=0.,tolerance=.003,
        basis=plan['hanging_contact_semantics']))
    bpy.context.view_layer.update()
    actual_points=[healthy_obj.matrix_world@v.co for v in healthy_obj.data.vertices]
    actual_bounds={'min':[min(v[i] for v in actual_points) for i in range(3)],'max':[max(v[i] for v in actual_points) for i in range(3)]}
    fit_error=max(abs(actual_bounds[k][i]-plan['native_bell_reference_bounds'][k][i]) for k in ('min','max') for i in range(3))
    if fit_error>.0001:raise RuntimeError('Whole-model attachment transform/bounds mismatch')
    pose=N.pose_probe(ref_arm.name,'hlp_main_dest_bell_01',[damaged.name,healthy_obj.name])
    reference['native_source_state_contract_json']=json.dumps(plan['source_state_contract'])
    reference['native_family_attachment_plan_json']=json.dumps(plan)
    reference['native_nonselected_donor_arch_included']=False
    reference['native_source_selector_alternatives_json']=json.dumps(next(a for a in plan['all_retained_candidate_alternatives'] if a['target']==target and a['inventory_category']==inventory_category))
    reference.hide_render=True
    for obj in reference.objects:obj.hide_set(True)
    result=dict(body_key=body_key,target=target,chosen_source_preview_category=inventory_category,
        all_retained_candidate_alternatives=plan['all_retained_candidate_alternatives'],
        active_healthy_bell_object=healthy_obj.name,original_frame_objects=[o.name for o in feet+posts]+[lintel.name],
        whole_model_root=assembly.name,model_to_authored_stamp_matrix=plan['exact_source_whole_model_transform_row_major'],
        actual_bell_reference_bounds=actual_bounds,maximum_bounds_error=fit_error,
        inspectable_native_alternative_collection=reference_name,native_reference_armature=ref_arm.name,
        native_damaged_bell_object=damaged.name,damaged_bell_reference_geometry_error=error,
        damaged_bell_appearance=damaged_appearance,native_source_pose_probe=pose,
        source_state_contract=plan['source_state_contract'],planned_visible_triangles=272,
        actual_visible_triangles=sum(len(o.data.polygons) for o in feet+posts+[lintel])+len(healthy_obj.data.polygons),
        triangle_measurement='All created frame faces are quads; planned60 triangles need loop-triangle readback below',
        generated_contact_check_pending=True,visual_hanging_hardware_check_pending=True,
        native_runtime_category_selection_proven=False,clips_created=False)
    actual_triangles=0
    for ob in feet+posts+[lintel,healthy_obj]:
        ob.data.calc_loop_triangles();actual_triangles+=len(ob.data.loop_triangles)
    result['actual_visible_triangles']=actual_triangles
    result['triangle_measurement']='Actual Mesh.loop_triangles across active healthy bell plus five original frame members; alternatives excluded'
    H.ANCHORS[body_key]['native_bell_source_attachment']=result
    return result


def select_source_bell_alias(H,body_key,selector_alias):
    """Explicit source preview of native selector alternatives, no HP mapping.

    This never turns native numeric predicates into authored damage thresholds.
    A caller chooses the actual alias for inspection; native graph/physics
    playback remains untouched. The original donor arch is never activated.
    """
    import bpy
    if selector_alias not in ('healthy','dmg_01','dead'):
        raise ValueError('Only actual supplied native bell source selector aliases')
    receipt=H.ANCHORS[body_key]['native_bell_source_attachment']
    healthy=bpy.data.objects[receipt['active_healthy_bell_object']]
    damaged=bpy.data.objects[receipt['native_damaged_bell_object']]
    native_alternative=selector_alias!='healthy'
    healthy.hide_set(native_alternative);healthy.hide_render=native_alternative
    damaged.hide_set(not native_alternative);damaged.hide_render=not native_alternative
    reference=bpy.data.collections[receipt['inspectable_native_alternative_collection']]
    reference.hide_render=not native_alternative
    # One object can be linked to both its retained reference collection and the
    # chosen family source composition; Blender does not duplicate its geometry.
    family=H.root(body_key)
    if native_alternative and damaged not in list(family.objects):family.objects.link(damaged)
    if not native_alternative and damaged in list(family.objects):family.objects.unlink(damaged)
    receipt['explicit_source_preview_selector_alias']=selector_alias
    receipt['native_numeric_predicates_evaluated']=False
    return dict(selector_alias=selector_alias,active_object=damaged.name if native_alternative else healthy.name,
        native_bell_triangles=212,frame_unchanged=True,native_HP_or_build_thresholds_invented=False,
        native_physics_or_ringing_playback_qualified=False)
