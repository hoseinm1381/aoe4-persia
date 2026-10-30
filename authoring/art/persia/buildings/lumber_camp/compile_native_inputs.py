"""Parent entry: Blender --background --factory-startup --python THIS.

Writes only selected source library and owned Lumber dependency receipts.
Never imports the Garrison extension, decodes, cooks or modifies native sources.
"""
from pathlib import Path
import sys,json,traceback
import bpy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'_shared'))
import native_lumber_sources as L
import native_mechanisms as N

def main():
 if not bpy.app.background or bpy.data.filepath:raise RuntimeError('Use a dedicated factory process, not a live scene')
 report=L.compile_library()
 plan,binding,_=L._sources()
 family_path=ROOT/'family.json';family=json.loads(family_path.read_text());before=N._sha(family_path)
 paths=[ROOT.parent/'_shared'/n for n in ('native_lumber_sources.py','native_mechanisms.py','native_skin_sources.py','native_source_appearance.py')]
 paths += [L.LIBRARY,L.LIBRARY.with_suffix('.json'),L.PARTITION,Path(plan['manifest_path']),
  N.INVENTORY/'RIGID_MECHANISM_BINDINGS.json',N.INVENTORY/'mechanism-composition/lumber_camp.json',
  L.LIBRARY.parent/'lumber_crane.blend',L.LIBRARY.parent/'lumber_crane-probe.json',
  Path(binding['native_rgm_local_path']),Path(binding['native_rrgeom_local_path'])]
 body=json.loads((ROOT/'native-contracts.json').read_text())['bodies']['A1']
 paths += [Path(g['local_path']) for g in body['native_animation_graphs']]
 paths += [Path(row['path']) for row in report['image_dependencies']]
 if any(not p.is_file() for p in paths):raise RuntimeError('Retained source dependency missing')
 family['retained_input_paths']=sorted(set(family.get('retained_input_paths',[]))|{str(p.resolve()) for p in paths})
 family_path.write_text(json.dumps(family,indent=2)+'\n')
 contract_path=ROOT/'mechanism-input-contract.json';contract=json.loads(contract_path.read_text())
 contract.update(library_actual_compilation_pending=False,library_sha256=report['library_sha256'],
  actual_compilation_receipt=str(ROOT/'evidence/native-input-library-compilation.json'))
 contract_path.write_text(json.dumps(contract,indent=2)+'\n')
 report['family_dependency_receipt']=dict(previous_family_sha256=before,current_family_sha256=N._sha(family_path),retained_file_count=len(paths))
 (ROOT/'evidence').mkdir(parents=True,exist_ok=True)
 (ROOT/'evidence/native-input-library-compilation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('LUMBER_FUNCTIONAL_LIBRARY_COMPILED',report['library_sha256'],flush=True)
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'evidence').mkdir(parents=True,exist_ok=True)
  (ROOT/'evidence/native-input-library-failure.txt').write_text(traceback.format_exc())
  raise
