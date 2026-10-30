"""Independent construction, damage and ruined compositions. No native HP mapping."""
import bpy,bmesh,math,json,random
from mathutils import Vector,Matrix
import asset_runner as R
ROOT=R.ROOT;P=R.PREFIX;G=.28
STATES=['healthy',*[f'damage_{i}' for i in range(1,6)],'ruins']

def root(state):return R.collection(P+state+'_LOD0',bpy.data.scenes['PS_Gundeshapur'].collection)
def stagecol(state,stage):return R.collection(P+state+'_'+stage,root(state))
def clone(o,state,col=None):
    q=o.copy();q.data=o.data.copy();q.name=P+state+'__'+o.name.removeprefix(P);q.data.name=q.name+'_mesh'
    (col or stagecol(state,o.get('construction_stage','finish'))).objects.link(q)
    q['healthy_source']=o.name;q['state']=state;return q

def copy_state(state):
    return {o.name.removeprefix(P):clone(o,state) for o in bpy.data.collections[P+'healthy_LOD0'].all_objects if o.type=='MESH'}

def remove(ob):
    me=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
    if me.users==0:bpy.data.meshes.remove(me)

def reproject(ob):
    # Retain exact surface atlas region on cut caps and repaired triangles.
    tile=R.TILES.index(ob.get('surface','brick'));tx=tile%4;ty=3-tile//4;me=ob.data;me.update()
    for layer in me.uv_layers:
        for poly in me.polygons:
            ax=max(range(3),key=lambda j:abs(poly.normal[j]));axes=[i for i in range(3) if i!=ax]
            for li in poly.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co
                layer.data[li].uv=((tx+.04+.92*((co[axes[0]]*.41)%1))/4,(ty+.04+.92*((co[axes[1]]*.41)%1))/4)

def cut(ob,point,normal):
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:
        bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    if bm.faces:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    if not ob.data.polygons:remove(ob);return None
    reproject(ob);return ob

def shard(name,state,pos,size,material='rubble',rr=None):
    rr=rr or random.Random(19);x,y,z=pos;w,d,h=size
    # Grounded irregular stone with a non-pristine top face.
    verts=[(x+sx*w/2,y+sy*d/2,z) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    verts += [(x+sx*w*(.32+rr.random()*.13),y+sy*d*(.32+rr.random()*.13),z+h*(.6+rr.random()*.4)) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    return R.mesh(state+'__'+name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material,stagecol(state,'debris'),'finish','debris')

def debris(state,n,center,radii,scale=.25,seed=23):
    rr=random.Random(seed)
    for i in range(n):
        a=rr.random()*math.tau;r=math.sqrt(rr.random());x=center[0]+r*radii[0]*math.cos(a);y=center[1]+r*radii[1]*math.sin(a)
        h=scale*(.4+rr.random());z=.32
        shard('Debris'+str(seed)+'_'+str(i),state,(x,y,z),(h*1.5,h,h*.6),'brick' if i%3 else 'rubble',rr)

def scarring(state,level):
    rr=random.Random(901+level)
    for sign,side in ((-1,'West'),(1,'East')):
        for j in range(level+1):
            yy=-4.8+rr.random()*6.4;zz=.73+rr.random()*(.2+level*.17);ww=.3+level*.16;hh=.18+level*.10
            shape=[(yy+ww*(.4+rr.random()*.1)*math.cos(i*math.tau/12),zz+hh*(.4+rr.random()*.1)*math.sin(i*math.tau/12)) for i in range(12)]
            R.extrude_xz(state+'__'+side+'Scar'+str(j),shape,sign*6.21-.004,sign*6.21+.007,'brick',stagecol(state,'surface_wear'),'finish',transform=lambda u,v,z:(v,u,z),role='surface_wear')

def damage(level):
    state='damage_'+str(level);obs=copy_state(state);scarring(state,level)
    # Minor fraying progressively shortens the same hanging cloth pieces.
    for name,o in list(obs.items()):
        if 'HangingTextile' in name:
            z=2.10+.035*level
            cut(o,(0,0,z),(.02,.12,-1))
            o['treatment']='frayed lower cloth edge'
    if level>=3:
        ob=obs.get('EastWingUpperBand')
        if ob:cut(ob,(0,-3.20,0),(0,-1,0))
        debris(state,14,(5.82,-4.15),(.35,1.0),.18,13)
    if level>=4:
        # Subsidiary roof is fractured at a partition; its disconnected front remnant
        # remains on two bearing walls until the partial collapse composition.
        for name in ('EastWingVault','EastRoofRibs','EastClayTileCourses'):
            ob=obs.get(name)
            if ob:
                if level==4:
                    front=clone(ob,state,stagecol(state,'vaults'));front.name=ob.name+'_front_remnant'
                    cut(front,(0,-4.63,0),(0,1,0))
                cut(ob,(0,-1.75,0),(0,-1,0))
        debris(state,37,(4.96,-3.27),(1.10,1.48),.26,14)
    if level>=5:
        for name,o in list(obs.items()):
            if o.name not in bpy.data.objects:continue
            if name.startswith('EastBay1') or name.startswith('EastBay2') or name.startswith('EastSouthVault') or name.startswith('EastRoomDoor0') or name.startswith('EastRoomDoor1'):
                remove(o);continue
            if name in ('EastPartition0','EastPartition1','EastWingOuterWall'):
                if name=='EastWingOuterWall':
                    low=clone(o,state,stagecol(state,'walls'));low.name=o.name+'_lower_stub';cut(low,(0,-1.75,0),(0,1,0));cut(low,(0,0,1.17),(.04,-.06,1))
                    cut(o,(0,-1.75,0),(0,-1,0))
                else:cut(o,(0,0,.99),(.03,-.08,1))
            if 'EastHangingTextile0' in name or 'EastBannerRod0' in name or 'EastBannerWallBracket0' in name:remove(o)
        for j,y in enumerate((-5.54,-3.65,-1.75)):
            R.block(state+'__BrokenEastPier'+str(j),(3.94,y,.71),(.33,.40,.86),'brick',stagecol(state,'walls'),'walls')
        debris(state,65,(4.95,-4.01),(1.20,1.46),.34,15)
    R.show_state(state)
    print('DAMAGE_READY',state,len(root(state).all_objects))

def ruins():
    state='ruins';col=root(state)
    for o in bpy.data.collections[P+'healthy_LOD0'].all_objects:
        name=o.name.removeprefix(P)
        if o.get('construction_stage')=='foundation':clone(o,state)
        elif o.get('construction_stage')=='walls':
            # Every standing remnant is a grounded lower section; no floating arches.
            if any(k in name for k in ('IwanFacade','HallWestWall','HallEastWall','HallRearDoor','WingOuterWall','Bay','Partition','FrontBoundary','EntryPier','RearConnector','WingNorthEnd','Buttress')):
                q=clone(o,state);height=1.95 if 'IwanFacade' in name else (1.66 if 'Hall' in name else 1.04+random.Random(name).random()*.27)
                cut(q,(0,0,height),(.016,.022,1))
                q['surface']='brick';reproject(q);q.color=R.COLOURS[1]
    rr=random.Random(667)
    for i,(x,y,angle) in enumerate(((-4.92,-3.9,.7),(4.97,-3.3,-.7),(-4.9,.7,-.9),(4.6,.5,1.1))):
        ob=R.vault(state+'__FallenVaultFragment'+str(i),0,-.48,.48,0,1.12,.47,.18,'roof',stagecol(state,'debris'),segments=12,along=3,angle0=.28,angle1=1.52)
        rot=Matrix.Rotation(angle,4,'Y')@Matrix.Rotation(.3+i*.62,4,'Z')
        for v in ob.data.vertices:v.co=rot@v.co
        lo,_=R.bounds(ob)
        for v in ob.data.vertices:v.co+=Vector((x,y,.33-lo[2]))
        ob['fallen_source']='subsidiary wing barrel vault'
    # Hollow curved dome shards lie on rubble instead of a miniature intact dome.
    for j in range(4):
        verts=[];faces=[];N=9;M=4
        for sh in (0,1):
            for k in range(M+1):
                lat=.15+k*.19
                for i in range(N+1):
                    a=j*1.3+i*.11;r=1.44-sh*.17
                    verts.append((r*math.cos(lat)*math.cos(a),r*math.cos(lat)*math.sin(a),1.16*math.sin(lat)))
        n=(N+1)*(M+1)
        for sh in (0,1):
            for k in range(M):
                for i in range(N):a=sh*n+k*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
        for k in (0,M):
            for i in range(N):a=k*(N+1)+i;faces.append((a,a+1,a+1+n,a+n))
        for i in (0,N):
            for k in range(M):a=k*(N+1)+i;faces.append((a,a+N+1,a+N+1+n,a+n))
        ob=R.mesh(state+'__DomeShard'+str(j),verts,faces,'roof',stagecol(state,'debris'),'finish','debris')
        rot=Matrix.Rotation(.7+j*.34,4,'Y')@Matrix.Rotation(j*.91,4,'Z')
        for v in ob.data.vertices:v.co=rot@v.co
        lo,hi=R.bounds(ob);cx=(lo[0]+hi[0])/2;cy=(lo[1]+hi[1])/2
        for v in ob.data.vertices:v.co+=Vector(((-1.7+j*1.1)-cx,4.35+(j%2)*.7-cy,.33-lo[2]))
        ob['fallen_source']='rear reading dome'
    debris(state,190,(0,4.10),(2.30,1.6),.43,96)
    debris(state,90,(-4.92,-1.72),(1.05,3.48),.34,97)
    debris(state,90,(4.92,-1.72),(1.05,3.48),.34,98)
    R.block(state+'__OwnerFragment',(-2.16,2.187,1.14),(.21,.035,.29),'owner',stagecol(state,'finish'),'finish','owner')
    R.show_state(state);print('RUINS_READY',len(col.all_objects))

def construction():
    scene=bpy.data.scenes['PS_Gundeshapur'];stages=['foundation','walls','vaults','finish']
    for index,stage in enumerate(stages):
        col=R.collection(P+'construct_'+stage,scene.collection)
        for o in bpy.data.collections[P+'healthy_LOD0'].all_objects:
            if o.get('construction_stage') in stages[:index+1]:
                q=clone(o,'construct_'+stage,col)
                if index in (1,2) and q.get('surface')=='plaster':
                    q['surface']='brick';q.color=R.COLOURS[1];R.retile_surface(q);q['construction_treatment']='exposed masonry; plaster added in finish'
        if stage in ('walls','vaults'):
            # Four-foot scaffold, braces and continuous deck planks outside central approach.
            for sign in (-1,1):
                for yy in (2.0,3.35):
                    R.beam('construct_'+stage+f'__ScaffoldPost{sign}_{yy}',(sign*3.10,yy,.30),(sign*3.10,yy,4.25),.10,'timber',col,'walls','construction')
                for zz in (1.62,3.08):
                    R.beam('construct_'+stage+f'__ScaffoldLedger{sign}_{zz}',(sign*3.1,1.96,zz),(sign*3.1,3.39,zz),.10,'timber',col,'walls','construction')
                R.beam('construct_'+stage+f'__ScaffoldBrace{sign}',(sign*3.10,2,.31),(sign*3.10,3.35,4.10),.075,'timber',col,'walls','construction')
                R.block('construct_'+stage+f'__ScaffoldDeck{sign}',(sign*3.10,2.68,3.12),(.68,1.59,.09),'timber',col,'walls','construction')
        print('CONSTRUCTION_READY',stage,len(col.all_objects))
    R.show_state()


def reset_state(state):
    col=bpy.data.collections.get(P+state+'_LOD0')
    if not col:return
    for ob in list(col.all_objects):remove(ob)
    children=list(col.children)
    for child in children:bpy.data.collections.remove(child)
    bpy.data.collections.remove(col)
