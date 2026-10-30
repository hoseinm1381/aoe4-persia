"""Read-only native evidence -> Outpost equipment source contract. No Blender."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'_shared'))
import native_mechanisms as N

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from strings(v)
 elif isinstance(x,list):
  for v in x:yield from strings(v)

def main():
 import numpy as np
 source=N.INVENTORY/'mechanism-composition/outpost.json';native=json.loads(source.read_text())
 configpath=ROOT.parent/'configuration.json';config=json.loads(configpath.read_text())
 targets={};files={}
 def retain(p,expected=None):
  p=Path(p).resolve();assert p.is_file(),p;digest=sha(p);assert not expected or digest==expected,p
  files[str(p)]=dict(path=str(p),sha256=digest,bytes=p.stat().st_size)
 for t in native['targets']:
  target=t['target'];plan=N.retained_plan(target);binding=N._bindings(N._model(target));N._assert_plan_fingerprint(plan,binding)
  selected=set(t['selected_mechanism_fragment_ids']);byname={f['source_name']:f for f in t['source_fragments'] if f['id'] in selected}
  fragments=[]
  for record,group,used,tris in N._source_fragments(plan,binding):
   f=byname.get(record['source_name'])
   if not f:continue
   assert group['mesh_index']==2 and group['group_index']==0,'Non-equipment group selected'
   v=np.asarray([group['positions'][i] for i in used]);tri=np.asarray(tris,int)
   zero=np.flatnonzero(np.linalg.norm(np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]),axis=1)/2<1e-10).tolist()
   fragments.append(dict(id=f['id'],native_source_index=record['source_index'],source_name=record['source_name'],
    native_parent_bone=record['native_parent_bone'],raw_reference_TRS=record['raw_reference_trs_xyzw_translation_scale'],
    raw_reference_semantics='Native inverse parent reference, not ordinary object placement',binding_header_sha256=record['binding_header_sha256'],
    mesh_index=group['mesh_index'],group_index=group['group_index'],native_material_slot='misc',triangles=len(tris),vertices=len(used),
    reference_bounds=f['projected_model_reference_bounds'],original_zero_area_triangle_indices=zero,
    role='Native upgrade component; combined arrow fragments require visual shell-content check before original-body integration'))
  assert len(fragments)==len(selected)
  probe_path=Path(t['actual_probe_path']);probe=json.loads(probe_path.read_text());library=Path(t['qualified_source_library'])
  retain(library,probe['saved_file_sha256']);retain(probe_path);retain(plan['manifest_path'])
  for k in ('native_rgm_path','native_rrgeom_path'):retain(t[k],t[k.replace('_path','_sha256')])
  for res in plan['resources'].values():
   if isinstance(res,dict) and res.get('cache_path'):retain(res['cache_path'],res.get('sha256'))
  retain(plan['material']['source']['path'],plan['material']['source']['sha256'])
  for tex in plan['textures']:
   s=tex.get('source',{});path=s.get('cache_path',s.get('path'))
   if path:retain(path,s.get('sha256'))
   if tex.get('projection',{}).get('path'):retain(tex['projection']['path'],tex['projection'].get('sha256'))
  for graph in t['native_owner_graphs']:retain(N.INVENTORY/'native'/graph['graph'],graph['sha256'])
  markers=t['native_markers'];assert markers.get('valid') is True
  actual={m['name'] for m in markers['markers']}
  requested={s for s in strings(config['inherited_combat']) if s.startswith(('fx_muz_','wep_hardpoint'))}
  targets[target]=dict(model=t['model'],source_library=str(library),source_library_sha256=sha(library),
   source_probe=str(probe_path),source_probe_sha256=sha(probe_path),public_plan_path=plan['manifest_path'],public_plan_sha256=sha(plan['manifest_path']),
   native_rgm_sha256=t['native_rgm_sha256'],native_rrgeom_sha256=t['native_rrgeom_sha256'],
   fragments=fragments,reference_hierarchy=t['reference_hierarchy'],native_skeleton_bone_count=plan['skeleton']['bone_count'],
   reference_armature_object=probe.get('explicit_reference_hierarchy',{}).get('armature'),public_mesh_objects=probe['mesh_object_names'],
   native_markers=markers,combat_requested_marker_names=sorted(requested),unresolved_combat_marker_names=sorted(requested-actual),
   native_selectors=t['native_selectors'],native_lifecycle_values=t['actual_geometry_lifecycle_values'],composition_cases=t['composition_cases'],
   stamp_placements=t['distinct_stamp_placements'],source_uses=t['source_uses'],native_owner_graphs=t['native_owner_graphs'],
   rig_action_references=t['rig_action_references'],reference_bone_formula=t['reference_bone_formula'],
   original_full_reference_library_retained=True,engine_aim_recoil_pivot_qualified=False,appearance_qualified=False,
   original_tower_main_roof_groups_excluded=True)
  assert (target=='outpost_fortified' and plan['skeleton']['bone_count']==0 and not any(f['native_parent_bone'] for f in fragments)) or target=='outpost_wood'
 cases=[]
 for c in config['configurations']:
  target='outpost_wood' if c['body_key']=='A1Basic' else 'outpost_fortified';t=targets[target]
  matching=[r for r in t['composition_cases'] if r['context']==c['selector_context']];assert len(matching)==1
  row=matching[0];byid={f['id']:f for f in t['fragments']};ids=row['possible_fragment_ids']
  cases.append(dict(id=c['id'],body_key=c['body_key'],target=target,emplacement=c['emplacement'],
   selector_context=c['selector_context'],definite_fragment_ids=row['definite_fragment_ids'],possible_fragment_ids=ids,
   simultaneous_triangles=row['simultaneous_projectable_triangles'],reference_bounds=row['possible_model_reference_bounds'],
   original_zero_area_face_count=sum(len(byid[i]['original_zero_area_triangle_indices']) for i in ids),
   baseline_garrison_fire=c['baseline_garrison_fire'],inspectable_source_library_ready=False,active_original_family_assembly_created=False))
 assert len(cases)==8
 cannon_path=N.INVENTORY/'mechanism-decode-logs/cannon-child-native-inspection.json';retain(cannon_path)
 for resource in json.loads(cannon_path.read_text())['resource_records']:retain(resource['native_path'],resource['sha256'])
 out=dict(schema='ccp.persia.outpost-equipment-source/v1',configuration_count=8,configurations=cases,targets=targets,
  source_evidence=dict(path=str(source),sha256=sha(source)),upgrade_requirements_source=dict(path=str(configpath),sha256=sha(configpath)),
  ordered_native_upgrade_requirements=config['requirements'],standard_reachability_qualification=config['requirement_evaluation'],
  inherited_combat=config['inherited_combat'],cannon_child=json.loads(cannon_path.read_text()),retained_files=list(files.values()),
  frame='Projected cooked model reference B(native)=(-x,-z,y); original native stamp alternatives separate; no world-space claim',
  gates=dict(native_decode_repeated=False,Blender_executed=False,all8_actual_append_probes_required=True,native_motion_playback_qualified=False),
  limits=['Full original tower raw libraries/graphs retained externally; active candidates select only exact upgrade components from native misc, excluding main/roof tower shell.',
   'Combined arrow component shell content and original-body interfaces require isolated visual review; names alone do not qualify them as moving machinery.',
   'Basic seven independent reference roots are collapse/reference helpers; no aiming/recoil motion inferred. Fortified has no native skeleton/bone binding and receives none.',
   'Fortified cannon/springald muzzle marker heights differ from visible native component heights; no auto-snap or guessed correction.',
   'Absent combat-requested markers remain unresolved; names are never aliased or fabricated.',
   'Zero-area original arrow faces remain intact; selected appearance failures are local to their configurations and retain full raw source.',
   'Geometry-free cannon child contributes zero mesh triangles; its original FX graph and marker owner remain required dependencies.',
   'Full state/LOD/configuration fits and visuals remain parent source gates; no cook/import/runtime claim.'])
 (ROOT/'source-contract.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(configurations=[(c['id'],c['simultaneous_triangles']) for c in cases],native_bones={k:t['native_skeleton_bone_count'] for k,t in targets.items()},retained_files=len(files))))
if __name__=='__main__':main()
