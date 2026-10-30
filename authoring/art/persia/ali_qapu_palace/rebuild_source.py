"""Cold deterministic reconstruction. Default verify never writes the canonical master."""
from pathlib import Path
import bpy,sys,json,importlib,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));importlib.invalidate_caches()
import state_contacts as A
import asset_runner as R,healthy_recipe as B,states_recipe as S,lod_recipe as L,source_checks as C,handoff as H
def run(save=False):
 if bpy.data.scenes.get(R.PREFIX[:-1]) and list(bpy.data.scenes[R.PREFIX[:-1]].objects):raise RuntimeError('Use a fresh --factory-startup process; never overwrite a loaded or hand-edited source scene')
 master=ROOT/(ROOT.name+'.blend');before=hashlib.sha256(master.read_bytes()).hexdigest() if master.exists() else None
 expected=json.loads((ROOT/'state-manifest.json').read_text()) if not save else None
 manifest_sha=hashlib.sha256((ROOT/'state-manifest.json').read_bytes()).hexdigest() if not save else None
 B.build_all(save=save);S.build_all();L.all_lods();audit=C.run(report_name='cold-source-checks.json');contacts=H.contacts();all_contacts=A.run();actual=H.write(save=save)
 differences=[]
 if expected:
  if expected.get('material_contract',{}).get('sha256')!=actual['material_contract']['sha256']:differences.append({'material_contract':'shader node/input/link mismatch'})
  for state,row in expected['states'].items():
   old={p['name']:p['mesh_uv_sha256'] for p in row['parts']};new={p['name']:p['mesh_uv_sha256'] for p in actual['states'][state]['parts']}
   for name in old.keys()|new.keys():
    if old.get(name)!=new.get(name):differences.append({'state':state,'part':name})
  for row in expected['source_dependencies']:
   if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']:differences.append({'dependency':row['path']})
 if save:R.show_state();R.save()
 after=hashlib.sha256(master.read_bytes()).hexdigest() if master.exists() else None
 result={'passed':audit['passed'] and contacts['passed'] and all_contacts['passed'] and not differences and (save or before==after),'mode':'explicit rebuild and replace owned master' if save else 'cold verification in fresh Blender; canonical bytes preserved','differences':differences,'source_checks':audit['passed'],'contacts':contacts['passed'],'master_sha256_before':before,'master_sha256_after':after,'manifest_sha256':manifest_sha,'canonical_unchanged':before==after,'construction_finish_exact':actual['construction_finish_restores_healthy_exactly'],'compositions':len(actual['states'])}
 (ROOT/'evidence'/('recipe-save.json' if save else 'cold-rebuild.json')).write_text(json.dumps(result,indent=2)+'\n')
 print('COLD_REBUILD',result['passed'],'DIFFERENCES',len(differences));assert result['passed'],result
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 if args not in (['--verify'],['--rebuild-and-save']):raise SystemExit('Use -- --verify, or explicit -- --rebuild-and-save with fresh --factory-startup')
 run(save=args==['--rebuild-and-save'])
