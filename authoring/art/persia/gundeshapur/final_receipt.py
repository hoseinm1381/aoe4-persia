"""Repository protection, source dependency and current artifact receipt."""
from pathlib import Path
import json,hashlib
from PIL import Image
import preflight
ROOT=Path(__file__).resolve().parent

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    base=json.loads((ROOT/'evidence/repository-baseline.json').read_text());now=preflight.snapshot()
    preservation={'head_unchanged':base['head']==now['head'],'git_status_unchanged':base['git_status']==now['git_status'],'protected_hashes_unchanged':base['files']==now['files'],'protected_files':len(base['files']),'initial_git_status':base['git_status'],'final_git_status':now['git_status']}
    preservation['passed']=all(preservation[k] for k in ('head_unchanged','git_status_unchanged','protected_hashes_unchanged'))
    (ROOT/'evidence/repository-preservation.json').write_text(json.dumps(preservation,indent=2))
    errors=[];files={};size=0
    for p in ROOT.rglob('*'):
        if not p.is_file():continue
        assert p.resolve().is_relative_to(ROOT.resolve()),'Artifact escapes owned root'
        size+=p.stat().st_size
        if p.suffix in ('.blend','.py','.md') or p.parent.name=='textures' or (p.parent.name=='previews' and p.name[:2].isdigit()) or p.name in ('state-manifest.json','anchors.json'):
            files[p.relative_to(ROOT).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
        if p.suffix=='.py':compile(p.read_text(encoding='utf-8'),str(p),'exec')
        if p.parent.name in ('textures','previews') and p.suffix=='.png':
            with Image.open(p) as im:
                if p.parent.name=='textures' and im.size!=(2048,2048):errors.append('wrong texture size '+p.name)
                im.verify()
    gates={n:json.loads((ROOT/'evidence'/n).read_text())['passed'] for n in ('source-checks.json','contact-checks.json','rebuild-verification.json','saved-file-readback.json','original-scene-preservation.json')}
    result={'status':'source_art_complete','passed':preservation['passed'] and all(gates.values()) and not errors,'checks':gates,'repository':preservation['passed'],'errors':errors,'asset_folder_total_bytes_including_retained_reference_evidence':size,'editable_blend_bytes':(ROOT/'gundeshapur.blend').stat().st_size,'closure':files,'native_gates':'deferred; no integration, cook, mod build, version bump, push or cleanup'}
    (ROOT/'evidence/final-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='closure'},indent=2));assert result['passed']
if __name__=='__main__':main()
