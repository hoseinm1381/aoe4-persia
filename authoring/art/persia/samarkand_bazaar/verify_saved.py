"""Read back only this saved asset file; optional normal save fixes its opening scene."""
from pathlib import Path
import bpy,sys,importlib,json
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));importlib.invalidate_caches()
import asset_runner as R,source_checks as C,handoff as H

def main():
 assert Path(bpy.data.filepath).resolve().parent==ROOT.resolve(),bpy.data.filepath
 R.show_state();r=C.run();h=H.contacts();assert r['passed'],r['errors'];assert h['passed']
 missing=[];outside=[]
 for im in bpy.data.images:
  if not im.name.startswith(R.PREFIX):continue
  p=Path(bpy.path.abspath(im.filepath)).resolve()
  if not p.is_file():missing.append(str(p))
  if not p.is_relative_to(ROOT):outside.append(str(p))
  im.filepath=bpy.path.relpath(str(p),start=str(ROOT))
 assert not missing and not outside,(missing,outside)
 assert not any(s.name.startswith('PS_') and s.name!=R.PREFIX[:-1] for s in bpy.data.scenes),'unrelated custom scene in asset file'
 # Normal file save writes the selected scene/layout, unlike library-only export.
 old=bpy.context.preferences.filepaths.save_version
 try:
  bpy.context.preferences.filepaths.save_version=0
  R.view(center=(0,0,2.4) if 'Bazaar' in R.PREFIX else (0,-2,2.4),distance=19 if 'Bazaar' in R.PREFIX else 12,solid=False)
  bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
 finally:bpy.context.preferences.filepaths.save_version=old
 result={'passed':True,'file':bpy.data.filepath,'asset_scene':bpy.context.scene.name,'compositions':len(r['compositions']),'source_checks':r['passed'],'contacts':h['passed'],'relative_images':[i.filepath for i in bpy.data.images if i.name.startswith(R.PREFIX)],'unrelated_custom_scenes':False,'native_gates':'deferred'}
 (ROOT/'evidence/saved-readback.json').write_text(json.dumps(result,indent=2)+'\n');print('SAVED_READBACK_PASS')
if __name__=='__main__':main()
