"""One exact cached Garrison source in a new task-owned background scene.

Run without factory-startup so the installed, configured extension is enabled.
No original/startup scene is saved or modified. Successful source libraries use
libraries.write on the owned scene only. This is source inspection, not playback.
"""
from pathlib import Path
import sys,json,bpy,traceback,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import native_mechanisms as N

def main(target):
    if not bpy.app.background:raise RuntimeError('Use a dedicated background probe process')
    out=ROOT/'mechanisms';out.mkdir(exist_ok=True);report=out/(target+'-probe.json')
    if bpy.data.scenes.get('NSRC_'+target):raise RuntimeError('Owned probe scene already exists; do not reset external edits')
    scene=bpy.data.scenes.new('NSRC_'+target);bpy.context.window.scene=scene
    doc={'target':target,'source_art_only':True,'native_playback_qualified':False,'passed':False}
    try:
        doc['api']=N.inspect_import_api();doc['decoded_bone_projection']=N.inspect_decoded_armature_bones(target);project=N.project_cached(target);doc['project']=project
        doc['import_audit']=N.audit_import(target,project['object_names'])
        meshes=[n for n in project['object_names'] if bpy.data.objects[n].type=='MESH' and 'garrison_group_index' in bpy.data.objects[n]]
        doc['mesh_object_names']=meshes
        doc['reference_geometry']=N.compare_public_reference_geometry(target,meshes)
        arms=[bpy.data.objects[n] for n in project['object_names'] if bpy.data.objects[n].type=='ARMATURE']
        if not arms and doc['decoded_bone_projection'].get('native_skeleton_bone_count'):
            reference=N.reference_armature_views(target);doc['explicit_reference_hierarchy']=reference
            project['object_names']+=reference['object_names']
            arms=[bpy.data.objects[n] for n in reference['object_names'] if bpy.data.objects[n].type=='ARMATURE']
        doc['reference_bones']=[N.audit_reference_bones(target,o.name) for o in arms]
        try:
            if target=='lumber_crane':
                import native_skin_sources as skin_sources
                # Preserve public deform/control rigs intact, then isolate the
                # exact native reference forest for independent LBS tests.
                reference=N.reference_armature_views(target);doc['explicit_reference_hierarchy']=reference
                project['object_names']+=reference['object_names']
                arms=[bpy.data.objects[n] for n in reference['object_names'] if bpy.data.objects[n].type=='ARMATURE']
                if len(arms)!=1:raise RuntimeError('Lumber needs exactly one retained reference armature')
                source=skin_sources.source_views(target,arms[0].name);doc['skin_and_rigid_sources']=source
                doc['skin_weights']=skin_sources.audit_skin_weights(source['skin_object'])
                doc['skin_poses']=[skin_sources.skin_pose_probe(source['skin_object'],arms[0].name,bone) for bone in ['bone_cable_twist','bone_wheel_base']]
                rigid={'armature':arms[0].name,'source_view_objects':source['rigid_objects']};doc['rigid_views']=rigid
            else:
                rigid=N.rigid_source_views(target,project['object_names']);doc['rigid_views']=rigid
            arm=bpy.data.objects[rigid['armature']]
            bound=[b.name for b in arm.data.bones if any(bpy.data.objects[n].parent_bone==b.name for n in rigid['source_view_objects'])]
            bound.sort(key=lambda n:(0 if any(t in n.lower() for t in ['bell','cannon','springald','wheel']) else 1,n))
            if bound:doc['reversible_pose']=N.pose_probe(arm.name,bound[0],rigid['source_view_objects'])
        except Exception:
            doc['rigid_view_qualification_error']=traceback.format_exc()
        try:
            import native_source_appearance as appearance
            doc['native_public_appearance']=appearance.inspect_public_groups(target,project['object_names'])
            views=(doc.get('skin_and_rigid_sources',{}).get('object_names') if target=='lumber_crane'
                   else doc.get('rigid_views',{}).get('source_view_objects'))
            if views:
                doc['native_source_appearance']=appearance.preserve(target,project['object_names'],views)
        except Exception:
            doc['appearance_qualification_error']=traceback.format_exc()
        if target in ('tc_bell_1','tc_bell_2'):
            try:
                import native_bell_sources as bell_sources
                doc['healthy_bell_subset']=bell_sources.healthy_bell_view(target,project['object_names'])
            except Exception:
                doc['healthy_bell_subset_error']=traceback.format_exc()
        doc['sockets']=N.socket_views(target)
        doc['image_dependencies']=[{'name':im.name,'path':bpy.path.abspath(im.filepath)} for im in bpy.data.images if im.source=='FILE' and im.filepath]
        doc['passed']=True;doc['cached_projection_completed']=True
        doc['mechanism_source_qualified']=False
        doc['qualification_scope']='Cached public projection completed; inspect geometry, skeleton, binding and pose evidence separately. Success here is not mechanism acceptance.'
        # Preserve imported reference AND inspectable rigid views. Qualification
        # fields above retain exact limits; a saved library is not native proof.
        destination=out/(target+'.blend')
        known=json.loads(report.read_text()).get('saved_file_sha256') if report.exists() else None
        if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest()!=known:raise RuntimeError('Manual/external mechanism library edit; save refused')
        bpy.data.libraries.write(str(destination),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
        doc['saved_file_sha256']=hashlib.sha256(destination.read_bytes()).hexdigest()
    except Exception:
        doc['error']=traceback.format_exc();doc['passed']=False
    N.write_report(report,doc)
    print('NATIVE_SOURCE_PROBE',target,doc['passed'],doc.get('error',''),flush=True)
    if not doc['passed']:raise RuntimeError('Native source probe failed; inspect '+str(report))

if __name__=='__main__':main(sys.argv[sys.argv.index('--')+1])
