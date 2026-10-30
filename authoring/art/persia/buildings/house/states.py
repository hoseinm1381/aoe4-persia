"""House-specific structural collapse and construction source compositions.

No native HP thresholds. Source assemblies are independent, editable and named.
"""
import bpy,bmesh,random,json,math
from mathutils import Vector
import recipe as H
R=H.R
STATES=['healthy',*[f'damage_{n}' for n in range(1,6)],'ruins','preview','targeting']

def destination(key,state,lod=0):
    name=R.PREFIX+key+'_'+state+'_LOD'+str(lod);old=bpy.data.collections.get(name)
    c=R.collection(name,bpy.data.scenes[R.SCENE].collection)
    if old is None:c.hide_render=c.hide_viewport=True
    return c

def clone(o,col,state):
    q=o.copy();q.data=o.data.copy();q.name=o.name+'__'+state;q.data.name=q.name+'_mesh';col.objects.link(q)
    q['healthy_source']=o.get('healthy_source',o.name);q['source_state']=state;return q

def remove(o):
    me=o.data;bpy.data.objects.remove(o,do_unlink=True)
    if not me.users:bpy.data.meshes.remove(me)

def cut(o,point,normal,fracture_surface=None):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
    boundary=[e for e in bm.edges if e.is_boundary]
    caps=bmesh.ops.holes_fill(bm,edges=boundary,sides=0).get('faces',[]) if boundary else []
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.faces.index_update();cap_indices={f.index for f in caps if f.is_valid}
    bm.to_mesh(o.data);bm.free();o.data.update()
    if not o.data.polygons:remove(o);return None
    k=R.TILES.index(fracture_surface or o.get('surface','brick'));tx=k%4;ty=3-k//4
    for p in o.data.polygons:
        if p.index not in cap_indices:continue
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        coords=[o.data.vertices[o.data.loops[i].vertex_index].co for i in p.loop_indices]
        lo=[min(v[a] for v in coords) for a in axes];scale=max(2.0,max(max(v[a] for v in coords)-lo[j] for j,a in enumerate(axes)))
        for li,v in zip(p.loop_indices,coords):
            uv=((tx+.04+.92*(v[axes[0]]-lo[0])/scale)/4,(ty+.04+.92*(v[axes[1]]-lo[1])/scale)/4)
            for layer in o.data.uv_layers:layer.data[li].uv=uv
    return o

def rough_edge(o,point,normal):
    """Matched top/bottom edge chips preserve slab thickness and closure."""
    p=Vector(point);n=Vector(normal).normalized();bm=bmesh.new();bm.from_mesh(o.data)
    edges=[e for e in bm.edges if all(abs((v.co-p).dot(n))<1e-5 for v in e.verts) and abs(e.verts[0].co.z-e.verts[1].co.z)<1e-5 and (e.verts[0].co-e.verts[1].co).length>.12]
    if edges:
        bmesh.ops.subdivide_edges(bm,edges=edges,cuts=3,use_grid_fill=False)
        verts=[v for v in bm.verts if abs((v.co-p).dot(n))<1e-5]
        tangent=Vector((n.y,-n.x,0));coords=[v.co.dot(tangent) for v in verts];a,b=min(coords),max(coords)
        if b-a>1e-5:
            for v in verts:
                t=(v.co.dot(tangent)-a)/(b-a)
                v.co+=n*(math.sin(t*math.pi)*(.055*math.sin(t*5*math.pi)+.022*math.sin(t*9*math.pi)))
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(o.data);bm.free();o.data.update();o['fracture']='matched irregular slab edge; existing top/bottom thickness retained'
    return o

def apply_boolean(q,operand,operation):
    bpy.context.view_layer.update()
    mod=q.modifiers.new('Owned source fracture','BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=operand
    if 'material_mode' in mod.bl_rna.properties:mod.material_mode='INDEX'
    with bpy.context.temp_override(object=q,active_object=q,selected_objects=[q],selected_editable_objects=[q]):bpy.ops.object.modifier_apply(modifier=mod.name)

def corner_cutter(key,level):
    """Three unequal masonry losses form one connected, growing stepped notch."""
    rx,ry,rw,rd=H.PLANS[key[-1]]['rooms'][1];cx=rx+rw/2;cy=ry-rd/2;top=H.F+H.room_height(1,int(key[1]))
    e={1:.28,2:.48,3:.85,4:1.20}[level];c=R.collection(R.PREFIX+'TemporaryFracture',bpy.data.scenes[R.SCENE].collection)
    volumes=[(cx-e*.55,cy+e*.48,top-e*.95),(cx-e*.95,cy+.235,top-e*.37),(cx-.235,cy+e*.80,top-e*.54)]
    blocks=[]
    for j,(xa,yb,za) in enumerate(volumes):
        xb=cx+.60;ya=cy-.60;zb=top+1.0
        q=R.block(key+'_FractureCutter'+str(j),((xa+xb)/2,(ya+yb)/2,(za+zb)/2),(xb-xa,yb-ya,zb-za),'brick',c)
        q.data.materials.append(R.material())
        for p in q.data.polygons:p.material_index=1
        q.hide_render=True;blocks.append(q)
    q=blocks[0]
    for other in blocks[1:]:apply_boolean(q,other,'UNION');remove(other)
    return q,c

def subtract_corner(q,cutter):
    alo,ahi=R.bounds(q);blo,bhi=R.bounds(cutter)
    if any(min(ahi[i],bhi[i])-max(alo[i],blo[i])<=1e-6 for i in range(3)):return q
    q.data.materials.append(R.material());apply_boolean(q,cutter,'DIFFERENCE')
    if not q.data.polygons:remove(q);return None
    core='brick' if q.get('surface')=='plaster' else 'rubble' if q.get('surface') in ['roof','stone'] else q.get('surface','timber')
    tile=R.TILES.index(core);tx=tile%4;ty=3-tile//4
    for p in q.data.polygons:
        if p.material_index!=1:continue
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        pts=[q.data.vertices[q.data.loops[i].vertex_index].co for i in p.loop_indices]
        lo=[min(v[a] for v in pts) for a in axes];scale=max(2.,*(max(v[a] for v in pts)-lo[j] for j,a in enumerate(axes)))
        for li,v in zip(p.loop_indices,pts):
            for layer in q.data.uv_layers:layer.data[li].uv=((tx+.04+.92*(v[axes[0]]-lo[0])/scale)/4,(ty+.04+.92*(v[axes[1]]-lo[1])/scale)/4)
    for p in q.data.polygons:p.material_index=0
    while len(q.data.materials)>1:q.data.materials.pop(index=len(q.data.materials)-1)
    q['fracture']='three unequal connected losses; shared growing masonry/roof notch'
    return q

def debris(key,state,n,seed,center,scale=1):
    rr=random.Random(seed);col=destination(key,state)
    for j in range(n):
        x=max(-1.95,min(1.95,center[0]+rr.uniform(-.46,.46)));y=max(-2.60,min(2.16,center[1]+rr.uniform(-.85,.85)))
        w,d,h=rr.uniform(.11,.24)*scale,rr.uniform(.09,.22)*scale,rr.uniform(.055,.16)*scale;z=H.F
        vs=[(x+sx*w/2,y+sy*d/2,z) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        vs +=[(x+sx*w*.39,y+sy*d*.39,z+h*rr.uniform(.65,1.0)) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        o=R.mesh(key+'_'+state+'_FallenMasonry'+str(seed)+'_'+str(j),vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'rubble',col,'finish','debris')
        o['collapse_source']='secondary domestic room plaster/masonry';o['source_state']=state

def broken_cap(o,seed):
    """Jagged mortar/fracture line; preserve grounded bottom and wall thickness."""
    rr=random.Random(seed);bm=bmesh.new();bm.from_mesh(o.data)
    hi=max(v.co.z for v in bm.verts);lo=min(v.co.z for v in bm.verts);height=hi-lo
    amplitude=min(.13,height*.20)
    top=[v for v in bm.verts if v.co.z>hi-min(.10,height*.20)]
    for v in top:v.co.z+=rr.uniform(-amplitude,amplitude*.27)
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if all(v in top for v in f.verts)])
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    o['fracture']='deterministic irregular cap; base contact preserved'

def damage(key,level):
    state='damage_'+str(level);c=destination(key,state);source=list(H.root(key).all_objects)
    c.hide_viewport=False
    cutter,working=corner_cutter(key,level) if level<=4 else (None,None)
    for index,o in enumerate(source):
        if o.type!='MESH':continue
        q=clone(o,c,state);name=o.name;group=o.get('structural_group');role=o.get('role')
        if group=='room_1' and cutter and role!='ground':
            q=subtract_corner(q,cutter)
            if q is None:continue
        if level>=2 and 'OwnerFascia' in name:
            lo,hi=R.bounds(q);q=cut(q,(hi[0]-.08*level,0,0),(1,.05,0))
            if q is None:continue
        if level>=3 and group=='room_1' and 'ParapetY-1' in name:
            lo,hi=R.bounds(q);q=cut(q,((lo[0]+hi[0])/2,0,0),(1,.05,.05))
            if q is None:continue
        if level>=5 and group=='room_1':
            if role=='architecture':cut(q,(0,0,H.F+.78),(.02,.025,1),fracture_surface='brick' if o.get('surface')=='plaster' else None)
            elif role not in ('ground',):remove(q)
        if level>=5 and group=='room_0':
            top=H.F+H.room_height(0,int(key[1]))*.80
            q=cut(q,(0,0,top),(.025,.025,1),fracture_surface='brick' if o.get('surface')=='plaster' else None)
            if q and role=='architecture':broken_cap(q,1100+index)
    if level<=2:debris(key,state,4+level*2,310+level,H.PLANS[key[-1]]['rooms'][1][:2],scale=.4)
    else:debris(key,state,8+level*5,310+level,H.PLANS[key[-1]]['rooms'][1][:2])
    if level>=5:debris(key,state,18,490,H.PLANS[key[-1]]['rooms'][0][:2])
    if cutter:
        remove(cutter);bpy.data.collections.remove(working)
    c.hide_viewport=True
    print('HOUSE_DAMAGE',key,level)

def ruins(key):
    state='ruins';c=destination(key,state);rr=random.Random(713+ord(key[-1])+int(key[1]))
    healthy=list(H.root(key).all_objects);height=max(R.bounds(o)[1][2] for o in healthy if o.type=='MESH');cap=H.F+(height-H.F)*.29
    for index,o in enumerate(healthy):
        if o.type!='MESH':continue
        if o.get('role') not in ('ground','architecture'):continue
        q=clone(o,c,state)
        if o.get('role')=='architecture':
            localcap=H.F+.30+rr.uniform(0,.12) if o.get('structural_group')=='boundary' else cap-rr.uniform(0,.17)
            q=cut(q,(0,0,localcap),(.015,.01,1),fracture_surface='brick' if o.get('surface')=='plaster' else None)
            if q:broken_cap(q,900+index)
    for j,(x,y,w,d) in enumerate(H.PLANS[key[-1]]['rooms']):debris(key,state,38,710+j,(x,y))
    # Fallen roof timbers are grounded, with one small worn owner fragment.
    for j in range(3):
        R.block(key+'_ruins_FallenTimber'+str(j),(-.65+j*.43,.15+j*.24,H.F+.045),(.73,.08,.09),'timber',c,'finish','debris',rotation=.30+j*.37)
    for j,(x,y) in enumerate([(-.52,.50),(.68,.84),(-1.12,-.40)]):
        w,d,h=.64,.47,.12
        outline=[(-.5,-.5),(.37,-.5),(.5,.10),(.23,.5),(-.5,.32)]
        vs=[(x+a*w,y+b*d,H.F+z) for z in [0,h] for a,b in outline]
        n=len(outline)
        slab=R.mesh(key+'_ruins_RoofFragment'+str(j),vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'roof',c,'finish','debris')
        slab['collapse_source']='grounded broken clay roof slab; no suspended vertices'
    f=R.block(key+'_ruins_OwnerFragment',(.62,-1.72,H.F+.016),(.22,.17,.032),'owner',c,'finish','owner');f['healthy_source']=R.PREFIX+key+'_OwnerFascia';f['source_state']=state
    print('HOUSE_RUINS',key,'cap',cap)

def construction(key):
    stages=['foundation','walls','vaults','finish']
    for n,stage in enumerate(stages):
        c=R.collection(R.PREFIX+key+'_construct_'+stage,bpy.data.scenes[R.SCENE].collection)
        for o in list(H.root(key).all_objects):
            if o.type!='MESH' or stages.index(o.get('construction_stage','finish'))>n:continue
            q=clone(o,c,'construct_'+stage)
            if n<3 and q.get('surface')=='plaster':q['surface']='brick';q.color=R.COLOURS[R.TILES.index('brick')];R.retile_surface(q)
        if n in [1,2]:
            for j in range(3):
                x=-1.55+j*1.45
                R.block(key+'_construct_'+stage+'_ScaffoldPost'+str(j),(x,-2.05,H.F+.78),(.07,.07,1.56),'timber',c,'walls','scaffold')
            R.block(key+'_construct_'+stage+'_ScaffoldDeck',(-.10,-2.05,H.F+1.60),(3.15,.38,.08),'timber',c,'walls','scaffold')
        print('HOUSE_CONSTRUCTION',key,stage)

def placement(key):
    # Exact native inventory: preview == healthy source membership. Targeting
    # omits geo_base_* only; our corresponding authored plot base is EarthBed /
    # CourtBase, while building sills and entrance paving remain architecture.
    for state in ['preview','targeting']:
        c=destination(key,state)
        for o in list(H.root(key).all_objects):
            if o.type!='MESH':continue
            if state=='targeting' and any(n in o.name for n in ['_EarthBed','_CourtBase']):continue
            clone(o,c,state)
        print('HOUSE_PLACEMENT_SOURCE',key,state)

def lods(key):
    from checks import tris
    result=[]
    for state in STATES:
        source=destination(key,state);base=tris(source.all_objects)
        for level in [1,2]:
            c=destination(key,state,level)
            stair_source=[o for o in source.all_objects if o.type=='MESH' and o.get('structural_group')=='stair']
            for i,o in enumerate(list(source.all_objects)):
                if o.type!='MESH':continue
                role=o.get('role');name=o.name
                skip=role in ('fine_detail','wear')
                if 'Joist' in name:skip=True
                if 'FoodBowl' in name:skip=True
                if 'Footing' in name:skip=True
                if level==2 and any(t in name for t in ['GateOwnerBanner','GateOwnerBracket']):skip=True
                if o.get('structural_group')=='stair':skip=True
                if level==2 and (role=='fittings' and 'Door' not in name or 'EntryPaver' in name):skip=True
                step=(3 if level==1 else 8) if state=='ruins' else (2 if level==1 else 4)
                if state=='damage_5' and level==1:step=3
                if role=='debris' and i%step:skip=True
                if role=='props' and level==2 and any(t in name for t in ['Basket','Firewood','FoodBowl','Quern']):skip=True
                if skip:continue
                q=clone(o,c,f'LOD{level}')
                if (q.get('role')=='props' and len(q.data.polygons)>18) or (q.get('role')=='roofs' and 'Vault' in name) or ('UpperHead' in name and len(q.data.polygons)>18):
                    dec=q.modifiers.new('Curved source simplification','DECIMATE');dec.ratio=.5 if level==1 else .22;dec.use_collapse_triangulate=True
                    with bpy.context.temp_override(object=q,active_object=q,selected_objects=[q],selected_editable_objects=[q]):bpy.ops.object.modifier_apply(modifier=dec.name)
                    R.retile_surface(q)
                q['lod_level']=level
            if stair_source:
                lo=[min(R.bounds(o)[0][j] for o in stair_source) for j in range(3)];hi=[max(R.bounds(o)[1][j] for o in stair_source) for j in range(3)]
                x0,y0,z0=lo;x1,y1,z1=hi;steps=6 if level==1 else 3
                profile=[(y0,z0),(y1,z0),(y1,z1)]
                for j in range(steps-1,-1,-1):
                    yy=y0+(y1-y0)*j/steps;profile.append((yy,z0+(z1-z0)*(j+1)/steps))
                    if j:profile.append((yy,z0+(z1-z0)*j/steps))
                q=R.extrude_xz(key+'_'+state+'_LOD'+str(level)+'_SimplifiedStair',profile,x0,x1,'stone',c,'walls',lambda u,v,z:(v,u,z),'architecture')
                q['source_parts']=json.dumps([o.name for o in stair_source]);q['lod_level']=level;q['structural_group']='stair'
            result.append({'body':key,'state':state,'level':level,'triangles':tris(c.all_objects),'base':base,'ratio':tris(c.all_objects)/base})
    (H.ROOT/'evidence'/('lods-'+key+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result

def build(key):
    for n in range(1,6):damage(key,n)
    ruins(key);construction(key);placement(key);return lods(key)
