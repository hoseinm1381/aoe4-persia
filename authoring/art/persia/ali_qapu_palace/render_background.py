"""Final source review from the owned saved file; no mod export or integration."""
from pathlib import Path
import bpy,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import asset_runner as R,presentation as V
assert Path(bpy.data.filepath).resolve()==(ROOT/(ROOT.name+'.blend')).resolve()
R.show_state();s=V.setup();helper=bpy.data.collections['Presentation_'+R.PREFIX[3:-1]]
target=Vector((0,0,6));old_engine=s.render.engine;oldhelper=helper.hide_render
# Workbench uses the camera for headless solid construction inspections.
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';s.display.shading.show_shadows=True
s.render.resolution_x=640;s.render.resolution_y=640;s.camera.data.ortho_scale=21.0
ground=bpy.data.objects.get(helper.name+'_Ground');oldground=ground.hide_render if ground else None
if ground:ground.hide_render=True
for name,pos in [('front',(target.x,-30,target.z)),('back',(target.x,30,target.z)),('left',(-30,target.y,target.z)),('right',(30,target.y,target.z)),('top',(target.x,target.y,30)),('bottom',(target.x,target.y,-30))]:
 s.camera.location=pos;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(ROOT/'previews'/('solid-'+name+'.png'));bpy.ops.render.render(write_still=True)
 print('ORTHOGRAPHIC',name,flush=True)
if ground:ground.hide_render=oldground
s.render.engine=old_engine
for state in ['healthy']+[f'damage_{i}' for i in range(1,6)]+['ruins']+['construct_'+x for x in ('foundation','walls','vaults','finish')]:V.render(state,state)
V.render('owner-red',owner='red');V.render('owner-yellow',owner='yellow');V.render('rear',reverse=True)
for level in (1,2):V.render('lod'+str(level),lod=level)
R.show_state();R.material().node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=(.035,.22,.48,1)
R.save();print('BACKGROUND_REVIEW_COMPLETE',flush=True)
