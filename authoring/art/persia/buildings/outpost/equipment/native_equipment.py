"""Parent-run exact Outpost equipment source library, no Garrison API/decode.

Native main/roof tower geometry never enters the selected equipment library.
Failed component appearance gates remain inspectable, explicitly unqualified.
"""
from pathlib import Path
import sys,json,math
from functools import lru_cache
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'_shared'))
import native_mechanisms as N
import native_skin_sources as S
import native_source_appearance as A
CONTRACT=ROOT/'source-contract.json'
LIBRARY=ROOT/'native_equipment_inputs.blend'
_TEMPLATE_CACHE={}

def require(value,message):
 if not value:raise RuntimeError(message)
@lru_cache(maxsize=1)
def inputs():
 c=json.loads(CONTRACT.read_text())
 for row in c['retained_files']:require(Path(row['path']).is_file() and N._sha(row['path'])==row['sha256'],'Retained Outpost input changed: '+row['path'])
 return c
@lru_cache(maxsize=2)
def sources(target):
 p=N.retained_plan(target);b=N._bindings(N._model(target));N._assert_plan_fingerprint(p,b)
 return p,b,{r['source_name']:(r,g,u,t) for r,g,u,t in N._source_fragments(p,b)}

def audit_mesh(obj,target):
 p,b,fragments=sources(target);r,g,used,tris=fragments[obj['native_source_name']]
 require([list(poly.vertices) for poly in obj.data.polygons]==tris and len(obj.data.vertices)==len(used),'Equipment native topology changed')
 position=max(abs(v.co[a]-g['positions'][old][a]) for v,old in zip(obj.data.vertices,used) for a in range(3))
 raw=obj.data.attributes.get('native_reference_normal');require(raw is not None,'Raw native normals missing')
 normal=max(abs(n.vector[a]-g['normals'][old][a]) for n,old in zip(raw.data,used) for a in range(3))
 uv=0
 for name,values in g['uv_layers'].items():
  layer=obj.data.uv_layers.get(name);require(layer is not None,'Original equipment UV layer missing')
  uv=max(uv,max(abs(layer.data[loop.index].uv[a]-values[used[loop.vertex_index]][a]) for loop in obj.data.loops for a in (0,1)))
 require(max(position,normal,uv)<1e-7,'Native source geometry/UV/raw normals changed')
 require(obj['native_source_geometry_sha256']==b['native_rrgeom_sha256'],'Native equipment provenance changed')
 require(len(obj.data.materials)==1 and {p.material_index for p in obj.data.polygons}=={0},'Native material face join changed')
 material=obj.data.materials[0];identity=A.material_identity({k:material[k] for k in material.keys()},p)
 require(identity['name']=='misc','Native equipment must use exact misc material identity')
 require(not obj.modifiers and not obj.vertex_groups,'Outpost component unexpectedly has skin/modifiers')
 if r['native_parent_bone']:
  require(obj.parent is not None and obj.parent.type=='ARMATURE' and obj.parent_bone==r['native_parent_bone'],'Exact native reference parent lost')
 else:require(obj.parent is None or obj.parent.type=='EMPTY','Unbound native component acquired fabricated bone binding')
 return dict(object=obj.name,native_source_name=r['source_name'],triangles=len(tris),position_max_error=position,
  UV_max_error=uv,raw_normal_max_error=normal,native_parent_bone=r['native_parent_bone'],material_identity=identity,passed=True)

def _absolute_images(objects,source_library):
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
   for mat in obj.data.materials:
    if mat and mat.use_nodes:visit(mat.node_tree)
 rows=[]
 for image in images.values():
  raw=image.filepath;path=(Path(source_library).parent/raw[2:]).resolve() if raw.startswith('//') else Path(bpy.path.abspath(raw)).resolve()
  require(path.is_file(),'Native source image missing: '+str(path));image.filepath=str(path)
  rows.append(dict(image=image.name,path=str(path),sha256=N._sha(path)))
 return rows

def compile_library():
 import bpy
 from mathutils import Matrix,Vector
 require(bpy.app.background and not bpy.data.filepath,'Dedicated factory process required')
 if LIBRARY.exists():
  sidecar=LIBRARY.with_suffix('.json');require(sidecar.is_file(),'Existing native equipment library has no receipt; overwrite refused')
  require(N._sha(LIBRARY)==json.loads(sidecar.read_text()).get('library_sha256'),'Native equipment library changed; preserving manual edits')
 c=inputs();collection=bpy.data.collections.new('NSRC_OutpostEquipmentCompiler');bpy.context.scene.collection.children.link(collection)
 output={};all_ids=set();reports={};dependencies=[]
 for target,t in c['targets'].items():
  p,b,fragments=sources(target);names=list(t['public_mesh_objects'])
  if t['reference_armature_object']:names.append(t['reference_armature_object'])
  requested=tuple(names)  # Blender replaces entries in its supplied load list.
  with bpy.data.libraries.load(t['source_library'],link=False) as (available,loaded):
   require(all(name in available.objects for name in requested),'Cached public import ID absent');loaded.objects=list(requested)
  imported=dict(zip(requested,loaded.objects));public=[imported[name] for name in t['public_mesh_objects']]
  arm=imported.get(t['reference_armature_object']);owner='NSRC_OutpostEquipment_'+target
  for ob in imported.values():collection.objects.link(ob);ob['native_probe_owner']=owner
  if arm:
   require(len(arm.data.bones)==7,'Basic exact reference forest changed')
   arm.name=owner+'_ReferenceForest';audit=N.audit_reference_bones(target,arm.name)
   require(all(row['public_reference_projection_matches'] and row['actual_parent']==row['expected_parent'] for row in audit['bones']),'Native basic reference hierarchy mismatch')
   all_ids.add(arm)
  else:require(t['native_skeleton_bone_count']==0 and target=='outpost_fortified','Do not fabricate fortified reference bones')
  pool=A._material_pool(public,p);require(len(pool.get('misc',[]))==1,'Need exact authoritative misc material')
  material,material_source,identity=pool['misc'][0]
  rows={};appearance={};views=[]
  for f in t['fragments']:
   record,group,used,tris=fragments[f['source_name']]
   data=S._mesh_data(bpy,owner+'_'+str(record['source_index']),group,used,tris)
   ob=bpy.data.objects.new(data.name,data);collection.objects.link(ob);views.append(ob)
   ob['native_probe_owner']=owner;ob['native_probe_model']=t['model'];ob['native_source_name']=record['source_name']
   ob['native_mesh_index']=group['mesh_index'];ob['native_group_index']=group['group_index'];ob['native_source_vertex_indices_json']=json.dumps(used)
   ob['native_source_parent_bone']=record['native_parent_bone'];ob['native_source_binding_sha256']=record['binding_header_sha256']
   ob['native_reference_TRS_json']=json.dumps(record['raw_reference_trs_xyzw_translation_scale'])
   ob['native_source_geometry_sha256']=b['native_rrgeom_sha256'];ob['retained_native_dependency']=True
   ob['native_equipment_fragment_id']=f['id'];ob['native_equipment_target']=target
   ob['native_raw_zero_area_faces_json']=json.dumps(f['original_zero_area_triangle_indices'])
   data.materials.append(material)
   if record['native_parent_bone']:
    require(arm is not None,'Bound component needs exact basic reference forest')
    ob.parent=arm;ob.parent_type='BONE';ob.parent_bone=record['native_parent_bone'];bpy.context.view_layer.update()
    ob.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
   error=max(((ob.matrix_world@v.co)-Vector(group['positions'][old])).length for v,old in zip(data.vertices,used))
   require(error<=1e-5,'Basic reference parent changed native component rest pose')
   try:
    result=A.preserve(target,[o.name for o in public],[ob.name]);appearance[f['id']]=dict(qualified=True,report=result)
   except Exception as exc:
    # Preserve exact full source geometry and authoritative material even if
    # original zero-area faces prevent normal projection qualification.
    appearance[f['id']]=dict(qualified=False,error=str(exc),original_zero_area_faces=f['original_zero_area_triangle_indices'])
   ob['native_equipment_appearance_qualified']=appearance[f['id']]['qualified'];ob['native_equipment_appearance_report_json']=json.dumps(appearance[f['id']])
   audit_mesh(ob,target);rows[f['id']]=ob.name;all_ids.add(ob)
  poses=[]
  if arm:
   for bone in arm.data.bones:
    pose=N.pose_probe(arm.name,bone.name,[o.name for o in views]);require(pose['reference_restored'] and all(x['movement_partition_matches'] for x in pose['rigid_movement_partition']),'Reference forest reversible partition failed');poses.append(pose)
  dependencies.extend(_absolute_images(views,t['source_library']))
  output[target]=dict(armature=arm.name if arm else None,fragments=rows)
  reports[target]=dict(appearance=appearance,geometry=[audit_mesh(ob,target) for ob in views],reversible_reference_poses=poses,
   native_reference_bones=t['native_skeleton_bone_count'],native_aim_recoil_motion_qualified=False)
 text=bpy.data.texts.new('OutpostEquipment_SourceContract.json');text.write(json.dumps(c,indent=2));all_ids.add(text)
 bpy.data.libraries.write(str(LIBRARY),all_ids,path_remap='RELATIVE',fake_user=True,compress=True)
 receipt=dict(schema='ccp.persia.outpost-equipment-library/v1',library=str(LIBRARY),library_sha256=N._sha(LIBRARY),
  source_contract_sha256=N._sha(CONTRACT),objects=output,reports=reports,image_dependencies=dependencies,
  complete_raw_reference_libraries_retained=True,original_tower_main_roof_geometry_in_library=False,
  inspectable_source_extraction_completed=True,all_component_appearance_qualified=all(a['qualified'] for r in reports.values() for a in r['appearance'].values()),
  native_motion_playback_qualified=False,clips_created=False)
 LIBRARY.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

def append_configuration(collection,configuration_id,matrix=None,lifecycle='healthy',collapsed='false',allow_unqualified_source_inspection=False):
 import bpy
 from mathutils import Matrix,Quaternion,Vector
 c=inputs();receipt=json.loads(LIBRARY.with_suffix('.json').read_text())
 require(N._sha(LIBRARY)==receipt['library_sha256'] and N._sha(CONTRACT)==receipt['source_contract_sha256'],'Native equipment library/contract changed')
 cases=[x for x in c['configurations'] if x['id']==configuration_id];require(len(cases)==1,'Unknown legal Outpost configuration')
 case=cases[0];target=case['target'];t=c['targets'][target];context=dict(case['selector_context'],life_cycle_state=lifecycle,has_collapsed_ruins=collapsed)
 matches=[x for x in t['composition_cases'] if x['context']==context];require(len(matches)==1,'No exact native lifecycle/configuration case')
 state=matches[0];require(state['definite_fragment_ids']==state['possible_fragment_ids'],'Ambiguous native selector case retained, not silently activated')
 selected=state['definite_fragment_ids'];entry=receipt['objects'][target]
 failures=[fid for fid in selected if not receipt['reports'][target]['appearance'][fid]['qualified']]
 require(not failures or allow_unqualified_source_inspection,'Selected equipment appearance is unqualified: '+str(failures))
 key=(receipt['library_sha256'],target)
 if key not in _TEMPLATE_CACHE:
  requested=tuple(list(entry['fragments'].values())+([entry['armature']] if entry['armature'] else []))
  with bpy.data.libraries.load(str(LIBRARY),link=False) as (_,loaded):loaded.objects=list(requested)
  _TEMPLATE_CACHE[key]=dict(zip(requested,loaded.objects))
 templates=_TEMPLATE_CACHE[key]
 root=bpy.data.objects.new('OutpostConfig_'+configuration_id+'_'+lifecycle+'_NativeEquipment',None);collection.objects.link(root);root.matrix_world=Matrix(matrix) if matrix is not None else Matrix.Identity(4)
 source_arm=templates.get(entry['armature']);arm=None
 if source_arm:
  arm=source_arm.copy();arm.data=source_arm.data.copy();collection.objects.link(arm);arm.parent=root;arm.matrix_basis=Matrix.Identity(4);arm['native_probe_owner']='NSRC_'+root.name
 views=[]
 for fid in selected:
  original=templates[entry['fragments'][fid]];ob=original.copy();ob.data=original.data.copy();collection.objects.link(ob)
  if ob.get('native_source_parent_bone'):
   require(arm is not None,'Exact bound component requires its copied native reference forest')
   ob.parent=arm;ob.parent_type=original.parent_type;ob.parent_bone=original.parent_bone
   ob.matrix_parent_inverse=original.matrix_parent_inverse.copy();ob.matrix_basis=original.matrix_basis.copy()
  else:ob.parent=root;ob.matrix_basis=Matrix.Identity(4)
  ob['native_probe_owner']='NSRC_'+root.name;ob['source_configuration']=configuration_id;ob['source_lifecycle']=lifecycle;views.append(ob)
  audit_mesh(ob,target)
 B=Matrix(((-1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
 marker_objects=[]
 for m in t['native_markers']['markers']:
  socket=bpy.data.objects.new(configuration_id+'_'+m['name'],None);collection.objects.link(socket);socket.parent=root
  socket['native_raw_marker_json']=json.dumps(m);socket['native_marker_world_transform_qualified']=False
  if m['native_frame_flag']==0 and not m['parent_bone']:
   q=m['quaternion_xyzw'];native=Matrix.LocRotScale(Vector(m['translation']),Quaternion((q[3],q[0],q[1],q[2])),Vector(m['scale']))
   socket.matrix_basis=B@native@B.inverted();socket['native_root_reference_projected']=True
  else:socket.hide_viewport=True;socket.hide_render=True;socket['native_marker_quarantined']=True
  marker_objects.append(socket.name)
 triangles=sum(len(p.vertices)-2 for o in views for p in o.data.polygons)
 require(state['simultaneous_projectable_triangles']==[triangles,triangles],'Exact selected triangle contribution changed')
 result=dict(configuration_id=configuration_id,body_key=case['body_key'],native_context=context,root=root.name,
  native_reference_armature=arm.name if arm else None,component_objects=[o.name for o in views],markers=marker_objects,
  actual_visible_equipment_triangles=triangles,appearance_qualified=not failures,unqualified_appearance_fragment_ids=failures,
  baseline_garrison_fire=case['baseline_garrison_fire'],original_tower_shell_excluded=True,
  source_only=True,native_motion_playback_qualified=False,original_architecture_fit_and_visual_review_pending=True)
 root['native_configuration_report_json']=json.dumps(result);return result

if __name__=='__main__':print(json.dumps(compile_library(),indent=2))
