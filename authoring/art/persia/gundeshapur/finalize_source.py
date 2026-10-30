"""Explicit source corrections and diagnostics, reproducible without native game tools."""
import bpy,bmesh,json
import asset_runner as R
import states_recipe as S

def independent_leaf_shells(ob):
    # Each leaf is six sequential quad faces. Keep common plant bases disconnected
    # so separate closed leaves never become a four-face nonmanifold junction.
    me=ob.data;verts=[];faces=[];uvs=[[],[]]
    assert len(me.polygons)%6==0
    for start in range(0,len(me.polygons),6):
        lookup={}
        for p in list(me.polygons)[start:start+6]:
            face=[]
            for vi,li in zip(p.vertices,p.loop_indices):
                if vi not in lookup:lookup[vi]=len(verts);verts.append(tuple(me.vertices[vi].co))
                face.append(lookup[vi])
                for k in range(2):uvs[k].append(tuple(me.uv_layers[k].data[li].uv))
            faces.append(tuple(face))
    new=bpy.data.meshes.new(ob.name+'_closed_leaf_mesh');new.from_pydata(verts,[],faces);new.materials.append(R.material());new.update()
    for k in range(2):
        layer=new.uv_layers.new(name='UVMap' if k==0 else 'UVMap1')
        for a,uv in zip(layer.data,uvs[k]):a.uv=uv
    old=ob.data;ob.data=new
    if old.users==0:bpy.data.meshes.remove(old)

def repairs():
    for ob in list(bpy.data.scenes['PS_Gundeshapur'].objects):
        if ob.type!='MESH' or 'LOD1' in ob.name or 'LOD2' in ob.name:continue
        if ob.name.endswith('PlantedHerbLeaves'):independent_leaf_shells(ob)
        if ob.name.endswith('HallWestWall') or ob.name.endswith('HallEastWall'):
            for v in ob.data.vertices:
                if v.co.y>6.20:v.co.y=6.20
        if '__Debris' in ob.name:
            lo,_=R.bounds(ob)
            for v in ob.data.vertices:v.co.z+=.32-lo[2]
    col=bpy.data.collections.get(R.PREFIX+'damage_5_LOD0')
    for ob in list(col.all_objects) if col else []:
        n=ob.name;lo,hi=R.bounds(ob)
        if any(x in n for x in ('EastRoomDoorPlank','EastDoorBrace','EastDoorFrame')) and hi[1]<-1.75:S.remove(ob)
        elif 'EastWingUpperBand' in n:S.cut(ob,(0,-1.75,0),(0,-1,0))
        elif 'EastScar' in n and hi[1]<-1.75:S.cut(ob,(0,0,1.12),(0,0,1))
    print('CONTACT_AND_FOLIAGE_REPAIRS_COMPLETE')

def clear_lods():
    for state in S.STATES:
        for level in (1,2):
            col=bpy.data.collections.get(R.PREFIX+state+'_LOD'+str(level))
            if col:
                for ob in list(col.all_objects):S.remove(ob)
                bpy.data.collections.remove(col)

def topology():
    rows=[]
    for ob in bpy.data.scenes['PS_Gundeshapur'].objects:
        if ob.type!='MESH' or not ob.name.startswith(R.PREFIX):continue
        bm=bmesh.new();bm.from_mesh(ob.data)
        boundary=sum(e.is_boundary for e in bm.edges);nm=sum(not e.is_manifold for e in bm.edges)
        if boundary or nm:rows.append({'object':ob.name,'boundary_edges':boundary,'nonmanifold_edges':nm})
        bm.free()
    (R.ROOT/'evidence/topology-final.json').write_text(json.dumps(rows,indent=2))
    print('TOPOLOGY_FINAL',len(rows));return rows


def refine():
    import random
    for ob in list(bpy.data.scenes['PS_Gundeshapur'].objects):
        if ob.type!='MESH' or 'LOD1' in ob.name or 'LOD2' in ob.name:continue
        n=ob.name
        if 'DocumentBundle' in n:
            lo,_=R.bounds(ob)
            for v in ob.data.vertices:v.co.z+=.89-lo[2]
        elif 'WritingReed' in n:
            lo,_=R.bounds(ob)
            for v in ob.data.vertices:v.co.z+=.89-lo[2]
        elif 'SupplyCrate2' in n or 'CrateBatten2_' in n:
            lo,_=R.bounds(ob)
            for v in ob.data.vertices:v.co.z+=.66-lo[2]
    for level in range(1,6):
        state='damage_'+str(level);col=bpy.data.collections[R.PREFIX+state+'_LOD0']
        for ob in list(col.all_objects):
            if 'HangingTextile' in ob.name:
                lo,hi=R.bounds(ob);cy=(lo[1]+hi[1])/2
                S.cut(ob,(0,cy,2.13+.018*level),(0,.09,-1))
            if 'EntryCap' in ob.name:
                lo,hi=R.bounds(ob);x=lo[0] if 'West' in ob.name else hi[0]
                S.cut(ob,(x,lo[1],hi[2]-.045*level),(-.4 if x<0 else .4,-.4,1))
    col=bpy.data.collections[R.PREFIX+'ruins_LOD0']
    for ob in list(col.all_objects):
        if ob.get('construction_stage')!='walls' or ob.get('ragged_top'):continue
        bm=bmesh.new();bm.from_mesh(ob.data);lo,hi=R.bounds(ob);rr=random.Random(ob.name)
        top=[e for e in bm.edges if all(v.co.z>hi[2]-.32 for v in e.verts) and e.calc_length()>.5]
        if top:bmesh.ops.subdivide_edges(bm,edges=top,cuts=3,use_grid_fill=False)
        for v in bm.verts:
            if v.co.z>hi[2]-.30:v.co.z-=.035+rr.random()*.14
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob['ragged_top']=True
    print('FINAL_VISUAL_AND_PROP_CONTACT_REFINEMENTS_COMPLETE')
