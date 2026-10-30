"""Independent source acceptance checks, executed inside Blender."""
from pathlib import Path
import hashlib,json,math
import bpy,bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
STATES=['healthy',*[f'damage_{i}' for i in range(1,6)],'ruins']

def triangles(objects):return sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects if o.type=='MESH')
def run(require_complete=True):
    errors=[];rows=[]
    if 'PS_Gundeshapur' not in bpy.data.scenes:errors.append('missing dedicated asset scene')
    scene=bpy.data.scenes.get('PS_Gundeshapur')
    expected=STATES if require_complete else ['healthy']
    for state in expected:
        col=bpy.data.collections.get('PS_Gundeshapur_'+state+'_LOD0')
        if col is None:errors.append('missing state '+state);continue
        obs=[o for o in col.all_objects if o.type=='MESH']
        for o in obs:
            if o.data.users!=1:errors.append('shared mesh: '+o.name)
            if any(abs(v-1)>1e-6 for v in o.scale):errors.append('non-unit scale: '+o.name)
            if any(abs(v)>1e-6 for v in o.location) or any(abs(v)>1e-6 for v in o.rotation_euler):errors.append('unapplied transform: '+o.name)
            if len(o.data.uv_layers)!=2:errors.append('UV0/UV1 missing: '+o.name)
            if not o.data.materials or not o.data.polygons:errors.append('empty material or mesh: '+o.name)
            for v in o.data.vertices:
                if not all(math.isfinite(x) for x in v.co):errors.append('nonfinite vertex: '+o.name);break
            for p in o.data.polygons:
                if p.area<1e-10:errors.append('degenerate face: '+o.name);break
            if len(o.users_collection)!=1:errors.append('multiple collection ownership: '+o.name)
        points=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
        lo=[min(v[i] for v in points) for i in range(3)] if points else []
        hi=[max(v[i] for v in points) for i in range(3)] if points else []
        if points and (max(abs(lo[0]),abs(hi[0]))>6.7032 or max(abs(lo[1]),abs(hi[1]))>7.1954):errors.append('outside measured current visual envelope: '+state)
        rows.append({'state':state,'objects':len(obs),'triangles':triangles(obs),'bounds_min':lo,'bounds_max':hi})
    if require_complete:
        for stage in ('foundation','walls','vaults','finish'):
            if not bpy.data.collections.get('PS_Gundeshapur_construct_'+stage):errors.append('missing construction '+stage)
        for level,ratio in ((1,.5),(2,.25)):
            for state in STATES:
                col=bpy.data.collections.get(f'PS_Gundeshapur_{state}_LOD{level}')
                if not col:errors.append('missing reduced detail '+state+' '+str(level));continue
                n=triangles(col.all_objects);base=next(r['triangles'] for r in rows if r['state']==state)
                if abs(n/base-ratio)>.09:errors.append(f'LOD ratio outside tolerance: {state}/{level}: {n/base}')
    # Validate every detail level and construction assembly, not only the healthy state.
    for o in scene.objects:
        if o.type!='MESH' or not o.name.startswith('PS_Gundeshapur_'):continue
        bm=bmesh.new();bm.from_mesh(o.data)
        if any(not e.is_manifold for e in bm.edges):errors.append('nonmanifold mesh: '+o.name)
        if bm.calc_volume(signed=True)<-1e-7:errors.append('inward volume: '+o.name)
        bm.free()
        if o.data.users!=1 or len(o.data.uv_layers)!=2:errors.append('LOD/construction mesh ownership or UV failure: '+o.name)
        for layer in o.data.uv_layers:
            if any(not all(math.isfinite(v) and -.0001<=v<=1.0001 for v in a.uv) for a in layer.data):errors.append('invalid UV range: '+o.name);break
    for name in ('albedo','normal','roughness','metalness','owner_mask'):
        p=ROOT/'textures'/(name+'.png')
        if not p.is_file():errors.append('missing texture '+name)
    for image in bpy.data.images:
        if image.name.startswith('PS_Gundeshapur_') and image.source=='FILE' and not Path(bpy.path.abspath(image.filepath)).is_file():errors.append('unresolved image '+image.name)
    for im in bpy.data.images:
        if im.name.startswith('PS_Gundeshapur_') and list(im.size)!=[2048,2048]:errors.append('wrong atlas size '+im.name)
    if require_complete and rows:
        healthy=next(r for r in rows if r['state']=='healthy');ruin=next(r for r in rows if r['state']=='ruins')
        if not .25<ruin['bounds_max'][2]/healthy['bounds_max'][2]<.34:errors.append('ruin height ratio outside target')
    p=ROOT/'evidence/stock-budget.json'
    if p.exists() and rows:
        cap=json.loads(p.read_text())['budget']['cap']
        if rows[0]['triangles']>cap:errors.append('stock triangle cap exceeded')
    result={'passed':not errors,'errors':errors,'states':rows,'complete':require_complete,'native_validation':'deferred; no build or integration'}
    print(json.dumps(result,indent=2))
    return result
