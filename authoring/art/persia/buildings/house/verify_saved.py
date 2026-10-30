"""Fresh-file source readback, not native engine verification."""
from pathlib import Path
import sys,json,bpy,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import recipe as H,checks as C

def actual_parts(collection):return {o.name:C.digest(o) for o in collection.all_objects if o.type=='MESH'}

def main():
    family=json.loads((ROOT/'family.json').read_text());expected=json.loads((ROOT/'state-manifest.json').read_text())['compositions'];errors=[];checks=[]
    file_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    build=json.loads((ROOT/'evidence/build-receipt.json').read_text())
    if file_sha!=build['saved_file_sha256']:errors.append('saved source hash differs from build receipt')
    for rel,wanted in build['geometry_input_sha256'].items():
        if hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest()!=wanted:errors.append('geometry input changed '+rel)
    for key in family['expected_body_keys']:
        r=C.run(key,complete=True,write=False);checks.append({'body':key,'passed':r['passed'],'errors':r['errors']});errors+=r['errors']
    for name,row in expected.items():
        c=bpy.data.collections.get(name)
        wanted={o['name']:o['geometry_uv_digest_q5'] for o in row['parts']}
        if c is None or actual_parts(c)!=wanted:errors.append('saved manifest mismatch '+name)
    wanted_count=len(family['expected_body_keys'])*family['expected_source_compositions_per_body']
    if len(expected)!=wanted_count:errors.append('manifest composition count')
    if set(bpy.data.scenes.keys())!={'Scene',H.R.SCENE}:errors.append('unexpected scene included')
    result={'passed':not errors,'saved_file_sha256':file_sha,'state_manifest_sha256':hashlib.sha256((ROOT/'state-manifest.json').read_bytes()).hexdigest(),'checked_compositions':len(expected),'expected_compositions':wanted_count,'checked_bodies':checks,'errors':errors,'native_gates':'unverified; fresh Blender source readback only'}
    (ROOT/'evidence/saved-file-readback.json').write_text(json.dumps(result,indent=2)+'\n');print('SAVED_READBACK',result['passed'],len(expected),len(errors),flush=True)
    if errors:raise RuntimeError(str(errors[:12]))

if __name__=='__main__':main()
