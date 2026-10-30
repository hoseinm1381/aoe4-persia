"""Regenerate only owned Gundeshapur art, on explicit request. Never builds a mod."""
import bpy,sys,importlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

def build(reset_owned=False):
    import asset_runner as R
    existing=bpy.data.scenes.get('PS_Gundeshapur')
    if existing and not reset_owned:raise RuntimeError('Existing editable art; pass reset_owned=True only when discarding owned generated output intentionally')
    if existing:
        bpy.context.window.scene=bpy.data.scenes['Scene']
        for ob in list(existing.objects):
            if not (ob.name.startswith(R.PREFIX) or ob.name.startswith(('Presentation_Gundeshapur','Anchor_Gundeshapur'))):raise RuntimeError('Unowned object in generated scene; preserve manually before resetting')
        for ob in list(existing.objects):
            data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
            if isinstance(data,bpy.types.Mesh) and data.users==0:bpy.data.meshes.remove(data)
        bpy.data.scenes.remove(existing)
        for col in list(bpy.data.collections):
            if col.name.startswith((R.PREFIX,'Presentation_Gundeshapur','Guides_Gundeshapur')):bpy.data.collections.remove(col)
    import gundeshapur_recipe as G;importlib.reload(G)
    G.phase1();G.phase2();G.phase3();G.phase4();G.contact_repairs();G.support_repair();G.batch_healthy()
    import lod_recipe as L;L.heal_closed_loops()
    import finalize_source as F;F.repairs()
    import states_recipe as S
    for i in range(1,6):S.damage(i)
    S.ruins();S.construction();F.repairs();F.refine();L.all_lods();F.topology()
    R.show_state();return bpy.data.scenes['PS_Gundeshapur']
