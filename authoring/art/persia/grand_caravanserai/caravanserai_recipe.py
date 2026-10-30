"""Deterministic, measured Grand Caravanserai source construction. No native operations."""
import math,random,json,bpy,bmesh
from mathutils import Vector
import asset_runner as R
P=R.PREFIX;G=.20;F=.38
ANCHORS={'ground':(0,0,G),'gate_front':(0,-5.78,G),'gate_spring':(0,-5.78,2.50),'west_front':(-3.20,0,F),'east_front':(3.20,0,F),'bay_spring':(3.48,-3,1.73),'rear_iwan':(0,3.6,F),'unloading':(-2.45,-1.7,G),'water':(2.38,.15,G),'tally':(0,3.0,G)}

def root():return R.collection(P+'healthy_LOD0',bpy.data.scenes['PS_Caravanserai'].collection)
def col(role):return R.collection(P+'healthy_'+role,root())
def B(name,xyz,size,surface='brick',stage='walls',role='architecture',rotation=0):return R.block(name,xyz,size,surface,col(role),stage,role,rotation)
def V(name,cx,y0,y1,spring,rx,rise,t,surface='roof',segments=32,transform=None,role='vaults'):
    inn=profile(cx,rx,rise,spring,segments);out=profile(cx,rx+t,rise+t,spring,segments)
    return R.extrude_xz(name,inn+list(reversed(out)),y0,y1,surface,col(role),'vaults',transform,role)
def profile(cx,rx,rise,spring,n=32):
    c=(rise*rise-rx*rx)/(2*rx);rad=rx+c
    return [(cx+x,spring+math.sqrt(max(0,rad*rad-(abs(x)+c)**2))) for x in [-rx+2*rx*i/n for i in range(n+1)]]
def A(name,cx,y0,y1,z0,w,h,opening,spring,rise,transform=None):
    outline=[(cx-w/2,z0),(cx-w/2,z0+h),(cx+w/2,z0+h),(cx+w/2,z0),(cx+opening/2,z0)]+list(reversed(profile(cx,opening/2,rise,z0+spring,40)))+[(cx-opening/2,z0)]
    return R.extrude_xz(name,outline,y0,y1,'brick',col('architecture'),'walls',transform)
def transform(side):return lambda x,y,z:(side*(3.2+y),x,z)

def foundation():
    R.setup_scene();R.view(distance=18,solid=True)
    B('Plinth',(0,0,.06),(12.20,12.20,.28),'earth','foundation','ground')
    B('CourtBed',(0,0,.175),(10.60,10.60,.05),'earth','foundation','ground')
    for side in [-1,1]:B(('West' if side<0 else 'East')+'Platform',(side*4.24,0,.29),(2.08,8.4,.18),'stone','foundation','ground')
    B('RearPlatform',(0,4.49,.29),(6.4,1.78,.18),'stone','foundation','ground')
    B('EntrySill',(0,-5.62,.24),(2.4,1.12,.08),'stone','foundation','ground')
    print('PHASE foundation: ground plane .20; raised platforms top .38')

def bay(side,cy,index):
    label=('West' if side<0 else 'East')+'Bay'+str(index);tr=transform(side)
    a=A(label+'_Facade',cy,0,.28,F,2.0,2.78,1.4,1.35,1.05,tr);a['module']='pointed_lodging_bay';a['bay_index']=index
    v=V(label+'_Vault',cy,.28,2.15,1.73,.70,1.05,.18,segments=48,transform=tr);v['module']='pointed_lodging_bay';v['bay_index']=index
    for s in [-1,1]:
        o=R.block(label+'_Bearing'+str(s),(cy+s*.85,1.215,1.055),(.30,1.87,1.35),'brick',col('architecture'),'walls')
        # Bake the same world-space transform as the vault.
        for q in o.data.vertices:q.co=tr(*q.co)
        o.data.update();R.retile_surface(o)
    return a,v

def first_module():bay(-1,-3,0);print('PHASE first complete west bay; inspect spring and front/back cap contact before repetition')

def architecture():
    for side in [-1,1]:
        for j,cy in enumerate([-3,-1,1,3]):
            if side==-1 and j==0:continue
            bay(side,cy,j)
        B(('West' if side<0 else 'East')+'OuterWall',(side*5.43,0,1.52),(.36,10.7,2.64))
        for yy in [-4.40,4.40]:B(('West' if side<0 else 'East')+('South' if yy<0 else 'North')+'EndWall',(side*4.24,yy,1.52),(2.02,.40,2.64))
    B('RearOuterWall',(0,5.43,1.52),(10.5,.36,2.64))
    for side in [-1,1]:
        B('FrontWall'+str(side),(side*3.58,-5.43,1.52),(3.76,.36,2.64))
        for y in [-5.35,5.35]:
            label=('West' if side<0 else 'East')+('South' if y<0 else 'North')+'Buttress'
            ob=R.lathe(label,(side*5.35,y,G),[(.58,0),(.65,.18),(.58,.35),(.58,2.65),(.62,2.70),(.62,2.90),(.54,3.02)],'brick',col('architecture'),sides=48,stage='walls',role='architecture');ob['structural']='corner_buttress'
    # Gateway is an open deep recess, never a dark painted rectangle.
    A('GateFacade',0,-5.78,-5.33,G,3.60,5.20,2.36,2.30,1.68)
    for side in [-1,1]:B('GateReturn'+str(side),(side*1.49,-4.89,1.35),(.62,.88,2.30))
    V('GateVault',0,-5.33,-4.25,2.50,1.18,1.68,.24,segments=64)
    A('GateInnerTympanum',0,-4.45,-4.20,G,3.6,4.34,2.36,2.30,1.68)
    B('GateCoping',(0,-5.51,5.46),(3.78,.67,.12),'stone','vaults','trim')
    # Rear iwan and two low rooms close the fourth side of the lodging court.
    A('RearIwanFront',0,3.60,3.88,F,2.9,3.34,2.16,1.55,1.35)
    V('RearIwanVault',0,3.88,5.25,1.93,1.08,1.35,.19,segments=48)
    for side in [-1,1]:
        B('RearIwanReturn'+str(side),(side*1.30,4.56,1.155),(.44,1.37,1.55))
        A('RearRoom'+str(side),side*2.34,4.15,4.40,F,1.77,2.5,.96,1.15,.8)
        V('RearRoomVault'+str(side),side*2.34,4.40,5.25,1.53,.48,.8,.16,segments=24)
        B('RearRoomBearing'+str(side),(side*2.94,4.825,.955),(.32,.85,1.15))
        B('RearRoomInnerBearing'+str(side),(side*1.78,4.825,.955),(.16,.85,1.15))
    print('PHASE full masonry: enclosure, 8 bays, rear iwan, recessed gateway and four buttresses')

def ring_bricks(name,cx,y0,y1,spring,rx,rise,t,segments=32,tr=None,role='brick_detail'):
    a=profile(cx,rx,rise,spring,segments);b=profile(cx,rx+t,rise+t,spring,segments)
    for i in range(segments):
        # Distinct voussoirs with tiny intentional mortar reveals.
        aa=a[i];ab=a[i+1];ba=b[i];bb=b[i+1]
        R.extrude_xz(name+str(i),[aa,ab,bb,ba],y0,y1,'carving',col(role),'finish',tr,role)

def details():
    ring_bricks('GateVoussoir',0,-5.84,-5.775,2.50,1.18,1.68,.16,48)
    for s in [-1,1]:
        B('GateInsetOwner'+str(s),(s*1.51,-5.795,2.39),(.28,.035,2.84),'owner','finish','owner')
        # Nested brick frame grows out of the pier and lintel surfaces.
        for x in [1.77,1.25]:B('GateFrame'+str(s)+'_'+str(x),(s*x,-5.82,2.76),(.055,.075,4.98),'carving','finish','trim')
    B('GateFrameTop',(0,-5.82,5.24),(3.6,.075,.08),'carving','finish','trim')
    # Geometric brickwork: ornamental diamonds, intentionally no pseudo-calligraphy.
    for row in range(3):
        for j in range(13):
            x=-1.58+j*.263;z=4.57+row*.20
            if abs(x)<.42 and row==0:continue
            B('GateGeometric_'+str(row)+'_'+str(j),(x,-5.823,z),(.14,.06,.14),'carving','finish','brick_detail',rotation=0)
    for s in [-1,1]:
        for j,cy in enumerate([-3,-1,1,3]):
            label=('West' if s<0 else 'East')+'Bay'+str(j);tr=transform(s)
            ring_bricks(label+'_Voussoir',cy,-.045,.005,1.73,.70,1.05,.10,28,tr)
            # A few raised rib courses trace actual vaulted roof curvature.
            for k in range(6):V(label+'_RoofCourse'+str(k),cy,.35+k*.29,.40+k*.29,1.73,.88,1.23,.035,'roof',segments=40,transform=tr,role='roof_detail')
            for ss in [-1,1]:
                R.extrude_xz(label+'_PierBorder'+str(ss),[(cy+ss*.91-.035,F),(cy+ss*.91+.035,F),(cy+ss*.91+.035,3.10),(cy+ss*.91-.035,3.10)],-.035,.008,'carving',col('trim'),'finish',tr,'trim')
            ob=R.block(label+'_Fascia',(cy,.0,3.12),(1.82,.04,.14),'owner',col('owner'),'finish','owner')
            for v in ob.data.vertices:v.co=tr(*v.co)
            ob.data.update();R.retile_surface(ob)
        # Low outer cornices with clear continuous bearing below them.
        B(('West' if s<0 else 'East')+'OuterCoping',(s*5.43,0,2.90),(.43,10.68,.12),'stone','vaults','trim')
        for yy in [-5.43,5.43]:
            for j in range(12):
                x=s*(1.86+j*.275)
                B('PerimeterCap'+str(s)+'_'+str(yy)+'_'+str(j),(x,yy,2.91),(.263,.42,.14),'brick','vaults','brick_detail')
    ring_bricks('RearIwanVoussoir',0,3.55,3.61,1.93,1.08,1.35,.11,40)
    # Worn, jointed court with an open central route.
    rr=random.Random(202)
    for ix in range(9):
        for iy in range(12):
            x=-2.95+ix*.735;y=-4.15+iy*.68
            if abs(x)>1.3 and -2.6<y<1.0:continue
            height=.0355+rr.random()*.01
            B('Paving_'+str(ix)+'_'+str(iy),(x,y,G+(height-.005)/2),(.68,.63,height+.005),'stone','foundation','ground',rotation=rr.uniform(-.025,.025))
    print('PHASE brick frames, measured vault ribs, neutral courtyard paving and owner areas')

def crate(label,xyz,w=.58,d=.48,h=.48):
    x,y,z=xyz;B(label+'_Body',(x,y,z+h/2),(w,d,h),'timber','finish','cargo')
    for s in [-1,1]:
        B(label+'_Strap'+str(s),(x+s*w*.29,y,z+h/2),(.025,d+.016,h+.015),'cloth','finish','cargo')
    for j in range(4):B(label+'_LidSlat'+str(j),(x-w/2+(j+.5)*w/4,y,z+h+.009),(w/4-.012,d,.018),'timber','finish','cargo')
def bale(label,xyz,size=(.62,.43,.38)):
    x,y,z=xyz;w,d,h=size
    # Rounded faceted bundle generated as rings, horizontal axis along Y.
    rings=[(w*.36,0),(w*.50,.08),(w*.51,d-.08),(w*.36,d)]
    ob=R.lathe(label,(0,0,0),rings,'cloth',col('cargo'),sides=16,stage='finish',role='cargo')
    for v in ob.data.vertices:
        a=v.co.copy();v.co=(x+a.x,y+a.z-d/2,z+h/2+a.y*h/w)
    ob.data.update();R.retile_surface(ob)
    # Narrow bindings seat on the top and sides of the wrapped bundle.
    for off in [-d*.28,d*.28]:
        R.beam(label+'_Rope'+str(off),(x-w*.48,y+off,z+h*.58),(x+w*.48,y+off,z+h*.58),.025,'timber',col('cargo'),'finish','cargo')
    return ob
def jar(label,xyz,r=.19):
    return R.lathe(label,xyz,[(r*.65,0),(r*.9,.05),(r,.25),(r*.78,.42),(r*.48,.49),(r*.53,.51),(r*.36,.51),(r*.32,.46)],'pottery',col('cargo'),sides=28,role='cargo')
def cloth(label,x0,x1,y0,y1,z0,z1,owner=True):
    verts=[];faces=[];nx=12;ny=8
    for iy in range(ny+1):
        t=iy/ny
        for ix in range(nx+1):
            s=ix/nx;verts.append((x0+(x1-x0)*s,y0+(y1-y0)*t,z0+(z1-z0)*t-.09*math.sin(math.pi*s)*math.sin(math.pi*t)))
    n=len(verts);verts +=[(x,y,z-.014) for x,y,z in verts]
    for sh in [0,n]:
        for iy in range(ny):
            for ix in range(nx):
                a=sh+iy*(nx+1)+ix;faces.append((a,a+1,a+nx+2,a+nx+1))
    boundary=list(range(nx+1))+[iy*(nx+1)+nx for iy in range(1,ny+1)]+list(range(ny*(nx+1)+nx-1,ny*(nx+1)-1,-1))+[iy*(nx+1) for iy in range(ny-1,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+n,a+n))
    return R.mesh(label,verts,faces,'owner' if owner else 'cloth',col('owner' if owner else 'cargo'),'finish','owner' if owner else 'cargo')

def props():
    # West unloading awning: its two wall ends and front posts are actual supports.
    for y in [-2.75,-.55]:
        # Arcade openings cannot carry a rafter: ground the wall-edge ends on posts.
        R.beam('UnloadingRearPost'+str(y),(-3.20,y,G),(-3.20,y,2.32),.085,'timber',col('props'))
        R.beam('UnloadingPost'+str(y),(-1.75,y,G),(-1.75,y,2.0),.085,'timber',col('props'))
        R.beam('UnloadingRafter'+str(y),(-3.20,y,2.32),(-1.75,y,2.0),.07,'timber',col('props'))
    R.beam('UnloadingFrontRail',(-1.75,-2.75,2.0),(-1.75,-.55,2.0),.07,'timber',col('props'))
    cloth('UnloadingAwning',-3.20,-1.75,-2.75,-.55,2.32,2.32) # corrected planar slope in X below
    ob=bpy.data.objects[P+'UnloadingAwning']
    for v in ob.data.vertices:v.co.z-=.32*(v.co.x+3.20)/1.45
    ob.data.update()
    for j,xyz in enumerate([(-2.7,-2.28,G),(-2.06,-2.28,G),(-2.38,-2.28,G+.48)]):crate('UnloadingCrate'+str(j),xyz)
    for j,xyz in enumerate([(-2.7,-1.44,G),(-2.05,-1.38,G),(-2.36,-1.40,G+.38)]):bale('TradeBale'+str(j),xyz)
    # A working handcart sits beside the load, well clear of the centre route.
    B('CartBed',(-2.47,-3.42,.69),(1.05,.72,.10),'timber','finish','cart')
    for y in [-3.82,-3.02]:
        wheel=R.lathe('CartWheel'+str(y),(0,0,0),[(.35,-.045),(.35,.045),(.25,.045),(.25,-.045)],'timber',col('cart'),sides=32,role='cart',cap=False)
        # This ring is closed at both radial ends, no fake capped annular holes.
        me=wheel.data;bm=bmesh.new();bm.from_mesh(me);boundary=[e for e in bm.edges if e.is_boundary];bmesh.ops.bridge_loops(bm,edges=boundary);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        for v in me.vertices:a=v.co.copy();v.co=(-2.47+a.x,y+a.z,.55+a.y)
        for a in [i*math.pi/4 for i in range(4)]:R.beam('CartSpoke'+str(y)+'_'+str(a),(-2.47-.25*math.cos(a),y,.55-.25*math.sin(a)),(-2.47+.25*math.cos(a),y,.55+.25*math.sin(a)),.036,'timber',col('cart'),'finish','cart')
        R.retile_surface(wheel)
    R.beam('CartAxle',(-2.47,-3.9,.55),(-2.47,-2.94,.55),.09,'timber',col('cart'),'finish','cart')
    for y in [-3.65,-3.19]:R.beam('CartHandle'+str(y),(-2.05,y,.70),(-1.12,y,.25),.055,'timber',col('cart'),'finish','cart')
    for j in range(3):B('CartSideSlat'+str(j),(-2.98,-3.42,.85+j*.10),(.045,.72,.075),'timber','finish','cart')
    bale('CartLoad',(-2.55,-3.42,.74),(.64,.48,.36))
    # East water/feed station with thick-walled open trough and visible water surface.
    B('TroughBase',(2.50,.10,.27),(.65,1.90,.14),'stone','finish','water')
    for x in [2.20,2.80]:B('TroughLong'+str(x),(x,.10,.49),(.12,1.90,.32),'stone','finish','water')
    for y in [-.79,.99]:B('TroughEnd'+str(y),(2.50,y,.49),(.48,.12,.32),'stone','finish','water')
    B('TroughWater',(2.50,.10,.49),(.48,1.66,.035),'ink','finish','water')
    for j in range(4):jar('WaterJar'+str(j),(2.62+(j%2)*.31,1.55+(j//2)*.36,G),.16)
    for j in range(2):
        R.lathe('FodderBasket'+str(j),(2.45+j*.53,2.45,G),[(.22,0),(.31,.34),(.30,.38),(.26,.38),(.25,.31)],'timber',col('cargo'),sides=24,role='cargo')
        R.lathe('Fodder'+str(j),(2.45+j*.53,2.45,G+.31),[(.25,0),(.20,.13),(.01,.20)],'leaves',col('cargo'),sides=24,role='cargo')
    # Rear tally table seats on its four legs; only small original abstract markings.
    B('TallyTop',(-.6,3.05,.78),(1.08,.56,.07),'timber','finish','tally')
    for x in [-1.03,-.17]:
        for y in [2.85,3.25]:B('TallyLeg'+str(x)+str(y),(x,y,.4725),(.07,.07,.545),'timber','finish','tally')
    B('TallyLedger',(-.64,3.05,.827),( .42,.31,.024),'paper','finish','tally')
    for j in range(2):crate('MerchantChest'+str(j),(.65+j*.69,3.07,G),.58,.50,.42)
    for j in range(3):
        ob=R.lathe('CarpetRoll'+str(j),(0,0,0),[(.12,0),(.12,.86)],'cloth',col('cargo'),sides=20,role='cargo')
        for v in ob.data.vertices:a=v.co.copy();v.co=(-1.90+j*.31+a.y,3.05+a.z-.43,G+.12+a.x)
        ob.data.update();R.retile_surface(ob)
    print('PHASE purposeful cargo, cart, supported awning, water station and merchant tally')

def wear():
    rr=random.Random(88)
    # Small substrate patches are attached to wall faces, not scattered across the sky.
    for side in [-1,1]:
        for j in range(5):
            y=-3.7+j*1.72;h=rr.uniform(.25,.60)
            shape=[(y-.33,G),(y+.45,G),(y+.40,G+h*.65),(y+.16,G+h),(y-.19,G+h*.78)]
            R.extrude_xz(('West' if side<0 else 'East')+'PlasterRepair'+str(j),shape,side*5.61-.004,side*5.61+.004,'plaster',col('wear'),'finish',lambda u,v,z:(v,u,z),'surface_wear')
    for s in [-1,1]:B('DrainageDirt'+str(s),(s*3.07,0,G+.004),(.17,7.7,.008),'grime','finish','surface_wear')
    for x,y,w,d in [(-2.45,-1.6,1.55,2.6),(2.45,.12,1.10,2.2),(0,-4.50,2.2,1.1),(-.3,2.85,2.5,.75)]:
        # Shallow irregular footprint zones with real thickness, deliberately bounded.
        verts=[(x+math.cos(i*math.tau/20)*w/2*(.93+rr.random()*.07),y+math.sin(i*math.tau/20)*d/2*(.93+rr.random()*.07)) for i in range(20)]
        R.extrude_xz('DirtZone'+str(x)+str(y),verts,G-.001,G+.008,'grime',col('wear'),'foundation',lambda u,v,z:(u,z,v),'surface_wear')
    # Damage belongs to later states; these are small maintained edge and dust details.
    print('PHASE localized operational wear; healthy structure remains complete')

def capture(name,pos=(18,-23,18),center=(0,0,2.2),distance=18,solid=True):
    s=bpy.data.scenes['PS_Caravanserai'];bpy.context.window.scene=s;R.view(pos,center,distance,solid)
    s.render.resolution_x=1100;s.render.resolution_y=900;s.render.image_settings.file_format='PNG';s.render.filepath=str(R.ROOT/'evidence'/(name+'.png'))
    area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
    with bpy.context.temp_override(area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
    print('INSPECTION',name)

def counts():return sum(len(p.vertices)-2 for o in root().all_objects if o.type=='MESH' for p in o.data.polygons)

def density_and_finish():
    # Split large brick faces at fixed world planes so the shared atlas keeps
    # approximately 0.5 x 0.125 source-unit bricks instead of giant stretched blocks.
    for o in list(root().all_objects):
        if o.type!='MESH' or o.get('surface')!='brick':continue
        bm=bmesh.new();bm.from_mesh(o.data)
        lo,hi=R.bounds(o)
        for ax in range(3):
            normal=[0,0,0];normal[ax]=1
            for k in range(math.floor(lo[ax]/2)+1,math.ceil(hi[ax]/2)):
                point=[0,0,0];point[ax]=k*2
                bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,dist=1e-6,clear_inner=False,clear_outer=False)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
        for poly in o.data.polygons:
            axis=max(range(3),key=lambda j:abs(poly.normal[j]));axes=[j for j in range(3) if j!=axis]
            coords=[o.data.vertices[o.data.loops[i].vertex_index].co for i in poly.loop_indices];mins=[min(v[a] for v in coords) for a in axes]
            # Padded tile coordinates; two-world-unit cells never cross atlas regions.
            for li,v in zip(poly.loop_indices,coords):
                uv=((1.04+.92*(v[axes[0]]-mins[0])/2)/4,(3.04+.92*(v[axes[1]]-mins[1])/2)/4)
                for layer in o.data.uv_layers:layer.data[li].uv=uv
    for o in root().all_objects:
        if 'DirtZone' in o.name:
            center_x=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices)
            if abs(center_x)<1.3:
                for v in o.data.vertices:v.co.z+=.034
            o['construction_stage']='finish'
        if 'Paving_' in o.name:o['construction_stage']='finish'
    for side in [-1,1]:
        for j,cy in enumerate([-3,-1,1,3]):
            tr=transform(side)
            shape=[(cy-.63,F),(cy+.63,F),(cy+.60,F+.12),(cy+.37,F+.22),(cy-.20,F+.16),(cy-.63,F+.24)]
            R.extrude_xz(('West' if side<0 else 'East')+'DoorDust'+str(j),shape,-.003,.004,'grime',col('wear'),'finish',tr,'surface_wear')
    for side in [-1,1]:
        # Low masonry footings seat against the wall, with individual offset blocks.
        for j in range(16):
            y=-5.0+j*.66;h=.16+.025*math.sin(j*2.3+side)
            B('OuterFooting'+str(side)+'_'+str(j),(side*5.635,y,G+h/2),(.09,.63,h),'rubble','foundation','trim')
    for j in range(2):
        # Actual timber blocks bridge the cart axle to its bed.
        B('CartAxleBearing'+str(j),(-2.47,-3.67+j*.5,.6225),(.16,.10,.145),'timber','finish','cart')
    # Real cut edge on the short awning: healthy fabric is worn, still complete.
    aw=bpy.data.objects[R.PREFIX+'UnloadingAwning']
    for v in aw.data.vertices:
        if abs(v.co.x+1.75)<1e-5:v.co.x-=.035*(.5+.5*math.sin(v.co.y*14))
    aw.data.update()
    print('PHASE consistent brick density, seated footings, worn doorways and trafficked court')
