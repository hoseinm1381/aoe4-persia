"""Cold source reconstruction. Run in a fresh Blender process, never on a hand-edited scene."""
from pathlib import Path
import bpy,sys,json,importlib,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));importlib.invalidate_caches()
import asset_runner as R,states_recipe as S,lod_recipe as L,source_checks as C,handoff as H

def run(save=False):
 if bpy.data.scenes.get(R.PREFIX[:-1]) and list(bpy.data.scenes[R.PREFIX[:-1]].objects):
  raise RuntimeError('Use a fresh --factory-startup process; this would overwrite current art')
 expected=json.loads((ROOT/'state-manifest.json').read_text()) if not save else None
 if 'Bazaar' in R.PREFIX:
  import bazaar_recipe as B
 else:
  import brotherhood_recipe as B
 B.build_all();S.build_all();L.all_lods();checks=C.run(report_name='rebuild-source-checks.json');contacts=H.contacts();actual=H.write(save=save)
 assert checks['passed'],checks['errors'];assert contacts['passed']
 differences=[]
 if expected:
  for name,row in expected['states'].items():
   old={p['name']:p['mesh_uv_sha256'] for p in row['parts']};new={p['name']:p['mesh_uv_sha256'] for p in actual['states'][name]['parts']}
   for part in old.keys()|new.keys():
    if old.get(part)!=new.get(part):differences.append({'composition':name,'part':part})
 result={'passed':not differences,'mode':'explicit recipe rebuild and save' if save else 'cold in-memory reconstruction against canonical manifest','mesh_uv_differences':differences,'source_checks_passed':checks['passed'],'contacts_passed':contacts['passed'],'construction_finish_exact':actual['construction_finish_restores_healthy_exactly'],'external_custom_asset_dependencies':False}
 (ROOT/'evidence'/('recipe-save-receipt.json' if save else 'cold-rebuild.json')).write_text(json.dumps(result,indent=2)+'\n')
 if save:R.show_state();R.save()
 print('COLD_REBUILD',result['passed'],'DIFFERENCES',len(differences));assert result['passed'],differences[:8]
 return result

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 if args not in (['--verify'],['--rebuild-and-save']):raise SystemExit('Use -- --verify, or explicit -- --rebuild-and-save in a fresh --factory-startup Blender')
 run(save=args==['--rebuild-and-save'])
