"""Presentation helpers outside asset collections; no exported cameras or lights."""
import bpy,math,json
from mathutils import Vector
import asset_runner as R
from states_recipe import STATES
OUT=R.ROOT/'previews'

def setup():
    OUT.mkdir(exist_ok=True);s=bpy.data.scenes['PS_Gundeshapur'];bpy.context.window.scene=s
    c=R.collection('Presentation_Gundeshapur',s.collection)
    def light(name,kind,pos,power,size=5):
        ob=bpy.data.objects.get(name)
        if not ob:
            data=bpy.data.lights.new(name,kind);ob=bpy.data.objects.new(name,data);c.objects.link(ob)
        ob.location=pos;ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.energy=power
        if kind=='AREA':ob.data.shape='DISK';ob.data.size=size
        if kind=='SUN':ob.data.angle=.13
        return ob
    light('Presentation_Gundeshapur_Sun','SUN',(-9,-11,18),2.0)
    light('Presentation_Gundeshapur_Fill','AREA',(9,-2,13),700,10)
    light('Presentation_Gundeshapur_Rim','AREA',(-2,11,14),900,8)
    name='Presentation_Gundeshapur_Camera';cam=bpy.data.objects.get(name)
    if not cam:
        data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);c.objects.link(cam)
    s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=19.3
    pose((17,-23,20),(0,0,2.3),19.3)
    # Receiver is separate, untextured and explicitly excluded from asset counts.
    if 'Presentation_Gundeshapur_Ground' not in bpy.data.objects:
        me=bpy.data.meshes.new('Presentation_Ground_mesh');me.from_pydata([(-200,-200,-.085),(200,-200,-.085),(200,200,-.085),(-200,200,-.085)],[],[(0,1,2,3)]);ob=bpy.data.objects.new('Presentation_Gundeshapur_Ground',me);c.objects.link(ob)
        mat=bpy.data.materials.new('Presentation_Ground');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.19,.17,.135,1);bs.inputs['Roughness'].default_value=.94;me.materials.append(mat)
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
    s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100
    s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
    s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
    return s

def pose(pos,target=(0,0,2.3),scale=19.3):
    s=bpy.data.scenes['PS_Gundeshapur'];cam=s.camera
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale

def owner(name):
    values={'blue':(.035,.22,.48,1),'red':(.60,.035,.018,1),'yellow':(.85,.56,.025,1)}
    R.material().node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=values[name]

def render(name,state='healthy',lod=0,colour='blue',pos=(17,-23,20),target=(0,0,2.3),scale=19.3):
    s=bpy.data.scenes['PS_Gundeshapur'];R.show_state(state,lod);owner(colour);pose(pos,target,scale);s.render.filepath=str(OUT/(name+'.png'));write_render();print('RENDERED',name)

def all_states():
    for state in STATES:render(state,state)

def extras():
    for stage in ('foundation','walls','vaults','finish'):
        s=bpy.data.scenes['PS_Gundeshapur']
        for c in s.collection.children:
            if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+'construct_'+stage
        pose((17,-23,20));s.render.filepath=str(OUT/('construction_'+stage+'.png'));write_render()
    for lod in (1,2):render('lod_'+str(lod),lod=lod)
    for col in ('red','yellow'):render('owner_'+col,colour=col)
    render('working_courtyard',pos=(-15,-17,23),target=(0,-.5,1.0),scale=15.5)
    render('teaching_detail',pos=(-8,-7,9),target=(-3.8,.8,.7),scale=5.7)
    render('herb_service_detail',pos=(0,-8,8),target=(3.7,-.6,.8),scale=5.8)
    render('damage_5_reverse','damage_5',pos=(-17,-23,20))
    render('ruins_reverse','ruins',pos=(-17,-23,20))
    R.show_state();owner('blue');pose((17,-23,20))


def write_render():
    # Use available OptiX for this render only, restoring user device preferences.
    s=bpy.data.scenes['PS_Gundeshapur'];p=bpy.context.preferences.addons['cycles'].preferences
    old=p.compute_device_type;oldscene=s.cycles.device;devices=p.get_devices_for_type('OPTIX');flags=[(d,d.use) for d in devices]
    try:
        p.compute_device_type='OPTIX'
        for d in devices:d.use=d.type=='OPTIX'
        s.cycles.device='GPU';bpy.ops.render.render(write_still=True)
    finally:
        s.cycles.device=oldscene
        for d,v in flags:d.use=v
        p.compute_device_type=old


def capture(name,state='healthy',lod=0,colour='blue',pos=(18,-23,18),center=(0,0,2.2),distance=17,solid=False,construction=None):
    s=bpy.data.scenes['PS_Gundeshapur'];R.show_state(state,lod);owner(colour)
    if construction:
        for c in s.collection.children:
            if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+'construct_'+construction
    bpy.data.collections['Presentation_Gundeshapur'].hide_viewport=True
    R.view(pos,center,distance,solid);s.render.resolution_x=1000;s.render.resolution_y=900;s.render.filepath=str(OUT/(name+'.png'))
    a=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in a.regions if r.type=='WINDOW')
    with bpy.context.temp_override(area=a,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
    bpy.data.collections['Presentation_Gundeshapur'].hide_viewport=False
    print('CAPTURED',name)

def capture_set():
    for state in STATES:capture('state_'+state,state)
    for stage in ('foundation','walls','vaults','finish'):capture('construction_'+stage,construction=stage)
    for lod in (0,1,2):capture('lod_'+str(lod),lod=lod)
    for colour in ('red','blue','yellow'):capture('owner_'+colour,colour=colour)
    capture('working_courtyard',pos=(-15,-17,23),center=(0,-.5,1.0),distance=14)
    capture('teaching_detail',pos=(-.3,1.0,2.7),center=(-4.1,1.0,.9),distance=4.4)
    capture('herb_service_detail',pos=(0,-8,8),center=(3.7,-.6,.8),distance=5.7)
    capture('damage_5_reverse','damage_5',pos=(-17,-23,20))
    capture('ruins_reverse','ruins',pos=(-17,-23,20))
    for name,pos in [('front',(0,-25,2.2)),('back',(0,25,2.2)),('left',(-25,0,2.2)),('right',(25,0,2.2)),('top',(0,0,30)),('bottom',(0,0,-30))]:capture('ortho_'+name,pos=pos,distance=17,solid=True)
    R.show_state();owner('blue');R.view(distance=17,solid=False)
