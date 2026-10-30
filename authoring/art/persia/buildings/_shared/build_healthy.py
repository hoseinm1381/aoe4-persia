"""Serialized healthy-source checkpoint, not family acceptance.

Blender --background --factory-startup --python-exit-code 1 --python THIS -- SLUG
Never imports another family's recipe or changes native files. All source data
is owned by the selected family. Saved master hashes guard manual edits.
"""
from pathlib import Path
import sys,json,hashlib,traceback,importlib.util
import bpy
from mathutils import Matrix
ART=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ART/'_shared'))
import mesh_checks as C

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main(slug,probe=False):
    if not bpy.app.background or bpy.data.filepath:raise RuntimeError('Healthy generation requires a task-owned background factory process, not an open user scene')
    root=ART/slug
    if slug=='house':raise ValueError('House has a separate qualified pipeline')
    native=json.loads((root/'native-contracts.json').read_text())
    keys=json.loads((root/'family.json').read_text())['expected_body_keys']
    spec=importlib.util.spec_from_file_location('recipe',root/'recipe.py')
    H=importlib.util.module_from_spec(spec);sys.modules['recipe']=H;spec.loader.exec_module(H)
    R=H.R;master=root/(slug+'.blend');receipt=root/'evidence/healthy-build-receipt.json'
    before_master=sha(master) if master.exists() else None
    if master.exists():
        old=json.loads(receipt.read_text()) if receipt.exists() else {}
        if old.get('saved_file_sha256')!=before_master:raise RuntimeError('Master manual/external change: preserve and reconcile before rebuild')
    inputs=[root/'recipe.py',root/'native-contracts.json',root/'family.json',ART/'_shared/source_runner.py',Path(__file__),ART/'_shared/mesh_checks.py']+sorted((root/'textures').glob('*.png'))
    fingerprints={str(p.relative_to(ART)):sha(p) for p in inputs}
    reports=[];errors=[]
    for key in keys:
        H.build_body(key);col=H.root(key);obs=[o for o in col.all_objects if o.type=='MESH']
        body=native['bodies'][key];anchor=H.ANCHORS[key]
        contacts=[C.contact_report(c) for c in H.CONTRACTS if c['body']==key]
        interfaces=[C.interface_report(c) for c in anchor.get('numerical_interfaces',[])]
        rows=[C.mesh_report(o) for o in obs]
        for row in rows:
            if not row['passed']:errors.append({'body':key,'object':row['object'],'errors':row['errors']})
        for row in contacts+interfaces:
            if not row['passed']:errors.append({'body':key,'contact':row})
        nominal=C.composition_report(col)
        # The draft must explicitly declare stamp-space when applicable. Native
        # reference matrices are projected inventory inputs, never guessed.
        if 'authored_space' not in anchor:raise RuntimeError('Recipe must explicitly declare its authored coordinate frame '+key)
        authored=str(anchor['authored_space']).lower()
        stamp_space='stamp' in authored and not authored.startswith('model')
        transform=Matrix.Identity(4)
        if stamp_space:
            stamps=body['stamp_contracts']
            matrices={json.dumps(s['blender_matrix_row_major']) for s in stamps}
            if len(matrices)!=1:raise RuntimeError('Multiple native stamp frames require per-consumer adapter: '+key)
            transform=Matrix(stamps[0]['blender_matrix_row_major']).inverted()
            for ob in obs:
                for v in ob.data.vertices:v.co=transform@v.co
                ob.data.update()
        anchor['source_checkpoint_frame']={'authored_space':authored,'saved_space':'projected native resource space','authored_to_resource_matrix':[list(r) for r in transform],'native_actor_stamp_markers_changed':False}
        age=body['native_age_label_from_resource_name'];budgetdoc=json.loads((root/'evidence/stock-budgets.json').read_text())
        budgets=budgetdoc['budgets_by_age'];budget=budgets.get(str(age))
        if budget is None:
            profiles_path=root/'state-profiles.json'
            profile=json.loads(profiles_path.read_text())['bodies'][key] if profiles_path.is_file() else {}
            comparison=profile.get('comparison_budget',{})
            if not comparison.get('basis') or str(comparison.get('age')) not in budgets:raise RuntimeError('Ambiguous reference class/age budget; require explicit comparison_budget age and basis '+key)
            budget=budgets[str(comparison['age'])]
        composition=C.composition_report(col,body['healthy_definite_rest_bounds'],budget['cap_guaranteed_native_maximum_triangles'])
        if not composition['passed']:errors.append({'body':key,'composition':composition})
        reports.append({'body':key,'nominal_composition':nominal,'resource_composition':composition,'mesh_checks':rows,'authored_frame_contact_checks':contacts,'authored_frame_interface_checks':interfaces,'native_model_sha256':body['native_model_sha256'],'source_to_resource':[list(r) for r in transform]})
        print('HEALTHY_CHECKPOINT_BODY',slug,key,'errors',len(errors),flush=True)
    doc={'family':slug,'healthy_checkpoint_passed':not errors,'family_accepted':False,'errors':errors,'bodies':reports,'geometry_input_sha256':fingerprints,'remaining':'All other states/LODs, native mechanisms, visual critique, saved readback and cold reconstruction remain separate gates.'}
    (root/'evidence/healthy-checks.json').write_text(json.dumps(doc,indent=2)+'\n')
    if errors:raise RuntimeError(str(errors[:8]))
    if probe:print('HEALTHY_UNSAVED_PROBE_PASS',slug);return
    if (sha(master) if master.exists() else None)!=before_master:raise RuntimeError('Master changed during generation; save aborted')
    if fingerprints!={str(p.relative_to(ART)):sha(p) for p in inputs}:raise RuntimeError('Inputs changed during generation; save aborted')
    H.write_anchors();H.show(keys[0])
    for image in bpy.data.images:
        if image.name.startswith(R.PREFIX):image.filepath='//textures/'+Path(image.filepath).name
    R.save();doc['saved_file_sha256']=sha(master)
    receipt.write_text(json.dumps(doc,indent=2)+'\n')
    print('HEALTHY_SOURCE_CHECKPOINT_SAVED',slug,len(keys),flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    try:main(args[0],probe='--probe' in args)
    except Exception:
        if args:(ART/args[0]/'evidence/healthy-build-error.txt').write_text(traceback.format_exc())
        raise
