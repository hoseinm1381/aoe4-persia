"""Manifest, guide anchors and source preservation receipts."""
import bpy,json,hashlib,struct
import asset_runner as R
from states_recipe import STATES

def fingerprint(ob):
    h=hashlib.sha256()
    for v in ob.data.vertices:h.update(struct.pack('<3f',*v.co))
    for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
    for layer in ob.data.uv_layers:
        for v in layer.data:h.update(struct.pack('<2f',*v.uv))
    return h.hexdigest()

def write():
    scene=bpy.data.scenes['PS_Gundeshapur'];manifest={'schema':1,'asset':'Gundeshapur','status':'source_art_complete_native_validation_deferred','hp_thresholds':None,'native_bindings':None,'states':{},'restoration':'Restore the exact healthy_LOD0 object/mesh composition recorded here; no scripted gameplay replacement has been assigned.'}
    for c in scene.collection.children:
        if not c.name.startswith(R.PREFIX):continue
        parts=[]
        for o in c.all_objects:
            if o.type!='MESH':continue
            parts.append({'name':o.name,'healthy_source':o.get('healthy_source'), 'role':o.get('role'),'stage':o.get('construction_stage'),'surface':o.get('surface'),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'mesh_uv_sha256':fingerprint(o),'collection':o.users_collection[0].name})
        manifest['states'][c.name]={'parts':parts,'triangles':sum(p['triangles'] for p in parts),'exclusive_with':'all other source state/LOD and construction collections'}
    healthy=manifest['states'][R.PREFIX+'healthy_LOD0']['parts'];finish=manifest['states'][R.PREFIX+'construct_finish']['parts']
    expected={p['name']:p['mesh_uv_sha256'] for p in healthy};actual={p['healthy_source']:p['mesh_uv_sha256'] for p in finish}
    manifest['construction_finish_restores_healthy_exactly']=expected==actual
    (R.ROOT/'state-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    anchors={'compound_origin':[0,0,.28],'entry_axis':[0,-5.95,.28],'iwan_front_face':[0,2.20,.28],'iwan_arch_spring':[0,2.20,2.33],'main_vault_bearing':[0,2.72,4.98],'rear_wall_front':[0,6.20,.28],'dome_drum_bearing':[0,5.0,5.06],'dome_shell_bearing':[0,5.0,5.50],'west_vault_bearing':[-5.05,-1.72,2.96],'east_vault_bearing':[5.05,-1.72,2.96],'teaching_activity':[-3.8,1,.30],'medical_service_activity':[3.2,-.6,.30],'entrance_supplies':[3.3,-5.0,.30]}
    (R.ROOT/'anchors.json').write_text(json.dumps(anchors,indent=2)+'\n')
    c=R.collection('Guides_Gundeshapur',scene.collection)
    for n,xyz in anchors.items():
        name='Anchor_Gundeshapur_'+n;o=bpy.data.objects.get(name)
        if not o:o=bpy.data.objects.new(name,None);c.objects.link(o)
        o.location=xyz;o.empty_display_type='PLAIN_AXES';o.empty_display_size=.18;o.hide_render=True
    c.hide_render=True;c.hide_viewport=True
    original=json.loads((R.ROOT/'evidence/original-scene.json').read_text());s=bpy.data.scenes[original['scene']]
    current={'scene':s.name,'world':s.world.name if s.world else None,'objects':[{'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'mesh_vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in s.objects]}
    preserved=original==current
    (R.ROOT/'evidence/original-scene-preservation.json').write_text(json.dumps({'passed':preserved,'recorded_fields':current},indent=2)+'\n')
    assert preserved,'Original Scene changed';assert manifest['construction_finish_restores_healthy_exactly'],'Construction finish differs from healthy'
    print('MANIFEST',len(manifest['states']),'ORIGINAL_SCENE_UNCHANGED',preserved,'HEALTHY_RESTORATION',manifest['construction_finish_restores_healthy_exactly'])
    return manifest
