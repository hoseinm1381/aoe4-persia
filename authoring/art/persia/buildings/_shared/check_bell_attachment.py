"""Fresh-process real TC/native bell source fit; never writes a family master."""
from pathlib import Path
import sys,json,bpy,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_family as B
import mesh_checks as C
import native_bell_library as BL

B.factory_guard();args=sys.argv[sys.argv.index('--')+1:]
key,target,category=args;root=B.family_root('town_center');out=root/'evidence'/('bell-'+key+'-'+category+'.json')
doc={'passed':False,'body':key,'target':target,'category':category,'source_art_only':True,'native_playback_qualified':False}
try:
    H=B.load_recipe(root);H.build_body(key)
    doc['attachment']=BL.append_and_attach(H,key,target,category)
    doc['mesh_checks']=[C.mesh_report(o) for o in H.root(key).all_objects if o.type=='MESH']
    doc['contacts']=[C.contact_report(c) for c in H.CONTRACTS if c['body']==key]
    doc['interfaces']=[C.interface_report(c) for c in H.ANCHORS[key].get('numerical_interfaces',[])]
    doc['passed']=all(r['passed'] for k in ('mesh_checks','contacts','interfaces') for r in doc[k])
except Exception:doc['error']=traceback.format_exc()
out.write_text(json.dumps(doc,indent=2)+'\n')
print('BELL_ATTACHMENT_PROBE',key,category,doc['passed'],doc.get('error',''),flush=True)
if not doc['passed']:raise RuntimeError('Actual cold bell attachment failed; inspect '+str(out))
