"""Fresh saved-master load audit; no saves or native operations."""
from pathlib import Path
import bpy,sys,json
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import caravan_checks as K,contact_checks as C,asset_runner as R
r=K.run();c=C.run(True);errors=[]
if not r['passed'] or not c['passed']:errors+=r['errors'];errors+=['contacts'] if not c['passed'] else []
visible=[x.name for x in bpy.data.scenes['PS_Caravanserai'].collection.children if x.name.startswith(R.PREFIX) and not x.hide_viewport]
if visible!=[R.PREFIX+'healthy_LOD0']:errors.append('saved state visibility')
textures=[]
for im in bpy.data.images:
    if not im.name.startswith(R.PREFIX):continue
    rel=im.filepath.replace('\\','/');textures.append({'name':im.name,'path':im.filepath,'exists':Path(bpy.path.abspath(im.filepath)).is_file()})
    if not rel.startswith('//textures/'):errors.append('nonrelative source texture '+im.name)
doc={'passed':not errors,'errors':errors,'actual_file':bpy.data.filepath,'visible_asset_collections':visible,'textures':textures,'native_build':False}
(ROOT/'evidence/saved-file-readback.json').write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps(doc,indent=2));assert doc['passed']
