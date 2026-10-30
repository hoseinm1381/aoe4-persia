"""Actual Blender parent/mesh preservation and nonidentity rejection regression."""
from pathlib import Path
from types import SimpleNamespace
import sys,json,bpy
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_family as B
import mesh_checks as C
B.factory_guard();prefix='PSB_frame_regression_';key='A1';scene=bpy.context.scene
for name in B.expected_names(prefix,[key]):
    col=bpy.data.collections.new(name);scene.collection.children.link(col)
col=bpy.data.collections[prefix+key+'_healthy_LOD0']
parent=bpy.data.objects.new(prefix+'NativeRoot',None);col.objects.link(parent);parent.location=(1,2,3)
mesh=bpy.data.meshes.new(prefix+'mesh');mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)],[],[(0,1,2)])
ob=bpy.data.objects.new(prefix+'Surface',mesh);col.objects.link(ob);ob.parent=parent;ob.location=(.5,.2,.1)
bpy.context.view_layer.update()
H=SimpleNamespace(R=SimpleNamespace(PREFIX=prefix),ANCHORS={key:{'authored_space':'model-space'}})
before=(C.digest(ob),tuple(tuple(r) for r in ob.matrix_world),ob.parent.as_pointer())
B.apply_frame(H,key,Matrix.Identity(4));bpy.context.view_layer.update()
after=(C.digest(ob),tuple(tuple(r) for r in ob.matrix_world),ob.parent.as_pointer())
preserved=before==after
del ob['source_resource_frame_applied'];rejected=False
try:B.apply_frame(H,key,Matrix.Translation((1,0,0)))
except RuntimeError as e:rejected='preserved dependency adapter' in str(e)
result={'passed':preserved and rejected,'identity_preserves_mesh_world_and_parent':preserved,'nonidentity_parent_graph_rejected':rejected,
        'scope':'Coordinate-adapter guard only; actual native pose/binding compatibility requires separate source probes'}
(Path(__file__).parent/'identity-frame-regression.json').write_text(json.dumps(result,indent=2)+'\n')
print('IDENTITY_FRAME_REGRESSION',result)
if not result['passed']:raise RuntimeError('Identity frame regression failed')
