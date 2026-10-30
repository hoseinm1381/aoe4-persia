"""Retain a compact real pre-repair failure receipt before replacing master."""
from pathlib import Path
import sys,json,bpy,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import recipe as H,checks as C
if __name__=='__main__':
    defects=C.coplanar_roof_overlaps(H.root('A4a'))
    wanted=[d for d in defects if 'room_1_Roof' in (d['a']+d['b']) and 'PorchFloor' in (d['a']+d['b'])]
    result={'actual_pre_repair_master_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'passed_regression':bool(wanted),'detected_real_defects':wanted,'scope':'Same-facing upward roof/deck rectangular faces; buried joinery is outside this detector.'}
    (ROOT/'evidence/roof-joint-pre-repair-regression.json').write_text(json.dumps(result,indent=2)+'\n')
    print('REAL_ROOF_REGRESSION',bool(wanted),len(wanted),flush=True)
    if not wanted:raise RuntimeError('Pre-repair failure was not reproduced')
