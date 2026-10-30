"""Readback checks for the saved master. No save, export or mod build."""
import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import source_checks,contact_checks
checks=source_checks.run();contacts=contact_checks.run();errors=[]
for stage in ('walls','vaults'):
    if any(o.get('surface')=='plaster' for o in bpy.data.collections['PS_Gundeshapur_construct_'+stage].all_objects if o.type=='MESH'):errors.append('premature finish plaster in '+stage)
visible=[c.name for c in bpy.data.scenes['PS_Gundeshapur'].collection.children if c.name.startswith('PS_Gundeshapur_') and not c.hide_render]
if visible!=['PS_Gundeshapur_healthy_LOD0']:errors.append('saved source visibility differs from healthy only')
if any(not im.filepath.replace(chr(92),'/').startswith('//textures/') for im in bpy.data.images if im.name.startswith('PS_Gundeshapur_')):errors.append('nonportable atlas reference')
result={'passed':checks['passed'] and contacts['passed'] and not errors,'errors':errors,'source_checks':checks['passed'],'contacts':contacts['passed'],'saved_visible_asset_collections':visible,'file':bpy.data.filepath,'image_paths':{im.name:im.filepath for im in bpy.data.images if im.name.startswith('PS_Gundeshapur_')},'native_build':False}
(ROOT/'evidence/saved-file-readback.json').write_text(json.dumps(result,indent=2))
assert result['passed'],result
