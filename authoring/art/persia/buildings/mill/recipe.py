"""Original Persian grain compound. Single unbuilt healthy-source draft."""
from pathlib import Path
import sys,math,json
import bpy

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'mill')
BODY_KEYS=('A1',)
CURRENT='A1'
ANCHORS={}
CONTRACTS=[]
F=.12
P=.24
STORE=(-1.00,.67,2.36,2.36)
SPRING=P+2.10
INVENTORY=ROOT.parents[3]/'research/persia_buildings/inventory'
MODEL='art/civilizations/chinese/structures/gristmill/chi_gristmill_control_age01/chi_gristmill_control_age01'
NATIVE_DEPENDENCY={
    'model':MODEL+'.rgm','native_rgm':str(INVENTORY/'native'/(MODEL+'.rgm')),
    'native_rrgeom':str(INVENTORY/'native'/(MODEL+'.rrgeom')),
    'native_rgo':str(INVENTORY/'native'/(MODEL+'.rgo')),
    'rgm_sha256':'ad48c681f820bf851123aab9aaa9b32b019d5d9bfc855bcf68b0b01037252fee',
    'rrgeom_sha256':'787b0946099a1c9801c6df72905c5651311d57badb3f3eb18958d5d78f7fed8e',
    'rgo_sha256':'fe4c1ce2daa540114896f144a5b05a6330faebdcc6fec414874a0544f4f2cf91',
    'rigid_reference_contract':str(INVENTORY/'RIGID_MECHANISM_BINDINGS.json'),
    'import_method_contract':str(INVENTORY/'MECHANISM_IMPORT_HANDOFF.md'),
    'bone_parent_names':{'bone_root':None,'bone_4quaternary':'bone_root','bone_3tertiary':'bone_root','bone_2secondary':'bone_root','bone_1primary':'bone_root'},
    'status':'Retain compatible native collapse/reference hierarchy and owners. No operating rotor, grinding clip, new rig or playback is established or supplied.',
}
REFERENCE_ENVELOPES={
    'whole_native_body':{'min':[-2.4140625,-2.26171875,-.88134765625],'max':[4.265625,2.26171875,6.35546875]},
    'bone_1primary_sources':{'min':[-2.4140625,-2.17578125,-.00000017881393432617188],'max':[2.4140625,2.17578125,6.18359375]},
    'bone_2secondary_sources':{'min':[1.0576171875,-.56494140625,.353759765625],'max':[3.021484375,.61572265625,1.53515625]},
    'bone_3tertiary_sources':{'min':[2.861328125,-.45458984375,.317626953125],'max':[3.935546875,.6201171875,.8017578125]},
    'bone_4quaternary_sources':{'min':[2.732421875,.517578125,.319580078125],'max':[3.908203125,1.69140625,1.0205078125]},
}

def activate():R.configure(ROOT,'mill')

def root(key=None,state='healthy',lod=0):
    activate()
    return R.collection(R.PREFIX+(key or CURRENT)+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)

def col(role):return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,root())

def tag(o,stage,role,group):
    o['body_key']=CURRENT;o['construction_stage']=stage;o['role']=role;o['structural_group']=group
    o['draft_status']='Unbuilt recipe; parent source/rig verification required'
    return o

def B(name,xyz,size,surface='brick',stage='walls',role='architecture',group='grain_store'):
    activate()
    return tag(R.block(CURRENT+'_'+name,xyz,size,surface,col(role),stage,role),stage,role,group)

def beam(name,a,b,width=.07,stage='walls',role='architecture',group='grain_porch'):
    activate()
    return tag(R.beam(CURRENT+'_'+name,a,b,width,'timber',col(role),stage,role),stage,role,group)

def obj(name):return bpy.data.objects[R.PREFIX+CURRENT+'_'+name]

def contact(name,a,b,axis='bottom-top',target=0,tolerance=.003):
    CONTRACTS.append({'body':CURRENT,'name':name,'a':a.name,'b':b.name,'axis':axis,'target':target,'tolerance':tolerance})

def interface(name,a,b,point,overlap=.025):
    ANCHORS[CURRENT]['numerical_interfaces'].append({'name':name,'a':a.name,'b':b.name,'authored_contact_point':list(point),'intentional_socket_overlap_metres':overlap,'verification':'Contact plan; parent must inspect the actual generated interface, not only its bounding boxes.'})

def foundation(key='A1'):
    global CURRENT
    if key not in BODY_KEYS:raise ValueError('Only one existing shared Mill body is authorized')
    CURRENT=key;activate();R.setup_scene()
    if root().all_objects:raise ValueError('Owned body exists; inspect before an explicit parent reset')
    ANCHORS[key]={'authored_space':'model-space','native_body_key':key,'ground_top':F,'work_floor_top':P,'vault_spring':SPRING,'front_direction':'-Y','numerical_interfaces':[],
        'chosen_horizontal_bounds':[[-2.25,-2.12],[4.08,2.12]],
        'native_reference_envelopes':REFERENCE_ENVELOPES,
        'native_reference_envelope_meaning':'Measured donor collapse/reference source envelopes, not operational keepouts and not world poses. Do not retain the whole Chinese shell as a mechanism.',
        'native_operating_rotor_requirement':None,'native_dependency':NATIVE_DEPENDENCY,
        'clear_work_approach':{'x_interval':[.36,3.75],'y_interval':[-1.72,-.67],'minimum_depth':1.05},
        'native_stamp_matrix_row_major':[[-1,0,0,.8513259887695312],[0,-1,0,-.02334900014102459],[0,0,1,0],[0,0,0,1]],
        'native_stamp_status':'Exact retained static transform; apply once after source fit. Bone/reference projection remains a separate gate.'}
    outline=[(-2.17,-2.06),(-.31,-2.12),(3.92,-2.02),(4.08,-1.37),(4.04,1.92),(3.46,2.12),(-1.82,2.04),(-2.25,1.44)]
    n=len(outline);vs=[(x,y,z) for z in (-.03,F) for x,y in outline]
    tag(R.mesh(CURRENT+'_EarthBed',vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'earth',col('ground'),'foundation','ground'),'foundation','ground','plot')
    for name,center,size in [('StorePlinth',(-1,.67,(F+P)/2),(2.48,2.48,P-F)),('PorchPlinth',(2.05,.67,(F+P)/2),(3.64,2.48,P-F))]:
        slab=B(name,center,size,'stone','foundation','ground','grain_store' if name=='StorePlinth' else 'grain_porch');contact(name+'Bed',slab,obj('EarthBed'))
    apron=B('GrainApron',(2.05,-1.39,F+.025),(3.66,.96,.05),'earth','foundation','ground','grain_apron');contact('GrainApronBed',apron,obj('EarthBed'))

def first_room():
    x,y,w,d=STORE;t=.22;h=SPRING-P;front=y-d/2
    B('StoreWest',(x-w/2+t/2,y+t/2,P+h/2),(t,d-t,h),'plaster')
    B('StoreEast',(x+w/2-t/2,y+t/2,P+h/2),(t,d-t,h),'plaster')
    B('StoreBack',(x,y+d/2-t/2,P+h/2),(w-2*t,t,h),'brick')
    arch=tag(R.archwall(CURRENT+'_StoreDoorArch',x,front,front+t,P,w,h,.82,1.55,.43,'brick',col('architecture'),segments=14),'walls','architecture','grain_store')
    sill=B('StoreThreshold',(x,front+.07,P+.035),(.96,.34,.07),'stone','foundation','ground','grain_store');contact('ThresholdPlinth',sill,obj('StorePlinth'))
    door_profile=[(x-.365,P+.07),(x+.365,P+.07)]+[(x+.365*math.cos(j*math.pi/14),P+1.53+.38*math.sin(j*math.pi/14)) for j in range(15)]
    door=tag(R.extrude_xz(CURRENT+'_GrainDoorLeaf',door_profile,front+.1475,front+.1925,'timber',col('fittings'),'finish',role='fittings'),'finish','fittings','grain_store');contact('DoorThreshold',door,sill)
    for z in (P+.43,P+1.48):B('DoorCrossRail'+str(z),(x,front+.14,z),(.69,.025,.055),'timber','finish','fittings','grain_store')
    ANCHORS[CURRENT]['store_door']={'clear_width':.82,'arch_top_above_floor':1.98,'front_y':front,'leaf_recess':.17,'closed_healthy_store':'No opening animation claimed'}

def architecture():
    x,y,w,d=STORE
    vault=tag(R.vault(CURRENT+'_GrainStoreVault',x,y-d/2-.015,y+d/2+.015,SPRING,1.065,.53,.12,'roof',col('roofs'),segments=18,along=3,stage='vaults'),'vaults','roofs','grain_store')
    contact('VaultWestWall',vault,obj('StoreWest'));contact('VaultEastWall',vault,obj('StoreEast'))
    outline=[(x-1.065,SPRING),(x+1.065,SPRING)]+[(x+1.065*math.cos(j*math.pi/18),SPRING+.53*math.sin(j*math.pi/18)) for j in range(1,18)]
    for label,yy,base in [('Front',y-d/2+.04,'StoreDoorArch'),('Back',y+d/2-.10,'StoreBack')]:
        end=tag(R.extrude_xz(CURRENT+'_VaultEnd'+label,outline,yy,yy+.08,'brick',col('architecture'),'vaults',role='architecture'),'vaults','architecture','grain_store');contact('VaultEndBearing'+label,end,obj(base))
    posttop=2.19;beamtop=2.34;joisttop=2.43;posts={};rails=[]
    for xx in (.48,2.05,3.62):
        for yy in (-.32,1.66):
            post=B('PorchPost'+str(xx)+str(yy),(xx,yy,(P+posttop)/2),(.13,.13,posttop-P),'timber','walls','architecture','grain_porch');contact('PorchPostFoot'+str(xx)+str(yy),post,obj('PorchPlinth'));posts[(xx,yy)]=post
    for yy in (-.32,1.66):
        rail=B('PorchBearing'+str(yy),(2.05,yy,(posttop+beamtop)/2),(3.49,.17,beamtop-posttop),'timber','walls','architecture','grain_porch')
        for xx in (.48,2.05,3.62):contact('PorchRailPost'+str(xx)+str(yy),rail,posts[(xx,yy)])
        rails.append(rail)
    joists=[]
    for j in range(8):
        joist=B('PorchJoist'+str(j),(.42+j*.465,.67,(beamtop+joisttop)/2),(.07,2.34,joisttop-beamtop),'timber','vaults','fittings','grain_porch')
        for k,rail in enumerate(rails):contact('PorchJoistBearing'+str(j)+str(k),joist,rail)
        joists.append(joist)
    reed=B('PorchReedDeck',(2.05,.67,joisttop+.025),(3.78,2.52,.05),'cloth','vaults','roofs','grain_porch')
    for j,joist in enumerate(joists):contact('PorchReedBearing'+str(j),reed,joist)
    clay=B('PorchEarthCap',(2.05,.67,joisttop+.08),(3.78,2.52,.06),'roof','vaults','roofs','grain_porch');contact('PorchEarthReed',clay,reed)
    for xx in (.48,3.62):
        sign=1 if xx<2 else -1
        brace=beam('PorchKnee'+str(xx),(xx,-.32,posttop-.37),(xx+sign*.37,-.32,posttop+.025),.065)
        interface('PorchKneePost'+str(xx),brace,posts[(xx,-.32)],(xx,-.32,posttop-.37),.065)
        interface('PorchKneeRail'+str(xx),brace,rails[0],(xx+sign*.37,-.32,posttop+.025))
    ANCHORS[CURRENT]['porch_clear_head']=posttop-P

def round_piece(name,x,y,z,rings,surface='stone',group='quern',sides=18):
    q=tag(R.lathe(CURRENT+'_'+name,(x,y,z),rings,surface,col('props'),sides=sides,stage='finish',role='props'),'finish','props',group)
    q['lod_lathe_spec']=json.dumps({'center':[x,y,z],'rings':rings,'surface':surface,'sides':sides})
    return q

def quern():
    x=1.15;y=.64;pedestal=B('QuernPedestal',(x,y,P+.23),(.83,.83,.46),'brick','walls','props','quern');contact('QuernPedestalFloor',pedestal,obj('PorchPlinth'))
    seat=B('QuernBearingSlab',(x,y,P+.50),(.91,.91,.08),'stone','finish','props','quern');contact('QuernSlabPedestal',seat,pedestal)
    lower=round_piece('LowerQuernStone',x,y,P+.54,[(.36,0),(.39,.08),(.36,.16)]);contact('LowerStoneSeat',lower,seat)
    # Closed annular upper stone: real feed eye, no opaque cylinder pretending to be a hole.
    rings=[(.34,P+.70),(.35,P+.79),(.075,P+.79),(.075,P+.70)];sides=18;vs=[(x+r*math.cos(j*2*math.pi/sides),y+r*math.sin(j*2*math.pi/sides),z) for r,z in rings for j in range(sides)];faces=[]
    for k in range(4):
        for j in range(sides):a=k*sides+j;b=k*sides+(j+1)%sides;c=((k+1)%4)*sides+(j+1)%sides;d=((k+1)%4)*sides+j;faces.append((a,b,c,d))
    upper=tag(R.mesh(CURRENT+'_UpperQuernStone',vs,faces,'stone',col('props'),'finish','props'),'finish','props','quern');contact('UpperLowerStoneBearing',upper,lower)
    upper['lod_annulus_spec']=json.dumps({'center_xy':[x,y],'rings_radius_z':rings,'surface':'stone'})
    handle=B('QuernHandPeg',(x+.245,y,P+.90),(.05,.05,.22),'timber','finish','props','quern');contact('QuernPegStone',handle,upper)
    ANCHORS[CURRENT]['quern']={'center':[x,y],'feed_eye_radius':.075,'lower_stone_top':P+.70,'upper_stone_top':P+.79,'handle_top':P+1.01,'operating_space':{'x_interval':[.55,1.75],'y_interval':[-.16,1.42]},'motion':'Static hand-quern function cue only; no new or inherited rotation clip claimed'}

def cleaning_bench():
    x=2.97;y=.52;top=P+.72;th=.075;underside=top-th
    slab=B('CleaningBenchTop',(x,y,top-th/2),(1.02,.60,th),'timber','finish','props','cleaning_bench')
    for sx in (-1,1):
        for sy in (-1,1):
            leg=B('CleaningLeg'+str(sx)+str(sy),(x+sx*.40,y+sy*.20,(P+underside)/2),(.085,.085,underside-P),'timber','finish','props','cleaning_bench');contact('CleaningLegTop'+str(sx)+str(sy),leg,slab,'top-bottom');contact('CleaningLegFoot'+str(sx)+str(sy),leg,obj('PorchPlinth'))
    sieve=B('SieveBed',(x,y,top+.0125),(.76,.43,.025),'cloth','finish','props','cleaning_bench');contact('SieveBenchSeat',sieve,slab)
    for sx in (-1,1):
        rim=B('SieveEnd'+str(sx),(x+sx*.365,y,top+.0625),(.03,.43,.075),'timber','finish','props','cleaning_bench');contact('SieveEndSeat'+str(sx),rim,sieve)
    for sy in (-1,1):
        rim=B('SieveSide'+str(sy),(x,y+sy*.20,top+.0625),(.70,.03,.075),'timber','finish','props','cleaning_bench');contact('SieveSideSeat'+str(sy),rim,sieve)
    ANCHORS[CURRENT]['cleaning_bench']={'top_above_floor':.72,'front_work_y':-.02,'clear_approach_y_interval':[-.64,-.02]}

def grain_bin(name,x,y,w=.77,d=.62):
    base=B(name+'Base',(x,y,P+.035),(w,d,.07),'timber','finish','props','grain_bins');contact(name+'BaseFloor',base,obj('PorchPlinth'))
    for side in (-1,1):
        wall=B(name+'Side'+str(side),(x+side*(w/2-.045),y,P+.32),(.09,d,.50),'brick','finish','props','grain_bins');contact(name+'SideFloor'+str(side),wall,base)
    for side in (-1,1):
        wall=B(name+'End'+str(side),(x,y+side*(d/2-.045),P+.32),(w-.18,.09,.50),'plaster','finish','props','grain_bins');contact(name+'EndFloor'+str(side),wall,base)
    fill=B(name+'Grain',(x,y,P+.14),(w-.20,d-.20,.14),'earth','finish','props','grain_bins');contact(name+'GrainBed',fill,base)

def props():
    quern();cleaning_bench()
    for j,x in enumerate((2.59,3.44)):grain_bin('GrainBin'+str(j),x,1.20)
    # Small stone-supported drying mat leaves a broad loading route in front of the porch.
    drying=B('DryingPlatform',(2.97,-1.43,F+.075),(1.24,.58,.15),'stone','foundation','ground','grain_apron');contact('DryingPlatformBed',drying,obj('EarthBed'))
    mat=B('DryingMat',(2.97,-1.43,F+.161),(1.15,.50,.022),'cloth','finish','props','grain_apron');contact('DryingMatPlatform',mat,drying)
    for j,x in enumerate((2.65,2.97,3.29)):
        heap=round_piece('GrainPortion'+str(j),x,-1.43,F+.172,[(.12,0),(.14,.035),(.04,.11)],'earth','grain_apron',sides=10);contact('GrainPortionMat'+str(j),heap,mat)
    # Grounded grain sacks beside the store, with a distinct short neck profile.
    for j,y in enumerate((.96,1.40)):
        sack=round_piece('StoredSack'+str(j),-1.57,y,P,[(.16,0),(.25,.11),(.22,.40),(.10,.47),(.07,.51)],'cloth','grain_store',sides=12);contact('SackStoreFloor'+str(j),sack,obj('StorePlinth'))
    bracket=B('OwnerBracket',(.90,-.43,2.24),(.38,.08,.06),'timber','finish','fittings','owner')
    cloth=B('OwnerCloth',(.90,-.47,2.085),(.28,.025,.25),'owner','finish','owner','owner');contact('OwnerClothBracket',cloth,bracket,'top-bottom')
    interface('OwnerBracketBearing',bracket,obj('PorchBearing-0.32'),(.90,-.395,2.24),.02)

def detail():
    # Wear is localized at grain handling/stone grinding/thresholds rather than scattered.
    for j in range(4):B('StoreApproachPaver'+str(j),(-1.00,-1.77+j*.30,F+.025),(.67,.27,.05),'stone','foundation','ground','grain_store')
    for j in range(2):B('QuernFlourDust'+str(j),(.94+j*.27,.17,P+.002),(.27,.22,.004),'paper','finish','wear','quern')
    B('CleaningBenchScuff',(2.97,.52,P+.721),(.46,.24,.002),'grime','finish','wear','cleaning_bench')
    for j,x in enumerate((2.59,3.44)):B('BinTraffic'+str(j),(x,.80,P+.002),(.45,.22,.004),'earth','finish','wear','grain_bins')
    x,y,w,d=STORE
    for side in (-1,1):
        for j in range(5):B('StoreBaseRepair'+str(side)+str(j),(x+side*(w/2+.007),y-.88+j*.43,P+.12),(.025,.29,.20),'brick','finish','fine_detail','grain_store')
    # Laid exterior vault brickwork, each course independently editable. The
    # inner face beds into the structural vault; narrow mortar reveals expose
    # the original roof surface. This is masonry construction, not extra bays.
    for row in range(8):
        y0=y-d/2+row*d/8+.006;y1=y-d/2+(row+1)*d/8-.006
        for segment in range(18):
            a=segment*math.pi/18+.003;b=(segment+1)*math.pi/18-.003
            q=tag(R.vault(CURRENT+'_VaultBond_'+str(row)+'_'+str(segment),x,y0,y1,SPRING,
                1.180,.645,.025,'brick',col('details'),segments=1,along=1,
                angle0=a,angle1=b,stage='vaults'),'vaults','fine_detail','grain_store')
            q['mill_vault_bond_row']=row;q['mill_vault_bond_segment']=segment
            q['detail_basis']='Original laid brick course over bedded barrel vault; eight longitudinal courses, eighteen voussoir units across each course'
            center=((x+1.185*math.cos(segment*math.pi/18)+x+1.185*math.cos((segment+1)*math.pi/18))/2,
                    (y0+y1)/2,SPRING+.65*(math.sin(segment*math.pi/18)+math.sin((segment+1)*math.pi/18))/2)
            interface('VaultBondSeat_'+str(row)+'_'+str(segment),q,obj('GrainStoreVault'),center,.012)

def build_lod(H,key,state,source,destination,level,profile):
    import importlib.util
    spec=importlib.util.spec_from_file_location('persia_mill_lods',ROOT/'lods.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)

def show(key='A1',state='healthy',lod=0):
    activate();s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s

def build_body(key='A1'):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_REQUIRES_PARENT_VERIFICATION',key)

def write_anchors():
    (ROOT/'evidence').mkdir(parents=True,exist_ok=True)
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n')
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n')
