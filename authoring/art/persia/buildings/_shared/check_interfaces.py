"""Analytic contact regression: embedded timber joint versus a real missed joint."""
from pathlib import Path
import sys,json,bpy
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import source_runner as R,mesh_checks as C
R.configure(ROOT/'interface_check','interface_check')
s=R.setup_scene();col=R.collection('OwnedAnalyticContacts',s.collection)
material=bpy.data.materials.new('AnalyticJointMaterial');R.material=lambda:material
post=R.block('Post',(0,0,0),(.14,.14,1),'timber',col)
brace=R.block('Brace',(.2,0,0),(.4,.1,.1),'timber',col)
miss=R.block('MissedBrace',(.5,0,0),(.4,.1,.1),'timber',col)
base={'name':'AnalyticPostCentre','a':post.name,'b':brace.name,'authored_contact_point':[0,0,0],'intentional_socket_overlap_metres':.07}
rows=[C.interface_report(base),C.interface_report({**base,'b':miss.name}),C.interface_report({**base,'intentional_socket_overlap_metres':.025})]
assert [r['passed'] for r in rows]==[True,False,False],rows
out=ROOT/'interface_check/evidence/analytic-joint-regression.json'
out.write_text(json.dumps({'passed':True,'basis':'Analytic closed14cm post, exact brace endpoint, and30cm missedjoint. Intentionalembed cannot allow an outsidepoint gap.','cases':rows},indent=2)+'\n')
print('ANALYTIC_INTERFACE_REGRESSION_PASS',flush=True)
