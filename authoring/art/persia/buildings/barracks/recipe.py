"""DRAFT Barracks source art. Four existing resource ages only.
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
FAMILY = 'barracks'
PREFIX = 'PSB_' + FAMILY + '_'
R.configure(ROOT, FAMILY)
INVENTORY = ROOT.parents[3] / 'research/persia_buildings/inventory'
KEYS = ('A1','A2','A3','A4')
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
                     'resource_bounds':b['healthy_definite_rest_bounds'],
                     'stamp':stamps[0], 'complete_category_bounds':cases,
                     'native_animation_graphs':b['native_animation_graphs'],
                     'dependencies':[{'model':path,'native_model_sha256':m['native_model_sha256'],
                        'native_owner_graphs':m['native_owner_graphs'],
                        'pose_and_sweep_status':m['pose_and_sweep_status']}
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
    return tag(R.block(CURRENT+'_'+name,center,size,surface,col(role),stage,role),stage,role,group)

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
       'native_dependencies':native['dependencies'],'complete_category_bounds':native['complete_category_bounds'],
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
                      'walls','architecture',g);front.append(arch)
            arch['lod_curve_spec']=json.dumps({'kind':'arch','x':u,'y0':-d/2,'y1':-d/2+t,'bottom':bottom,'width':ow+.34,'height':h,'opening':ow,'spring':dh-.25,'rise':.25,'origin':[x,y],'turn':turn})
        else:
            for s in (-1,1):front.append(P('Jamb'+str(i)+'_'+str(s),(u+s*(ow/2+.085),-d/2+t/2,bottom+h/2),(.17,t,h)))
            front.append(P('Head'+str(i),(u,-d/2+t/2,bottom+(dh+h)/2),(ow,t,h-dh)))
        leaf=P('Door'+str(i),(u,-d/2+t*.80,bottom+dh/2),(ow*.88,.055,dh),'timber','finish','fittings')
        last=u+half
    if last<w/2:front.append(P('FrontEnd',((last+w/2)/2,-d/2+t/2,bottom+h/2),(w/2-last,t,h)))
    floor=P('Floor',(0,0,bottom+.04),(w-.24,d-.24,.08),'earth','foundation','architecture')
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
        cap['lod_curve_spec']=json.dumps({'kind':'vault','x':0,'y0':-d/2,'y1':d/2,'spring':top,'rx':rx,'rise':rise,'thickness':.10,'origin':[x,y],'turn':turn})
        for s in (-1,1):
            out=[(-rx,top),(rx,top)]+[(rx*math.cos(j*math.pi/20),top+rise*math.sin(j*math.pi/20)) for j in range(1,20)]
            end=tag(R.extrude_xz(CURRENT+'_'+name+'_VaultEnd'+str(s),out,s*d/2-.04,s*d/2+.04,
                            'plaster',col('roofs'),'vaults',transform),'vaults','roofs',name)
            end['lod_curve_spec']=json.dumps({'kind':'end','x':0,'y0':s*d/2-.04,'y1':s*d/2+.04,'spring':top,'rx':rx,'rise':rise,'origin':[x,y],'turn':turn})
    else:
        cap=P('RoofBed',(0,0,top+.09),(w,d,.18))
        for s in (-1,1):
            P('ParapetSide'+str(s),(s*(w/2-.07),0,top+.26),(.14,d,.16),'plaster')
            P('ParapetEnd'+str(s),(0,s*(d/2-.07),top+.26),(w-.28,.14,.16),'plaster')
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

ENVELOPES={1:[[-3.95,-4.35,-.06],[3.95,4.05,4.45]],
           2:[[-4.10,-4.65,-.06],[4.10,4.45,5.50]],
           3:[[-4.10,-4.65,-.06],[4.10,4.45,5.50]],
           4:[[-4.20,-4.65,-.06],[4.20,4.55,7.40]]}
VIEW_CENTER=(0.,-.1,1.8)
VIEW_DISTANCE=15.
PROGRAMMES={1:'earthen lodging range, low guard room and open preparation lean-to',
            2:'three real vaulted lodging cells, masonry guard room and east equipment shelter',
            3:'long west lodging range joined to a taller rear guard hall; open infantry court',
            4:'broad lower lodging/preparation hall, west upper duty room, supported stair landing'}
PLAN={1: {'primary':(-.45,2.70,6.70,2.0,2.55),'doors':(-1.5,1.5)},
      2: {'primary':(0.,2.60,2.4,2.6,2.80),'doors':(0.,)},
      3: {'primary':(-2.1,.50,5.8,3.4,2.90),'doors':(-1.5,.5)},
      4: {'primary':(-.50,2.60,6.8,2.4,2.70),'doors':(1.0,2.6)}}

def first_room():
    p=PLAN[age()]
    room('Lodging',p['primary'],p['doors'],arched=(age()>=2),turn=(age()==3))
    print('FIRST_ROOM_DRAFT',CURRENT,'real lodging openings; roof not added')

def architecture():
    a=age()
    roof_room('Lodging','vault' if a==2 else 'flat')
    if a==1:
        room('GuardRoom',(2.70,-.90,1.8,2.2,2.35),(0.,));roof_room('GuardRoom')
        canopy('PreparationLean',-2.70,-.60,1.50,3.1,2.25,posts=2)
    elif a==2:
        # Three distinct rooms carry three vaulted roofs, with proper masonry
        # ends/bearings; this is a lodging range, not one stretched civic dome.
        for label,xx in [('WestCell',-2.4),('EastCell',2.4)]:
            room(label,(xx,2.60,2.4,2.6,2.80),(0.,),arched=True);roof_room(label,'vault')
        room('WestGuard',(-3.1,-.65,1.25,3.5,2.60),(0.,));roof_room('WestGuard')
        canopy('EastEquipment',2.80,-.80,1.45,3.2,2.40,posts=2)
    elif a==3:
        # The north end joins blank masonry, not a doorway hidden by the new wing.
        room('RearGuard',(1.60,2.95,4.0,2.1,3.48),(-1.0,1.0),arched=True);roof_room('RearGuard')
        canopy('CourtPreparation',2.65,-1.65,1.8,2.1,2.30,posts=2)
    else:
        room('EastGuard',(2.90,-.80,1.6,3.4,2.65),(0.,),arched=True);roof_room('EastGuard')
        upper_bottom=F+2.70+.18
        room('DutyRoom',(-1.80,2.60,2.6,2.4,2.60),(0.,),arched=True,bottom=upper_bottom)
        floor=ASSEMBLIES[CURRENT]['rooms']['DutyRoom']['floor']
        contact('DutyFloorOnLodgingRoof',floor,ASSEMBLIES[CURRENT]['rooms']['Lodging']['roof'])
        roof_room('DutyRoom')
        # Solid stair pod and upper landing are a purposeful military guard-room
        # access, not a hovering stone balcony. The stair enters an explicit gap.
        landing=wall('DutyLanding',-1.8,1.05,2.6,.70,upper_bottom-F,group='duty_access')
        count=18;start=-2.7;end=.70
        for j in range(count):
            h=(upper_bottom-F)*(j+1)/count;run=(end-start)/count
            step=B('DutyStair'+str(j),(-2.60,start+(j+.5)*run,F+h/2),(.8,run,h),
                   'stone','walls','architecture','duty_access')
            contact('DutyStairOnGround'+str(j),step,ASSEMBLIES[CURRENT]['ground'])
        # Landing parapets flank rather than block the stair/door route.
        wall('LandingLeftParapet',-3.04,1.05,.12,.70,.58,bottom=upper_bottom,group='duty_access')
        wall('LandingFrontParapet',-1.28,.76,1.56,.12,.58,bottom=upper_bottom,group='duty_access')
        wall('LandingRightParapet',-.56,1.05,.12,.70,.58,bottom=upper_bottom,group='duty_access')
    # Infantry court has a wide open front, unlike the secure caravanserai gate.
    left=wall('FrontBoundaryWest',-2.85,-3.95,1.9,.22,.65,group='training_court')
    right=wall('FrontBoundaryEast',2.85,-3.95,1.9,.22,.65,group='training_court')
    for i,p in enumerate((left,right)):contact('BoundaryOnGround'+str(i),p,ASSEMBLIES[CURRENT]['ground'])
    ANCHORS[CURRENT]['program']=PROGRAMMES[a]
    ANCHORS[CURRENT]['training_court']={'center':[0.,-1.6],'front_gap':[-1.90,1.90],'status':'visual source proposal, not pathfinding proof'}
    print('ARCHITECTURE_DRAFT',CURRENT,PROGRAMMES[a])

def _rack():
    poles=[]
    for i,xx in enumerate((2.05,3.05)):
        foot=B('RackFoot'+str(i),(xx,-3.25,F+.04),(.30,.45,.08),'timber','foundation','props','equipment_rack')
        pole=B('RackPost'+str(i),(xx,-3.25,F+.80),(.10,.10,1.44),'timber','finish','props','equipment_rack')
        contact('RackPostOnFoot'+str(i),pole,foot);poles.append(pole)
    rail=B('RackRail',(2.55,-3.25,F+1.57),(1.12,.12,.10),'timber','finish','props','equipment_rack')
    for i,pole in enumerate(poles):contact('RackRailOnPost'+str(i),rail,pole)
    for i,xx in enumerate((2.28,2.55,2.82)):
        board=B('TrainingBoard'+str(i),(xx,-3.32,F+1.14),(.20,.07,.76),'timber','finish','props','equipment_rack')
        contact('TrainingBoardOnRack'+str(i),board,rail,'top-bottom')
        # Original static training boards with small leather bindings, not a
        # copied native weapon/armour rig or a new combat model/animation.
        B('TrainingBoardBinding'+str(i),(xx,-3.365,F+1.14),(.22,.025,.08),'cloth','finish','props','equipment_rack')

def props():
    _rack()
    # Preparation bench is kept by an unoccupied court edge, with actual legs.
    x,y=-2.25,-3.25
    bench=B('PreparationBench',(x,y,F+.46),(1.55,.43,.10),'timber','finish','props','preparation')
    for i,xx in enumerate((x-.58,x+.58)):
        leg=B('BenchLeg'+str(i),(xx,y,F+.205),(.12,.32,.41),'timber','finish','props','preparation')
        contact('BenchTopOnLeg'+str(i),bench,leg);contact('BenchLegOnGround'+str(i),leg,ASSEMBLIES[CURRENT]['ground'])
    tag(R.lathe(CURRENT+'_WaterJar',(1.10,-2.80,F),[(.19,0),(.31,.16),(.32,.51),(.20,.68)],
                'pottery',col('props'),sides=16,stage='finish'),'finish','props','preparation')
    for i in range(2):
        B('EquipmentChest'+str(i),(.35+i*.68,-2.10,F+.18),(.58,.43,.36),'timber','finish','props','preparation')
    print('PROPS_DRAFT',CURRENT,'grounded infantry equipment and preparation, no soldiers/rigs')

def detail():
    a=age()
    if a==3:textile('InfantryOwner',1.6,1.86,F+3.12,1.3)
    elif a==4:textile('InfantryOwner',-1.8,1.37,F+4.85,1.3)
    else:textile('InfantryOwner',PLAN[a]['primary'][0],PLAN[a]['primary'][1]-PLAN[a]['primary'][3]/2-.04,F+2.40,1.3)
    # Wear is tied to entrance/training handling; not random all-over damage.
    for i in range(4):
        B('CourtTrafficWear'+str(i),(.10,-3.6+i*.65,F+.001),(.9,.53,.006),'grime','finish','wear','court_wear')
    for i in range(5):
        B('BeddedApproach'+str(i),(-.65,-3.5+i*.55,F+.025),(.58,.45,.05),'stone','foundation','ground','approach')
    # Small protected bins under the equipment canopy reinforce preparation.
    print('DETAIL_DRAFT',CURRENT,'owner textile, traffic wear and a clear useful court')



def build_lod(H,key,state,source,destination,lod,profile):
    import importlib.util
    spec=importlib.util.spec_from_file_location('persia_'+FAMILY+'_lods',ROOT/'lods.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build(H,key,state,source,destination,lod,profile)
