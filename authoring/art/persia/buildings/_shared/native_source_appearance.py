"""Strict parent-run native source material/normal preservation, no auto ops.

Call inspect_public_groups first (read only), then preserve with explicit import
IDs and source-view IDs. No Blender import-time side effects or material guesses.
"""
import json
import math
from pathlib import Path
import native_mechanisms as N

# Source-view fidelity policy, not bit-identical Blender storage. Blender5.2
# encodes custom normals as a short2 corner-fan angular representation, uses
# approximate acos and a 1-1e-4 trigonometric branch threshold. Exact raw native
# normals remain authoritative. See inventory/NORMAL_FIDELITY_CONTRACT.md.
NORMAL_ANGULAR_LIMIT_DEGREES=.1


def angular_error_degrees(a,b):
    """Double-precision normalized atan2 metric; robust near parallel vectors."""
    la=math.sqrt(sum(x*x for x in a));lb=math.sqrt(sum(x*x for x in b))
    _require(la>1e-12 and lb>1e-12,'Zero normal cannot be a qualified source-view direction')
    a=[x/la for x in a];b=[x/lb for x in b]
    cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    return math.degrees(math.atan2(math.sqrt(sum(x*x for x in cross)),max(-1.,min(1.,sum(x*y for x,y in zip(a,b))))))


def _require(value, message):
    if not value:
        raise RuntimeError(message)


def _groups(target, manifest_path=None):
    plan=N.retained_plan(target,manifest_path)
    N._assert_plan_fingerprint(plan,N._bindings(N._model(target)))
    source=plan['material']['source']
    _require(Path(source['path']).is_file() and N._sha(source['path'])==source['sha256'], 'Native RRMaterial source hash changed')
    groups=plan['geometry']['groups']
    _require(len({(g['mesh_index'],g['group_index']) for g in groups})==len(groups),'Duplicate native mesh/group key')
    slots={}
    maps=(plan.get('structure_collection_contract') or {}).get('maps',[])
    if maps:
        _require(plan['structure_collection_contract']['source']['sha256']==plan['skeleton']['source_sha256'], 'MSCL material contract/RGM source mismatch')
    collection_groups=[g for g in groups if g.get('collection_bone_indices')]
    cursor=0
    for mapping in maps:
        for group in collection_groups[cursor:cursor+mapping['geometry_group_span']]:
            _require(group['effect'].lower()==mapping['effect'].lower(),'Collection effect/group join mismatch')
            slots[(group['mesh_index'],group['group_index'])]=(mapping['slot'],'exact_native_MSCL_collection_slot')
        cursor+=mapping['geometry_group_span']
    _require(cursor==len(collection_groups),'Unaccounted collection material group')
    for group in groups:
        key=(group['mesh_index'],group['group_index'])
        if key not in slots:
            _require(group.get('preview_material_confidence')=='confirmed_gohd' and group.get('material')==group.get('preview_material'),
                     'No confirmed GOHD/native collection material identity for '+str(key))
            slots[key]=(group['material'],'confirmed_GOHD')
    native_names={m['name'] for m in plan['material']['materials']}
    _require(all(slot in native_names for slot,_ in slots.values()),'Collection/GOHD slot absent from native RRMaterial')
    return plan,{(g['mesh_index'],g['group_index']):g for g in groups},slots


def inspect_public_groups(target, public_object_names, manifest_path=None):
    """Read-only actual public ID/material binding inventory; safe diagnostic."""
    contract_error=None
    try:
        plan,groups,slots=_groups(target,manifest_path)
    except RuntimeError as exc:
        # Inspection must still report actual public IDs for a quarantined plan;
        # only preserve() needs full admission and never takes this fallback.
        plan=N.retained_plan(target,manifest_path);slots={};contract_error=str(exc)
    objects=N._owned_objects(public_object_names)
    result=[]
    for obj in objects:
        if obj.type!='MESH' or 'garrison_mesh_index' not in obj or 'garrison_group_index' not in obj:
            continue  # excludes pose-control display meshes
        key=(int(obj['garrison_mesh_index']),int(obj['garrison_group_index']))
        used=sorted({p.material_index for p in obj.data.polygons})
        materials=[]
        for index in used:
            material=obj.data.materials[index] if index<len(obj.data.materials) else None
            images=[]
            if material and material.use_nodes:
                for node in material.node_tree.nodes:
                    image=getattr(node,'image',None)
                    if image:images.append(dict(node=node.name,image=image.name,filepath=image.filepath,packed=bool(image.packed_file)))
            materials.append(dict(slot=index,name=material.name if material else None,
                custom_properties={k:material[k] for k in material.keys()} if material else {},images=images))
        result.append(dict(object=obj.name,mesh_index=key[0],group_index=key[1],
            garrison_logical_path=obj.get('garrison_logical_path'),
            garrison_material_slot=obj.get('garrison_material_slot'),
            garrison_material_assignment_confidence=obj.get('garrison_material_assignment_confidence'),
            expected_native_slot=slots.get(key),materials=materials,
            polygon_material_indices=used,vertices=len(obj.data.vertices),polygons=len(obj.data.polygons)))
    return dict(target=target,groups=result,read_only=True,manifest_path=plan['manifest_path'],
                source_contract_error=contract_error)


def _fragments(target,plan):
    if target=='lumber_crane':
        import native_skin_sources as S
        _,fragments,_=S._collection_subset(plan,N._bindings(N._model(target)))
    else:
        fragments=list(N._source_fragments(plan,N._bindings(N._model(target))))
    return fragments


def _view_join(obj, groups, fragments, target=None):
    candidates=[]
    for record,group,used,triangles in fragments:
        if record['source_name']==obj.get('native_source_name'):
            candidates.append((group,used,triangles))
    for group in groups.values():
        if group['name']==obj.get('native_SKMS_name'):
            candidates.append((group,list(range(len(group['positions']))),group['triangles']))
    if obj.get('native_exact_bell_healthy_subset'):
        import native_bell_sources as B
        subset=B.qualified_subset(target)
        candidates.append((subset['group'],subset['used'],subset['triangles']))
    matches=[]
    for group,used,triangles in candidates:
        if len(used)!=len(obj.data.vertices):continue
        if any(max(abs(v.co[a]-group['positions'][old][a]) for a in range(3))>1e-6 for v,old in zip(obj.data.vertices,used)):continue
        projected=[list(t) for t in triangles if len(set(t))==3]
        actual=[list(p.vertices) for p in obj.data.polygons]
        if actual!=projected:continue
        matches.append((group,used))
    _require(len(matches)==1,'Source view requires one exact source-name/vertex/topology join: '+obj.name)
    return matches[0]


def material_identity(properties, plan):
    """Exact observed public material contracts, not a Blender datablock name.

    Supports the two actually inspected graph schemas. Class/name and native
    RRMaterial content hash identify one native entry. Structure parameters and
    textures are additionally compared to their complete native block records.
    """
    _require(properties.get('garrison_rrmaterial_sha256')==plan['material']['source']['sha256'],
             'Public material RRMaterial content hash mismatch')
    key=('garrison_structure_preview_contract_json' if 'garrison_structure_preview_contract_json' in properties
         else 'garrison_generic_preview_contract_json')
    _require(key in properties,'Public material lacks an inspectable native identity contract')
    contract=json.loads(properties[key])
    _require(contract.get('schema') in ('garrison.structure-preview-graph/v2','garrison.generic-material-preview/v4'),
             'Unqualified public material identity schema')
    name=contract.get('material_name');kind=contract.get('material_class')
    native=[m for m in plan['material']['materials'] if m['name']==name and m['class']==kind]
    _require(len(native)==1 and properties.get('garrison_material_class')==kind,'Material name/class does not join one native RRMaterial entry')
    if key=='garrison_structure_preview_contract_json':
        params=[x for block in native[0]['blocks'] for x in block.get('parameters',[])]
        textures=[x for block in native[0]['blocks'] for x in block.get('textures',[])]
        _require(json.loads(properties.get('garrison_parameters_json','null'))==params and
                 json.loads(properties.get('garrison_texture_bindings_json','null'))==textures,
                 'Complete structure parameter/texture records disagree with native material')
    return dict(name=name,material_class=kind,rrmaterial_sha256=properties['garrison_rrmaterial_sha256'],schema=contract['schema'])


def _material_pool(public,plan):
    pool={}
    for obj in public:
        if obj.type!='MESH' or 'garrison_mesh_index' not in obj:continue
        for index in {p.material_index for p in obj.data.polygons}:
            _require(index<len(obj.data.materials) and obj.data.materials[index] is not None,'Public material slot absent')
            material=obj.data.materials[index]
            identity=material_identity({k:material[k] for k in material.keys()},plan)
            bucket=pool.setdefault(identity['name'],[])
            if not any(entry[0]==material for entry in bucket):bucket.append((material,obj.name,identity))
    return pool


def preserve(target, public_object_names, source_object_names, manifest_path=None):
    """Apply original material datablocks and exact native custom loop normals.

    Validate ALL joins/materials/normals before mutation. Original public objects,
    material nodes and texture references remain identical. Multiple used material
    slots require a qualified face join and fail here; no cyclic/name guesses.
    """
    import bpy
    from mathutils import Vector
    plan,groups,slots=_groups(target,manifest_path)
    public=N._owned_objects(public_object_names)
    views=N._owned_objects(source_object_names)
    fragments=_fragments(target,plan)
    pool=_material_pool(public,plan)
    pending=[]
    for obj in views:
        if obj.type!='MESH':continue
        group,used=_view_join(obj,groups,fragments,target)
        key=(group['mesh_index'],group['group_index'])
        imported=[o for o in public if o.type=='MESH' and
            o.get('garrison_mesh_index')==key[0] and o.get('garrison_group_index')==key[1]]
        _require(len(imported)==1,'Ambiguous/missing exact public group '+str(key))
        original=imported[0]
        _require(str(original.get('garrison_logical_path','')).lower()==N._model(target),'Public mesh model identity mismatch')
        expected,authority=slots[key]
        used_materials={p.material_index for p in original.data.polygons}
        _require(len(used_materials)==1,'Mixed native material faces require exact per-face join; refusing '+original.name)
        material_index=next(iter(used_materials))
        _require(material_index<len(original.data.materials) and original.data.materials[material_index] is not None,'Missing original public material')
        choices=pool.get(expected,[])
        _require(len(choices)==1,'Need one exact hash/class/contract-identified public material for native slot '+expected)
        material,material_source,identity=choices[0]
        # The actual Lumber public projector assigned two cyclic fallback slots
        # in reverse. Correct only the new view via exact native MSCL authority;
        # retain the original imported group/data as unmodified evidence.
        public_slot=original.get('garrison_material_slot')
        if public_slot!=expected:
            _require(original.get('garrison_material_assignment_confidence')=='inferred_cyclic_slot' and
                     authority=='exact_native_MSCL_collection_slot', 'Unexpected non-cyclic public/native material disagreement')
        normals=group.get('normals',[])
        _require(len(normals)==len(group['positions']) and all(len(n)==3 and all(math.isfinite(x) for x in n) and sum(x*x for x in n)>1e-12 for n in normals),
            'Native normal array incomplete/nonfinite/zero')
        _require(callable(getattr(obj.data,'normals_split_custom_set',None)),'Blender custom loop-normal API unavailable')
        corners=[tuple(Vector(normals[used[loop.vertex_index]]).normalized()) for loop in obj.data.loops]
        _require(len(corners)==len(obj.data.loops),'Native corner-normal join incomplete')
        pending.append((obj,group,used,original,material,corners,expected,authority,material_source,identity))
    result=[]
    try:
        for obj,group,used,original,material,corners,expected,authority,material_source,identity in pending:
            obj.data.materials.clear()
            obj.data.materials.append(material)  # identical editable nodes/images, never a guessed replacement
            for poly in obj.data.polygons:poly.material_index=0;poly.use_smooth=True
            obj.data.normals_split_custom_set(corners)
            obj.data.update()
            actual=[tuple(n.vector) for n in obj.data.corner_normals]
            errors=[max(abs(a[i]-b[i]) for i in range(3)) for a,b in zip(actual,corners)]
            residual=max(errors,default=0)
            _require(all(all(math.isfinite(x) for x in v) for v in actual),'Nonfinite Blender corner normal')
            angles=[angular_error_degrees(a,b) for a,b in zip(actual,corners)]
            maximum_angle=max(angles,default=0)
            maximum_length_error=max((abs(math.sqrt(sum(x*x for x in a))-1) for a in actual),default=0)
            face_by_loop={i:p for p in obj.data.polygons for i in p.loop_indices}
            zero_area=[]
            for poly in obj.data.polygons:
                coords=[obj.data.vertices[i].co for i in poly.vertices]
                if len(coords)!=3 or (coords[1]-coords[0]).cross(coords[2]-coords[0]).length<=1e-12:
                    zero_area.append(poly.index)
            worst=[]
            for index in sorted(range(len(errors)),key=lambda i:errors[i],reverse=True)[:8]:
                poly=face_by_loop[index]
                worst.append(dict(loop=index,polygon=poly.index,vertex=obj.data.loops[index].vertex_index,
                    maximum_component_error=errors[index],expected=list(corners[index]),actual=list(actual[index]),
                    angular_error_degrees=angles[index],
                    actual_length=Vector(actual[index]).length,dot_expected_actual=Vector(actual[index]).dot(Vector(corners[index])),
                    polygon_area=poly.area,polygon_normal=list(poly.normal),degenerate_polygon=poly.index in zero_area))
            audit=dict(object=obj.name,mesh_index=group['mesh_index'],group_index=group['group_index'],
                api='Mesh.normals_split_custom_set(corner_vectors); Mesh.update(); Mesh.corner_normals[].vector',
                expected_corner_count=len(corners),actual_corner_count=len(actual),maximum_component_error=residual,
                corners_exceeding_original_provisional_component_tolerance=sum(e>=.0002 for e in errors),
                maximum_angular_error_degrees=maximum_angle,angular_fidelity_limit_degrees=NORMAL_ANGULAR_LIMIT_DEGREES,
                maximum_normal_length_error=maximum_length_error,raw_native_normals_authoritative=True,
                Blender_normals_mathematically_identical=False,
                native_normal_attribute_retained='native_reference_normal' in obj.data.attributes,
                has_custom_normals=obj.data.has_custom_normals,
                normals_domain=getattr(obj.data,'normals_domain',None),
                polygon_count=len(obj.data.polygons),degenerate_polygon_indices=zero_area,worst_corners=worst)
            obj['native_custom_normals_audit_json']=json.dumps(audit)
            _require(len(actual)==len(corners) and maximum_angle<=NORMAL_ANGULAR_LIMIT_DEGREES and maximum_length_error<.0001,
                'Applied custom normal mismatch; raw retained; exact audit='+json.dumps(audit,separators=(',',':')))
            obj['native_mesh_index']=group['mesh_index'];obj['native_group_index']=group['group_index']
            obj['native_source_vertex_indices_json']=json.dumps(used)
            obj['native_material_public_object']=original.name
            obj['native_material_datablock_source_public_object']=material_source
            obj['native_material_public_assigned_slot']=str(original.get('garrison_material_slot'))
            obj['native_material_public_cyclic_assignment_corrected_on_view_only']=original.get('garrison_material_slot')!=expected
            obj['native_material_exact_identity_json']=json.dumps(identity)
            obj['native_material_identity']=expected
            obj['native_material_identity_authority']=authority
            obj['native_material_original_datablock']=material.name
            obj['native_custom_normals_applied']=True
            obj['native_custom_normals_maximum_error']=residual
            obj['native_custom_normals_maximum_angular_error_degrees']=maximum_angle
            obj['native_custom_normals_raw_data_authoritative']=True
            result.append(dict(object=obj.name,public_group=original.name,material=material.name,
                native_slot=expected,authority=authority,material_source_public_object=material_source,
                original_public_assigned_slot=original.get('garrison_material_slot'),
                public_cyclic_assignment_corrected_on_view_only=original.get('garrison_material_slot')!=expected,
                exact_material_identity=identity,custom_normal_corners=len(corners),maximum_normal_error=residual,
                maximum_normal_angular_error_degrees=maximum_angle,normal_angular_limit_degrees=NORMAL_ANGULAR_LIMIT_DEGREES,
                raw_normal_attribute_retained='native_reference_normal' in obj.data.attributes))
    except Exception as exc:
        for obj,*_ in pending:
            obj['native_appearance_quarantined']=True
            obj['native_appearance_failure']=str(exc)
        raise
    return dict(target=target,objects=result,original_material_datablocks_shared=True,
        original_nodes_and_texture_references_preserved=True,custom_normals_applied=True,
        native_engine_shader_equivalence_qualified=False,clips_created=False)
