"""Rebuild owned art in memory. No automatic save, cook, export or mod changes."""
import bpy,json,sys,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name):
    spec=importlib.util.spec_from_file_location(name,str(ROOT/(name+'.py')));m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def build(reset_owned=False,preview_setup=False):
    R=load('asset_runner');scene=bpy.data.scenes.get('PS_Caravanserai')
    if scene and list(scene.objects):
        if not reset_owned:raise RuntimeError('Existing generated art: pass reset_owned=True explicitly to reconstruct only owned objects.')
        for o in list(scene.objects):
            if not o.name.startswith((R.PREFIX,'Presentation_Caravanserai','Anchor_Caravanserai')):raise RuntimeError('Unowned object in generated scene: '+o.name)
        objects=list(scene.objects);data=[o.data for o in objects if o.data];bpy.data.batch_remove(ids=objects)
        bpy.data.batch_remove(ids=[d for d in data if d.users==0])
        bpy.data.batch_remove(ids=[c for c in bpy.data.collections if c.name.startswith((R.PREFIX,'Presentation_Caravanserai','Guides_Caravanserai'))])
    C=load('caravanserai_recipe');S=load('caravan_states');F=load('caravan_finalize');L=load('caravan_lods')
    C.foundation();C.first_module();C.architecture();C.details();C.props();C.wear();C.density_and_finish();S.normals()
    for i in range(1,6):S.damage(i)
    S.ruins();F.refine_damage();S.construction();S.normals();L.all_lods();issues=F.topology()
    if issues:raise RuntimeError('Topology issues: '+json.dumps(issues))
    K=load('caravan_checks');contacts=load('contact_checks');report=K.run();cr=contacts.run(True)
    assert report['passed'] and cr['passed'];K.manifest();R.show_state()
    if preview_setup:load('caravan_presentation').setup()
    return {'checks':report,'contacts':cr,'composition':K.composition()}
