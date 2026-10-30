"""Source-art gates. No native build or gameplay success is implied."""
import bpy,bmesh,math,json,hashlib,struct
from pathlib import Path
import asset_runner as R
from caravan_states import STATES
from caravan_lods import tris
def digest(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(struct.pack('<3f',*(round(x,5) for x in v.co)))
    for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
    for layer in o.data.uv_layers:
        for v in layer.data:h.update(struct.pack('<2f',*(round(x,5) for x in v.uv)))
    return h.hexdigest()
def composition():
    result={}
    for c in bpy.data.scenes['PS_Caravanserai'].collection.children:
        if c.name.startswith(R.PREFIX):result[c.name]={'triangles':tris(c.all_objects),'parts':{o.name:digest(o) for o in c.all_objects if o.type=='MESH'}}
    return result
def original_record():
    s=bpy.data.scenes['Scene'];return {'scene':s.name,'world':s.world.name if s.world else None,'objects':[{'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'mesh_vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in s.objects]}
def run(complete=True,write=True):
    errors=[];rows=[];s=bpy.data.scenes['PS_Caravanserai'];budget=json.loads((R.ROOT/'evidence/stock-budget.json').read_text())['budget']
    expected=[R.PREFIX+state+'_LOD'+str(lod) for state in STATES for lod in [0,1,2]]+[R.PREFIX+'construct_'+st for st in ['foundation','walls','vaults','finish']]
    for name in expected:
        c=bpy.data.collections.get(name)
        if c is None:errors.append('missing composition '+name);continue
        obs=[o for o in c.all_objects if o.type=='MESH'];n=tris(obs)
        points=[v.co for o in obs for v in o.data.vertices];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
        if lo[0]<-6.1001 or hi[0]>6.1001 or lo[1]<-6.3001 or hi[1]>6.1001:errors.append('outside chosen envelope '+name)
        if n>budget['cap']:errors.append('triangle cap '+name)
        if '_LOD' in name and not name.endswith('LOD0'):
            base=bpy.data.collections[name[:-1]+'0'];ratio=n/tris(base.all_objects);target=.5 if name.endswith('1') else .25
            if abs(ratio-target)>.09:errors.append(f'LOD ratio {name}: {ratio:.4f}')
        rows.append({'collection':name,'objects':len(obs),'triangles':n,'bounds_min':lo,'bounds_max':hi,'visible':not c.hide_viewport})
        for o in obs:
            if o.data.users!=1:errors.append('shared mesh '+o.name)
            if any(abs(x)>1e-7 for x in (*o.location,*o.rotation_euler)) or any(abs(x-1)>1e-7 for x in o.scale):errors.append('transform '+o.name)
            if len(o.users_collection)!=1:errors.append('collection ownership '+o.name)
            if len(o.data.uv_layers)!=2 or len(o.data.materials)!=1:errors.append('UV/material '+o.name)
            if o.modifiers:errors.append('unbaked modifier '+o.name)
            for layer in o.data.uv_layers:
                if any(not all(math.isfinite(v) and -.0001<=v<=1.0001 for v in a.uv) for a in layer.data):errors.append('UV range '+o.name);break
            bm=bmesh.new();bm.from_mesh(o.data)
            if any(not e.is_manifold for e in bm.edges):errors.append('nonmanifold '+o.name)
            if any(f.calc_area()<1e-10 for f in bm.faces):errors.append('degenerate '+o.name)
            if bm.calc_volume(signed=True)<=0:errors.append('inward or zero-volume '+o.name)
            bm.free()
    for kind in ['albedo','normal','roughness','metalness','owner_mask']:
        im=bpy.data.images.get(R.PREFIX+kind)
        if not im or list(im.size)!=[2048,2048] or not Path(bpy.path.abspath(im.filepath)).is_file():errors.append('unresolved 2048 texture '+kind)
    if set(bpy.data.scenes.keys())!={'Scene','PS_Caravanserai'}:errors.append('unrelated asset scene included')
    original=json.loads((R.ROOT/'evidence/original-scene.json').read_text())
    if original!=original_record():errors.append('original default scene changed')
    hc=bpy.data.collections[R.PREFIX+'healthy_LOD0'];cc=bpy.data.collections[R.PREFIX+'construct_finish']
    a={o.name:digest(o) for o in hc.all_objects if o.type=='MESH'};b={o.get('healthy_source'):digest(o) for o in cc.all_objects if o.type=='MESH'}
    if a!=b:errors.append('construction finish does not restore healthy exactly')
    hr=max(v.co.z for o in hc.all_objects if o.type=='MESH' for v in o.data.vertices)
    rc=bpy.data.collections[R.PREFIX+'ruins_LOD0'];rz=max(v.co.z for o in rc.all_objects if o.type=='MESH' for v in o.data.vertices)
    if not .25<rz/hr<.34:errors.append('ruin height')
    if sum(o.get('surface')=='owner' for o in rc.all_objects)!=1:errors.append('ruin owner fragment count')
    result={'passed':not errors,'errors':errors,'compositions':rows,'construction_exact_healthy_restore':a==b,'ruin_height_ratio':rz/hr,'stock_budget':budget,'native_gates':'deferred; source art only'}
    if write:(R.ROOT/'evidence/source-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print('SOURCE_CHECKS',not errors,'ERROR_COUNT',len(errors),json.dumps(errors[:30]));return result
def manifest():
    states={}
    for c in bpy.data.scenes['PS_Caravanserai'].collection.children:
        if not c.name.startswith(R.PREFIX):continue
        states[c.name]={'mutually_exclusive':True,'parts':[{'name':o.name,'source_parts':o.get('source_parts'),'healthy_source':o.get('healthy_source'),'surface':o.get('surface'),'stage':o.get('construction_stage'),'role':o.get('role'),'triangles':tris([o]),'mesh_uv_sha256_q5':digest(o)} for o in c.all_objects if o.type=='MESH']}
    doc={'asset':'The Grand Caravanserai','schema':1,'status':'source_art','native_hp_thresholds':None,'native_bindings':None,'states':states,'construction_finish':'Exact healthy composition, including mesh/UV digests; use this manifest for future repair restoration.'}
    (R.ROOT/'state-manifest.json').write_text(json.dumps(doc,indent=2)+'\n')
    from caravanserai_recipe import ANCHORS
    (R.ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n')
    c=R.collection('Guides_Caravanserai',bpy.data.scenes['PS_Caravanserai'].collection)
    for name,xyz in ANCHORS.items():
        o=bpy.data.objects.get('Anchor_Caravanserai_'+name)
        if o is None:o=bpy.data.objects.new('Anchor_Caravanserai_'+name,None);c.objects.link(o)
        o.location=xyz;o.empty_display_type='PLAIN_AXES';o.empty_display_size=.15
    c.hide_viewport=c.hide_render=True
    return doc
