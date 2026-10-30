"""Editable, explicitly optional TC bell configurations; no native admission claim.

Run only in a new factory background process: KEY TARGET CATEGORY MODE.
Modes build/readback/cold/render never mutate the main Town Center master.
Each candidate retains both native selector meshes and the exact reference rig.
"""
from pathlib import Path
import sys,json,traceback
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_family as B
import mesh_checks as C
import native_bell_library as BL
import native_bell_sources as BS
import render_family as RF

def require(test,message):
    if not test:raise RuntimeError(message)

def snapshot(H,key):
    objects={o.name:o for o in H.root(key).all_objects}
    attachment=H.ANCHORS[key]['native_bell_source_attachment']
    reference=bpy.data.collections[attachment['inspectable_native_alternative_collection']]
    objects.update({o.name:o for o in reference.all_objects})
    return {'parts':[B.part_record(o) for o in sorted(objects.values(),key=lambda o:o.name) if o.type=='MESH'],
        'rigs':{o.name:{'matrix':[list(row) for row in o.matrix_world],
            'bones':{b.name:{'parent':b.parent.name if b.parent else None,'matrix_local':[list(row) for row in b.matrix_local]} for b in o.data.bones},
            'poses':{b.name:[list(row) for row in b.matrix_basis] for b in o.pose.bones}}
            for o in objects.values() if o.type=='ARMATURE'}}

def construct(key,target,category):
    root=B.family_root('town_center');H=B.load_recipe(root);H.build_body(key)
    attachment=BL.append_and_attach(H,key,target,category)
    checks=[C.mesh_report(o) for o in H.root(key).all_objects if o.type=='MESH']
    checks += [C.contact_report(c) for c in H.CONTRACTS if c['body']==key]
    checks += [C.interface_report(c) for c in H.ANCHORS[key].get('numerical_interfaces',[])]
    require(all(r['passed'] for r in checks),'Actual alternative mesh/contact/interface check failed')
    aliases=[]
    for alias in ('healthy','dmg_01','dead'):
        aliases.append(BS.select_source_bell_alias(H,key,alias))
    BS.select_source_bell_alias(H,key,'healthy')
    return H,attachment,checks,aliases

def main(key,target,category,mode):
    B.factory_guard();root=B.family_root('town_center')
    owned=root/'mechanisms';owned.mkdir(exist_ok=True)
    token=key+'_'+category;master=owned/(token+'.blend');receipt=owned/(token+'.json')
    inputs=B.fingerprints(root)
    for p in (Path(__file__),BL.DEFAULT_LIBRARY,BL.DEFAULT_LIBRARY.with_suffix('.json'),
              Path(BL.__file__),Path(BS.__file__)):
        inputs[str(p.resolve())]=B.sha(p)
    main_sha=B.sha(root/'town_center.blend');main_manifest_sha=B.sha(root/'state-manifest.json')
    if mode in ('build','cold'):
        H,attachment,checks,aliases=construct(key,target,category)
        geometry=snapshot(H,key)
        if mode=='cold':
            wanted=json.loads(receipt.read_text())
            require(wanted['geometry_input_sha256']==inputs and B.sha(master)==wanted['saved_file_sha256'],'Cold alternative input/master changed')
            require(geometry==wanted['snapshot'],'Cold alternative geometry/rig reconstruction differs')
            B.write(owned/(token+'-cold.json'),{'passed':True,'saved_file_sha256':B.sha(master),'geometry_input_sha256':inputs,'exact_snapshot_match':True})
            print('TC_BELL_ALTERNATIVE_COLD_PASS',token,flush=True);return
        if master.exists():
            require(receipt.exists() and B.sha(master)==json.loads(receipt.read_text())['saved_file_sha256'],'Manual alternative source edit; overwrite refused')
        text=bpy.data.texts.new('TC_BELL_EDITING_AND_SCOPE.json')
        text.write(json.dumps({'key':key,'target':target,'category':category,'source_art_only':True,
            'coordinates':'Authored TC stamp-space. Main family master uses recorded resource-space inverse; do not apply both.',
            'source_selector_aliases':aliases,'attachment':attachment,
            'instructions':'Select healthy/dmg_01/dead with retained shared native_bell_sources.select_source_bell_alias. The damaged mesh and reference forest remain individually editable. No new clips.',
            'runtime_category_admission':'Unproved. These are three supplied alternatives for each existing body, not an invented age-category assignment.'},indent=2))
        old=bpy.context.preferences.filepaths.save_version
        try:
            bpy.context.preferences.filepaths.save_version=0
            bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
        finally:bpy.context.preferences.filepaths.save_version=old
        B.write(receipt,{'passed':True,'body':key,'target':target,'category':category,'saved_file_sha256':B.sha(master),
            'geometry_input_sha256':inputs,'snapshot':geometry,'attachment':attachment,'checks':checks,'aliases':aliases,
            'source_anchors':H.ANCHORS,'source_art_only':True,'native_runtime_category_selection_proven':False})
        print('TC_BELL_ALTERNATIVE_SAVED',token,flush=True)
    else:
        wanted=json.loads(receipt.read_text());before=B.sha(master)
        require(wanted['passed'] and before==wanted['saved_file_sha256'] and wanted['geometry_input_sha256']==inputs,'Stale alternative source')
        bpy.ops.wm.open_mainfile(filepath=str(master));H=B.load_recipe(root);H.CURRENT=key;H.ANCHORS.update(wanted['source_anchors'])
        require(snapshot(H,key)==wanted['snapshot'],'Saved alternative geometry/rig readback differs')
        if mode=='readback':
            B.write(owned/(token+'-readback.json'),{'passed':True,'saved_file_sha256':before,'geometry_input_sha256':inputs,'exact_snapshot_match':True})
            print('TC_BELL_ALTERNATIVE_READBACK_PASS',token,flush=True)
        elif mode=='render':
            unused,scene,presentation=RF.setup('town_center');scene.cycles.samples=8
            scene.render.resolution_x=scene.render.resolution_y=640
            frames=[]
            for alias in ('healthy','dmg_01','dead'):
                BS.select_source_bell_alias(H,key,alias)
                RF.frame(scene,H.root(key),Vector((8,-11,9)))
                path=root/'previews'/('bell_'+token+'_'+alias+'.png');scene.render.filepath=str(path)
                bpy.ops.render.render(write_still=True)
                frames.append({'file':path.name,'selector_alias':alias,'sha256':B.sha(path)})
            BS.select_source_bell_alias(H,key,'healthy')
            focus=[bpy.data.objects[wanted['attachment']['active_healthy_bell_object']]]+[bpy.data.objects[n] for n in wanted['attachment']['original_frame_objects']]
            RF.frame(scene,H.root(key),Vector((4,-8,3)),focus)
            path=root/'previews'/('bell_'+token+'_support.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            frames.append({'file':path.name,'selector_alias':'healthy_support_closeup','sha256':B.sha(path)})
            require(B.sha(master)==before,'Render changed alternative master')
            B.write(owned/(token+'-render.json'),{'passed':True,'saved_file_sha256':before,'frames':frames,'native_playback_qualified':False})
        else:raise ValueError('Expected build/readback/cold/render')
    require(B.sha(root/'town_center.blend')==main_sha and B.sha(root/'state-manifest.json')==main_manifest_sha,'Main family source changed')

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    try:main(*args)
    except Exception:
        if args:
            p=Path(__file__).resolve().parent.parent/'town_center/evidence'/('bell-alternative-'+args[0]+'-failure.txt')
            p.write_text(traceback.format_exc())
        raise
