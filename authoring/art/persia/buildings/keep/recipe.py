"""DRAFT original Persia keep source art. Existing resources only.
No Blender execution was performed while authoring this file. Native motion,
footprints, selectors and gameplay remain external preserved dependencies.
"""
from pathlib import Path
import sys
import json
import math
import bpy

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / '_shared'
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
import source_runner as R
FAMILY = 'keep'
PREFIX = 'PSB_' + FAMILY + '_'
R.configure(ROOT, FAMILY)
INVENTORY = ROOT.parents[3] / 'research/persia_buildings/inventory'
KEYS = ('A3',)
F = .08
CURRENT = KEYS[0]
ANCHORS, CONTRACTS, ASSEMBLIES = {}, [], {}
TEXTURE_INPUTS = {k: str(ROOT/'textures'/(k+'.png')) for k in
                  ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC = {'size':[2048,2048], 'original_pixels_required':True, 'status':'parent creates family atlas'}

def _native_records():
    handoff=json.loads((INVENTORY/'PRIMARY_BODY_HANDOFF.json').read_text(encoding='utf-8'))
    rest=json.loads((INVENTORY/'HEALTHY_REST_BOUNDS.json').read_text(encoding='utf-8'))
    compounds=json.loads((INVENTORY/'SOURCE_CATEGORY_COMPOUND_BOUNDS.json').read_text(encoding='utf-8'))
    dependencies=json.loads((INVENTORY/'MECHANISM_DEPENDENCIES.json').read_text(encoding='utf-8'))
    result={}
    for b in handoff['families'][FAMILY]['bodies']:
        key='A'+str(b['native_age_label_from_resource_name'])
        if key not in KEYS: raise ValueError('Unexpected native resource age: '+key)
        uses=b['source_uses']
        private=[u for u in uses if u['variant_evidence_class']=='existing_private_compiled_variant']
        candidates=[u for u in uses if u['variant_evidence_class']!='existing_private_compiled_variant']
        stamps=rest['stamp_transform_bounds_by_model'][b['model']]
        if len(stamps)!=1:raise ValueError('Multiple stamp transforms require explicit parent mapping')
        attachments={u['attachment'] for u in private}
        cases=[{k:c.get(k) for k in ('actor','variant','variant_evidence_class','attachment',
                    'attachment_category','inventory_category','healthy_definite_category_rest_bounds',
                    'healthy_possible_category_rest_bounds')}
               for c in compounds['category_cases']
               if c.get('family')==FAMILY and c.get('attachment') in attachments
               and c.get('variant') in {u['variant'] for u in private}]
        result[key]={'age':b['native_age_label_from_resource_name'],'model':b['model'],
                     'source_uses':uses,'private_compiled_source_uses':private,
                     'official_parent_candidates':candidates,
                     'native_model_sha256':b['native_model_sha256'],
                     'native_geometry_sha256':b['native_geometry_sha256'],
                     'healthy_lod0_triangle_interval':b['healthy_lod0_triangle_interval'],
                     'resource_bounds':b['healthy_definite_rest_bounds'],
                     'stamp':stamps[0], 'complete_category_bounds':cases,
                     'native_animation_graphs':b['native_animation_graphs'],
                     'dependencies':[{'model':path,'native_model_sha256':m['native_model_sha256'],
                        'native_owner_graphs':m['native_owner_graphs'],
                        'pose_and_sweep_status':m['pose_and_sweep_status'],
                        'native_skeleton':m['native_skeleton'],
                        'markers':m['markers'],'marker_contract':m['marker_contract']}
                       for path,m in dependencies['dependencies'].items()
                       if FAMILY in m['used_by_families']]}
    if set(result)!=set(KEYS):raise ValueError('Existing body roster incomplete')
    return result
NATIVE = _native_records()

def age(): return NATIVE[CURRENT]['age']

def activate():
    if R.ROOT!=ROOT or R.SLUG!=FAMILY:R.configure(ROOT,FAMILY)

def root(key=None,state='healthy',lod=0):
    activate();key=key or CURRENT
    if key not in KEYS:raise ValueError('Only exact native body keys admitted')
    return R.collection(PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)

def col(role):return R.collection(PREFIX+CURRENT+'_healthy_'+role,root())

def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role
    ob['structural_group']=group;ob['draft_uninspected']=True
    ob['authored_space']='measured native stamp space; resource inverse not yet applied'
    return ob

def B(name,center,size,surface='plaster',stage='walls',role='architecture',group=''):
    if any(v<=0 for v in size):raise ValueError('Nonpositive geometry '+name)
    activate()
    ob=tag(R.block(CURRENT+'_'+name,center,size,surface,col(role),stage,role),stage,role,group)
    ob['lod_reference_geometry_sha256']=_lod_module().geometry_key(R,ob)
    return ob

def contact(name,a,b,axis='bottom-top',target=0.,tolerance=.003):
    CONTRACTS.append({'body':CURRENT,'name':name,'a':a.name,'b':b.name,
                      'axis':axis,'target':target,'tolerance':tolerance})

def wall(name,x,y,w,d,h,bottom=F,group=''):
    return B(name,(x,y,bottom+h/2),(w,d,h),'plaster','walls','architecture',group)

def _inverse_rigid(m):
    r=[[m[j][i] for j in range(3)] for i in range(3)]
    return [r[i]+[-sum(r[i][j]*m[j][3] for j in range(3))] for i in range(3)]+[[0,0,0,1]]

def foundation(key=KEYS[0]):
    global CURRENT
    if key not in KEYS:raise ValueError('No invented age/body: '+str(key))
    CURRENT=key;activate();R.setup_scene()
    if root().all_objects:raise ValueError('Owned body exists; reset explicitly')
    native=NATIVE[key];env=ENVELOPES[age()]
    lo,hi=env;raw=native['stamp']['healthy_definite_stamp_space_rest_bounds']
    if any(lo[i]<raw['min'][i]-1e-6 or hi[i]>raw['max'][i]+1e-6 for i in range(3)):
        raise ValueError('Proposed envelope exceeds measured primary healthy body')
    ground=B('EarthBed',((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+F)/2),
             (hi[0]-lo[0],hi[1]-lo[1],F-lo[2]),'earth','foundation','ground','ground')
    ASSEMBLIES[key]={'ground':ground,'rooms':{}}
    ANCHORS[key]={'ground_top':F,'native_body_key':key,'native_model':native['model'],'authored_space':'measured native stamp-space; inverse resource projection required exactly once',
       'chosen_horizontal_bounds':[lo[:2],hi[:2]],'authoring_bounds_proposal':env,
       'native_stamp_rest_bounds':raw,'native_resource_bounds':native['resource_bounds'],
       'resource_to_stamp':native['stamp']['blender_matrix_row_major'],
       'stamp_to_resource':_inverse_rigid(native['stamp']['blender_matrix_row_major']),
       'source_uses':native['source_uses'],'private_compiled_source_uses':native['private_compiled_source_uses'],
       'official_parent_candidates':native['official_parent_candidates'],
       'native_dependencies':native['dependencies'],
       'native_animation_graphs':native['native_animation_graphs'],
       'native_model_sha256':native['native_model_sha256'],
       'native_geometry_sha256':native['native_geometry_sha256'],
       'healthy_lod0_triangle_interval':native['healthy_lod0_triangle_interval'],'complete_category_bounds':native['complete_category_bounds'],
       'terrain_origin_note':'native origin retained; no Z recenter from buried geometry minimum; .08 source surface is provisional',
       'clearance_status':'Only conservative rest-body envelope; native exits/markers/weapon motion unqualified',
       'door_dimensions':'original source proposals, not measured stock doorways',
       'visual_status':'unbuilt and uninspected in Blender'}
    print('FOUNDATION_DRAFT',FAMILY,key)

def _P(name,origin,xyz,size,surface='plaster',stage='walls',role='architecture',group='',turn=0):
    x,y=origin;u,v,z=xyz
    if turn:cx,cy=x-v,y+u;sx,sy,sz=size[1],size[0],size[2]
    else:cx,cy=x+u,y+v;sx,sy,sz=size
    return B(name,(cx,cy,z),(sx,sy,sz),surface,stage,role,group)

def _lod_module():
    import hashlib
    import importlib.util
    path=ROOT/'lods.py';name='persia_'+FAMILY+'_authored_lods'
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    module=sys.modules.get(name)
    if module is None or getattr(module,'_source_sha256',None)!=digest:
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module);module._source_sha256=digest;sys.modules[name]=module
    return module


def _lod_curve(ob,kind,**spec):return _lod_module().mark_curve(R,ob,kind,**spec)


def _lod_run(ob,kind,run,index,count,axis=0,**spec):
    return _lod_module().mark_run(R,ob,kind,run,index,count,axis,**spec)


def build_lod(H,key,state,source,destination,level,profile):
    return _lod_module().build_lod(H,key,state,source,destination,level,profile)


def room(name,spec,doors=(0.,),roof='flat',arched=False,bottom=F,turn=0):
    x,y,w,d,h=spec;t=.24;g=name;P=lambda label,xyz,size,mat='plaster',stage='walls',role='architecture':_P(
        name+'_'+label,(x,y),xyz,size,mat,stage,role,g,turn)
    back=P('Back',(0,d/2-t/2,bottom+h/2),(w,t,h))
    sides=[P('Side'+str(s),(s*(w/2-t/2),0,bottom+h/2),(t,d-2*t,h)) for s in (-1,1)]
    dh=min(2.02,h-.32);ow=min(1.02,w*.54)
    edges=[(-w/2,None)];front=[];last=-w/2
    for i,u in enumerate(sorted(doors)):
        half=(ow+.34)/2
        if u-half<last-1e-7 or u+half>w/2:raise ValueError('Door module does not fit '+name)
        if u-half>last:front.append(P('FrontSolid'+str(i),((last+u-half)/2,-d/2+t/2,bottom+h/2),(u-half-last,t,h)))
        if arched:
            transform=(lambda a,b,z:(x-b,y+a,z)) if turn else (lambda a,b,z:(x+a,y+b,z))
            arch=tag(R.archwall(CURRENT+'_'+name+'_Arch'+str(i),u,-d/2,-d/2+t,bottom,
                      ow+.34,h,ow,dh-.25,.25,'plaster',col('architecture'),segments=14,transform=transform),
                      'walls','architecture',g)
            _lod_curve(arch,'arch',cx=u,y0=-d/2,y1=-d/2+t,z0=bottom,outer_w=ow+.34,height=h,
                       inner_w=ow,spring=dh-.25,rise=.25,origin=[x,y],turn=turn)
            front.append(arch)
        else:
            for s in (-1,1):front.append(P('Jamb'+str(i)+'_'+str(s),(u+s*(ow/2+.085),-d/2+t/2,bottom+h/2),(.17,t,h)))
            front.append(P('Head'+str(i),(u,-d/2+t/2,bottom+(dh+h)/2),(ow,t,h-dh)))
        leaf=P('Door'+str(i),(u,-d/2+t*.80,bottom+dh/2),(ow*.88,.055,dh),'timber','finish','fittings')
        last=u+half
    if last<w/2:front.append(P('FrontEnd',((last+w/2)/2,-d/2+t/2,bottom+h/2),(w/2-last,t,h)))
    floor=P('Floor',(0,0,bottom+.04),(w-.24,d-.24,.08),'timber' if FAMILY=='dock' else 'stone','foundation','architecture')
    record={'spec':spec,'back':back,'sides':sides,'front':front,'floor':floor,'bottom':bottom,'turn':turn}
    ASSEMBLIES[CURRENT]['rooms'][name]=record
    return record

def roof_room(name,kind='flat'):
    a=ASSEMBLIES[CURRENT]['rooms'][name];x,y,w,d,h=a['spec'];bottom=a['bottom'];turn=a['turn'];top=bottom+h
    P=lambda label,xyz,size,mat='roof',stage='vaults',role='roofs':_P(name+'_'+label,(x,y),xyz,size,mat,stage,role,name,turn)
    if kind=='vault':
        rx=(w-.18)/2;rise=.45
        transform=(lambda u,v,z:(x-v,y+u,z)) if turn else (lambda u,v,z:(x+u,y+v,z))
        cap=tag(R.vault(CURRENT+'_'+name+'_Vault',0,-d/2,d/2,top,rx,rise,.10,'roof',
                      col('roofs'),segments=20,along=3,transform=transform),'vaults','roofs',name)
        _lod_curve(cap,'vault',cx=0.,y0=-d/2,y1=d/2,z0=top,rx=rx,rz=rise,thickness=.10,origin=[x,y],turn=turn)
        for s in (-1,1):
            out=[(-rx,top),(rx,top)]+[(rx*math.cos(j*math.pi/20),top+rise*math.sin(j*math.pi/20)) for j in range(1,20)]
            end=tag(R.extrude_xz(CURRENT+'_'+name+'_VaultEnd'+str(s),out,s*d/2-.04,s*d/2+.04,
                            'plaster',col('roofs'),'vaults',transform),'vaults','roofs',name)
            _lod_curve(end,'vault_end',rx=rx,z0=top,rz=rise,y0=s*d/2-.04,y1=s*d/2+.04,origin=[x,y],turn=turn)
    else:
        cap=P('RoofBed',(0,0,top+.09),(w,d,.18))
        for index,s in enumerate((-1,1)):
            rail=P('ParapetSide'+str(s),(s*(w/2-.07),0,top+.26),(.14,d,.16),'plaster')
            _lod_run(rail,'parapet_ring',name,index*2,4,axis=0,thickness=.14)
            rail=P('ParapetEnd'+str(s),(0,s*(d/2-.07),top+.26),(w-.28,.14,.16),'plaster')
            _lod_run(rail,'parapet_ring',name,index*2+1,4,axis=0,thickness=.14)
    for i,bearing in enumerate([a['back']]+a['sides']+a['front']):
        contact(name+'_RoofBearing'+str(i),cap,bearing)
    a['roof']=cap
    return cap

def canopy(name,x,y,w,d,h,posts=3):
    g=name;beam_h=.18;rafter_h=.12;posttop=F+h-beam_h-rafter_h
    feet=[];poles=[]
    for row,yy in enumerate((y-d/2+.10,y+d/2-.10)):
        rowposts=[]
        for i in range(posts):
            xx=x-w/2+.10+i*(w-.20)/(posts-1)
            foot=B(name+'_Foot'+str(row)+'_'+str(i),(xx,yy,F+.04),(.24,.24,.08),'stone','foundation','architecture',g)
            pole=B(name+'_Post'+str(row)+'_'+str(i),(xx,yy,(F+.08+posttop)/2),(.12,.12,posttop-F-.08),'timber','walls','architecture',g)
            contact(name+'_PoleFoot'+str(row)+'_'+str(i),pole,foot);rowposts.append(pole);poles.append(pole)
        beam=B(name+'_Beam'+str(row),(x,yy,posttop+beam_h/2),(w,.18,beam_h),'timber','vaults','architecture',g)
        for i,pole in enumerate(rowposts):contact(name+'_BeamPost'+str(row)+'_'+str(i),beam,pole)
        feet.append(beam)
    rafters=[]
    for i in range(7):
        xx=x-w/2+.12+i*(w-.24)/6
        joist=B(name+'_Rafter'+str(i),(xx,y,F+h-rafter_h/2),(.09,d,rafter_h),'timber','vaults','fittings',g)
        for j,beam in enumerate(feet):contact(name+'_RafterBearing'+str(i)+'_'+str(j),joist,beam)
        rafters.append(joist)
    cap=B(name+'_Roof',(x,y,F+h+.055),(w+.10,d+.10,.11),'roof','vaults','roofs',g)
    for i,joist in enumerate(rafters):contact(name+'_RoofRafter'+str(i),cap,joist)
    return {'roof':cap,'posts':poles,'height':h}

def textile(name,x,y,z,w=.92):
    beam=B(name+'_Support',(x,y,z),(w+.18,.08,.08),'timber','finish','fittings','owner')
    cloth=B(name+'_Cloth',(x,y-.04,z-.23),(w,.025,.38),'owner','finish','owner','owner')
    contact(name+'_Suspended',cloth,beam,'top-bottom')
    return cloth

def show(key=KEYS[0],state='healthy',lod=0):
    activate();s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(PREFIX):c.hide_render=c.hide_viewport=c.name!=PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s
    R.view(pos=(14,-18,14),center=VIEW_CENTER,distance=VIEW_DISTANCE,solid=True)

def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_UNINSPECTED',FAMILY,key)

def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')

def reset_owned(key=None):
    if key is not None and key not in KEYS:raise ValueError('Unknown body')
    owned=PREFIX+(key+'_' if key else '')
    for ob in list(bpy.data.objects):
        if ob.name.startswith(owned):
            data=ob.data if ob.type=='MESH' else None;bpy.data.objects.remove(ob,do_unlink=True)
            if data and not data.users:bpy.data.meshes.remove(data)
    for c in list(bpy.data.collections):
        if c.name.startswith(owned):bpy.data.collections.remove(c)
    if key:
        ANCHORS.pop(key,None);ASSEMBLIES.pop(key,None);CONTRACTS[:]=[c for c in CONTRACTS if c['body']!=key]
    else:ANCHORS.clear();ASSEMBLIES.clear();CONTRACTS.clear()


# Exactly one existing primary resource; no artificial Age I/II/IV tier.
ENVELOPES={3:[[-6.95,-6.95,-.08],[6.95,6.95,11.60]]}
VIEW_CENTER=(0.,0.,3.4)
VIEW_DISTANCE=25.
H=4.20
WALK_Z=F+H+.18
STRONG=(1.45,2.90,5.40,4.40,7.70)
STRONG_ROOF=F+STRONG[4]+.18


def _prism(name,outline,bottom,top,surface,stage,role,group):
    n=len(outline);verts=[(x,y,z) for z in (bottom,top) for x,y in outline]
    # Polygon is counter-clockwise; fan-free planar end n-gons remain inspectable.
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return tag(R.mesh(CURRENT+'_'+name,verts,faces,surface,col(role),stage,role),stage,role,group)


def first_room():
    # A lofty guard/store hall is deliberately one occupied volume. An invented
    # inaccessible second floor is not hidden inside the high defensive mass.
    x,y,w,d,h=STRONG;t=.60;g='strong_hall'
    back=wall('StrongBack',x,y+d/2-t/2,w,t,h,group=g)
    west=wall('StrongWest',x-w/2+t/2,y,t,d-2*t,h,group=g)
    # The east wall has one genuine narrow high guard/light opening.
    slit_y=2.80;slit_w=.30;slit_bottom=F+4.20;slit_top=slit_bottom+1.20
    east_x=x+w/2-t/2;y0=y-d/2+t;y1=y+d/2-t
    east=[]
    for label,a,b in [('South',y0,slit_y-slit_w/2),('North',slit_y+slit_w/2,y1)]:
        east.append(wall('StrongEast'+label,east_x,(a+b)/2,t,b-a,h,group=g))
    east.append(wall('StrongEastSill',east_x,slit_y,t,slit_w,slit_bottom-F,group=g))
    east.append(wall('StrongEastHead',east_x,slit_y,t,slit_w,F+h-slit_top,bottom=slit_top,group=g))
    opening=1.25;module=1.70;front_y=y-d/2
    front=tag(R.archwall(CURRENT+'_StrongPortal',x,front_y,front_y+t,F,module,h,opening,2.02,.38,
                    'plaster',col('architecture'),segments=16),'walls','architecture',g)
    _lod_curve(front,'arch',cx=x,y0=front_y,y1=front_y+t,z0=F,outer_w=module,height=h,
               inner_w=opening,spring=2.02,rise=.38)
    for i,(a,b) in enumerate(((x-w/2,x-module/2),(x+module/2,x+w/2))):
        wall('StrongFrontSolid'+str(i),(a+b)/2,front_y+t/2,b-a,t,h,group=g)
    # Narrow recessed leaves retain visible side/top recesses; no fake painted door.
    B('StrongDoorLeaf',(x,front_y+.36,F+1.03),(1.09,.08,2.06),'timber','finish','fittings',g)
    floor=B('StrongFloor',(x,y,F+.04),(w-2*t,d-2*t,.08),'stone','foundation','architecture',g)
    ASSEMBLIES[CURRENT]['strong']={'back':back,'west':west,'east':east,'front':front,'floor':floor}
    ANCHORS[CURRENT]['strong_hall']={'program':'lofty guard/store hall; accessible defensive roof, not an unmodeled upper storey',
         'plan':STRONG,'wall_thickness':t,'roof_target_z':STRONG_ROOF,'east_guard_opening':[slit_y,slit_w,slit_bottom,slit_top]}
    print('FIRST_ROOM_DRAFT',CURRENT,'thick occupied strong hall and real portal/slit')


def _curtain(name,x,y,w,d,outer_axis,outer_sign):
    b=wall(name,x,y,w,d,H,group='curtain_'+name)
    cap=B(name+'_WalkCap',(x,y,F+H+.09),(w,d,.18),'stone','vaults','roofs','curtain_'+name)
    contact(name+'_CapBearing',cap,b)
    if outer_axis=='x':
        para=wall(name+'_Parapet',x+outer_sign*(w/2-.16),y,.32,d,.62,bottom=WALK_Z,group='curtain_'+name)
        count=max(2,int(d/1.35));span=d
        for i in range(count):
            yy=y-span/2+(i+.5)*span/count
            merlon=B(name+'_Merlon'+str(i),(x+outer_sign*(w/2-.16),yy,WALK_Z+.62+.18),(.32,.62,.36),'plaster','finish','architecture','curtain_'+name)
            _lod_run(merlon,'merlon_course',name,i,count,axis=1)
            contact(name+'_MerlonSeat'+str(i),merlon,para)
    else:
        para=wall(name+'_Parapet',x,y+outer_sign*(d/2-.16),w,.32,.62,bottom=WALK_Z,group='curtain_'+name)
        count=max(2,int(w/1.35));span=w
        for i in range(count):
            xx=x-span/2+(i+.5)*span/count
            merlon=B(name+'_Merlon'+str(i),(xx,y+outer_sign*(d/2-.16),WALK_Z+.80),(.62,.32,.36),'plaster','finish','architecture','curtain_'+name)
            _lod_run(merlon,'merlon_course',name,i,count,axis=0)
            contact(name+'_MerlonSeat'+str(i),merlon,para)
    contact(name+'_ParapetSeat',para,cap)
    return cap


def _corner_platform(name,x,y):
    # Low chamfered platforms flank the gate; no needle turrets or miniature Bam.
    r=1.30;c=.42
    ring=[(x-r+c,y-r),(x+r-c,y-r),(x+r,y-r+c),(x+r,y+r-c),
          (x+r-c,y+r),(x-r+c,y+r),(x-r,y+r-c),(x-r,y-r+c)]
    base=_prism(name+'_Core',ring,F,F+H,'plaster','walls','architecture',name)
    cap=_prism(name+'_Walk',ring,F+H,WALK_Z,'stone','vaults','roofs',name)
    contact(name+'_WalkSeat',cap,base)
    # North cardinal edge stays open where the side curtain walk enters.
    for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        if i==4 or i==(2 if x<0 else 6):continue
        dx,dy=b[0]-a[0],b[1]-a[1];ln=math.hypot(dx,dy)
        ob=tag(R.block(CURRENT+'_'+name+'_Parapet'+str(i),((a[0]+b[0])/2,(a[1]+b[1])/2,WALK_Z+.38),
              (ln,.30,.76),'plaster',col('architecture'),'walls','architecture',math.atan2(dy,dx)),
              'walls','architecture',name)
        contact(name+'_ParapetSeat'+str(i),ob,cap)
    return cap


def _stair(name,x,y0,y1,width,z0,z1,count,grounded=True):
    run=(y1-y0)/count;rise=(z1-z0)/count
    parts=[]
    for i in range(count):
        # Grounded masonry access has no unsupported treads or hovering ramp.
        top=z0+(i+1)*rise
        bottom=F if grounded else z0
        ob=B(name+'_Tread'+str(i),(x,y0+(i+.5)*run,(bottom+top)/2),(width,run,top-bottom),
             'stone','walls','architecture',name);parts.append(ob)
        _lod_run(ob,'masonry_stair',name,i,count,axis=1)
        if grounded:contact(name+'_Ground'+str(i),ob,ASSEMBLIES[CURRENT]['ground'])
    return parts


def _strong_roof():
    x,y,w,d,h=STRONG;roof=B('StrongRoof',(x,y,F+h+.09),(w,d,.18),'roof','vaults','roofs','strong_hall')
    a=ASSEMBLIES[CURRENT]['strong']
    for i,b in enumerate([a['back'],a['west'],a['front']]+a['east'][:2]+a['east'][3:]):contact('StrongRoofBearing'+str(i),roof,b)
    # West parapet deliberately omits Y2.6..3.3, matching the actual roof landing.
    for label,yy,dd in [('South',1.65,1.90),('North',4.20,1.80)]:
        p=wall('StrongWestParapet'+label,x-w/2+.16,yy,.32,dd,.85,bottom=STRONG_ROOF,group='strong_defense')
        contact('StrongWestSeat'+label,p,roof)
    for label,xx,yy,ww,dd in [('East',x+w/2-.16,y,.32,d),('North',x,y+d/2-.16,w-.64,.32),('South',x,y-d/2+.16,w-.64,.32)]:
        p=wall('StrongParapet'+label,xx,yy,ww,dd,.85,bottom=STRONG_ROOF,group='strong_defense')
        contact('StrongParapetSeat'+label,p,roof)
    for i,xx in enumerate((-.40,1.45,3.30)):
        merlon=B('StrongFrontMerlon'+str(i),(xx,.86,STRONG_ROOF+1.025),(.70,.32,.35),'plaster','finish','architecture','strong_defense')
        _lod_run(merlon,'merlon_course','StrongFront',i,3,axis=0)
        # Explicit relative-height equation; exact parent mesh checked by adapter.
        CONTRACTS.append({'body':CURRENT,'name':'StrongFrontMerlonSeat'+str(i),'a':merlon.name,
             'b':PREFIX+CURRENT+'_StrongParapetSouth','axis':'bottom-top','target':0.,'tolerance':.003})
    ASSEMBLIES[CURRENT]['strong']['roof']=roof


def architecture():
    _strong_roof()
    _curtain('WestCurtain',-5.50,.70,1.10,9.30,'x',-1)
    _curtain('EastCurtain',5.50,.70,1.10,9.30,'x',1)
    _curtain('RearCurtain',0.,5.80,12.10,.90,'y',1)
    _curtain('FrontWest',-2.975,-5.50,1.95,1.0,'y',-1)
    _curtain('FrontEast',2.975,-5.50,1.95,1.0,'y',-1)
    _corner_platform('WestGatePlatform',-5.25,-5.25)
    _corner_platform('EastGatePlatform',5.25,-5.25)
    # Through gatehouse: front and back arch openings share one clear axis.
    gatewalls=[]
    for label,y0,y1 in [('Outer',-6.15,-5.55),('Inner',-4.75,-4.15)]:
        ob=tag(R.archwall(CURRENT+'_Gate'+label,0.,y0,y1,F,4.0,H,1.85,2.15,.50,
                 'plaster',col('architecture'),segments=18),'walls','architecture','gatehouse');gatewalls.append(ob)
        _lod_curve(ob,'arch',cx=0.,y0=y0,y1=y1,z0=F,outer_w=4.,height=H,
                   inner_w=1.85,spring=2.15,rise=.50)
    for sign in (-1,1):gatewalls.append(wall('GateFlank'+str(sign),sign*1.70,-5.15,.60,.80,H,group='gatehouse'))
    gatecap=B('GateWalkCap',(0.,-5.15,F+H+.09),(4.0,2.0,.18),'stone','vaults','roofs','gatehouse')
    for i,ob in enumerate(gatewalls):contact('GateCapBearing'+str(i),gatecap,ob)
    gatepara=wall('GateOuterParapet',0.,-5.99,4.0,.32,.76,bottom=WALK_Z,group='gatehouse')
    contact('GateParapetSeat',gatepara,gatecap)
    # First stair rises from the court onto a solid landing that meets the curtain
    # and the parallel upper access walk. The second stair remains outside hall.
    podium=wall('WestAccessPodium',-2.65,-.60,2.20,6.40,WALK_Z-F,group='roof_access')
    returnwalk=wall('UpperReturnWalk',-3.20,2.95,1.10,.70,WALK_Z-F,group='roof_access')
    landing=wall('CurtainAccessLanding',-4.35,2.95,1.20,.70,WALK_Z-F,group='roof_access')
    flight1=_stair('CourtToCurtain',-4.30,-3.80,2.60,1.10,F,WALK_Z,29)
    flight2=_stair('WalkToStrongRoof',-2.10,-2.60,2.60,1.10,WALK_Z,STRONG_ROOF,24,grounded=False)
    for i,ob in enumerate(flight2):contact('UpperStairPodium'+str(i),ob,podium)
    rooflanding=wall('StrongRoofLanding',-1.95,2.95,1.40,.70,STRONG_ROOF-F,group='roof_access')
    # The landing's large base is a deliberately occupied defensive buttress; no
    # balcony slab pretends to span a court without bearing.
    contact('CurtainLandingGround',landing,ASSEMBLIES[CURRENT]['ground'])
    contact('PodiumGround',podium,ASSEMBLIES[CURRENT]['ground'])
    contact('ReturnWalkGround',returnwalk,ASSEMBLIES[CURRENT]['ground'])
    contact('RoofLandingGround',rooflanding,ASSEMBLIES[CURRENT]['ground'])
    ANCHORS[CURRENT]['defensive_access']={'curtain_walk_z':WALK_Z,'strong_roof_z':STRONG_ROOF,
       'first_stair':{'x':-4.3,'y':[-3.8,2.6],'steps':29},
       'upper_walk_clear_x':[-3.75,-2.65],'second_stair':{'x':-2.1,'y':[-2.6,2.6],'steps':24},
       'roof_parapet_gap_y':[2.6,3.3],'native_marker_clearance':'unqualified; bone-local marker is not world position'}
    ANCHORS[CURRENT]['program']='controlled gate, thick curtain court, low chamfered flanks, lofty strong hall and accessed defense roof'
    print('ARCHITECTURE_DRAFT',CURRENT,'grounded defensive compound and continuous roof access')


def props():
    # A small covered cistern/service station reinforces prolonged occupation;
    # a Keep is not identified by a pile of Barracks weapons.
    cistern=B('CisternBody',(3.80,-2.35,F+.42),(1.05,.90,.84),'stone','walls','props','court_service')
    _lod_run(cistern,'cistern_unit','Cistern',0,3)
    lid=B('CisternCover',(3.80,-2.35,F+.89),(1.15,1.0,.10),'stone','finish','props','court_service')
    _lod_run(lid,'cistern_unit','Cistern',1,3)
    contact('CisternCoverSeat',lid,cistern);contact('CisternGround',cistern,ASSEMBLIES[CURRENT]['ground'])
    hatch=B('CisternHatch',(3.8,-2.35,F+.96),(.45,.38,.04),'timber','finish','props','court_service')
    _lod_run(hatch,'cistern_unit','Cistern',2,3)
    for i,xx in enumerate((2.70,3.40)):
        chest=B('GuardSupplyChest'+str(i),(xx,-3.60,F+.22),(.58,.44,.44),'timber','finish','props','court_service')
        contact('ChestGround'+str(i),chest,ASSEMBLIES[CURRENT]['ground'])
    print('PROPS_DRAFT',CURRENT,'restrained water and guard supplies')


def detail():
    textile('GateOwner',0.,-6.18,F+3.60,1.55)
    # Load-bearing brick/stone foot course is restrained; wear follows the gate
    # and stair approach instead of blanket damage on every defensive surface.
    for i in range(7):
        B('GateTraffic'+str(i),(0.,-5.85+i*.72,F+.001),(1.10,.58,.006),'grime','finish','wear','gate_traffic')
    for i in range(4):
        B('StairApproachPaver'+str(i),(-4.30,-4.65+i*.20,F+.025),(.75,.16,.05),'stone','foundation','ground','roof_access')
    print('DETAIL_DRAFT',CURRENT,'functional wear, controlled owner cue; no royal ornament')
