"""Presentation helpers stay outside source-asset composition collections."""
import bpy,math,json
from mathutils import Vector
import recipe as H
R=H.R

def setup():
    s=bpy.data.scenes[R.SCENE];c=R.collection('Presentation_PSB_house',s.collection)
    name='Presentation_PSB_house_Camera';o=bpy.data.objects.get(name)
    if o is None:
        d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);c.objects.link(o)
    o.location=(8,-11,9);target=Vector((0,-.25,1.1));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=7.7;s.camera=o
    for name,loc,power,size in [('Key',(-4,-6,10),950,5),('Fill',(5,-1,6),400,4)]:
        n='Presentation_PSB_house_'+name;light=bpy.data.objects.get(n)
        if light is None:
            d=bpy.data.lights.new(n,'AREA');light=bpy.data.objects.new(n,d);c.objects.link(light)
        light.location=loc;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=power;light.data.shape='DISK';light.data.size=size
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=20;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.film_transparent=True
    (H.ROOT/'previews').mkdir(exist_ok=True)
    return s

def render(key='A1a',state='healthy',lod=0,colour='blue'):
    H.show(key,state,lod);s=setup();m=bpy.data.materials[R.PREFIX+'SharedAtlas']
    fit_camera(key,state,lod)
    m.node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value={'blue':(.035,.22,.48,1),'red':(.58,.025,.018,1),'yellow':(.78,.54,.025,1)}[colour]
    s.render.filepath=str(H.ROOT/'previews'/f'{key}_{state}_LOD{lod}_{colour}.png');bpy.ops.render.render(write_still=True)
    return s.render.filepath

def fit_camera(key,state='healthy',lod=0,direction=(8,-11,9)):
    """Frame actual transformed source bounds; never crop a high alternate body."""
    s=bpy.data.scenes[R.SCENE];cam=s.camera
    col=bpy.data.collections[R.PREFIX+key+'_'+state+'_LOD'+str(lod)]
    points=[o.matrix_world@v.co for o in col.all_objects if o.type=='MESH' for v in o.data.vertices]
    lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
    center=(lo+hi)/2;cam.location=center+Vector(direction).normalized()*20
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    rot=cam.rotation_euler.to_matrix().transposed();xy=[rot@(v-center) for v in points]
    cam.data.ortho_scale=max(max(p[i] for p in xy)-min(p[i] for p in xy) for i in [0,1])*1.16
    return cam
