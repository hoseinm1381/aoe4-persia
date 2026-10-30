"""Current saved-source inspection; never saves presentation into the master."""
from pathlib import Path
import sys,json,hashlib
import bpy
from mathutils import Vector,Matrix
ART=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ART/'_shared'))
import source_runner as R
import mesh_checks as C
DIRECTIONS={'front':(0,-20,0),'back':(0,20,0),'left':(-20,0,0),'right':(20,0,0),'top':(0,0,20),'bottom':(0,0,-20),'game':(8,-11,9)}

def setup(slug):
    root=ART/slug;R.configure(root,slug);s=bpy.data.scenes[R.SCENE];bpy.context.window.scene=s
    collection=R.collection('Presentation_'+R.SCENE,s.collection)
    name='Presentation_'+R.SCENE+'_Camera';data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);collection.objects.link(camera);s.camera=camera;data.type='ORTHO'
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12
    s.render.resolution_x=s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True
    for label,location,power,size in [('Key',(-4,-6,10),950,5),('Fill',(5,-1,6),400,4)]:
        name='Presentation_'+R.SCENE+'_'+label;d=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,d);collection.objects.link(ob);ob.location=location;d.energy=power;d.shape='DISK';d.size=size
    return root,s,collection

def frame(s,collection,direction,focus_objects=None):
    points=[p for ob in (focus_objects if focus_objects is not None else collection.all_objects) if ob.type=='MESH' for p in C.world_points(ob)]
    lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);center=(lo+hi)/2
    cam=s.camera;cam.location=center+Vector(direction).normalized()*30;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    rotation=cam.rotation_euler.to_matrix().transposed();xy=[rotation@(v-center) for v in points];scale=max(max(p[i] for p in xy)-min(p[i] for p in xy) for i in [0,1])*1.16;cam.data.ortho_scale=scale
    pres=bpy.data.collections['Presentation_'+R.SCENE]
    for ob in pres.objects:
        if ob.type=='LIGHT':
            offset=Vector((-4,-6,10) if ob.name.endswith('Key') else (5,-1,6))*max(1,scale/7)
            ob.location=center+offset;ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.energy=(950 if ob.name.endswith('Key') else 400)*max(1,scale/7)**2;ob.data.size=(5 if ob.name.endswith('Key') else 4)*max(1,scale/7)

def main(slug,mode='healthy'):
    root,s,_=setup(slug);source=Path(bpy.data.filepath);source_sha=hashlib.sha256(source.read_bytes()).hexdigest();anchors=json.loads((root/'anchors.json').read_text());keys=json.loads((root/'family.json').read_text())['expected_body_keys'];frames=[]
    if mode=='closeups':
        s.render.resolution_x=s.render.resolution_y=960;s.cycles.samples=20
        view_path=root/'review-views.json'
        if not view_path.is_file():view_path=root/'evidence/review-views.json'
        for view in json.loads(view_path.read_text())['views']:
            key=view['body'];name=R.PREFIX+key+'_'+view.get('state','healthy')+'_LOD'+str(view.get('lod',0))
            col=bpy.data.collections[name]
            for c in s.collection.children:
                if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=(c!=col)
            focus=[bpy.data.objects[n] for n in view['objects']]
            if not focus or any(o not in list(col.all_objects) for o in focus):raise RuntimeError('Closeup focus outside selected composition')
            transform=Matrix(anchors[key].get('source_checkpoint_frame',{}).get('authored_to_resource_matrix',Matrix.Identity(4)))
            frame(s,col,transform.to_3x3()@Vector(view['direction']),focus)
            s.render.engine='CYCLES';file='closeup_'+view['name']+'.png';path=root/'previews'/file
            m=bpy.data.materials[R.PREFIX+'SharedAtlas'];m.node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=(.035,.22,.48,1)
            s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            frames.append({'file':file,'composition':name,'view':view,'engine':s.render.engine,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'orthographic_scale':s.camera.data.ortho_scale})
        if hashlib.sha256(source.read_bytes()).hexdigest()!=source_sha:raise RuntimeError('Saved source changed during closeup inspection')
        (root/'evidence/render-closeups-receipt.json').write_text(json.dumps({'passed':True,'saved_file_sha256':source_sha,'frames':frames,'source_art_only':True,'family_accepted':False},indent=2)+'\n')
        return
    if mode not in ('healthy','coverage'):raise ValueError('Unknown render mode')
    if mode=='coverage':
        # Coverage grids inspect silhouette and state/LOD completeness. Detailed
        # healthy/RGB and structural closeups keep their larger resolutions.
        s.render.resolution_x=s.render.resolution_y=384;s.cycles.samples=8
    for key in keys:
        cols=[c for c in s.collection.children if c.name.startswith(R.PREFIX+key+'_') and (mode=='coverage' or c.name==R.PREFIX+key+'_healthy_LOD0')]
        for col in cols:
            for c in s.collection.children:
                if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=(c!=col)
            transform=Matrix(anchors[key].get('source_checkpoint_frame',{}).get('authored_to_resource_matrix',Matrix.Identity(4)))
            directions=DIRECTIONS if mode=='healthy' else {'game':DIRECTIONS['game']}
            for label,direction in directions.items():
                direction=transform.to_3x3()@Vector(direction);frame(s,col,direction)
                s.render.engine='CYCLES' if label=='game' else 'BLENDER_WORKBENCH'
                if s.render.engine=='BLENDER_WORKBENCH':
                    s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_shadows=True
                colors=['blue','red','yellow'] if label=='game' and mode=='healthy' else ['blue']
                for color in colors:
                    m=bpy.data.materials[R.PREFIX+'SharedAtlas'];m.node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value={'blue':(.035,.22,.48,1),'red':(.58,.025,.018,1),'yellow':(.78,.54,.025,1)}[color]
                    name=col.name[len(R.PREFIX):]+'_'+label+'_'+color+('_coverage' if mode=='coverage' else '')+'.png';path=root/'previews'/name;s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
                    frames.append({'file':name,'composition':col.name,'direction':label,'colour':color,'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'cycles_samples':s.cycles.samples if s.render.engine=='CYCLES' else None,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),'orthographic_scale':s.camera.data.ortho_scale})
                    print('FAMILY_SOURCE_FRAME',slug,name,flush=True)
    if hashlib.sha256(source.read_bytes()).hexdigest()!=source_sha:raise RuntimeError('Saved source changed during inspection')
    (root/'evidence'/('render-'+mode+'-receipt.json')).write_text(json.dumps({'passed':True,'saved_file_sha256':source_sha,'frames':frames,'source_art_only':True,'family_accepted':False},indent=2)+'\n')

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];main(args[0],args[1] if len(args)>1 else 'healthy')
