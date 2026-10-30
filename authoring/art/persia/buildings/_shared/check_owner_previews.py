"""Visible RGB owner identity from current rendered pixels, not shader presence."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageChops
ART=Path(__file__).resolve().parent.parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main(slug):
    root=ART/slug;master=sha(root/(slug+'.blend'));receipt_path=root/'evidence/render-healthy-receipt.json';receipt=json.loads(receipt_path.read_text())
    if receipt['saved_file_sha256']!=master:raise RuntimeError('RGB frames are stale against saved source')
    rows=[]
    for key in json.loads((root/'family.json').read_text())['expected_body_keys']:
        frames={f['colour']:f for f in receipt['frames'] if f['composition']=='PSB_'+slug+'_'+key+'_healthy_LOD0' and f['direction']=='game'}
        if set(frames)!=set(['blue','red','yellow']):raise RuntimeError('Missing body RGB frames '+key)
        pictures={}
        for colour,row in frames.items():
            file=root/'previews'/row['file']
            if sha(file)!=row['sha256']:raise RuntimeError('Changed current RGB frame '+str(file))
            pictures[colour]=Image.open(file).convert('RGB')
        counts={}
        for colour in ['red','yellow']:
            diff=ImageChops.difference(pictures['blue'],pictures[colour]);counts[colour+'_vs_blue']=sum(max(px)>10 for px in diff.getdata())
        minimum=max(25,int(pictures['blue'].width*pictures['blue'].height*.00025))
        rows.append({'body':key,'changed_pixels_threshold_10':counts,'minimum_visible_pixels':minimum,'passed':all(n>=minimum for n in counts.values())})
    doc={'passed':all(r['passed'] for r in rows),'saved_file_sha256':master,'render_receipt_sha256':sha(receipt_path),'bodies':rows,'scope':'Source shader/game-camera RGB pixels only; native owner colour remains unverified.'}
    (root/'evidence/owner-preview-check.json').write_text(json.dumps(doc,indent=2)+'\n');print('VISIBLE_OWNER_PIXELS',slug,doc['passed'],rows)
    if not doc['passed']:raise RuntimeError('Owner identity is missing/too occluded in one or more body previews')

if __name__=='__main__':main(sys.argv[1])
