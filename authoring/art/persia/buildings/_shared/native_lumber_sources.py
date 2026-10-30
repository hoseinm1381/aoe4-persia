"""Bounded Lumber source library/assembly adapter. Parent executes Blender calls.

No Garrison API, new native clips, native mutation or import-time Blender work.
Exact full native reference library remains separate from selected active inputs.
"""
from pathlib import Path
import json, math
from contextlib import contextmanager
import native_mechanisms as N
import native_skin_sources as S
import native_source_appearance as A
TARGET='lumber_crane'
LIBRARY=N.BUILDINGS/'_shared/mechanisms/lumber_functional_inputs.blend'
PARTITION=N.INVENTORY/'LUMBER_FUNCTIONAL_SOURCE_PARTITION.json'
SELECTED=(0,1,3,5,7)
WHEEL=(0,1,3,5)

def require(value,message):
 if not value:raise RuntimeError(message)
@contextmanager
def visible_collections(*collections):
 """Temporary probe visibility; restores the source presentation afterwards."""
 import bpy
 saved={}
 def visit(c):
  if c.as_pointer() in saved:return
  saved[c.as_pointer()]=(c,c.hide_viewport,c.hide_render)
  c.hide_viewport=False;c.hide_render=False
  for child in c.children:visit(child)
 for c in collections:visit(c)
 bpy.context.view_layer.update()
 try:yield
 finally:
  for c,viewport,render in saved.values():c.hide_viewport=viewport;c.hide_render=render
  bpy.context.view_layer.update()
def _sources():
 plan=N.retained_plan(TARGET);binding=N._bindings(N._model(TARGET));sub,fragments,_=S._collection_subset(plan,binding)
 return plan,binding,{r['source_index']:(r,g,used,tris) for r,g,used,tris in fragments}
def triangles(obj):return sum(len(p.vertices)-2 for p in obj.data.polygons)
def _meta(obj,role,index=None):
 _,binding,_=_sources();obj['retained_native_dependency']=True;obj['native_lumber_role']=role
 obj['native_source_geometry_sha256']=binding['native_rrgeom_sha256'];obj['native_probe_model']=N._model(TARGET)
 obj['native_lumber_source_index']=-1 if index is None else index
 obj['native_source_numeric_frame']='Exact public projected model reference; not runtime world'
 obj['native_original_full_reference_library']=str(LIBRARY.parent/'lumber_crane.blend')
 obj['native_original_vertices_preserved']=True

def audit_exact(obj,role,index=None):
 plan,binding,sources=_sources()
 if role=='skin':
  group=next(g for g in plan['geometry']['groups'] if g['name']==S.SKIN_NAME);used=list(range(len(group['positions'])));tris=group['triangles']
 else:_,group,used,tris=sources[index]
 require(obj.type=='MESH' and len(obj.data.vertices)==len(used),'Native Lumber vertex count changed')
 require([list(p.vertices) for p in obj.data.polygons]==tris,'Native Lumber topology changed')
 pos=max((abs(v.co[a]-group['positions'][old][a]) for v,old in zip(obj.data.vertices,used) for a in range(3)),default=0)
 require(pos<1e-7,'Native Lumber source coordinates changed')
 raw=obj.data.attributes.get('native_reference_normal');require(raw is not None and len(raw.data)==len(used),'Native raw normals missing')
 ne=max((abs(row.vector[a]-group['normals'][old][a]) for row,old in zip(raw.data,used) for a in range(3)),default=0)
 require(ne<1e-7,'Native raw normals changed')
 uv=0
 for name,values in group['uv_layers'].items():
  layer=obj.data.uv_layers.get(name);require(layer is not None,'Native UV layer missing')
  uv=max(uv,max((abs(layer.data[l.index].uv[a]-values[used[l.vertex_index]][a]) for l in obj.data.loops for a in range(2)),default=0))
 require(uv<1e-7,'Native UV data changed')
 angular=max((A.angular_error_degrees(n.vector,group['normals'][used[l.vertex_index]]) for n,l in zip(obj.data.corner_normals,obj.data.loops)),default=0)
 require(angular<=A.NORMAL_ANGULAR_LIMIT_DEGREES,'Native normal angular fidelity failed')
 require(len(obj.data.materials)==1 and {p.material_index for p in obj.data.polygons}=={0},'Native material face join changed')
 mat=obj.data.materials[0];identity=A.material_identity({k:mat[k] for k in mat.keys()},plan)
 require(identity['name']=='crane','Native source material identity changed')
 weights=S.audit_skin_weights(obj.name) if role=='skin' else None
 return dict(object=obj.name,role=role,source_index=index,triangles=triangles(obj),maximum_position_error=pos,
  maximum_raw_normal_error=ne,maximum_UV_error=uv,maximum_custom_normal_angle_degrees=angular,material_identity=identity,weights=weights)

def _images(objects,source):
 import bpy
 seen=set();images={}
 def visit(tree):
  if tree is None or tree.as_pointer() in seen:return
  seen.add(tree.as_pointer())
  for node in tree.nodes:
   im=getattr(node,'image',None)
   if im and im.source=='FILE':images[im.as_pointer()]=im
   visit(getattr(node,'node_tree',None))
 for obj in objects:
  if obj.type=='MESH':
   for m in obj.data.materials:
    if m and m.use_nodes:visit(m.node_tree)
 rows=[]
 for im in images.values():
  raw=im.filepath;p=(source.parent/raw[2:]).resolve() if raw.startswith('//') else Path(bpy.path.abspath(raw)).resolve()
  require(p.is_file(),'Original native image missing: '+str(p));im.filepath=str(p)
  rows.append(dict(image=im.name,path=str(p),sha256=N._sha(p),bytes=p.stat().st_size))
 return rows

def compile_library(output_path=None):
 """Run once in a parent-owned factory process; selects actual qualified IDs."""
 import bpy
 output=Path(output_path or LIBRARY).resolve();require(output.is_relative_to(N.BUILDINGS.resolve()),'Owned output only')
 sidecar=output.with_suffix('.json')
 if output.exists():require(sidecar.is_file() and N._sha(output)==json.loads(sidecar.read_text())['library_sha256'],'Changed existing input library; overwrite refused')
 report_path=LIBRARY.parent/'lumber_crane-probe.json';report=json.loads(report_path.read_text());source=LIBRARY.parent/'lumber_crane.blend'
 require(N._sha(source)==report['saved_file_sha256'],'Qualified source library changed')
 require(report['native_source_appearance']['custom_normals_applied'] and report['skin_weights']['maximum_weight_error']==0,'Actual source appearance/weights qualification missing')
 plan,binding,sources=_sources();_,fragments,_=S._collection_subset(plan,binding)
 names={'armature':report['skin_and_rigid_sources']['armature'],'skin':report['skin_and_rigid_sources']['skin_object']}
 for i,(record,g,used,tris) in enumerate(fragments):
  if record['source_index'] in SELECTED:names['rigid_'+str(record['source_index'])]=report['skin_and_rigid_sources']['rigid_objects'][i]
 require(len(names)==7,'Need exact selected six meshes and five-bone armature')
 with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
  require(all(n in available.objects for n in names.values()),'Qualified native ID missing');loaded.objects=list(names.values())
 objects=dict(zip(names,loaded.objects));owner=N.PREFIX+'LumberFunctionalCompiler'
 collection=bpy.data.collections.new(owner);bpy.context.scene.collection.children.link(collection)
 for role,obj in objects.items():
  collection.objects.link(obj);obj.name='NLF_'+role;obj['native_probe_owner']=owner
  if role!='armature':_meta(obj,'skin' if role=='skin' else 'wheel' if int(role[6:]) in WHEEL else 'payload',None if role=='skin' else int(role[6:]))
 arm=objects['armature'];audits=[audit_exact(o,'skin' if k=='skin' else 'rigid',None if k=='skin' else int(k[6:])) for k,o in objects.items() if k!='armature']
 require(sum(x['triangles'] for x in audits)==1604,'Selected native active count changed')
 reference=N.audit_reference_bones(TARGET,arm.name);require(all(x['public_reference_projection_matches'] and x['actual_parent']==x['expected_parent'] for x in reference['bones']),'Exact reference bones changed')
 require(all(objects[k].parent==arm for k in objects if k.startswith('rigid_')),'Selected rigid parent linkage changed')
 require(objects['skin'].modifiers[0].object==arm,'Native skin modifier lost exact armature')
 poses=[S.skin_pose_probe(objects['skin'].name,arm.name,bone) for bone in ('bone_cable_twist','bone_wheel_base')]
 require(all(x['reversible_source_pose_passed'] for x in poses),'Native skin pose failed')
 rigid_pose=N.pose_probe(arm.name,'bone_wheel',[objects[k].name for k in objects if k.startswith('rigid_')])
 require(rigid_pose['reference_restored'] and all(x['movement_partition_matches'] for x in rigid_pose['rigid_movement_partition']),'Native rigid pose/static partition failed')
 images=_images(list(objects.values()),source)
 contract=dict(schema='ccp.persia.lumber-functional-library/v1',objects={k:o.name for k,o in objects.items()},
  source_library=str(source),source_library_sha256=N._sha(source),source_probe=str(report_path),source_probe_sha256=N._sha(report_path),
  native_rgm_sha256=binding['native_rgm_sha256'],native_rrgeom_sha256=binding['native_rrgeom_sha256'],
  public_plan_path=plan['manifest_path'],public_plan_sha256=N._sha(plan['manifest_path']),partition_path=str(PARTITION),partition_sha256=N._sha(PARTITION),
  audits=audits,reference_bones=reference,skin_pose_checks=poses,rigid_pose=rigid_pose,image_dependencies=images,
  active_triangles=1604,full_native_reference_library_preserved=True,all_five_bones_preserved=True,
  stock_static_timber_triangles_excluded=880,deep_foundation_triangles_excluded=256,clips_created=False,native_playback_qualified=False)
 text=bpy.data.texts.new('NLF_ExactNativeInputs.json');text.write(json.dumps(contract,indent=2))
 for o in objects.values():o['native_lumber_library_contract_json']=json.dumps(contract)
 output.parent.mkdir(exist_ok=True,parents=True);bpy.data.libraries.write(str(output),set(objects.values())|{text},path_remap='RELATIVE',fake_user=True,compress=True)
 contract['library_path']=str(output);contract['library_sha256']=N._sha(output);sidecar.write_text(json.dumps(contract,indent=2)+'\n')
 return contract

def append_inputs(collection,library_path=None):
 import bpy
 path=Path(library_path or LIBRARY);contract=json.loads(path.with_suffix('.json').read_text())
 require(contract['schema']=='ccp.persia.lumber-functional-library/v1' and N._sha(path)==contract['library_sha256'],'Functional library fingerprint mismatch')
 plan,binding,_=_sources();require(binding['native_rrgeom_sha256']==contract['native_rrgeom_sha256'] and N._sha(plan['manifest_path'])==contract['public_plan_sha256'],'Native source plan changed')
 require(N._sha(binding['native_rrgeom_local_path'])==binding['native_rrgeom_sha256'],'Original RRGeom bytes changed')
 require(N._sha(binding['native_rgm_local_path'])==binding['native_rgm_sha256'],'Original RGM bytes changed')
 require(N._sha(PARTITION)==contract['partition_sha256'],'Selected source partition changed')
 keys=list(contract['objects'])
 with bpy.data.libraries.load(str(path),link=False) as (available,loaded):
  require(all(contract['objects'][k] in available.objects for k in keys),'Compiled functional input IDs missing');loaded.objects=[contract['objects'][k] for k in keys]
 objects=dict(zip(keys,loaded.objects))
 for role,obj in objects.items():
  obj.data=obj.data.copy();collection.objects.link(obj);obj['native_probe_owner']=N.PREFIX+collection.name
  obj['native_lumber_compiled_library_sha256']=contract['library_sha256']
  if role!='armature':_meta(obj,'skin' if role=='skin' else 'wheel' if int(role[6:]) in WHEEL else 'payload',None if role=='skin' else int(role[6:]))
 arm=objects['armature'];arm['native_lumber_reference_root']=True
 require(objects['skin'].modifiers[0].object==arm and all(objects[k].parent==arm for k in keys if k.startswith('rigid_')),'Cold append parent/modifier references changed')
 audits=[audit_exact(o,'skin' if k=='skin' else 'rigid',None if k=='skin' else int(k[6:])) for k,o in objects.items() if k!='armature']
 require(sum(x['triangles'] for x in audits)==1604,'Cold active triangle count changed')
 return dict(objects=objects,contract=contract,audits=audits,image_dependencies=_images(list(objects.values()),path))

def bind_original(obj,arm,bone='bone_wheel_base'):
 """Reference-only rigid binding, no geometry bake or fabricated native weights."""
 import bpy
 from mathutils import Matrix
 before=obj.matrix_world.copy();require(max(abs(before[r][c]-int(r==c)) for r in range(4) for c in range(4))<1e-7,'Original members must be authored model-reference geometry')
 obj.parent=arm;obj.parent_type='BONE';obj.parent_bone=bone;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
 bpy.context.view_layer.update();effective=obj.matrix_world.copy();obj.matrix_parent_inverse=effective.inverted();obj.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
 error=max(abs(obj.matrix_world[r][c]-before[r][c]) for r in range(4) for c in range(4))
 require(error<1e-6,'Original support reference parenting moved geometry')
 obj['source_original_reference_bone']=bone;obj['source_original_reference_parent_inverse_json']=json.dumps([list(r) for r in obj.matrix_parent_inverse])
 obj['source_original_reference_binding_error']=error;obj['native_lumber_reference_support']=True
 return dict(object=obj.name,bone=bone,reference_world_matrix_error=error,vertex_bake=False,weights_invented=False)

def attach(H,key,library_path=None):
 import bpy
 collection=H.R.collection(H.R.PREFIX+key+'_healthy_NativeFunctional',H.root(key))
 prepared=append_inputs(collection,library_path);objects=prepared['objects'];arm=objects['armature']
 for role,o in objects.items():
  if role=='armature':continue
  H.tag(o,'walls' if role.startswith('rigid_') and int(role[6:]) in WHEEL else 'finish','native_mechanism','native_functional')
  o['native_lumber_role']='skin' if role=='skin' else 'wheel' if int(role[6:]) in WHEEL else 'payload'
 bound=[bind_original(o,arm) for o in H.root(key).all_objects if o.type=='MESH' and not o.get('retained_native_dependency') and o.get('structural_group') in ('axle_frame','guide_frame') and o.get('role')!='ground']
 for row in H.ANCHORS[key]['native_bearing_candidates']:
  H.interface('NativeWheelBearing'+str(row['native_source_index']),H.obj(row['original_member']),objects['rigid_'+str(row['native_source_index'])],row['point'])
 H.interface('NativeCableGuideSeat',H.obj('GuideLintel'),objects['skin'],H.ANCHORS[key]['native_guide_candidate']['point'])
 native_ids=[o.name for k,o in objects.items() if k!='armature']
 probe=N.pose_probe(arm.name,'bone_wheel',native_ids)
 require(probe['reference_restored'] and all(x['movement_partition_matches'] for x in probe['rigid_movement_partition']),'Active wheel/payload rigid partition failed')
 skin_poses=[S.skin_pose_probe(objects['skin'].name,arm.name,bone) for bone in ('bone_cable_twist','bone_wheel_base')]
 require(all(x['reversible_source_pose_passed'] for x in skin_poses),'Active skin poses failed')
 collection['native_lumber_state_normalized']=True;collection['native_source_state']='healthy'
 H.root(key)['native_lumber_state_normalized']=True;H.root(key)['native_source_state']='healthy'
 arm['native_lumber_body_key']=key
 return dict(active_triangles=1604,armature=arm.name,object_names=native_ids,original_support_bindings=bound,
  library_path=prepared['contract']['library_path'],library_sha256=prepared['contract']['library_sha256'],
  source_geometry_audits=prepared['audits'],skin_pose_checks=skin_poses,rigid_pose=probe,
  frame='Model reference, whole assembly; no vertex transform or native stamp applied',
  clips_created=False,native_physical_pivot_qualified=False,native_sweep_qualified=False,source_acceptance_pending=True)

def selected_source_names(state):
 document=json.loads((N.INVENTORY/'mechanism-composition/lumber_camp.json').read_text())['targets'][0]
 native={'construct_foundation':'construct_20','construct_walls':'construct_40','construct_vaults':'construct_60','construct_finish':'construct_80'}.get(state,state)
 rows=[r for r in document['composition_cases'] if r['context']=={'life_cycle_state':native,'has_collapsed_ruins':'false'}]
 require(len(rows)==1,'Native source membership case missing: '+state);row=rows[0]
 require(row['definite_fragment_ids']==row['possible_fragment_ids'],'Native source membership is uncertain: '+state)
 names={r['id']:r['source_name'] for r in document['source_fragments']}
 return {names[i] for i in row['definite_fragment_ids']}

def _normalize_state(H,key,state,collection):
 """Own rig per source composition; exact native selected geometry members."""
 import bpy
 from mathutils import Matrix
 marker='native_lumber_state_normalized'
 if collection.get(marker):return next(o for o in collection.all_objects if o.type=='ARMATURE' and o.get('native_lumber_reference_root'))
 healthy=H.root(key);old_arm=next(o for o in healthy.all_objects if o.type=='ARMATURE' and o.get('native_lumber_reference_root'))
 arm=old_arm.copy();arm.data=old_arm.data.copy();arm.name=H.R.PREFIX+key+'_'+state+'_ReferenceRig';collection.objects.link(arm)
 arm['native_probe_owner']=N.PREFIX+arm.name
 wanted=selected_source_names(state)
 originals={o.get('native_SKMS_name',o.get('native_source_name')):o for o in healthy.all_objects if o.type=='MESH' and o.get('native_lumber_role')}
 support_originals={}
 for source in healthy.all_objects:
  if source.type=='MESH' and source.get('native_lumber_reference_support'):
   support_originals[source.name]=source;support_originals[source.get('healthy_source',source.name)]=source
 native=[o for o in collection.all_objects if o.type=='MESH' and o.get('native_lumber_role')]
 for o in native:
  name=o.get('native_SKMS_name',o.get('native_source_name'))
  if name not in wanted:
   mesh=o.data;bpy.data.objects.remove(o,do_unlink=True)
   # No cache cleanup. This just removes an incorrect freshly cloned source
   # composition member; its native source/library remains untouched.
 existing={o.get('native_SKMS_name',o.get('native_source_name')) for o in collection.all_objects if o.type=='MESH' and o.get('native_lumber_role')}
 for name in wanted & originals.keys():
  if name not in existing:
   original=originals[name];q=original.copy();q.data=original.data.copy();q.name=original.name+'__'+state;collection.objects.link(q)
   q['healthy_source']=original.get('healthy_source',original.name);q['source_state']=state
 for o in collection.all_objects:
  if o.type!='MESH':continue
  if o.get('native_lumber_role'):
   o['native_probe_owner']=N.PREFIX+arm.name
   # Reuse the ACTUAL qualified healthy local binding. Freshly linked clone
   # matrix_world can be stale until depsgraph evaluation; writing it after
   # reparenting may bake the bone offset twice. Exact cloned reference rigs
   # share the same rest frame, so inverse/basis/bone identity transfer verbatim.
   original=originals[o.get('native_SKMS_name',o.get('native_source_name'))]
   o.parent=arm if original.parent==old_arm else original.parent
   o.parent_type=original.parent_type;o.parent_bone=original.parent_bone
   o.matrix_parent_inverse=original.matrix_parent_inverse.copy();o.matrix_basis=original.matrix_basis.copy()
   if o.get('native_lumber_role')=='skin':
    require(len(o.modifiers)==1 and o.modifiers[0].type=='ARMATURE','Native skin modifier layout changed');o.modifiers[0].object=arm
   o['native_lumber_reference_binding_route']='Exact healthy local basis/inverse/bone identity, state-owned exact reference rig; no matrix_world rebake'
  elif o.get('native_lumber_reference_support'):
   identity=o.get('healthy_source',o.name);original=support_originals.get(identity)
   require(original is not None,'Original qualified support source missing: '+str(identity))
   o.parent=arm if original.parent==old_arm else original.parent
   o.parent_type=original.parent_type;o.parent_bone=original.parent_bone
   o.matrix_parent_inverse=original.matrix_parent_inverse.copy();o.matrix_basis=original.matrix_basis.copy()
   o['native_lumber_reference_binding_route']='Exact healthy support parent type/bone/local inverse/basis transferred to state-owned reference rig'
 if state=='ruins':
  payload=next((o for o in collection.all_objects if o.get('native_lumber_role')=='payload'),None)
  if payload:
   # Source-authored pose only: no Action, new clip or claim that this is the
   # original game's collapse. Original reference arm/library is unchanged.
   delta=H.F-min(v.co.z for v in payload.data.vertices)
   bone=arm.pose.bones['bone_cable_translate_z'];saved=bone.matrix_basis.copy();bone.matrix_basis=Matrix.Translation((0,0,delta))@saved
   bpy.context.view_layer.update()
   low=min((payload.matrix_world@v.co).z for v in payload.data.vertices)
   require(abs(low-H.F)<1e-5,'Authored payload resting pose did not meet original ground')
   collection['native_lumber_source_ruin_pose_json']=json.dumps(dict(bone='bone_cable_translate_z',local_translation=[0,0,delta],payload_bottom=low,ground=H.F,source_authored_static_pose=True,new_clip=False,native_collapse_playback_qualified=False))
 collection[marker]=True;collection['native_source_state']=state
 collection['native_source_membership_qualification']='Exact retained string selectors; original supports replace only excluded native timber. Source-authored ruin pose is not native collapse playback.'
 return arm


def normalize_state(H,key,state,collection):
 with visible_collections(collection):return _normalize_state(H,key,state,collection)


def probe_original_supports(H,key,collection=None):
 """Reversible exact rigid-reference response of the ORIGINAL supports."""
 import bpy
 from mathutils import Matrix
 c=collection or H.root(key)
 arm=next(o for o in c.all_objects if o.type=='ARMATURE' and o.get('native_lumber_reference_root'))
 objects=[o for o in c.all_objects if o.type=='MESH' and o.get('native_lumber_reference_support')]
 require(objects,'Original support bindings missing')
 def sample():
  bpy.context.view_layer.update()
  return {o.name:[(o.matrix_world@v.co).copy() for v in o.data.vertices] for o in objects}
 baseline=sample();bone=arm.pose.bones['bone_wheel_base'];saved=bone.matrix_basis.copy();rest=bone.matrix.copy()
 try:
  bone.matrix_basis=saved@Matrix.Rotation(.025,4,'Z');bpy.context.view_layer.update();posed=sample()
  delta=arm.matrix_world@bone.matrix@rest.inverted()@arm.matrix_world.inverted()
  errors=[(p-delta@r).length for name,pts in posed.items() for p,r in zip(pts,baseline[name])]
  movement=max(((p-r).length for name,pts in posed.items() for p,r in zip(pts,baseline[name])),default=0)
 finally:
  bone.matrix_basis=saved;bpy.context.view_layer.update()
 restored=sample();restoration=max(((p-r).length for name,pts in restored.items() for p,r in zip(pts,baseline[name])),default=0)
 result=dict(original_support_objects=[o.name for o in objects],bone='bone_wheel_base',
  maximum_exact_reference_rigid_error=max(errors,default=0),maximum_source_pose_movement=movement,
  maximum_restoration_error=restoration,new_weights_or_clips=False,
  qualification='Inspectable original source supports use the retained reference hierarchy; no physical pivot or native collapse playback claim')
 result['passed']=result['maximum_exact_reference_rigid_error']<1e-5 and restoration<1e-6 and movement>1e-7
 require(result['passed'],'Original reference-bound support pose failed: '+json.dumps(result))
 return result


def probe_assembly(H,key='A1'):
 """Actual parent-run healthy source evidence; never invokes Garrison."""
 import mesh_checks as C
 c=H.root(key);arm=next(o for o in c.all_objects if o.type=='ARMATURE' and o.get('native_lumber_reference_root'))
 exact=[audit_exact(o,'skin' if o.get('native_lumber_role')=='skin' else 'rigid',None if o.get('native_lumber_role')=='skin' else int(o['native_lumber_source_index'])) for o in c.all_objects if o.type=='MESH' and o.get('native_lumber_role')]
 checks=[C.mesh_report(o) for o in c.all_objects if o.type=='MESH']
 contacts=[C.contact_report(x) for x in H.CONTRACTS if x['body']==key]
 interfaces=[C.interface_report(x) for x in H.ANCHORS[key]['numerical_interfaces']]
 support=probe_original_supports(H,key,c);bones=N.audit_reference_bones(TARGET,arm.name)
 total=sum(triangles(o) for o in c.all_objects if o.type=='MESH')
 return dict(schema='ccp.persia.lumber-actual-source-probe/v1',body=key,triangles=total,
  original_architecture_triangles=H.ANCHORS[key]['original_architecture_triangles'],native_triangles=sum(x['triangles'] for x in exact),
  exact_native_mesh_audits=exact,mesh_checks=checks,scalar_contacts=contacts,numerical_interfaces=interfaces,
  original_support_pose=support,reference_bones=bones,
  passed=total<=2740 and all(x['passed'] for x in checks+contacts+interfaces) and support['passed'] and all(x['public_reference_projection_matches'] for x in bones['bones']),
  source_only=True,native_playback_qualified=False,visual_review_required=True)
