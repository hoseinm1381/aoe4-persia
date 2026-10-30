"""Parent-only factory source checkpoint: eight legal Outpost configurations.

Reads current original Outpost healthy source and compiled native equipment.
No body recipe edits, cook, Garrison, native playback or automatic acceptance.
Pass --render to write one consistent source preview per configuration.
"""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import native_equipment as E
import authored_equipment as AE

def bounds(objects):
 points=[o.matrix_world@v.co for o in objects if o.type=='MESH' for v in o.data.vertices]
 return dict(min=[min(v[a] for v in points) for a in range(3)],max=[max(v[a] for v in points) for a in range(3)]) if points else None

STATES=['healthy',*[f'damage_{n}' for n in range(1,6)],'ruins','preview','targeting']
SLOTS=[(state,lod) for state in STATES for lod in range(3)]+[(f'construct_{stage}',None) for stage in ('foundation','walls','vaults','finish')]


def construction_proof(contract,case):
 base=case['selector_context'];rows=[r for r in contract['targets'][case['target']]['composition_cases']
  if r['context']['life_cycle_state'].startswith('construct_') and all(r['context'].get(k)==v for k,v in base.items() if k!='life_cycle_state')]
 expected={f'construct_{n:02d}' for n in range(0,100,5)}
 E.require(len(rows)==20 and {r['context']['life_cycle_state'] for r in rows}==expected,'Incomplete literal native construction source cases')
 E.require(all(not r['definite_fragment_ids'] and not r['possible_fragment_ids'] and r['simultaneous_projectable_triangles']==[0,0] for r in rows),'Native construction equipment is not uniformly empty')
 return dict(literal_native_cases=sorted(expected),all_twenty_component_selections_identically_empty=True,
  first_three_authored_stages='Empty native equipment proven for ALL construct00..95 cases; no progress thresholds invented',
  finish='Exact healthy native equipment in authored complete source stage; not a native construct100 state')


def source_suffix(key,state,lod):return '_'+key+'_'+state+('_LOD'+str(lod) if lod is not None else '')


def clone_body(source,destination,label):
 import bpy
 originals=list(source.all_objects);copies={}
 for old in originals:
  ob=old.copy()
  if old.data:ob.data=old.data.copy()
  ob.name=label+'__'+old.name;destination.objects.link(ob);copies[old]=ob
  ob['source_configuration_slot']=label
 for old,ob in copies.items():
  if old.parent in copies:ob.parent=copies[old.parent]
  ob.matrix_parent_inverse=old.matrix_parent_inverse.copy();ob.matrix_basis=old.matrix_basis.copy()
  ob.hide_render=False;ob.hide_set(False)
 return list(copies.values())


def authored_ground_rest(scene,body_objects,gear,state):
 import bpy
 from mathutils import Matrix
 result=dict(applied=False,source_authored_static_pose=True,native_clip_or_pivot_changed=False)
 if state not in ('damage_5','ruins') or not gear['component_objects']:return result
 scene.view_layers[0].update()
 native_objects=[bpy.data.objects[n] for n in gear['component_objects']];nb=bounds(native_objects);bb=bounds(body_objects)
 # Only an original failed platform with no remaining architecture reaching
 # the equipment base authorizes this source-only whole-reference-root rest.
 architecture=[o for o in body_objects if o.type=='MESH' and o.get('role') not in ('debris','wear','owner')]
 ab=bounds(architecture)
 if not nb or not ab or nb['min'][2]<=ab['max'][2]+.05:return result
 beds=[o for o in body_objects if o.type=='MESH' and 'EarthBed' in o.name]
 E.require(beds,'Source authored ground rest requires actual original EarthBed')
 ground=bounds(beds)['max'][2];delta=ground-nb['min'][2]
 root=bpy.data.objects[gear['root']];root.matrix_world=Matrix.Translation((0,0,delta))@root.matrix_world
 scene.view_layers[0].update();after=bounds(native_objects)
 result.update(applied=True,whole_root_translation_metres=[0,0,delta],actual_original_ground_top=ground,
  original_equipment_bounds=nb,posed_equipment_bounds=after,actual_original_surviving_architecture_bounds=ab,
  ground_contact_error_metres=abs(after['min'][2]-ground),
  qualification='Authored static whole-input rest arrangement on actual ground after original platform loss; not native collapse simulation/clip or new physical pivot',
  relative_native_geometry_bones_pivots_preserved=True,individual_fragment_grounding_and_overlap_unchecked=True)
 root['source_authored_ground_rest_json']=json.dumps(result)
 return result


def set_visible(scene,slots,chosen):
 for name in slots:
  c=scene.collection.children.get(name)
  if c:c.hide_render=c.hide_viewport=name!=chosen
 scene.view_layers[0].update()


def setup_preview(scene,identifier):
 import bpy
 from mathutils import Vector
 scene.world=bpy.data.worlds.new('OutpostConfig_'+identifier+'_SourceWorld');scene.world.use_nodes=True
 scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.20,.24,1)
 scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
 for label,position,power,size in [('Key',(4,-7,14),1800,9),('Fill',(-7,-2,9),1000,10)]:
  data=bpy.data.lights.new(identifier+'_'+label,'AREA');data.energy=power;data.shape='DISK';data.size=size
  light=bpy.data.objects.new(data.name,data);scene.collection.objects.link(light);light.location=position;light.rotation_euler=(Vector((0,0,4))-light.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new(identifier+'_SourceCamera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera)
 camera.location=(12,-16,12);camera.rotation_euler=(Vector((0,0,4.7))-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=15;scene.camera=camera
 scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=880;scene.render.resolution_y=880;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'


def main(render=False,render_heavy=False):
 import bpy
 E.require(bpy.app.background and not bpy.data.filepath,'Use a dedicated unsaved factory process')
 output=ROOT/'outpost_configurations.blend';receipt_path=ROOT/'configuration-checkpoint.json'
 if output.exists():
  E.require(receipt_path.is_file(),'Existing configuration source has no matching receipt; overwrite refused')
  previous=json.loads(receipt_path.read_text())
  E.require(E.N._sha(output)==previous.get('saved_file_sha256'),'Configuration source changed after checkpoint; preserving manual edits')
 bpy.context.preferences.filepaths.save_version=0
 contract=E.inputs();source=ROOT.parent/'outpost.blend';E.require(source.is_file(),'Current original Outpost source master absent')
 keys=sorted({x['body_key'] for x in contract['configurations']});requested={}
 with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
  for key in keys:
   for state,lod in SLOTS:
    suffix=source_suffix(key,state,lod);matches=[n for n in available.collections if n.endswith(suffix)]
    E.require(len(matches)==1,'Need exact original body state collection '+suffix);requested[(key,state,lod)]=matches[0]
  immutable=tuple(requested.values());loaded.collections=list(immutable)
 sources=dict(zip(requested,loaded.collections));image_deps=[]
 for key in keys:image_deps.extend(E._absolute_images(list(sources[key,'healthy',0].all_objects),source))
 receipts=[];source_hash=E.N._sha(source)
 for case in contract['configurations']:
  identifier=case['id'];scene=bpy.data.scenes.new('OutpostConfig_'+identifier);setup_preview(scene,identifier)
  if bpy.context.window:bpy.context.window.scene=scene
  construction=construction_proof(contract,case);rows=[]
  for state,lod in SLOTS:
   label=identifier+'__'+state+('_LOD'+str(lod) if lod is not None else '')
   assembly=bpy.data.collections.new('OutpostConfig_'+label);scene.collection.children.link(assembly)
   body=bpy.data.collections.new('OutpostConfig_'+label+'_OriginalBody');assembly.children.link(body)
   body_objects=clone_body(sources[case['body_key'],state,lod],body,label)
   gear_collection=bpy.data.collections.new('OutpostConfig_'+label+'_NativeEquipment');assembly.children.link(gear_collection)
   native_state='healthy' if state=='construct_finish' else 'construct_00' if state.startswith('construct_') else state
   native=E.append_configuration(gear_collection,identifier,lifecycle=native_state,allow_unqualified_source_inspection=True)
   scene.view_layers[0].update()
   adaptation_collection=bpy.data.collections.new('OutpostConfig_'+label+'_OriginalConfigurationArchitecture');assembly.children.link(adaptation_collection)
   adaptation=AE.adapt(case,state,lod,body_objects,native,adaptation_collection,gear_collection)
   bpy.data.objects[native['root']]['native_configuration_report_json']=json.dumps(native)
   rest=dict(applied=False,qualification='No native root displacement; incompatible arrow housing or unsafe heavy intact compounds retained as inactive references')
   scene.view_layers[0].update()
   original_triangles=sum(sum(len(p.vertices)-2 for p in ob.data.polygons) for ob in body_objects if ob.type=='MESH')
   row=dict(source_state=state,lod=lod,collection=assembly.name,original_architecture_collection=body.name,
    native_equipment_collection=gear_collection.name,original_architecture_triangles=original_triangles,
    native_equipment=native,original_configuration_adaptation=adaptation,
    active_original_guards_triangles=adaptation['active_original_guard_triangles'],active_original_carrier_plinth_triangles=adaptation['active_original_plinth_triangles'],
    inactive_native_reference_triangles=adaptation['inactive_native_reference_triangles'],
    total_visible_source_triangles=original_triangles+adaptation['active_original_adaptation_triangles']+native['actual_visible_equipment_triangles'],
    original_architecture_bounds=bounds(body_objects),active_equipment_bounds=bounds([bpy.data.objects[n] for n in native['active_component_objects']]),
    inactive_reference_equipment_bounds=bounds([bpy.data.objects[n] for n in native['inactive_reference_component_objects']]),
    original_configuration_adaptation_bounds=bounds(list(adaptation_collection.all_objects)),
    source_authored_ground_rest=rest,native_full_LOD0_equipment_retained_exact=True,native_equipment_LOD_reduction_performed=False,
    source_LOD_ratio_qualification='Deferred; complete native equipment source retained, not silently reduced',
    native_hp_thresholds=None,validated=False,preview_rendered=False)
   assembly['source_configuration_state_receipt_json']=json.dumps(row);rows.append(row)
   assembly.hide_render=assembly.hide_viewport=True
  E.require(len(rows)==31,'Each legal configuration requires all 31 authored source compositions')
  healthy=next(r for r in rows if r['source_state']=='healthy' and r['lod']==0)
  set_visible(scene,[r['collection'] for r in rows],healthy['collection'])
  receipt=dict(configuration=identifier,source_body_key=case['body_key'],scene=scene.name,composition_count=len(rows),
   compositions=rows,construction_component_membership_proof=construction,
   source_master=str(source),source_master_sha256=source_hash,accepted=False,
   unresolved=['Actual original-body/equipment support/fit and incompatible combined-arrow architecture require one visual pass.',
    'Native muzzle/marker frame and aiming/recoil motion remain unqualified.',
    'Original zero-area faces retained; failed applied-normal qualifications localized.',
    'All states/configurations are authored source assemblies; exhaustive structural/LOD/native validation is deferred.'])
  scene['source_configuration_receipt_json']=json.dumps(receipt);receipts.append(receipt)
 if render:
  (ROOT/'previews').mkdir(exist_ok=True)
  selected_states=('healthy','damage_5','ruins') if render_heavy else ('healthy',)
  for receipt in receipts:
   scene=bpy.data.scenes[receipt['scene']];slot_names=[r['collection'] for r in receipt['compositions']]
   for state in selected_states:
    row=next(r for r in receipt['compositions'] if r['source_state']==state and r['lod']==0)
    set_visible(scene,slot_names,row['collection']);path=ROOT/'previews'/(receipt['configuration']+('__'+state if state!='healthy' else '')+'.png')
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=scene.name)
    row.update(preview_path=str(path),preview_rendered=True,preview_sha256=E.N._sha(path),preview_bytes=path.stat().st_size)
    bpy.data.collections[row['collection']]['source_configuration_state_receipt_json']=json.dumps(row)
   healthy=next(r for r in receipt['compositions'] if r['source_state']=='healthy' and r['lod']==0)
   set_visible(scene,slot_names,healthy['collection']);scene['source_configuration_receipt_json']=json.dumps(receipt)
 E.require(sum(r['composition_count'] for r in receipts)==248,'Need 8 x31 actual configuration source assemblies')
 report=dict(schema='ccp.persia.outpost-eight-source-configurations/v2',configuration_count=len(receipts),composition_count=248,configurations=receipts,
  native_library_sha256=E.N._sha(E.LIBRARY),equipment_contract_sha256=E.N._sha(E.CONTRACT),
  source_original_image_dependencies=image_deps,checkpoint_only=True,accepted=False,
  all_248_authored_in_current_file=True,exhaustive_checks_deferred=True,native_motion_playback_qualified=False,raw_full_references_retained=True)
 text=bpy.data.texts.new('Outpost_248ConfigurationStateSourceManifest.json');text.write(json.dumps(report,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
 report['saved_file']=str(output);report['saved_file_sha256']=E.N._sha(output)
 receipt_path.write_text(json.dumps(report,indent=2)+'\n')
 print('OUTPOST_248_CONFIGURATION_STATE_SOURCE_CHECKPOINT',len(receipts),sum(r['composition_count'] for r in receipts));return report

if __name__=='__main__':main('--render' in sys.argv,'--render-heavy' in sys.argv)
