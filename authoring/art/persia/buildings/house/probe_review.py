"""Small unsaved art-review diagnostic before a full family rebuild."""
from pathlib import Path
import sys,bpy,json,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import recipe as H,states as S,checks as C,fit,presentation as P
OUT=ROOT/'evidence/probe-images';OUT.mkdir(exist_ok=True)
if __name__=='__main__':
    jobs={'A1b':['healthy','damage_1','damage_2','damage_3','damage_4','ruins'],'A3a':['healthy'],'A4c':['healthy']}
    for key,states in jobs.items():
        H.build_body(key);S.build(key);fit.apply(key)
        r=C.run(key,complete=True,write=False)
        if not r['passed']:raise RuntimeError(str(r['errors']))
        for state in states:
            H.show(key,state);s=P.setup();P.fit_camera(key,'healthy');s.render.resolution_x=s.render.resolution_y=512;s.cycles.samples=10
            s.render.filepath=str(OUT/(key+'_'+state+'.png'));bpy.ops.render.render(write_still=True)
        if key=='A3a':
            for lod in [1,2]:
                H.show(key,'healthy',lod);s=P.setup();P.fit_camera(key,'healthy');s.render.resolution_x=s.render.resolution_y=512;s.cycles.samples=10
                s.render.filepath=str(OUT/(key+'_LOD'+str(lod)+'.png'));bpy.ops.render.render(write_still=True)
    (OUT/'receipt.json').write_text(json.dumps({'saved_master':False,'source_recipe_sha256':hashlib.sha256((ROOT/'recipe.py').read_bytes()).hexdigest(),'source_states_sha256':hashlib.sha256((ROOT/'states.py').read_bytes()).hexdigest(),'purpose':'Current unsaved in-memory art probe; not a family acceptance receipt.'},indent=2)+'\n')
    print('UNSAVED_PROBE_REVIEW_READY',flush=True)
