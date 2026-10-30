"""Current QA set from saved master. Does not save presentation into source."""
from pathlib import Path
import sys,json,bpy,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import recipe as H,presentation as P
R=H.R
KEYS=json.loads((ROOT/'family.json').read_text())['expected_body_keys']
DIRECTIONS={'front':(0,-20,0),'back':(0,20,0),'left':(-20,0,0),'right':(20,0,0),'top':(0,0,20),'bottom':(0,0,-20)}
FRAMES=[]

def frame(key,state,lod,direction,engine='CYCLES'):
    H.show(key,state,lod);s=P.setup();P.fit_camera(key,'healthy',0,direction)
    s.render.engine=engine;s.render.resolution_x=s.render.resolution_y=512
    if engine=='CYCLES':s.cycles.samples=10
    else:
        s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL'
        s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
        s.display.shading.show_shadows=True;s.display.shading.show_specular_highlight=False
    return s

def save(s,name):
    s.render.filepath=str(ROOT/'previews'/name);bpy.ops.render.render(write_still=True)
    path=Path(s.render.filepath)
    FRAMES.append({'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'engine':s.render.engine,'camera_location':list(s.camera.location),'camera_euler':list(s.camera.rotation_euler),'orthographic_scale':s.camera.data.ortho_scale})
    print('QA_FRAME',name,flush=True)

if __name__=='__main__':
    mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'solid'
    master_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    if mode=='solid':
        for key in KEYS:
            for label,d in DIRECTIONS.items():save(frame(key,'healthy',0,d,'BLENDER_WORKBENCH'),f'solid_{key}_{label}.png')
    elif mode=='materials':
        for key in KEYS:save(frame(key,'healthy',0,(8,-11,9)),f'{key}_healthy_LOD0_blue.png')
        for key in ['A1a','A4a']:
            for state in ['damage_1','damage_2','damage_3','damage_4','damage_5','ruins']:
                save(frame(key,state,0,(8,-11,9)),f'{key}_{state}_LOD0_blue.png')
            for stage in ['foundation','walls','vaults','finish']:
                H.show(key,'healthy');s=P.setup();P.fit_camera(key,'healthy',0)
                for c in bpy.data.scenes[R.SCENE].collection.children:
                    if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_construct_'+stage
                s.render.resolution_x=s.render.resolution_y=512;s.cycles.samples=10
                save(s,f'{key}_construct_{stage}.png')
        for key in ['A1a','A2a','A3a','A4a']:
            for lod in [1,2]:save(frame(key,'healthy',lod,(8,-11,9)),f'{key}_healthy_LOD{lod}_blue.png')
        for colour,rgba in [('red',(.58,.025,.018,1)),('yellow',(.78,.54,.025,1))]:
            for key in ['A1a','A4a']:
                s=frame(key,'healthy',0,(8,-11,9));bpy.data.materials[R.PREFIX+'SharedAtlas'].node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=rgba
                save(s,f'{key}_healthy_LOD0_{colour}.png')
        bpy.data.materials[R.PREFIX+'SharedAtlas'].node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=(.035,.22,.48,1)
        for key,part,label,zoom in [('A4a','room_0_PorchLowerBeam','porch-bearing',2.5),('A4c','room_0_SideWindowShutter','side-window',1.8)]:
            s=frame(key,'healthy',0,(8,-11,9));ob=bpy.data.objects[R.PREFIX+key+'_'+part]
            lo,hi=R.bounds(ob);center=(Vector(lo)+Vector(hi))/2;direction=(s.camera.location-center).normalized()
            s.camera.location=center+direction*20;s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=zoom
            save(s,f'close_{key}_{label}.png')
    elif mode=='coverage':
        manifest=json.loads((ROOT/'state-manifest.json').read_text())['compositions']
        for key in KEYS:
            for name in manifest:
                if not name.startswith(R.PREFIX+key+'_'):continue
                s=frame(key,'healthy',0,(8,-11,9),'BLENDER_WORKBENCH');s.render.resolution_x=s.render.resolution_y=256
                for c in bpy.data.scenes[R.SCENE].collection.children:
                    if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=name
                save(s,'coverage_'+name[len(R.PREFIX):]+'.png')
    if master_sha!=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest():raise RuntimeError('Master changed during rendering; set is not qualified as current')
    (ROOT/'evidence'/('render-'+mode+'-receipt.json')).write_text(json.dumps({'passed':True,'saved_file_sha256':master_sha,'frames':FRAMES,'native_rendering':'unverified; source inspection cameras only'},indent=2)+'\n')
