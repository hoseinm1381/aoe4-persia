"""Bounded unsaved regression for a thin Town Center arcade cut."""
from pathlib import Path
import sys,json,bpy,bmesh
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_family as B
import state_geometry as G
import mesh_checks as C

def volume(ob):
    bm=bmesh.new();bm.from_mesh(ob.data)
    value=bm.calc_volume(signed=True);bm.free();return value

B.factory_guard();root=B.family_root('town_center');H=B.load_recipe(root)
H.build_body('A4');R=H.R
source=bpy.data.objects['PSB_town_center_A4_Hall_Arcade2']
c=R.collection('PSB_fracture_check',bpy.data.scenes[R.SCENE].collection)
q=G.clone(source,c,'regression');values={'healthy_volume':volume(q)}
profile=json.loads((root/'state-profiles.json').read_text())['bodies']['A4']
cap=profile['damage']['heavy_failure_group_caps']['public_hall']
G.cut(R,q,(0,0,cap),(.018,.023,1),surface='brick')
values['cut_volume']=volume(q)
# Its exact sorted-source position selects the production deterministic seed.
sources=sorted(H.root('A4').all_objects,key=lambda o:o.name)
changed=0
for ob in sources:
    if ob.name==source.name:break
    if ob.type=='MESH' and ob.get('structural_group','') in profile['damage']['heavy_failure_group_caps'] and ob.get('role')!='ground':changed+=1
G.broken_cap(q,750+changed);values['broken_volume']=volume(q)
bm=bmesh.new();bm.from_mesh(q.data)
values['nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges);bm.free()
values['passed']=values['broken_volume']>0 and values['nonmanifold_edges']==0 and abs(values['broken_volume']/values['cut_volume']-1)<.05
(root/'evidence/fracture-regression.json').write_text(json.dumps(values,indent=2)+'\n')
print('FRACTURE_REGRESSION',json.dumps(values),flush=True)
if not values['passed']:raise RuntimeError('Thin arcade exposed-cap regression failed')
