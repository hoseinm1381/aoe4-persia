"""One batch review set per family: actual saved states, fast solid coverage.

Open the intended saved master with Blender --background before this script.
Full audits and native gates remain deferred; no source is saved by rendering.
"""
from pathlib import Path
import sys,json
import bpy
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_family as B
import render_family as RF
import source_runner as R

def main(slug):
    root=B.family_root(slug);master=root/(slug+'.blend');before=B.sha(master)
    if Path(bpy.data.filepath).resolve()!=master.resolve():raise RuntimeError('Wrong source master open')
    manifest=json.loads((root/'state-manifest.json').read_text())
    if manifest['saved_file_sha256']!=before:raise RuntimeError('Source manifest/master mismatch')
    unused,scene,presentation=RF.setup(slug);scene.cycles.samples=4
    anchors=json.loads((root/'anchors.json').read_text());frames=[];out=root/'previews/quick';out.mkdir(exist_ok=True)
    def select(col):
        for c in scene.collection.children:
            if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=(c!=col)
        bpy.context.view_layer.update()
    def render(col,direction,label,res,solid=False,colour='blue'):
        transform=Matrix(anchors[key].get('source_checkpoint_frame',{}).get('authored_to_resource_matrix',Matrix.Identity(4)))
        RF.frame(scene,col,transform.to_3x3()@Vector(direction))
        scene.render.resolution_x=scene.render.resolution_y=res
        scene.render.engine='BLENDER_WORKBENCH' if solid else 'CYCLES'
        if solid:
            scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
            scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_shadows=True
        else:
            m=bpy.data.materials[R.PREFIX+'SharedAtlas'];m.node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value={
                'blue':(.035,.22,.48,1),'red':(.58,.025,.018,1),'yellow':(.78,.54,.025,1)}[colour]
        file=label+'.png';scene.render.filepath=str(out/file);bpy.ops.render.render(write_still=True)
        frames.append({'file':file,'composition':col.name,'body':key,'label':label,'solid':solid,'colour':colour,'sha256':B.sha(out/file)})
    for key in manifest['expected_body_keys']:
        healthy=bpy.data.collections[R.PREFIX+key+'_healthy_LOD0'];select(healthy)
        for name,direction in RF.DIRECTIONS.items():
            if name!='game':render(healthy,direction,key+'_solid_'+name,320,True)
        for colour in ('blue','red','yellow'):render(healthy,RF.DIRECTIONS['game'],key+'_healthy_'+colour,448,False,colour)
        for name in sorted(n for n,row in manifest['compositions'].items() if row['body']==key):
            col=bpy.data.collections[name];select(col)
            render(col,RF.DIRECTIONS['game'],name[len(R.PREFIX):]+'_state_solid',224,True)
        for state in ('damage_5','ruins'):
            col=bpy.data.collections[R.PREFIX+key+'_'+state+'_LOD0'];select(col)
            render(col,RF.DIRECTIONS['game'],key+'_'+state+'_material',384)
        print('QUICK_REVIEW_BODY',slug,key,flush=True)
    if B.sha(master)!=before:raise RuntimeError('Rendering changed saved source')
    B.write(root/'evidence/quick-render-receipt.json',{'passed':True,'saved_file_sha256':before,'frames':frames,
        'source_art_only':True,'full_audits_deferred':True,'native_gates':B.NATIVE_GATES})
    print('QUICK_REVIEW_RENDERED',slug,len(frames),flush=True)

if __name__=='__main__':main(sys.argv[sys.argv.index('--')+1])
