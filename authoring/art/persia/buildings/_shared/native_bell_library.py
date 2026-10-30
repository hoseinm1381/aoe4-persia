"""Bounded bell library compiler and factory append; no Garrison API calls.

Parent executes compile_library once after qualified public probes. Factory
builds call append_and_attach. No import-time Blender operations or cleanup.
"""
from pathlib import Path
import json
import math
import native_mechanisms as N
import native_bell_sources as B
import native_skin_sources as S
import native_source_appearance as A

DEFAULT_LIBRARY=N.BUILDINGS/'_shared/mechanisms/native_bell_inputs.blend'


def _require(value,message):
    if not value:raise RuntimeError(message)


def _image_dependencies(objects,source_blend):
    """Resolve paths on appended owned datablocks, preserve nodes/image IDs."""
    import bpy
    trees=set();images={}
    def visit(tree):
        if tree is None or tree.as_pointer() in trees:return
        trees.add(tree.as_pointer())
        for node in tree.nodes:
            image=getattr(node,'image',None)
            if image and image.source=='FILE':images[image.as_pointer()]=image
            visit(getattr(node,'node_tree',None))
    for obj in objects:
        if obj.type=='MESH':
            for material in obj.data.materials:
                if material and material.use_nodes:visit(material.node_tree)
    rows=[]
    for image in images.values():
        raw=image.filepath
        path=(source_blend.parent/raw[2:]).resolve() if raw.startswith('//') else Path(bpy.path.abspath(raw)).resolve()
        _require(path.is_file(),'Required retained native image missing: '+str(path))
        image.filepath=str(path)
        rows.append(dict(image=image.name,path=str(path),sha256=N._sha(path),bytes=path.stat().st_size,original_append_filepath=raw))
    return rows


def _audit_mesh(target,obj,role):
    import bpy
    subset=B.qualified_subset(target)
    group=subset['group'] if role=='healthy' else subset['damaged_group']
    used=subset['used'] if role=='healthy' else subset['damaged_used']
    triangles=subset['triangles'] if role=='healthy' else subset['damaged_triangles']
    _require(obj.type=='MESH' and len(obj.data.vertices)==len(used),'Bell mesh vertex count changed')
    _require([list(p.vertices) for p in obj.data.polygons]==triangles,'Bell exact source triangle indices changed')
    pos_error=max((abs(v.co[a]-group['positions'][old][a]) for v,old in zip(obj.data.vertices,used) for a in range(3)),default=0)
    _require(pos_error<1e-7,'Bell source vertex coordinates changed')
    _require('native_reference_normal' in obj.data.attributes,'Exact native normal attribute missing')
    raw=obj.data.attributes['native_reference_normal']
    raw_error=max((abs(row.vector[a]-group['normals'][old][a]) for row,old in zip(raw.data,used) for a in range(3)),default=0)
    _require(len(raw.data)==len(used) and raw_error<1e-7,'Authoritative native normal attribute changed')
    uv_error=0
    for name,values in group['uv_layers'].items():
        layer=obj.data.uv_layers.get(name);_require(layer is not None,'Native UV layer lost: '+name)
        uv_error=max(uv_error,max((abs(layer.data[loop.index].uv[a]-values[used[loop.vertex_index]][a]) for loop in obj.data.loops for a in range(2)),default=0))
    _require(uv_error<1e-7,'Native bell UV coordinates changed')
    actual=[tuple(n.vector) for n in obj.data.corner_normals]
    expected=[group['normals'][used[loop.vertex_index]] for loop in obj.data.loops]
    _require(len(actual)==len(expected),'Native custom corner normal count changed')
    normal_angle=max((A.angular_error_degrees(a,b) for a,b in zip(actual,expected)),default=0)
    _require(normal_angle<=A.NORMAL_ANGULAR_LIMIT_DEGREES,'Bell custom normals exceed documented angular fidelity')
    _require({p.material_index for p in obj.data.polygons}=={0} and len(obj.data.materials)==1,'Bell material face join changed')
    material=obj.data.materials[0]
    identity=A.material_identity({k:material[k] for k in material.keys()},subset['plan'])
    _require(identity['name']=='main','Bell exact native main material identity changed')
    obj.data.calc_loop_triangles();_require(len(obj.data.loop_triangles)==212,'Bell must remain212 source triangles')
    return dict(role=role,vertices=len(used),triangles=212,maximum_vertex_component_error=pos_error,
        maximum_native_normal_attribute_error=raw_error,maximum_UV_error=uv_error,
        maximum_custom_normal_angle_degrees=normal_angle,material_identity=identity,
        native_vertex_data_unchanged=True,original_material_nodes_and_images_retained=True)


def compile_library(output_path=None):
    """Parent-run, from retained qualified .blend inputs; never native reimport."""
    import bpy
    output=Path(output_path or DEFAULT_LIBRARY).resolve();sidecar=output.with_suffix('.json')
    _require(output.is_relative_to(N.BUILDINGS.resolve()),'Bell library must stay in owned source tree')
    if output.exists():
        _require(sidecar.is_file() and N._sha(output)==json.loads(sidecar.read_text())['library_sha256'],
                 'Existing bell input library changed externally; overwrite refused')
    payload=set();targets={}
    for target in ('tc_bell_1','tc_bell_2'):
        report_path=output.parent/(target+'-probe.json');report=json.loads(report_path.read_text())
        source=output.parent/(target+'.blend')
        _require(N._sha(source)==report['saved_file_sha256'],'Retained native probe library fingerprint changed')
        _require(report.get('healthy_bell_subset',{}).get('appearance',{}).get('custom_normals_applied'), 'Actual healthy bell appearance probe missing')
        subset=B.qualified_subset(target)
        fragments=list(N._source_fragments(subset['plan'],N._bindings(N._model(target))))
        bell_indices=[i for i,f in enumerate(fragments) if f[0]['source_name']=='main_dest_bell_01']
        _require(len(bell_indices)==1,'Native damaged bell source fragment ambiguous')
        original_names=dict(healthy=report['healthy_bell_subset']['object_names'][0],
            damaged=report['rigid_views']['source_view_objects'][bell_indices[0]],
            armature=report['explicit_reference_hierarchy']['armature'],
            public=next(g['object'] for g in report['native_public_appearance']['groups'] if g['mesh_index']==0 and g['group_index']==0))
        with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
            _require(all(name in available.objects for name in original_names.values()),'Exact source library IDs missing')
            loaded.objects=list(original_names.values())
        objects=dict(zip(original_names,loaded.objects))
        owner_name=N.PREFIX+'BellLibraryCompile_'+target
        _require(bpy.data.collections.get(owner_name) is None,'Existing owned compiler collection; do not reuse partial data')
        owner=bpy.data.collections.new(owner_name);bpy.context.scene.collection.children.link(owner)
        for obj in objects.values():owner.objects.link(obj)
        healthy,damaged,arm=objects['healthy'],objects['damaged'],objects['armature']
        _require(damaged.parent==arm and damaged.parent_bone=='hlp_main_dest_bell_01','Append lost exact native damaged bell parent')
        # Only actual selected bell pieces. Nonselected donor arch normal failures
        # never enter this preservation pass or output library.
        appearance=A.preserve(target,[objects['public'].name],[healthy.name,damaged.name])
        audit=N.audit_reference_bones(target,arm.name)
        _require(all(x['public_reference_projection_matches'] and x['actual_parent']==x['expected_parent'] for x in audit['bones']), 'Retained reference skeleton changed')
        for role,obj in [('healthy',healthy),('damaged',damaged),('armature',arm)]:
            obj.name='NBI_'+target+'_'+role;obj['native_bell_library_role']=role
            obj['native_bell_library_target']=target;obj['retained_native_dependency']=True
            obj['native_probe_owner']=owner_name
        mesh_audits=[_audit_mesh(target,healthy,'healthy'),_audit_mesh(target,damaged,'damaged')]
        pose=N.pose_probe(arm.name,'hlp_main_dest_bell_01',[healthy.name,damaged.name])
        _require(pose['reference_restored'] and all(x['movement_partition_matches'] for x in pose['rigid_movement_partition']), 'Selected bell pose/static partition failed')
        images=_image_dependencies([healthy,damaged],source)
        contract=dict(target=target,model=N._model(target),source_probe=str(report_path),source_probe_sha256=N._sha(report_path),
            source_library=str(source),source_library_sha256=N._sha(source),
            objects={role:obj.name for role,obj in [('healthy',healthy),('damaged',damaged),('armature',arm)]},
            mesh_audits=mesh_audits,appearance=appearance,reference_bone_audit=audit,reversible_pose=pose,image_dependencies=images,
            native_rgm_sha256=subset['plan']['skeleton']['source_sha256'],public_plan_sha256=N._sha(subset['plan']['manifest_path']),
            declared_dependency_manifest=str(N.INVENTORY/'mechanism-composition/town_center.json'),
            native_source_state_contract=B.family_attachment_plan('A1')['source_state_contract'],
            original_donor_arch_geometry_included=False,clips_created=False,native_playback_qualified=False)
        for obj in (healthy,damaged,arm):obj['native_bell_compiled_contract_json']=json.dumps(contract)
        text=bpy.data.texts.new('NBI_'+target+'_NativeDependencyContract.json');text.write(json.dumps(contract,indent=2))
        payload.update({healthy,damaged,arm,text});targets[target]=contract
    document=dict(schema='ccp.persia.native-bell-input-library/v1',library_path=str(output),targets=targets,
        source_only=True,source_vertex_data_preserved=True,no_Garrison_API_calls=True,clips_created=False,
        all_body_alternatives={k:B.family_attachment_plan(k) for k in ('A1','A2','A3','A4')})
    output.parent.mkdir(exist_ok=True,parents=True)
    bpy.data.libraries.write(str(output),payload,path_remap='RELATIVE',fake_user=True,compress=True)
    document['library_sha256']=N._sha(output)
    sidecar.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
    return document


def append_inputs(target, library_path=None):
    """Cold factory route: append only selected mesh/rig IDs, with unique data."""
    import bpy
    path=Path(library_path or DEFAULT_LIBRARY).resolve();sidecar=path.with_suffix('.json')
    document=json.loads(sidecar.read_text(encoding='utf-8'))
    _require(document['schema']=='ccp.persia.native-bell-input-library/v1' and N._sha(path)==document['library_sha256'],'Qualified bell library hash mismatch')
    contract=document['targets'][target]
    subset=B.qualified_subset(target)
    _require(subset['plan']['skeleton']['source_sha256']==contract['native_rgm_sha256'] and N._sha(subset['plan']['manifest_path'])==contract['public_plan_sha256'],'Native inputs changed since compilation')
    binding=N._bindings(N._model(target))
    geometry_sha=subset['plan']['resources']['geometry']['sha256']
    geometry_path=Path(binding['native_rrgeom_local_path'])
    _require(geometry_sha==binding['native_rrgeom_sha256'] and geometry_path.is_file()
             and N._sha(geometry_path)==geometry_sha,'Exact retained RRGeom provenance mismatch')
    roles=list(contract['objects'])
    with bpy.data.libraries.load(str(path),link=False) as (available,loaded):
        _require(all(contract['objects'][role] in available.objects for role in roles),'Compiled bell IDs missing')
        loaded.objects=[contract['objects'][role] for role in roles]
    objects=dict(zip(roles,loaded.objects))
    token=0
    while bpy.data.collections.get(N.PREFIX+target+'_FactoryInputs'+str(token)):token+=1
    prefix=N.PREFIX+target+'_FactoryInputs'+str(token)
    healthy_collection=bpy.data.collections.new(prefix+'_Healthy');bpy.context.scene.collection.children.link(healthy_collection)
    reference=bpy.data.collections.new(prefix+'_Reference');bpy.context.scene.collection.children.link(reference)
    for role,obj in objects.items():
        _require(obj.get('native_bell_library_role')==role and obj.get('native_bell_library_target')==target,'Compiled role/target ID changed')
        obj.data=obj.data.copy()  # unique editable mesh/rig per family body
        (healthy_collection if role=='healthy' else reference).objects.link(obj)
        obj['native_probe_owner']=prefix;obj['retained_native_dependency']=True
        obj['native_bell_compiled_library_sha256']=document['library_sha256']
        if role in ('healthy','damaged'):
            # Original complete RRGeom resource hash, not a digest fabricated
            # from this selected subset or its transformed Blender vertices.
            obj['native_source_geometry_sha256']=geometry_sha
            obj['native_source_geometry_path']=str(geometry_path)
            obj['native_source_geometry_provenance']='Exact retained RRGeom bytes; subset identity audited separately'
    _require(objects['damaged'].parent==objects['armature'],'Cold append lost native parent linkage')
    images=_image_dependencies([objects['healthy'],objects['damaged']],path)
    mesh_audits=[_audit_mesh(target,objects['healthy'],'healthy'),_audit_mesh(target,objects['damaged'],'damaged')]
    bone_audit=N.audit_reference_bones(target,objects['armature'].name)
    _require(all(x['public_reference_projection_matches'] and x['actual_parent']==x['expected_parent'] for x in bone_audit['bones']), 'Cold append bone reference changed')
    return dict(target=target,healthy_view={'collection':healthy_collection.name,'object_names':[objects['healthy'].name]},
        reference_collection=reference.name,armature=objects['armature'].name,damaged_bell_object=objects['damaged'].name,
        appearance_contract={'route':'Hash-qualified retained bell input library; original nodes/images/custom normals preserved',
            'mesh_audits':mesh_audits,'image_dependencies':images},reference_bone_audit=bone_audit,
        source_library=str(path),source_library_sha256=document['library_sha256'],Garrison_API_invoked=False)


def append_and_attach(H,body_key,target,inventory_category,library_path=None):
    """Factory entry: no native decode/import/API dependency or vertex baking."""
    prepared=append_inputs(target,library_path)
    result=B.attach_call_frame(H,body_key,target,inventory_category,[],prepared['armature'],prepared_inputs=prepared)
    result['factory_input_library']=prepared['source_library']
    result['factory_input_library_sha256']=prepared['source_library_sha256']
    result['Garrison_API_invoked']=False
    return result
