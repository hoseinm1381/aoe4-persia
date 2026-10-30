"""Actual exposed store-corner coplanarity regression; no master writes."""
from pathlib import Path
import sys,json,hashlib,bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_family as B
import mesh_checks as C

B.factory_guard();root=B.family_root('mill');mode=sys.argv[sys.argv.index('--')+1]
if mode=='before':bpy.ops.wm.open_mainfile(filepath=str(root/'mill.blend'))
else:B.load_recipe(root).build_body('A1')
front=-.51;arch=bpy.data.objects['PSB_mill_A1_StoreDoorArch'];lo,hi=C.bounds(arch);rows=[]
for side in ('West','East'):
    ob=bpy.data.objects['PSB_mill_A1_Store'+side];area=0
    for p in ob.data.polygons:
        points=[ob.matrix_world@ob.data.vertices[i].co for i in p.vertices]
        if not all(abs(v.y-front)<1e-6 for v in points):continue
        # Both narrow side strips are outside the real .82-wide door opening;
        # the arch front at these X intervals is a full-height solid rectangle.
        a=max(0,min(hi[0],max(v.x for v in points))-max(lo[0],min(v.x for v in points)))
        z=max(0,min(hi[2],max(v.z for v in points))-max(lo[2],min(v.z for v in points)))
        area+=a*z
    rows.append({'side':side,'exposed_coincident_face_area_square_metres':area})
defect=any(r['exposed_coincident_face_area_square_metres']>1e-7 for r in rows)
result={'mode':mode,'defect_reproduced':defect,'checks':rows,'passed':defect if mode=='before' else not defect,
        'scope':'Narrow exposed front corner strips only; no generic collision or visual acceptance claim'}
(root/'evidence'/('corner-'+mode+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print('MILL_CORNER_REGRESSION',json.dumps(result),flush=True)
if not result['passed']:raise RuntimeError('Expected regression condition did not hold')
