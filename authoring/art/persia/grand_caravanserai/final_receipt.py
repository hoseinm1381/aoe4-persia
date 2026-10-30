"""Final independent filesystem/repository/artwork preservation and dependency receipt."""
from pathlib import Path
import hashlib,json,subprocess,ast,importlib.util
from PIL import Image
ROOT=Path(__file__).resolve().parent;PREV=ROOT.parent/'gundeshapur';REPO=Path('F:/aoe_4_temp/community_civilization_pack_garrison_aoe4')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf-8')
def main():
    errors=[];baseline=json.loads((ROOT/'evidence/repository-baseline.json').read_text())
    changed=[n for n,h in baseline['files'].items() if not (REPO/n).is_file() or sha(REPO/n)!=h]
    repo={'head_unchanged':git('rev-parse','HEAD').strip()==baseline['head'],'git_status_unchanged':git('status','--porcelain=v1')==baseline['git_status'],'protected_files_changed':changed};repo['passed']=repo['head_unchanged'] and repo['git_status_unchanged'] and not changed
    (ROOT/'evidence/repository-preservation.json').write_text(json.dumps(repo,indent=2)+'\n')
    gb=json.loads((ROOT/'evidence/gundeshapur-baseline.json').read_text());gchanged=[n for n,h in gb.items() if not (PREV/n).is_file() or sha(PREV/n)!=h]
    gund={'passed':not gchanged,'changed':gchanged,'master_sha256':sha(PREV/'gundeshapur.blend')};(ROOT/'evidence/gundeshapur-preservation.json').write_text(json.dumps(gund,indent=2)+'\n')
    gates={}
    for name in ['source-checks','contact-checks','rebuild-verification','saved-file-readback','review-receipt']:
        p=ROOT/'evidence'/(name+'.json');gates[name]=p.is_file() and json.loads(p.read_text()).get('passed',False)
    gates['repository']=repo['passed'];gates['gundeshapur']=gund['passed']
    for p in ROOT.glob('*.py'):
        try:compile(p.read_text(encoding='utf-8-sig'),str(p),'exec')
        except Exception as e:errors.append(str(p)+': '+str(e))
    for p in (ROOT/'textures').glob('*.png'):
        with Image.open(p) as im:
            if im.size!=(2048,2048):errors.append('atlas size '+str(p))
            im.verify()
    for p in (ROOT/'previews').glob('*.png'):
        with Image.open(p) as im:im.verify()
    files={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'owner-decode' not in p.parts and 'native-owners' not in p.parts and p.name!='final-receipt.json'}
    doc={'passed':all(gates.values()) and not errors,'gates':gates,'errors':errors,'bytes_total':sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file()),'blend_bytes':(ROOT/'grand_caravanserai.blend').stat().st_size,'files':files,'native_build':False,'integration':False,'promotion_push_cleanup':False}
    (ROOT/'evidence/final-receipt.json').write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps({k:v for k,v in doc.items() if k!='files'},indent=2));assert doc['passed']
if __name__=='__main__':main()
