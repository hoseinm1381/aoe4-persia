"""Fresh-process deterministic source build; never writes to permanent mod.

Run with Blender --background --factory-startup --python-exit-code 1 --python.
"""
from pathlib import Path
import sys,json,bpy,traceback,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import recipe as H,states as S,checks as C,fit

def build(keys,save=True):
    master=ROOT/'house.blend';receipt_path=ROOT/'evidence/build-receipt.json'
    inputs=[ROOT/n for n in ['recipe.py','states.py','fit.py','native-contracts.json']]+[ROOT.parent/'_shared/source_runner.py']+sorted((ROOT/'textures').glob('*.png'))
    hashes={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    expected_keys=json.loads((ROOT/'family.json').read_text())['expected_body_keys']
    if save and (set(keys)!=set(expected_keys) or len(keys)!=len(expected_keys)):raise RuntimeError('Master saves require every family body exactly once. Use --probe for a subset.')
    original_master_sha=hashlib.sha256(master.read_bytes()).hexdigest() if master.exists() else None
    if save and master.exists():
        previous=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        known=previous.get('saved_file_sha256')
        if not known:raise RuntimeError('Existing master has no verified ownership hash; inspect before overwriting')
        if hashlib.sha256(master.read_bytes()).hexdigest()!=known:raise RuntimeError('Manual/external master edit detected. Preserve and reconcile it before a recipe rebuild.')
    records=[]
    for key in keys:
        H.build_body(key)
        check=C.run(key,complete=False)
        if not check['passed']:raise RuntimeError('Healthy source failed '+key+': '+str(check['errors']))
        S.build(key)
        fit.apply(key)
        check=C.run(key,complete=True)
        if not check['passed']:raise RuntimeError('Complete source failed '+key+': '+str(check['errors']))
        records.append(check)
    if not save:
        (ROOT/'evidence/probe-receipt.json').write_text(json.dumps({'passed':True,'bodies':keys,'saved_master':False},indent=2)+'\n')
        print('SOURCE_PROBE_PASS',keys,flush=True);return
    H.show(keys[0])
    for im in bpy.data.images:
        if im.name.startswith(H.R.PREFIX):im.filepath='//textures/'+Path(im.filepath).name
    final_existing_sha=hashlib.sha256(master.read_bytes()).hexdigest() if master.exists() else None
    if final_existing_sha!=original_master_sha:raise RuntimeError('Master changed during generation. Save aborted to preserve the external/manual edit.')
    if hashes!={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}:raise RuntimeError('Geometry inputs changed during generation. Save aborted; rebuild from the final retained inputs.')
    H.write_anchors();C.manifest()
    H.R.save()
    (ROOT/'evidence/build-receipt.json').write_text(json.dumps({'passed':True,'bodies':keys,'complete_compositions':len(keys)*31,'geometry_input_sha256':hashes,'saved_file_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'native_gates':'deferred','checked_bodies':records},indent=2)+'\n')
    print('SOURCE_BUILD_PASS',keys,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['A1a']
    save='--probe' not in args;args=[a for a in args if a!='--probe']
    try:build(args,save=save)
    except Exception:
        (ROOT/'evidence/source-build-error.txt').write_text(traceback.format_exc());raise
