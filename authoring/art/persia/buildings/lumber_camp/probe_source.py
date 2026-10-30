"""Parent-run actual healthy source/contact/pose diagnostic; no master save."""
from pathlib import Path
import sys,json,importlib.util,traceback
import bpy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'_shared'))
import native_lumber_sources as L

def main():
 if not bpy.app.background or bpy.data.filepath:raise RuntimeError('Use a dedicated factory process')
 spec=importlib.util.spec_from_file_location('persia_lumber_probe_recipe',ROOT/'recipe.py')
 H=importlib.util.module_from_spec(spec);sys.modules[spec.name]=H;spec.loader.exec_module(H)
 H.build_body('A1');report=L.probe_assembly(H)
 (ROOT/'evidence/source-assembly-probe.json').write_text(json.dumps(report,indent=2)+'\n')
 if not report['passed']:raise RuntimeError('Actual healthy source/contact probe failed; receipt retained')
 print('LUMBER_ACTUAL_HEALTHY_SOURCE_PROBE_PASS',report['triangles'],flush=True)
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'evidence').mkdir(parents=True,exist_ok=True)
  (ROOT/'evidence/source-assembly-probe-failure.txt').write_text(traceback.format_exc())
  raise
