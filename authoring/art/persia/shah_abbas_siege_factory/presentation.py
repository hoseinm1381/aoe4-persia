"""Final-review lighting and renders; helpers are excluded from all source counts."""
import bpy,math
from mathutils import Vector
import asset_runner as R

def setup():
 s=bpy.data.scenes[R.PREFIX[:-1]];bpy.context.window.scene=s
 c=R.collection('Presentation_'+R.PREFIX[3:-1],s.collection)
 target=(0,0,6) if 'AliQapu' in R.PREFIX else (0,0,1.9)
 for name,kind,pos,power,size in [('Sun','SUN',(-10,-14,20),2.1,6),('Fill','AREA',(12,-4,15),650,10),('Rim','AREA',(-5,11,12),750,8)]:
  n=c.name+'_'+name;o=bpy.data.objects.get(n)
  if not o:
   d=bpy.data.lights.new(n,kind);o=bpy.data.objects.new(n,d);c.objects.link(o)
  o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=power
  if kind=='SUN':o.data.angle=.12
  else:o.data.shape='DISK';o.data.size=size
 n=c.name+'_Camera';o=bpy.data.objects.get(n)
 if not o:
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);c.objects.link(o)
 o.data.type='ORTHO';s.camera=o
 if not bpy.data.objects.get(c.name+'_Ground'):
  me=bpy.data.meshes.new(c.name+'_Ground_mesh');me.from_pydata([(-100,-100,-.02),(100,-100,-.02),(100,100,-.02),(-100,100,-.02)],[],[(0,1,2,3)])
  ob=bpy.data.objects.new(c.name+'_Ground',me);c.objects.link(ob);m=bpy.data.materials.new(c.name+'_Ground_mat');m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.19,.17,.13,1);bs.inputs['Roughness'].default_value=.98;me.materials.append(m)
 s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
 s.render.resolution_x=1100;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.30;s.view_settings.view_transform='AgX'
 return s
def render(name,state='healthy',lod=0,owner='blue',reverse=False):
 s=setup();R.show_state(state,lod)
 colours={'blue':(.035,.22,.48,1),'red':(.60,.035,.018,1),'yellow':(.85,.56,.025,1)}
 R.material().node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=colours[owner]
 target=(0,0,6) if 'AliQapu' in R.PREFIX else (0,0,1.9)
 s.camera.location=((-19 if reverse else 19),(26 if reverse else -26),22) if 'AliQapu' in R.PREFIX else ((-12 if reverse else 12),(18 if reverse else -18),15)
 s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=21.2 if 'AliQapu' in R.PREFIX else 12.8
 
 if name!='healthy':s.render.resolution_x=700;s.render.resolution_y=640;s.cycles.samples=12
 s.render.filepath=str(R.ROOT/'previews'/(name+'.png'))
 pref=bpy.context.preferences.addons['cycles'].preferences;old=pref.compute_device_type;olddev=s.cycles.device;flags=[]
 try:
  devices=pref.get_devices_for_type('OPTIX');flags=[(d,d.use) for d in devices]
  if any(d.type=='OPTIX' for d in devices):
   pref.compute_device_type='OPTIX'
   for d in devices:d.use=d.type=='OPTIX'
   s.cycles.device='GPU'
  bpy.ops.render.render(write_still=True)
 finally:
  pass # Dedicated task instance: keep its GPU context between review frames. No preferences are saved.
 print('FINAL_RENDER',name)
