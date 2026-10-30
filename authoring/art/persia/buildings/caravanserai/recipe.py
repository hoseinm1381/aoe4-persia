"""DRAFT original Persia caravanserai source art. Existing resources only.
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
FAMILY = 'caravanserai'
INVENTORY_FAMILY = 'caravanserai'
PREFIX = 'PSB_' + FAMILY + '_'
R.configure(ROOT, FAMILY)
INVENTORY = ROOT.parents[3] / 'research/persia_buildings/inventory'
KEYS = ('A2',)
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
    for b in handoff['families'][INVENTORY_FAMILY]['bodies']:
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
               if c.get('family')==INVENTORY_FAMILY and c.get('attachment') in attachments
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
                       if INVENTORY_FAMILY in m['used_by_families']]}
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
    ANCHORS[key]={'ground_top':F,'native_body_key':key,'inventory_family':INVENTORY_FAMILY,'native_model':native['model'],'authored_space':'measured native stamp-space; inverse resource projection required exactly once',
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
    if turn==1:cx,cy=x-v,y+u;sx,sy,sz=size[1],size[0],size[2]
    elif turn==-1:cx,cy=x+v,y-u;sx,sy,sz=size[1],size[0],size[2]
    elif turn==2:cx,cy=x-u,y-v;sx,sy,sz=size
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
            transform=(lambda a,b,z:(x-b,y+a,z)) if turn==1 else ((lambda a,b,z:(x+b,y-a,z)) if turn==-1 else ((lambda a,b,z:(x-a,y-b,z)) if turn==2 else (lambda a,b,z:(x+a,y+b,z))))
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
        rx=(w-.22)/2;rise=.45
        transform=(lambda u,v,z:(x-v,y+u,z)) if turn==1 else ((lambda u,v,z:(x+v,y-u,z)) if turn==-1 else ((lambda u,v,z:(x-u,y-v,z)) if turn==2 else (lambda u,v,z:(x+u,y+v,z))))
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



ENVELOPES={2:[[-5.95,-5.30,-.08],[5.95,5.30,6.60]]}
VIEW_CENTER=(0.,0.,1.6)
VIEW_DISTANCE=20.
GUEST_BOTTOM=F+.25
BAYS=(-2.60,-.50,1.60)


def _guest(name,x,y,turn):
    plinth=B(name+'_Plinth',(x,y,F+.125),(1.60,2.10,.25),'stone','foundation','architecture',name)
    a=room(name,(x,y,2.10,1.60,2.40),(0.,),arched=True,bottom=GUEST_BOTTOM,turn=turn)
    contact(name+'_FloorPlinth',a['floor'],plinth)
    for i,bearing in enumerate([a['back']]+a['sides']+a['front']):contact(name+'_WallPlinth'+str(i),bearing,plinth)
    return a


def first_room():
    _guest('WestGuest0',-4.70,BAYS[0],1)
    print('FIRST_ROOM_DRAFT',CURRENT,'raised inward guest room, not a market stall')


def _stable():
    # One deeper service roof has two actual broad passages. It is distinct from
    # the smaller lodging modules and does not imply a roof of ornamental domes.
    x,y,w,d,h=0.,3.65,11.0,2.0,2.65;t=.32;g='stable_service'
    back=wall('StableBack',x,4.65-t/2,w,t,h,group=g)
    sides=[wall('StableSide'+str(s),s*(w/2-t/2),y,t,d-2*t,h,group=g) for s in (-1,1)]
    front=[];last=-w/2
    for i,xx in enumerate((-3.30,3.30)):
        module=1.90
        if xx-module/2>last:
            front.append(wall('StableFrontSolid'+str(i),(last+xx-module/2)/2,2.65+t/2,xx-module/2-last,t,h,group=g))
        arch=tag(R.archwall(CURRENT+'_StablePassage'+str(i),xx,2.65,2.65+t,F,module,h,1.30,1.80,.32,
                    'brick',col('architecture'),segments=14),'walls','architecture',g);front.append(arch)
        _lod_curve(arch,'arch',cx=xx,y0=2.65,y1=2.65+t,z0=F,outer_w=module,height=h,
                   inner_w=1.30,spring=1.80,rise=.32)
        last=xx+module/2
    front.append(wall('StableFrontEnd',(last+w/2)/2,2.65+t/2,w/2-last,t,h,group=g))
    roof=B('StableServiceRoof',(x,y,F+h+.10),(w,d,.20),'roof','vaults','roofs',g)
    for i,bearing in enumerate([back]+sides+front):contact('StableRoofBearing'+str(i),roof,bearing)
    for i,xx in enumerate((-1.80,0.,1.80)):
        # Low interior feed dividers, kept behind the court-facing passage line.
        divider=wall('StableFeedDivider'+str(i),xx,4.05,.14,.85,.66,group=g)
        contact('StableDividerGround'+str(i),divider,ASSEMBLIES[CURRENT]['ground'])
    ASSEMBLIES[CURRENT]['stable']={'roof':roof}


def _gate():
    bearings=[]
    for label,y0,y1 in [('Outside',-5.20,-4.88),('Inside',-4.42,-4.10)]:
        a=tag(R.archwall(CURRENT+'_InnGate'+label,0.,y0,y1,F,2.60,3.65,1.78,2.03,.38,
                  'brick',col('architecture'),segments=18),'walls','architecture','gate');bearings.append(a)
        _lod_curve(a,'arch',cx=0.,y0=y0,y1=y1,z0=F,outer_w=2.60,height=3.65,
                   inner_w=1.78,spring=2.03,rise=.38)
    for s in (-1,1):bearings.append(wall('GateSide'+str(s),s*1.16,-4.65,.28,.46,3.65,group='gate'))
    roof=B('GateRoof',(0.,-4.65,F+3.74),(2.60,1.10,.18),'roof','vaults','roofs','gate')
    for i,a in enumerate(bearings):contact('GateRoofBearing'+str(i),roof,a)
    # Low exterior frontage closes the inn without landmark-scale towers.
    for s in (-1,1):
        b=wall('FrontEnclosure'+str(s),s*3.40,-4.65,4.20,.30,2.35,group='outer_enclosure')
        contact('FrontEnclosureGround'+str(s),b,ASSEMBLIES[CURRENT]['ground'])
    # Through-axis remains open; the two door leaves are parked inside gate piers.
    for s in (-1,1):
        B('ParkedGateLeaf'+str(s),(s*1.0,-4.65,F+1.06),(.06,.38,2.12),'timber','finish','fittings','gate')
    ANCHORS[CURRENT]['gate_clear_axis']={'x':[-.89,.89],'y':[-5.2,-4.1],
       'status':'original visible passage; native path/animal clearance unqualified'}


def architecture():
    roof_room('WestGuest0','vault')
    for side,x,turn in [('West',-4.70,1),('East',4.70,-1)]:
        for i,y in enumerate(BAYS):
            if side=='West' and i==0:continue
            _guest(side+'Guest'+str(i),x,y,turn);roof_room(side+'Guest'+str(i),'vault')
        platform=B(side+'GuestWalk',(x+(1 if side=='West' else -1)*1.05,-.50,F+.125),(.50,6.30,.25),
                   'stone','foundation','architecture','guest_access')
        contact(side+'GuestWalkGround',platform,ASSEMBLIES[CURRENT]['ground'])
        # One broad step at the middle bay avoids pretending the raised floor is
        # universally accessible from the court without a threshold.
        step=B(side+'GuestStep',(x+(1 if side=='West' else -1)*1.42,-.50,F+.0625),(.24,1.10,.125),
               'stone','walls','architecture','guest_access')
        contact(side+'GuestStepGround',step,ASSEMBLIES[CURRENT]['ground'])
    _stable();_gate()
    # Small closed strips between frontage and first lodging bays maintain secure
    # enclosure while preserving one single entrance and a useful central court.
    for s in (-1,1):wall('FrontReturn'+str(s),s*5.35,-4.075,.30,.85,2.35,group='outer_enclosure')
    ANCHORS[CURRENT]['program']='single secure roadside inn; six raised inward guest bays, deeper stable/service band, open unloading court'
    ANCHORS[CURRENT]['court']={'clear_guest_walk_edges_x':[-3.40,3.40],
      'open_court_y':[-4.10,2.65],'overall_building_xy':[11.0,9.85],
      'Grand_hierarchy':'lower single-storey target only; exact same-camera comparison with existing Grand unverified'}
    print('ARCHITECTURE_DRAFT',CURRENT,'one court; original modest lodging/service hierarchy')


def props():
    # A trough is an actual open-sided vessel: base + four walls, no blue block.
    x,y=2.55,.30
    base=B('WaterTroughBase',(x,y,F+.06),(1.35,.55,.12),'stone','foundation','props','water_service')
    _lod_run(base,'trough_shell','WaterTrough',0,5)
    for index,(label,xx,yy,w,d) in enumerate([('West',x-.60,y,.15,.55),('East',x+.60,y,.15,.55),
                           ('North',x,y+.22,1.05,.11),('South',x,y-.22,1.05,.11)]):
        a=B('TroughWall'+label,(xx,yy,F+.26),(w,d,.28),'stone','finish','props','water_service')
        _lod_run(a,'trough_shell','WaterTrough',index+1,5)
        contact('TroughWallSeat'+label,a,base)
    # Water surface is an original material patch inside the basin, not a claim
    # that a native water/reflection shader is already qualified.
    B('TroughInterior',(x,y,F+.25),(1.03,.30,.025),'ink','finish','props','water_service')
    for i,(xx,yy) in enumerate(((-2.70,1.55),(-2.0,1.55),(2.40,-2.75))):
        chest=B('TravelerChest'+str(i),(xx,yy,F+.21),(.57,.44,.42),'timber','finish','props','travel_goods')
        contact('TravelerChestGround'+str(i),chest,ASSEMBLIES[CURRENT]['ground'])
    jar=tag(R.lathe(CURRENT+'_ServiceJar',(-2.55,-2.65,F),[(.18,0),(.28,.14),(.30,.45),(.15,.66)],
                 'pottery',col('props'),sides=16,stage='finish'),'finish','props','water_service')
    _lod_curve(jar,'lathe',center=[-2.55,-2.65,F],rings=[(.18,0),(.28,.14),(.30,.45),(.15,.66)])
    print('PROPS_DRAFT',CURRENT,'water, limited traveler goods; no animal statue or hotel sign')


def detail():
    textile('InnOwner',0.,-5.23,F+2.95,1.10)
    # Deliberate handling/rain wear; no blue royal facade or formal palace garden.
    for i in range(8):
        B('EntryTraffic'+str(i),(0.,-4.9+i*.78,F+.001),(1.35,.60,.006),'grime','finish','wear','court_traffic')
    for i in range(4):
        B('StableApproachWear'+str(i),(-2.30+i*1.50,2.35,F+.001),(.70,.40,.006),'earth','finish','wear','stable_traffic')
    print('DETAIL_DRAFT',CURRENT,'muted materials, ordinary roadside hierarchy')
