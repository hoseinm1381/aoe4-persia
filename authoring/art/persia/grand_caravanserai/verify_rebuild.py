"""Cold in-memory reconstruction; never overwrites the saved Blender master."""
from pathlib import Path
import sys,json,traceback
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
try:
    expected=json.loads((ROOT/'state-manifest.json').read_text())
    import rebuild_source as B
    r=B.build();actual=r['composition'];errors=[]
    for name,comp in expected['states'].items():
        exp={p['name']:p['mesh_uv_sha256_q5'] for p in comp['parts']}
        got=actual.get(name,{})
        if exp!=got.get('parts'):errors.append({'composition':name,'expected_parts':len(exp),'actual_parts':len(got.get('parts',{})),'mismatched':[n for n in exp if exp[n]!=got.get('parts',{}).get(n)][:12]})
        if sum(p['triangles'] for p in comp['parts'])!=got.get('triangles'):errors.append({'triangles_changed':name})
    doc={'passed':not errors,'errors':errors,'compositions':len(actual),'exact_quantized_mesh_uv_digests':True,'quantization_decimal_places':5,'master_overwritten':False,'source_checks':r['checks']['passed'],'contacts':r['contacts']['passed']}
    (ROOT/'evidence/rebuild-verification.json').write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps(doc,indent=2));assert doc['passed']
except Exception:
    (ROOT/'evidence/rebuild-error.txt').write_text(traceback.format_exc());raise
