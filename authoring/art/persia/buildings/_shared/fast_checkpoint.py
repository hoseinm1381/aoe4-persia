"""Owner-requested quick source checkpoint, with unresolved checks retained.

Batch authoring is distinct from QA acceptance. No failed check becomes a pass.
Use a fresh factory process; existing task masters are replaced only by hash.
"""
from pathlib import Path
import sys,json,traceback
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_family as B
import state_geometry as G

def main(slug):
    B.factory_guard();root=B.family_root(slug);master=root/(slug+'.blend')
    before=B.sha(master) if master.exists() else None
    receipts=[root/'evidence'/n for n in ('healthy-build-receipt.json','build-receipt.json','source-checkpoint-receipt.json')]
    known=[json.loads(p.read_text()).get('saved_file_sha256') for p in receipts if p.is_file()]
    if before and before not in known:raise RuntimeError('Manual/external source edit; overwrite refused')
    pinned=B.fingerprints(root);fallbacks=[];load=B.load_recipe
    def quick_load(path):
        H=load(path);H.FAST_SOURCE_CHECKPOINT=True
        if hasattr(H,'build_lod'):
            original=H.build_lod
            def lod(h,key,state,source,dest,level,profile):
                try:return original(h,key,state,source,dest,level,profile)
                except Exception:
                    error=traceback.format_exc()
                    # Only newly generated owned destination data in this
                    # factory process. Original inputs and source are retained.
                    for ob in list(dest.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
                    for child in list(dest.children):bpy.data.collections.remove(child)
                    G.simplify(h.R,source,dest,level,profile)
                    fallbacks.append({'body':key,'state':state,'lod':level,'error':error,
                        'fallback':'Provisional proven generic source reduction. Family-specific ratio/rig qualification remains unchecked.'})
            H.build_lod=lod
        return H
    B.load_recipe=quick_load
    H,checks,manifest=B.generate(root)
    if len(manifest['compositions'])!=len(manifest['expected_body_keys'])*31:raise RuntimeError('Incomplete source coverage')
    if B.fingerprints(root)!=pinned or (B.sha(master) if master.exists() else None)!=before:raise RuntimeError('Inputs/master changed during source generation')
    H.write_anchors();H.show(manifest['expected_body_keys'][0])
    for image in bpy.data.images:
        if image.name.startswith(H.R.PREFIX):image.filepath='//textures/'+Path(image.filepath).name
    H.R.save();master_sha=B.sha(master)
    manifest.update({'saved_file_sha256':master_sha,'geometry_input_sha256':pinned,
        'source_checkpoint_only':True,'quality_accepted':False,'unresolved_check_count':len(checks['errors']),
        'provisional_lod_fallbacks':fallbacks,'checkpoint_generator_sha256':B.sha(__file__),
        'scope':'Owner-requested quick batch source art. One visual review pending; exhaustive audits/native validation deferred.'})
    B.write(root/'state-manifest.json',manifest)
    checks.update({'family':slug,'authored_source_set_saved':True,'source_quality_accepted':False,
        'saved_file_sha256':master_sha,'state_manifest_sha256':B.sha(root/'state-manifest.json'),
        'complete_compositions':len(manifest['compositions']),'geometry_input_sha256':pinned,
        'provisional_lod_fallbacks':fallbacks,'checkpoint_generator_sha256':B.sha(__file__),
        'owner_priority':'Quickly finish all20; reuse helpers, batch states/LODs, fix visible defects after one review, defer exhaustive audits/native validation.'})
    B.write(root/'evidence/source-checkpoint-receipt.json',checks)
    print('AUTHORED_SOURCE_CHECKPOINT',slug,len(manifest['compositions']),'unresolved_checks',len(checks['errors']),'LOD_fallbacks',len(fallbacks),flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    try:main(args[0])
    except Exception:
        if args:(B.ART/args[0]/'evidence/quick-checkpoint-error.txt').write_text(traceback.format_exc())
        raise
