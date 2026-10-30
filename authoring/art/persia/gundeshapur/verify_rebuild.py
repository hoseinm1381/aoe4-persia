"""Cold in-memory Blender recipe check. Does not save or alter the master blend."""
import sys,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
try:
    import rebuild_source
    scene=rebuild_source.build()
    import source_checks,contact_checks
    checks=source_checks.run();contacts=contact_checks.run()
    assert checks['passed'] and contacts['passed']
    expected=json.loads((ROOT/'state-manifest.json').read_text())['states']
    actual={c.name:source_checks.triangles(c.all_objects) for c in scene.collection.children if c.name.startswith('PS_Gundeshapur_')}
    counts={k:v['triangles'] for k,v in expected.items()}
    result={'passed':actual==counts,'master_overwritten':False,'expected_triangles':counts,'actual_triangles':actual}
    (ROOT/'evidence/rebuild-verification.json').write_text(json.dumps(result,indent=2))
    assert result['passed'],'Recipe output counts differ from saved source'
except Exception:
    (ROOT/'evidence/rebuild-error.txt').write_text(traceback.format_exc());raise
