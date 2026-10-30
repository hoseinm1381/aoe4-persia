"""Presentation helpers outside asset collections, added after modeling."""
import bpy
from mathutils import Vector
import asset_runner as R
from caravan_states import STATES
OUT=R.ROOT/'previews'
def owner(name='blue'):
    values={'blue':(.035,.22,.48,1),'red':(.60,.035,.018,1),'yellow':(.85,.56,.025,1)}
    R.material().node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=values[name]
def setup():
    OUT.mkdir(exist_ok=True);s=bpy.data.scenes['PS_Caravanserai'];bpy.context.window.scene=s;c=R.collection('Presentation_Caravanserai',s.collection)
    for name,kind,pos,power,size in [('Sun','SUN',(-9,-11,18),2.0,5),('Fill','AREA',(9,-2,13),700,10),('Rim','AREA',(-2,11,14),900,8)]:
        full='Presentation_Caravanserai_'+name;data=bpy.data.lights.new(full,kind);ob=bpy.data.objects.new(full,data);c.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler();data.energy=power
        if kind=='AREA':data.shape='DISK';data.size=size
        else:data.angle=.13
    data=bpy.data.cameras.new('Presentation_Caravanserai_Camera');cam=bpy.data.objects.new(data.name,data);c.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';pose()
    me=bpy.data.meshes.new('Presentation_Caravanserai_Ground');me.from_pydata([(-100,-100,-.085),(100,-100,-.085),(100,100,-.085),(-100,100,-.085)],[],[(0,1,2,3)]);ob=bpy.data.objects.new(me.name,me);c.objects.link(ob)
    mat=bpy.data.materials.new('Presentation_Caravanserai_Ground');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.19,.17,.135,1);bs.inputs['Roughness'].default_value=.94;me.materials.append(mat)
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
def pose(pos=(17,-23,20),target=(0,0,2.0),scale=17.6):
    cam=bpy.data.scenes['PS_Caravanserai'].camera;cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
def render(name,state='healthy',lod=0,colour='blue',pos=(17,-23,20),target=(0,0,2),scale=17.6):
    s=bpy.data.scenes['PS_Caravanserai'];R.show_state(state,lod);owner(colour);pose(pos,target,scale);s.render.filepath=str(OUT/(name+'.png'))
    p=bpy.context.preferences.addons['cycles'].preferences;old=p.compute_device_type;oldscene=s.cycles.device;devices=p.get_devices_for_type('OPTIX');flags=[(d,d.use) for d in devices]
    try:
        p.compute_device_type='OPTIX'
        for d in devices:d.use=d.type=='OPTIX'
        s.cycles.device='GPU';bpy.ops.render.render(write_still=True)
    finally:
        s.cycles.device=oldscene
        for d,v in flags:d.use=v
        p.compute_device_type=old
    print('RENDERED',name)
def capture(name,state='healthy',lod=0,colour='blue',pos=(18,-23,18),center=(0,0,2),distance=17,solid=False,construction=None):
    s=bpy.data.scenes['PS_Caravanserai'];R.show_state(state,lod);owner(colour)
    if construction:
        for c in s.collection.children:
            if c.name.startswith(R.PREFIX):c.hide_viewport=c.hide_render=c.name!=R.PREFIX+'construct_'+construction
    presentation=bpy.data.collections['Presentation_Caravanserai'];presentation.hide_viewport=True
    R.view(pos,center,distance,solid);s.render.resolution_x=1000;s.render.resolution_y=900;s.render.filepath=str(OUT/(name+'.png'))
    area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
    try:
        with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
    finally:presentation.hide_viewport=False
    print('CAPTURED',name)
def capture_states():
    for state in STATES:capture('state_'+state,state)
    for stage in ['foundation','walls','vaults','finish']:capture('construction_'+stage,construction=stage)
def capture_extras():
    for lod in [0,1,2]:capture('lod_'+str(lod),lod=lod)
    for colour in ['red','blue','yellow']:capture('owner_'+colour,colour=colour)
    capture('working_courtyard',pos=(-15,-17,23),center=(0,0,1),distance=15)
    capture('unloading_detail',pos=(0,-1.5,1.7),center=(-2.5,-1.65,.8),distance=4.8)
    capture('water_detail',pos=(-1,-3,5),center=(2.5,.8,.6),distance=5.3)
    capture('merchant_detail',pos=(0,-1,4.5),center=(-.20,3.0,.6),distance=5.2)
    capture('damage_5_reverse','damage_5',pos=(-17,-23,20));capture('ruins_reverse','ruins',pos=(-17,-23,20))
    for name,pos in [('front',(0,-25,2)),('back',(0,25,2)),('left',(-25,0,2)),('right',(25,0,2)),('top',(0,0,30)),('bottom',(0,0,-30))]:capture('ortho_'+name,pos=pos,distance=17,solid=True)
    R.show_state();owner();pose();R.view(distance=17,solid=False)
