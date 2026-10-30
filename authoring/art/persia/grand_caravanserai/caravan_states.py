"""Independent source states; intentionally no native health thresholds/selectors."""
import bpy,bmesh,math,random,json
from mathutils import Vector,Matrix
import asset_runner as R
STATES=['healthy',*[f'damage_{i}' for i in range(1,6)],'ruins'];P=R.PREFIX
def root(state):return R.collection(P+state+'_LOD0',bpy.data.scenes['PS_Caravanserai'].collection)
def sub(state,role):return R.collection(P+state+'_'+role,root(state))
def clone(o,state,col=None):
    q=o.copy();q.data=o.data.copy();q.name=P+state+'__'+o.name.removeprefix(P);q.data.name=q.name+'_mesh';(col or sub(state,o.get('role','architecture'))).objects.link(q)
    q['healthy_source']=o.name;q['state']=state;return q
def remove(o):
    me=o.data;bpy.data.objects.remove(o,do_unlink=True)
    if me.users==0:bpy.data.meshes.remove(me)
def cut(o,point,normal):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
    boundary=[e for e in bm.edges if e.is_boundary]
    caps=bmesh.ops.holes_fill(bm,edges=boundary,sides=0).get('faces',[]) if boundary else []
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.faces.index_update();cap_indices={f.index for f in caps if f.is_valid};bm.to_mesh(o.data);bm.free();o.data.update()
    if not o.data.polygons:remove(o);return None
    # Existing faces retain the original atlas scale. Only newly filled cut caps
    # require UV assignment; bmesh carries all surviving face-loop data through.
    tile=R.TILES.index(o.get('surface','brick'));tx=tile%4;ty=3-tile//4
    for p in o.data.polygons:
        if p.index not in cap_indices:continue
        axis=max(range(3),key=lambda j:abs(p.normal[j]));axes=[j for j in range(3) if j!=axis]
        coords=[o.data.vertices[o.data.loops[i].vertex_index].co for i in p.loop_indices];lo=[min(v[a] for v in coords) for a in axes];scale=max(2.0,max(max(v[a] for v in coords)-lo[k] for k,a in enumerate(axes)))
        for li,v in zip(p.loop_indices,coords):
            uv=((tx+.04+.92*(v[axes[0]]-lo[0])/scale)/4,(ty+.04+.92*(v[axes[1]]-lo[1])/scale)/4)
            for layer in o.data.uv_layers:layer.data[li].uv=uv
    return o
def healthy():return list(bpy.data.collections[P+'healthy_LOD0'].all_objects)
def ground(x,y):
    if 3.2<=abs(x)<=5.28 and abs(y)<=4.20:return .38
    if abs(x)<=3.20 and 3.60<=y<=5.38:return .38
    if abs(x)<1.20 and -6.18<y<-5.06:return .28
    if abs(x)<=3.40 and -4.5<=y<=3.70:return .247
    return .20
def shard(state,name,x,y,w,d,h,surface='brick',seed=0):
    rr=random.Random(seed);z=ground(x,y)
    verts=[(x+sx*w/2,y+sy*d/2,z) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    verts +=[(x+sx*w*(.33+rr.random()*.12),y+sy*d*(.33+rr.random()*.12),z+h*(.6+rr.random()*.4)) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return R.mesh(state+'__'+name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],surface,sub(state,'debris'),'finish','debris')
def debris(state,seed,n,center,radii,size=.25):
    rr=random.Random(seed)
    for j in range(n):
        a=rr.random()*math.tau;r=math.sqrt(rr.random());x=center[0]+math.cos(a)*radii[0]*r;y=center[1]+math.sin(a)*radii[1]*r
        w=size*rr.uniform(.7,1.4);shard(state,'Masonry'+str(seed)+'_'+str(j),x,y,w,w*.67,w*.48,'brick' if j%4 else 'rubble',seed+j)
def scars(state,level):
    rr=random.Random(100+level)
    for s in [-1,1]:
        for j in range(level+1):
            y=rr.uniform(-4.6,4.6);z=.40+rr.uniform(0,1.3);w=.18+level*.065;h=.10+level*.045
            if s==1 and level>=5 and y<-1.02:z=.55
            pts=[(y+math.cos(i*math.tau/10)*w*(.8+rr.random()*.2),z+math.sin(i*math.tau/10)*h*(.8+rr.random()*.2)) for i in range(10)]
            R.extrude_xz(state+'__ImpactScar'+str(s)+'_'+str(j),pts,s*5.615-.003,s*5.615+.003,'rubble',sub(state,'surface_wear'),'finish',lambda u,v,z:(v,u,z),'surface_wear')
def damage(level):
    state='damage_'+str(level);obs={o.name.removeprefix(P):clone(o,state) for o in healthy() if o.type=='MESH'};scars(state,level)
    # Small coping chips and frayed awning edges precede structural loss.
    cut(obs['GateCoping'],(1.78,0,5.45),(1,0,.4))
    aw=obs['UnloadingAwning']
    if level>=2:cut(aw,(-1.84-.025*level,0,0),(1,.03,0))
    for n,o in list(obs.items()):
        if level>=3 and n=='EastSouthButtress':cut(o,(0,0,2.83),(.04,-.03,1))
        if level>=3 and n.startswith('PerimeterCap1_-5.43_') and int(n.rsplit('_',1)[-1])>=7:remove(o)
        if level==4 and n.startswith('EastBay0_') and ('Vault' in n or 'RoofCourse' in n):cut(o,(0,0,2.35),(.02,.14,1))
        if level>=5:
            if n.startswith(('EastBay0_','EastBay1_')):
                if any(t in n for t in ('Facade','Bearing')):cut(o,(0,0,1.00+.12*('Bay1' in n)),(.04,.03,1))
                else:remove(o)
            elif n=='EastOuterWall':
                lower=clone(o,state,sub(state,'architecture'));lower.name=o.name+'_south_stub'
                cut(lower,(0,-1.02,0),(0,1,0));cut(lower,(0,0,1.07),(.02,-.03,1));cut(o,(0,-1.02,0),(0,-1,0))
            elif n=='EastOuterCoping':cut(o,(0,-1.02,0),(0,-1,0))
            elif n=='EastSouthEndWall':cut(o,(0,0,.94),(.02,0,1))
            elif n=='EastSouthButtress':cut(o,(0,0,1.39),(.03,.03,1))
            elif n.startswith('EastDoorDust') and int(n[-1])<2:remove(o)
    if level>=3:debris(state,330,18,(4.83,-5.10),(.6,.45),.22)
    if level>=4:debris(state,440,34,(4.30,-3.10),(.75,.65),.30)
    if level>=5:debris(state,550,52,(4.15,-2.0),(.8,1.75),.40)
    print('STATE',state)

def ragged(o,seed):
    # Jagged closed wall top; cut surfaces are triangulated before uneven displacement.
    rr=random.Random(seed);me=o.data;bm=bmesh.new();bm.from_mesh(me)
    top=max(v.co.z for v in bm.verts);caps=[f for f in bm.faces if f.normal.z>.90 and max(v.co.z for v in f.verts)>top-.12]
    if caps:bmesh.ops.triangulate(bm,faces=caps)
    for v in bm.verts:
        if v.co.z>top-.12:v.co.z-=rr.uniform(0,.13)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()

def ruins():
    state='ruins';rr=random.Random(141)
    for j,o in enumerate(healthy()):
        if o.type!='MESH':continue
        n=o.name.removeprefix(P);role=o.get('role')
        keep=role=='ground' or n.startswith('OuterFooting') or n.startswith('DrainageDirt')
        structural=role=='architecture'
        if not (keep or structural):continue
        q=clone(o,state)
        if structural:
            h=1.0+rr.random()*.43
            if n=='GateFacade':h=1.64
            if 'Buttress' in n:h=1.57
            q=cut(q,(0,0,h),(0,0,1))
            if q:ragged(q,j+510)
    # Recognizable fallen vault sections, still closed source meshes and grounded.
    for i,(x,y,a) in enumerate([(4.15,-2.9,.35),(-4.0,1.8,1.8),(1.9,4.5,2.4),(.1,-4.5,.8),(-3.8,-2.2,2.9)]):
        o=R.vault(state+'__FallenVault'+str(i),0,-.36,.36,0,.60,.84,.18,'brick',sub(state,'debris'),segments=20,along=2,angle0=.18,angle1=1.45,stage='finish')
        rot=Matrix.Rotation(a,4,'Z')@Matrix.Rotation(.7 if i%2 else -.7,4,'Y')
        for v in o.data.vertices:v.co=rot@v.co
        lo,hi=R.bounds(o)
        for v in o.data.vertices:v.co+=Vector((x,y,ground(x,y)-lo[2]))
        o['role']='debris';o['collapse_source']='healthy pointed subsidiary vaults; fragment interpretation';R.retile_surface(o)
    for seed,xy,rad in [(610,(4.1,-1.6),(.9,2.1)),(620,(-4.0,.8),(.8,2.7)),(630,(0,4.6),(2.7,.5)),(640,(0,-4.9),(2.2,.5))]:debris(state,seed,48,xy,rad,.37)
    for i in range(4):shard(state,'BrokenCargo'+str(i),-2.5+i*.38,-1.7,.42,.31,.20,'timber',730+i)
    # One short rag resting on fallen masonry; no pristine surviving banner.
    ob=shard(state,'OwnerFragment',1.70,-4.7,.32,.21,.065,'owner',995);ob['native_owner_marker']='Source mask only';ob['healthy_source']=P+'GateInsetOwner1'
    print('STATE ruins')

def construction():
    ordered=['foundation','walls','vaults','finish']
    for index,stage in enumerate(ordered):
        c=R.collection(P+'construct_'+stage,bpy.data.scenes['PS_Caravanserai'].collection)
        for o in healthy():
            if o.type!='MESH' or ordered.index(o.get('construction_stage','finish'))>index:continue
            q=clone(o,'construct_'+stage,c)
            if index<3 and q.get('surface') in ('plaster','owner','carving'):
                q['surface']='brick';q.color=R.COLOURS[R.TILES.index('brick')];R.retile_surface(q)
        print('CONSTRUCTION',stage)

def normals():
    for o in bpy.data.scenes['PS_Caravanserai'].objects:
        if o.type!='MESH' or not o.name.startswith(P):continue
        bm=bmesh.new();bm.from_mesh(o.data)
        if bm.calc_volume(signed=True)<0:
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);o.data.update()
        bm.free()

def batch():
    for i in range(1,6):damage(i)
    ruins();construction();normals();R.show_state()
