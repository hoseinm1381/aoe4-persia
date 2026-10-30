"""DRAFT original Persia dock source art. Existing resources only.
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
FAMILY = 'dock'
PREFIX = 'PSB_' + FAMILY + '_'
R.configure(ROOT, FAMILY)
INVENTORY = ROOT.parents[3] / 'research/persia_buildings/inventory'
KEYS = ('A2','A3','A4')
F = .80
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
    ground=_deck_foundation()
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
       'terrain_origin_note':'native origin retained; no Z recenter from buried geometry minimum; .80 source deck top is an original provisional proposal; native waterline unqualified',
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
        _lod_run(joist,'canopy_rafter',name,i,7,axis=0)
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


ENVELOPES={2:[[-3.25,-3.25,-1.15],[3.25,3.20,7.00]],
           3:[[-3.25,-3.25,-1.15],[3.25,3.20,7.00]],
           4:[[-3.25,-3.25,-1.15],[3.25,3.20,7.90]]}
VIEW_CENTER=(0.,0.,2.0)
VIEW_DISTANCE=16.
DECKS={}
PLAN={2:{'store':(-1.55,1.90,2.20,1.80,2.75),'doors':(0.,),'turn':0},
      3:{'store':(-1.90,.40,3.70,1.80,3.10),'doors':(-.90,.90),'turn':1},
      4:{'store':(0.,2.15,5.40,1.40,2.65),'doors':(-1.50,1.50),'turn':0}}
PROGRAMMES={2:'small shore store, open eastern work shelter and broad loading apron',
            3:'long west vaulted goods range, open rear goods shelter and clear loading lane',
            4:'broad two-door warehouse, small upper counting room and supported timber access'}


def _deck_foundation():
    # No solid earth rectangle across hypothetical water. Piles stop at measured
    # source-envelope depth; no terrain or native waterline has been changed.
    beams=[];piles=[];planks=[]
    for row,yy in enumerate((-2.60,-.80,1.0,2.65)):
        supports=[]
        if row==3:
            abut=B('LandwardAbutment',(0.,yy,(-1.15+.50)/2),(6.0,.65,1.65),
                   'stone','foundation','architecture','quay_support')
            supports.append(abut)
        else:
            for i,xx in enumerate((-2.50,0.,2.50)):
                pile=B('QuayPile'+str(row)+'_'+str(i),(xx,yy,(-1.15+.50)/2),(.26,.26,1.65),
                       'timber','foundation','architecture','quay_support')
                supports.append(pile);piles.append(pile)
        beam=B('DeckBeam'+str(row),(0.,yy,.57),(6.0,.22,.14),'timber','foundation','architecture','quay_support')
        for i,support in enumerate(supports):contact('DeckBeamSupport'+str(row)+'_'+str(i),beam,support)
        beams.append(beam)
    for i in range(12):
        plank=B('DeckPlank'+str(i),(-3.0+(i+.5)*.50,0.,.72),(.50,6.10,.16),
                'timber','foundation','ground','quay_deck')
        _lod_run(plank,'deck_plank','QuayDeck',i,12,axis=0)
        for row,beam in enumerate(beams):contact('DeckPlankBearing'+str(i)+'_'+str(row),plank,beam)
        planks.append(plank)
    DECKS[CURRENT]={'beams':beams,'piles':piles,'planks':planks}
    return planks[0]


def deck_contact(name,part):
    """Bind each load to the actual plank beneath it, not plank zero's height."""
    lo,hi=R.bounds(part);candidates=[]
    for plank in DECKS[CURRENT]['planks']:
        a,b=R.bounds(plank)
        overlap=[min(hi[i],b[i])-max(lo[i],a[i]) for i in (0,1)]
        if min(overlap)>1e-6:candidates.append((overlap[0]*overlap[1],plank.name,plank))
    if not candidates:raise ValueError('No actual deck support under '+part.name)
    bearing=max(candidates,key=lambda item:(item[0],item[1]))[2]
    contact(name,part,bearing)


def first_room():
    p=PLAN[age()]
    room('Warehouse',p['store'],p['doors'],arched=(age()>=3),turn=p['turn'])
    ANCHORS[CURRENT]['shoreline_contract']={'source_working_edge':'negative Y, an original source proposal',
       'proposed_deck_top':F,'proposed_pile_bottom':-1.15,'native_waterline':'unqualified',
       'native_boat_exit_axis':'unqualified; bone-local layout markers cannot alone establish world exit positions',
       'terrain_origin':'unchanged native origin; this recipe authors no terrain, ship or additional quay attachment'}
    print('FIRST_ROOM_DRAFT',CURRENT,'real warehouse openings; dock orientation still a source proposal')


def _warehouse4_roof():
    a=ASSEMBLIES[CURRENT]['rooms']['Warehouse'];x,y,w,d,h=a['spec']
    cap=B('Warehouse_RoofBed',(x,y,F+h+.09),(w,d,.18),'roof','vaults','roofs','Warehouse')
    for i,b in enumerate([a['back']]+a['sides']+a['front']):contact('Warehouse_RoofBearing'+str(i),cap,b)
    # Omit caps under the upper counting room; no coplanar embedded parapet.
    for label,xx,yy,ww,dd in [('East',2.63,2.15,.14,1.40),
         ('Front',1.225,1.52,2.95,.14),('Back',1.225,2.78,2.95,.14)]:
        B('Warehouse_Parapet'+label,(xx,yy,F+h+.26),(ww,dd,.16),'plaster','vaults','roofs','Warehouse')
    a['roof']=cap
    return cap


def _timber_stair(name,x,y0,y1,width,z0,z1,count):
    # Closed toothed stringers are derived from the same ledge planes as treads.
    run=(y1-y0)/count;rise=(z1-z0)/count;th=.09
    lod_stair={'x':x,'y0':y0,'y1':y1,'width':width,'z0':z0,'z1':z1,
               'tread_thickness':th,'web_depth':.35,
               'underside_policy':'parallel to stair slope below tread ledges; clipped at deck with grounded knee'}
    top=[]
    for i in range(count):
        z=z0+(i+1)*rise-th
        top.extend([(y0+i*run,z),(y0+(i+1)*run,z)])
    # The old deck-foot→upper-end chord crossed the first tread ledges.
    # A parallel underside .35 below those ledges stays below every tread;
    # clip it to deck Z until its actual knee, keeping the same ground/extent.
    knee=y0+(th+.35)/(z1-z0)*(y1-y0)
    outline=top+[(y1,z1-th-.35),(knee,z0),(y0,z0)]
    stringers=[]
    for side in (-1,1):
        xx=x+side*(width/2-.06)
        ob=tag(R.extrude_xz(CURRENT+'_'+name+'_Stringer'+str(side),outline,xx-.045,xx+.045,
                    'timber',col('architecture'),'walls',lambda u,v,z:(v,u,z)),
                    'walls','architecture',name);stringers.append(ob)
        _lod_run(ob,'timber_stair',name,0 if side<0 else 1,count,axis=1,stair=lod_stair)
        # The bottom face seats at deck top; underside is intentionally sloped.
        deck_contact(name+'_StringerDeck'+str(side),ob)
    for i in range(count):
        z=z0+(i+1)*rise
        tread=B(name+'_Tread'+str(i),(x,y0+(i+.5)*run,z-th/2),(width,run,th),
                'timber','walls','architecture',name)
        _lod_run(tread,'timber_stair',name,i+2,count,axis=1,stair=lod_stair)
        for j,stringer in enumerate(stringers):
            # Relative bounding-box contract plus explicit local seat plane.
            # Parent must inspect the sampled ledge topology, not treat this as
            # a general face-adjacency proof for a concave stepped solid.
            contact(name+'_TreadStringer'+str(i)+'_'+str(j),tread,stringer,
                    target=(z-th)-(z1-th))
            CONTRACTS[-1]['local_seat']={'y_interval':[y0+i*run,y0+(i+1)*run],
                 'stringer_ledge_z':z-th,'tread_bottom_z':z-th,'status':'derived stepped profile; verify real mesh after build'}
    return stringers


def _counting_access(z):
    # Landing deck top matches the upper room floor's bottom; .08 threshold.
    posts=[];beams=[]
    for row,yy in enumerate((.67,1.33)):
        rowposts=[]
        for i,xx in enumerate((-2.52,-.38)):
            foot=B('CountingLandingFoot'+str(row)+'_'+str(i),(xx,yy,F+.05),(.24,.24,.10),
                   'stone','foundation','architecture','counting_access')
            post=B('CountingLandingPost'+str(row)+'_'+str(i),(xx,yy,(F+.10+z-.30)/2),(.13,.13,z-.30-F-.10),
                   'timber','walls','architecture','counting_access')
            contact('CountingPostFoot'+str(row)+'_'+str(i),post,foot);rowposts.append(post);posts.append(post)
        beam=B('CountingLandingBeam'+str(row),(-1.45,yy,z-.21),(2.40,.16,.18),
               'timber','vaults','architecture','counting_access')
        for i,post in enumerate(rowposts):contact('CountingBeamPost'+str(row)+'_'+str(i),beam,post)
        beams.append(beam)
    landing=B('CountingLandingDeck',(-1.45,1.0,z-.06),(2.40,.90,.12),'timber','vaults','architecture','counting_access')
    for i,beam in enumerate(beams):contact('CountingDeckBeam'+str(i),landing,beam)
    _timber_stair('CountingStair',-2.20,-3.0,.55,.80,F,z,20)
    # Front rail starts east of the stair arrival, leaving an .90-wide opening.
    railposts=[]
    for i,xx in enumerate((-1.67,-.36)):
        post=B('CountingRailPost'+str(i),(xx,.60,z+.375),(.08,.08,.75),
               'timber','finish','architecture','counting_access');railposts.append(post)
        contact('CountingRailFoot'+str(i),post,landing)
    rail=B('CountingFrontRail',(-1.015,.60,z+.79),(1.47,.08,.08),'timber','finish','architecture','counting_access')
    for i,post in enumerate(railposts):contact('CountingRailSeat'+str(i),rail,post)
    ANCHORS[CURRENT]['counting_access']={'landing_bounds':[[-2.65,.55,z-.12],[-.25,1.45,z]],
           'stair':{'x':-2.2,'y':[-3.,.55],'width':.8,'steps':20,'rise':(z-F)/20},
           'rail_gap_x':[-2.65,-1.75],'upper_threshold':.08}


def architecture():
    a=age()
    if a==2:
        roof_room('Warehouse')
        canopy('WorkingShed',1.40,1.50,2.60,2.80,2.60,posts=3)
    elif a==3:
        roof_room('Warehouse','vault')
        canopy('RearGoodsShelter',1.15,2.10,3.70,1.70,2.80,posts=3)
    else:
        _warehouse4_roof()
        upper=F+PLAN[a]['store'][4]+.18
        room('CountingRoom',(-1.45,2.15,2.40,1.40,2.30),(0.,),arched=True,bottom=upper)
        roof_room('CountingRoom')
        contact('CountingRoomFloorBearing',ASSEMBLIES[CURRENT]['rooms']['CountingRoom']['floor'],
                   ASSEMBLIES[CURRENT]['rooms']['Warehouse']['roof'])
        _counting_access(upper)
    # Discrete mooring posts, not a new native collision strip around the dock.
    for i,xx in enumerate((-2.75,2.75)):
        foot=B('MooringFoot'+str(i),(xx,-2.75,F+.06),(.34,.34,.12),'stone','foundation','props','mooring')
        _lod_run(foot,'mooring_unit',str(i),0,3)
        post=B('MooringPost'+str(i),(xx,-2.75,F+.48),(.18,.18,.72),'timber','walls','props','mooring')
        _lod_run(post,'mooring_unit',str(i),1,3)
        contact('MooringPostFoot'+str(i),post,foot)
        cap=B('MooringCap'+str(i),(xx,-2.75,F+.87),(.28,.22,.06),'timber','finish','props','mooring')
        _lod_run(cap,'mooring_unit',str(i),2,3)
        contact('MooringCapSeat'+str(i),cap,post)
    ANCHORS[CURRENT]['program']=PROGRAMMES[a]
    print('ARCHITECTURE_DRAFT',CURRENT,PROGRAMMES[a])


def _lifting_frame():
    # Small static handling frame, not an animated crane or substituted native rig.
    y=-1.90;group='loading_frame';feet=[];braces=[]
    for i,(xx,outline) in enumerate(((1.40,[(1.33,F+.10),(1.47,F+.10),(2.12,F+2.10),(1.98,F+2.10)]),
                                     (2.70,[(2.63,F+.10),(2.77,F+.10),(2.12,F+2.10),(1.98,F+2.10)]))):
        foot=B('HandlingFoot'+str(i),(xx,y,F+.05),(.32,.42,.10),'timber','foundation','props',group)
        brace=tag(R.extrude_xz(CURRENT+'_HandlingLeg'+str(i),outline,y-.07,y+.07,'timber',col('props'),'finish'),
                  'finish','props',group)
        contact('HandlingLegFoot'+str(i),brace,foot);feet.append(foot);braces.append(brace)
    beam=B('HandlingCrossbar',(2.05,y,F+2.17),(1.0,.18,.14),'timber','finish','props',group)
    for i,brace in enumerate(braces):contact('HandlingCrossbarSeat'+str(i),beam,brace)
    rope=B('HandlingRope',(2.05,y,F+1.51),(.035,.035,1.18),'cloth','finish','props',group)
    contact('HandlingRopeSuspended',rope,beam,'top-bottom')
    load=B('HandlingPulleyBlock',(2.05,y,F+.77),(.18,.15,.30),'timber','finish','props',group)
    contact('HandlingBlockSuspended',load,rope,'top-bottom')


def props():
    _lifting_frame()
    a=age()
    positions={2:[(.60,1.35),(1.45,2.2),(2.30,1.35)],
               3:[(.15,2.20),(1.20,2.20),(2.30,2.20)],
               4:[(.65,-.10),(1.40,.50),(2.15,.50)]}[a]
    for i,(x,y) in enumerate(positions):
        box=B('GoodsCrate'+str(i),(x,y,F+.23),(.58,.54,.46),'timber','finish','props','goods')
        deck_contact('GoodsCrateDeck'+str(i),box)
        for sign in (-1,1):
            B('CrateBinding'+str(i)+'_'+str(sign),(x+sign*.18,y,F+.47),(.045,.54,.02),
              'cloth','finish','props','goods')
    # Low supported rope/tool bench at an occupied edge, clear of loading axis.
    x,y=({2:(-.95,.15),3:(-1.90,-.85),4:(.65,-.70)}[a])
    bench=B('DockBench',(x,y,F+.47),(.95,.38,.10),'timber','finish','props','goods')
    for i,xx in enumerate((x-.32,x+.32)):
        leg=B('DockBenchLeg'+str(i),(xx,y,F+.21),(.10,.28,.42),'timber','finish','props','goods')
        contact('DockBenchSeat'+str(i),bench,leg);deck_contact('DockBenchDeck'+str(i),leg)
    print('PROPS_DRAFT',CURRENT,'original compact goods, supported handling and mooring')


def detail():
    a=age()
    if a==2:textile('DockOwner',-1.55,.96,F+2.45,1.0)
    elif a==3:textile('DockOwner',1.15,1.35,F+2.65,1.2)
    else:textile('DockOwner',-1.45,1.41,F+4.80,1.0)
    # Foot/rope handling wear stays on the deck; no dry-earth land patch at sea.
    for i in range(5):
        B('LoadingWear'+str(i),(.25,-2.7+i*.58,F+.002),(.85,.45,.006),'grime','finish','wear','loading_wear')
    print('DETAIL_DRAFT',CURRENT,'timber handling wear and restrained owner textiles')
