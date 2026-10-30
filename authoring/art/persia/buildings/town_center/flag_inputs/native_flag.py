"""Cached native flag rest source. No Garrison, decode or Blender at import time.

Parent executes compile_library in a factory process, then cold attach() calls.
Sails engine motion is retained as native input, never fabricated as an armature.
"""
from pathlib import Path
import hashlib,json,math

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/'source-contract.json'
LIBRARY=ROOT/'native_flag_inputs.blend'

def require(value,message):
    if not value:raise RuntimeError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inputs():
    c=json.loads(CONTRACT.read_text())
    for row in c['retained_files']:
        require(Path(row['path']).is_file() and sha(row['path'])==row['sha256'],'Native flag dependency changed: '+row['path'])
    p=json.loads(Path(c['public_plan_path']).read_text())
    require(sha(c['public_plan_path'])==c['public_plan_sha256'],'Flag plan changed')
    return c,p

def _material(bpy,plan):
    """Inspectable primary native atlas preview, with ALL original inputs kept.

    Layered Sails shading/char/wind is deliberately not reimplemented here.
    """
    materials=plan['material']['materials'];require(len(materials)==1,'Expected exact single flags material')
    raw=materials[0];require(raw['name']=='flags' and raw['class']=='sails','Native material identity changed')
    mat=bpy.data.materials.new('NativeFlag_flags_Sails_RestAtlas');mat.use_nodes=True
    mat['native_material_name']=raw['name'];mat['native_material_class']=raw['class']
    mat['native_rrmaterial_sha256']=plan['material']['source']['sha256']
    mat['native_material_complete_parameters_json']=json.dumps(raw)
    mat['native_material_preview_scope']='Primary original albedo/alpha/normal rest-atlas preview only; layered Sails/wind/char not reproduced'
    tree=mat.node_tree;tree.nodes.clear();out=tree.nodes.new('ShaderNodeOutputMaterial');shader=tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Roughness'].default_value=.8;tree.links.new(shader.outputs['BSDF'],out.inputs['Surface'])
    uv=tree.nodes.new('ShaderNodeUVMap');uv.uv_map='UVMap';exact={}
    for bi,block in enumerate(raw['blocks']):
        frame=tree.nodes.new('NodeFrame');frame.label=block['name'];frame.name=block['name']
        frame['native_parameters_json']=json.dumps(block['parameters'])
        for ti,texture in enumerate(block['textures']):
            path=texture.get('projection_path')
            if not path:
                node=tree.nodes.new('NodeFrame');node.name=f'Unprojected_{bi}_{ti}';node.label=texture['name']+' (original native reference retained)'
                node['native_texture_record_json']=json.dumps(texture);node.parent=frame;continue
            image=bpy.data.images.load(str(Path(path).resolve()),check_existing=True)
            name=texture['name'];node=tree.nodes.new('ShaderNodeTexImage');node.image=image;node.name=f'Native_{bi}_{ti}_{name}';node.label=name;node.parent=frame
            node['native_texture_record_json']=json.dumps(texture);tree.links.new(uv.outputs['UV'],node.inputs['Vector'])
            if name not in ('albedoTex','albedoTex2','overlay1Albedo','overlay2Albedo','albedoTexCharred'):image.colorspace_settings.name='Non-Color'
            require(name not in exact or name=='__default','Unexpected duplicate native texture slot');exact[name]=node
    require('albedoTex' in exact and 'maskAlpha' in exact,'Original rest atlas/alpha projections missing')
    tree.links.new(exact['albedoTex'].outputs['Color'],shader.inputs['Base Color'])
    # Native maskAlpha is retained as RGB mask texture; red channel preview is
    # explicit source visualization, not claimed native layered shader parity.
    separate=tree.nodes.new('ShaderNodeSeparateColor');tree.links.new(exact['maskAlpha'].outputs['Color'],separate.inputs['Color'])
    tree.links.new(separate.outputs['Red'],shader.inputs['Alpha']);mat.surface_render_method='DITHERED'
    if 'normalMap' in exact:
        normal=tree.nodes.new('ShaderNodeNormalMap');tree.links.new(exact['normalMap'].outputs['Color'],normal.inputs['Color']);tree.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
    mat.use_backface_culling=False
    return mat

def audit(ob,plan):
    group=plan['geometry']['groups'][0];mesh=ob.data
    require(len(mesh.vertices)==414 and len(mesh.polygons)==304,'Native flag geometry count changed')
    require([list(p.vertices) for p in mesh.polygons]==group['triangles'],'Native flag topology changed')
    pe=max(abs(v.co[a]-p[a]) for v,p in zip(mesh.vertices,group['positions']) for a in range(3))
    layer=mesh.uv_layers['UVMap'];uv=max(abs(layer.data[l.index].uv[a]-group['uv_layers']['UVMap'][l.vertex_index][a]) for l in mesh.loops for a in (0,1))
    raw=mesh.attributes['native_reference_normal'];ne=max(abs(v.vector[a]-n[a]) for v,n in zip(raw.data,group['normals']) for a in range(3))
    require(pe<1e-7 and uv<1e-7 and ne<1e-7,'Exact flag positions/UV/raw normals changed')
    angles=[]
    for loop,normal in zip(mesh.loops,mesh.corner_normals):
        native=group['normals'][loop.vertex_index];n=normal.vector;length=math.sqrt(sum(x*x for x in native))
        require(length>0,'Invalid zero native flag normal')
        cosine=sum(n[a]*native[a] for a in range(3))/(length*n.length)
        angles.append(math.degrees(math.acos(max(-1,min(1,cosine)))))
    require(max(angles,default=0)<=.1,'Flag custom normal storage fidelity failed')
    require(not ob.modifiers and not ob.vertex_groups and ob.parent is None,'No fabricated native flag rig')
    mat=mesh.materials[0];rawmat=json.loads(mat['native_material_complete_parameters_json'])
    require(rawmat==plan['material']['materials'][0] and mat['native_rrmaterial_sha256']==plan['material']['source']['sha256'],'Native flag material identity/parameters lost')
    return dict(vertices=414,triangles=304,position_max_error=pe,UV_max_error=uv,raw_normal_max_error=ne,
        maximum_custom_normal_angle_degrees=max(angles,default=0),native_skeleton_bones=0,
        rest_atlas_preview='Original primary albedo + maskAlpha red + normalMap; layered Sails parity unqualified',
        native_wind_playback_qualified=False,passed=True)

def compile_library():
    import bpy
    require(bpy.app.background and not bpy.data.filepath,'Use a dedicated unsaved factory process')
    c,p=inputs();g=p['geometry']['groups'][0]
    require(g['stream']=='SailsPositionDataStream' and g['projection_kind']=='sail_surface_without_deformation','Unexpected flag stream projection')
    mesh=bpy.data.meshes.new('NativeFlag_ExactRestGeometry');mesh.from_pydata(g['positions'],[],g['triangles']);mesh.update()
    layer=mesh.uv_layers.new(name='UVMap')
    for loop in mesh.loops:layer.data[loop.index].uv=g['uv_layers']['UVMap'][loop.vertex_index]
    raw=mesh.attributes.new('native_reference_normal','FLOAT_VECTOR','POINT')
    for row,n in zip(raw.data,g['normals']):row.vector=n
    mesh.normals_split_custom_set([g['normals'][l.vertex_index] for l in mesh.loops]);mesh.update()
    ob=bpy.data.objects.new('NativeFlag_ExactRest',mesh);bpy.context.scene.collection.objects.link(ob);mesh.materials.append(_material(bpy,p))
    ob['retained_native_dependency']=True;ob['native_source_geometry_sha256']=c['native_rrgeom_sha256']
    ob['native_source_model']=c['model'];ob['native_effect']='Sails';ob['native_stream']='SailsPositionDataStream'
    ob['native_source_contract_json']=json.dumps(c);ob['native_material_wind_playback_qualified']=False
    result=audit(ob,p)
    text=bpy.data.texts.new('NativeFlag_SourceContract.json');text.write(json.dumps(c,indent=2))
    # Raw SailsPositionDataStream bytes are retained unchanged in hashed RRGeom;
    # the projected mesh intentionally contains inspectable rest coordinates.
    bpy.data.libraries.write(str(LIBRARY),{ob,text},path_remap='RELATIVE',fake_user=True,compress=True)
    receipt=dict(schema='ccp.persia.native-flag-library/v1',library=str(LIBRARY),library_sha256=sha(LIBRARY),
        contract_sha256=sha(CONTRACT),object=ob.name,text=text.name,audit=result,
        complete_native_stream_preserved_in_hashed_RRGeom=True,clips_created=False)
    LIBRARY.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

def attach(collection,matrix,label,selection_note):
    """Parent source assembly chooses placement/visibility; no vertex bake.

    matrix is projected model->authored source frame. Native stamp alternatives
    live in the source contract and are not silently selected here.
    """
    import bpy
    from mathutils import Matrix,Quaternion,Vector
    require(selection_note and len(selection_note)>12,'Explicit source selector/placement decision required')
    c,p=inputs();r=json.loads(LIBRARY.with_suffix('.json').read_text())
    require(sha(LIBRARY)==r['library_sha256'] and sha(CONTRACT)==r['contract_sha256'],'Flag library/contract fingerprint changed')
    with bpy.data.libraries.load(str(LIBRARY),link=False) as (_,loaded):loaded.objects=[r['object']]
    ob=loaded.objects[0];ob.data=ob.data.copy();collection.objects.link(ob);ob.name=label+'_NativeFlag';audit(ob,p)
    root=bpy.data.objects.new(label+'_NativeFlagRoot',None);collection.objects.link(root);root.matrix_world=Matrix(matrix)
    ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=Matrix.Identity(4)
    marker=c['native_markers']['markers'][0];require(marker['native_frame_flag']==0 and not marker['parent_bone'],'Root marker required')
    q=marker['quaternion_xyzw'];local=Matrix.LocRotScale(Vector(marker['translation']),Quaternion((q[3],q[0],q[1],q[2])),Vector(marker['scale']))
    B=Matrix(((-1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
    socket=bpy.data.objects.new(label+'_'+marker['name'],None);collection.objects.link(socket);socket.parent=root;socket.matrix_basis=B@local@B.inverted()
    socket['native_raw_marker_json']=json.dumps(marker);socket['native_marker_frame']='Projected model-root; not actor-world or playback proof'
    for obj in (root,ob,socket):obj['native_flag_source_selection_note']=selection_note;obj['native_flag_contract_sha256']=sha(CONTRACT)
    return dict(root=root.name,mesh=ob.name,wind_marker=socket.name,visible_triangles=304,
        native_skeleton_bones=0,native_wind_playback_qualified=False,
        placement='Exact object hierarchy matrix; native vertices/pivots unchanged')

if __name__=='__main__':print(json.dumps(compile_library(),indent=2))
