"""Cold reconstruction compares against retained master manifest, without saving."""
from pathlib import Path
import sys,json,bpy,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import recipe as H,states as S,checks as C,fit

def main():
    expected=json.loads((ROOT/'state-manifest.json').read_text())['compositions'];family=json.loads((ROOT/'family.json').read_text());errors=[];count=0
    for key in family['expected_body_keys']:
        H.build_body(key);S.build(key);fit.apply(key)
        r=C.run(key,complete=True,write=False)
        errors+=r['errors']
        for name,row in expected.items():
            if not name.startswith(H.R.PREFIX+key+'_'):continue
            c=bpy.data.collections.get(name);wanted={p['name']:p['geometry_uv_digest_q5'] for p in row['parts']}
            got={o.name:C.digest(o) for o in c.all_objects if o.type=='MESH'} if c else {}
            if got!=wanted:
                changed=[n for n in set(wanted)|set(got) if wanted.get(n)!=got.get(n)]
                errors.append({'composition':name,'changed_parts':changed[:20],'changed_part_count':len(changed)})
            count+=1
        print('COLD_BODY',key,'errors',len(errors),flush=True)
    result={'passed':not errors,'saved_file_sha256':hashlib.sha256((ROOT/'house.blend').read_bytes()).hexdigest(),'state_manifest_sha256':hashlib.sha256((ROOT/'state-manifest.json').read_bytes()).hexdigest(),'checked_compositions':count,'errors':errors,'saved_master':False,'method':'New factory process; retained recipes, compact contracts and texture files. Quantized geometry/UV comparison against master state manifest. No decode cache or stock media needed.'}
    (ROOT/'evidence/rebuild-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('COLD_REBUILD',result['passed'],count,len(errors),flush=True)
    if errors:raise RuntimeError(str(errors[:12]))

if __name__=='__main__':main()
