"""Original single-body timber yard; parent Blender qualification required."""
from pathlib import Path
import sys, math, json
import bpy
ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'lumber_camp')
BODY_KEYS=('A1',)
CURRENT='A1'
ANCHORS={}
CONTRACTS=[]
F=.12
P=.20
POST_TOP=2.70
BEAM_TOP=2.87
JOIST_TOP=2.95
GUIDE_BOTTOM=5.4765625
AXLE_Y=-.10693359375
AXLE_Z=2.097864985466003
AXLE_FACE=1.1689453125
INVENTORY=ROOT.parents[3]/'research/persia_buildings/inventory'
MODEL='art/civilizations/common/structures/lumber_camp/com_lumber_camp_crane_age01/com_lumber_camp_crane_age01'
NATIVE_DEPENDENCY={'model':MODEL+'.rgm','rgm_sha256':'55ad1d5227fc5d14355e6439b6bbf91695fbf1de913f6241b50b087f3997834b',
 'rrgeom_sha256':'d575467700cb88ecb8625358ef9b3c8afcdb65a74ad0c563a7ca8ecee9c96899',
 'rgo_sha256':'bc8497f934bfa6f284a85bf393c888d7e152cdd13fa3add43397795c95e8e5e2',
 'partition':str(INVENTORY/'LUMBER_FUNCTIONAL_SOURCE_PARTITION.json'),
 'functional_triangles':1604,'original_architecture_cap':1136,'stock_compound_cap':2740,
 'source_status':'Exact reference hierarchy/weights retained; native playback, physical pivots and working sweep unproved'}


def activate():R.configure(ROOT,'lumber_camp')
def root(key=None,state='healthy',lod=0):
 activate();return R.collection(R.PREFIX+(key or CURRENT)+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)
def col(role):return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,root())
def tag(o,stage,role,group):
 o['body_key']=CURRENT;o['construction_stage']=stage;o['role']=role;o['structural_group']=group
 o['source_status']='Original draft; parent generated checks and visual review required'
 return o
def B(name,xyz,size,surface='timber',stage='walls',role='architecture',group='shelter'):
 activate();return tag(R.block(CURRENT+'_'+name,xyz,size,surface,col(role),stage,role),stage,role,group)
def beam(name,a,b,width=.10,stage='walls',role='architecture',group='guide_frame'):
 activate();return tag(R.beam(CURRENT+'_'+name,a,b,width,'timber',col(role),stage,role),stage,role,group)
def obj(name):return bpy.data.objects[R.PREFIX+CURRENT+'_'+name]
def contact(name,a,b,axis='bottom-top',target=0,tolerance=.003):
 CONTRACTS.append(dict(body=CURRENT,name=name,a=a.name,b=b.name,axis=axis,target=target,tolerance=tolerance))
def interface(name,a,b,point,embed=0):
 ANCHORS[CURRENT]['numerical_interfaces'].append(dict(name=name,a=a.name,b=b.name,
  authored_space='model-space',authored_contact_point=list(point),intentional_socket_overlap_metres=embed,
  tolerance=.003,verification='Exact named surface/embedded joint; parent generated closed-solid check required'))


def foundation(key='A1'):
 global CURRENT
 if key not in BODY_KEYS:raise ValueError('Only the actual single A1 shared body')
 CURRENT=key;activate();s=R.setup_scene()
 if root().all_objects:raise ValueError('Owned body exists; no implicit cleanup')
 s['historical_basis']='Original functional timber yard in a Persian brick/earth/timber language; no recovered standard camp plan claimed'
 ANCHORS[key]=dict(authored_space='model-space',native_body_key=key,ground_top=F,work_floor_top=P,
  front_direction='-Y',numerical_interfaces=[],native_dependency=NATIVE_DEPENDENCY,
  raw_native_rest_bounds={'min':[-2.28125,-1.365234375,-2.4375],'max':[2.28125,4.28125,5.7265625]},
  working_clearances={'shelter_head_above_workfloor':POST_TOP-P,'bench_height':.70,'seat_height':.42,
   'approach_strip_y':[1.73,2.32],'payload_reference_zone_y':[3.056640625,4.28125],
   'wheel_reference_zone_y':[-1.33984375,1.2900390625],'working_sweep_qualified':False},
  native_bearing_candidates=[{'original_member':'AxleBearing'+str(side),'native_source_index':3 if side<0 else 0,
   'point':[side*AXLE_FACE,AXLE_Y,AXLE_Z],'meaning':'Exact closest native wheel surface point; proposed original bearing contact, not engine physical pivot'} for side in (-1,1)],
  native_guide_candidate={'original_member':'GuideLintel','point':[-.014007568359375,3.615234375,GUIDE_BOTTOM],
   'meaning':'Exact highest base-weighted cable vertex against original lintel underside; guide semantics/operating sweep require parent inspection'})
 outline=[(-2.18,-1.31),(1.94,-1.31),(2.18,-1.03),(2.18,4.12),(1.83,4.28125),(-1.91,4.28125),(-2.18,3.86)]
 n=len(outline);vs=[(x,y,z) for z in (-.03,F) for x,y in outline]
 tag(R.mesh(CURRENT+'_EarthBed',vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'earth',col('ground'),'foundation','ground'),'foundation','ground','plot')
 deck=B('WorkPlinth',(0,2.225,(F+P)/2),(4.14,1.51,P-F),'brick','foundation','ground','shelter')
 contact('WorkPlinthBed',deck,obj('EarthBed'))
 for side in (-1,1):
  x=side*(AXLE_FACE+.21)
  foot=B('AxleFoot'+str(side),(x,AXLE_Y,F+.04),(.50,.50,.08),'stone','foundation','ground','axle_frame')
  contact('AxleFootBed'+str(side),foot,obj('EarthBed'))
  foot=B('GuideFoot'+str(side),(side*1.93,3.615234375,F+.04),(.36,.44,.08),'stone','foundation','ground','guide_frame')
  contact('GuideFootBed'+str(side),foot,obj('EarthBed'))
  foot=B('GuideBraceFoot'+str(side),(side*1.93,2.40,P+.04),(.28,.36,.08),'stone','foundation','ground','guide_frame')
  contact('GuideBraceFootBed'+str(side),foot,deck)


def first_room():
 # The working bay remains open. A low masonry tool-store wind screen carries
 # no upper room and leaves the full 2.50m shelter head clearance visible.
 back=B('ToolStoreBack',(-1.10,2.91,P+.45),(1.50,.12,.90),'plaster','walls','architecture','tool_store')
 side=B('ToolStoreReturn',(-1.91,2.70,P+.45),(.12,.54,.90),'plaster','walls','architecture','tool_store')
 contact('ToolStoreBackBed',back,obj('WorkPlinth'));contact('ToolStoreReturnBed',side,obj('WorkPlinth'))
 contact('ToolStoreButtJoint',back,side,'left-right')


def architecture():
 for side in (-1,1):
  x=side*(AXLE_FACE+.21);bottom=P;top=AXLE_Z-.09
  post=B('AxlePier'+str(side),(x,AXLE_Y,(bottom+top)/2),(.24,.30,top-bottom),'brick','walls','architecture','axle_frame')
  contact('AxlePierFoot'+str(side),post,obj('AxleFoot'+str(side)))
  bearing=B('AxleBearing'+str(side),(x,AXLE_Y,AXLE_Z),(.42,.30,.18),'timber','walls','architecture','axle_frame')
  contact('AxleBearingPier'+str(side),bearing,post)
  post=B('GuidePost'+str(side),(side*1.93,3.615234375,(P+GUIDE_BOTTOM)/2),(.18,.22,GUIDE_BOTTOM-P),'timber','walls','architecture','guide_frame')
  contact('GuidePostFoot'+str(side),post,obj('GuideFoot'+str(side)))
  brace=beam('GuideRakingBrace'+str(side),(side*1.93,2.40,P+.04),(side*1.93,3.615234375,4.96),.12)
  interface('GuideBraceFootSeat'+str(side),brace,obj('GuideBraceFoot'+str(side)),(side*1.93,2.40,P+.04),.04)
  interface('GuideBracePostSeat'+str(side),brace,post,(side*1.93,3.615234375,4.96),.09)
 lintel=B('GuideLintel',(0,3.615234375,GUIDE_BOTTOM+.085),(4.10,.30,.17),'timber','vaults','architecture','guide_frame')
 for side in (-1,1):contact('GuideLintelPost'+str(side),lintel,obj('GuidePost'+str(side)))
 # Four full-height posts and two bearing beams carry a closed reed/earth roof.
 for x in (-1.88,1.88):
  for y in (1.60,2.86):
   post=B('ShelterPost'+str(x)+'_'+str(y),(x,y,(P+POST_TOP)/2),(.14,.14,POST_TOP-P))
   contact('ShelterPostPlinth'+str(x)+str(y),post,obj('WorkPlinth'))
 for label,y in [('Front',1.60),('Back',2.86)]:
  rail=B(label+'Bearing',(0,y,(POST_TOP+BEAM_TOP)/2),(4.04,.18,BEAM_TOP-POST_TOP))
  for x in (-1.88,1.88):contact(label+'BearingPost'+str(x),rail,obj('ShelterPost'+str(x)+'_'+str(y)))
 for j,x in enumerate((-1.87,-.62,.62,1.87)):
  joist=B('RoofJoist'+str(j),(x,2.23,(BEAM_TOP+JOIST_TOP)/2),(.085,1.64,JOIST_TOP-BEAM_TOP),'timber','vaults','architecture','shelter')
  for label in ('Front','Back'):contact('Joist'+str(j)+label,joist,obj(label+'Bearing'))
 reed=B('ReedRoof',(0,2.23,JOIST_TOP+.02),(4.20,1.62,.04),'cloth','vaults','roofs','shelter')
 for j in range(4):contact('ReedJoist'+str(j),reed,obj('RoofJoist'+str(j)))
 earth=B('EarthRoof',(0,2.23,JOIST_TOP+.065),(4.20,1.62,.05),'roof','vaults','roofs','shelter')
 contact('EarthRoofReed',earth,reed)
 # Four actual embedded knee joints, no decorative floating brackets.
 for x in (-1.88,1.88):
  for label,y in [('Front',1.60),('Back',2.86)]:
   inward=-1 if x>0 else 1
   q=beam('Knee'+str(x)+label,(x,y,POST_TOP-.34),(x+inward*.35,y,POST_TOP+.035),.10,group='shelter')
   interface('KneePost'+str(x)+label,q,obj('ShelterPost'+str(x)+'_'+str(y)),(x,y,POST_TOP-.34),.07)
   interface('KneeRail'+str(x)+label,q,obj(label+'Bearing'),(x+inward*.35,y,POST_TOP+.035),.035)


def workbench(name,x):
 y=2.55;w=.86;d=.40;top=P+.70;th=.06
 slab=B(name+'Top',(x,y,top-th/2),(w,d,th),'timber','finish','props','workbenches')
 for sx in (-1,1):
  for sy in (-1,1):
   leg=B(name+'Leg'+str(sx)+str(sy),(x+sx*(w/2-.065),y+sy*(d/2-.055),(P+top-th)/2),(.07,.07,top-th-P),'timber','finish','props','workbenches')
   contact(name+'LegTop'+str(sx)+str(sy),leg,slab,'top-bottom');contact(name+'LegFloor'+str(sx)+str(sy),leg,obj('WorkPlinth'))
 rail=B(name+'Stretcher',(x,y-d/2+.055,P+.22),(w-.13,.05,.055),'timber','finish','props','workbenches')
 for sx in (-1,1):interface(name+'StretcherSeat'+str(sx),rail,obj(name+'Leg'+str(sx)+'-1'),(x+sx*(w/2-.065),y-d/2+.055,P+.22),.035)
 return slab


def log(name,x,y,z,length,radius):
 sides=6
 # Flat bottom is z-radius*cos(pi/6); center is derived from the cradle top.
 points=[(math.cos(math.pi/6+j*math.tau/sides),math.sin(math.pi/6+j*math.tau/sides)) for j in range(sides)]
 vs=[(xx,y+radius*c,z+radius*s) for xx in (x-length/2,x+length/2) for c,s in points]
 faces=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(j,(j+1)%sides,(j+1)%sides+sides,j+sides) for j in range(sides)]
 return tag(R.mesh(CURRENT+'_'+name,vs,faces,'timber',col('props'),'finish','props'),'finish','props','log_intake')


def props():
 for j,x in enumerate((-1.15,0,1.15)):
  top=workbench('Bench'+str(j),x)
  if j!=1:
   stock=B('BenchStock'+str(j),(x,2.55,P+.735),(.55,.13,.07),'timber','finish','props','workbenches');contact('BenchStockTop'+str(j),stock,top)
 for j,x in enumerate((-1.15,1.15)):
  seat=B('StoolSeat'+str(j),(x,1.97,P+.395),(.28,.28,.05),'timber','finish','props','seating')
  for side in (-1,1):
   leg=B('StoolTrestle'+str(j)+str(side),(x+side*.09,1.97,P+.185),(.055,.22,.37),'timber','finish','props','seating')
   contact('StoolSeatLeg'+str(j)+str(side),leg,seat,'top-bottom');contact('StoolLegBed'+str(j)+str(side),leg,obj('WorkPlinth'))
 cradles=[]
 for x in (-1.10,1.10):
  q=B('LogCradle'+str(x),(x,-.72,F+.05),(.14,.77,.10),'timber','finish','props','log_intake');contact('LogCradleBed'+str(x),q,obj('EarthBed'));cradles.append(q)
 for j,y in enumerate((-.98,-.72,-.46)):
  q=log('IncomingLog'+str(j),0,y,F+.20,3.12,.10)
  for k,c in enumerate(cradles):contact('IncomingLogCradle'+str(j)+str(k),q,c)
 bearers=[]
 for y in (.28,1.05):
  q=B('BoardBearer'+str(y),(1.71,y,F+.04),(.65,.14,.08),'timber','finish','props','processed_stock');contact('BoardBearerBed'+str(y),q,obj('EarthBed'));bearers.append(q)
 previous=[]
 for level in range(2):
  layer=[]
  for j in range(3):
   q=B('Board'+str(level)+'_'+str(j),(1.47+j*.24,.665,F+.115+level*.07),(.22,1.20,.07),'timber','finish','props','processed_stock')
   if level==0:
    for k,b in enumerate(bearers):contact('BoardBearerSeat'+str(j)+str(k),q,b)
   else:contact('BoardStack'+str(j),q,previous[j])
   layer.append(q)
  previous=layer
 bracket=B('OwnerBracket',(1.10,1.49,POST_TOP+.05),(.68,.10,.06),'timber','finish','fittings','owner')
 interface('OwnerBracketFrontBeam',bracket,obj('FrontBearing'),(1.10,1.53,POST_TOP+.05),.02)
 cloth=B('OwnerCloth',(1.10,1.46,POST_TOP-.195),(.55,.025,.43),'owner','finish','owner','owner');contact('OwnerClothBracket',cloth,bracket,'top-bottom')


def detail():
 for j,x in enumerate((-1.15,0,1.15)):
  q=B('BenchScuff'+str(j),(x,2.55,P+.7015),(.36,.16,.003),'grime','finish','wear','workbenches');contact('ScuffOnBench'+str(j),q,obj('Bench'+str(j)+'Top'))


def show(key='A1',state='healthy',lod=0):
 activate();s=bpy.data.scenes[R.SCENE]
 for c in s.collection.children:
  if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
 bpy.context.window.scene=s


def build_body(key='A1'):
 foundation(key);first_room();architecture();props();detail()
 original=[o for o in root(key).all_objects if o.type=='MESH']
 count=sum(len(p.vertices)-2 for o in original for p in o.data.polygons)
 if count>1136:raise RuntimeError('Original Lumber architecture exceeds1136 triangles: '+str(count))
 ANCHORS[key]['original_architecture_triangles']=count
 import native_lumber_sources as L
 ANCHORS[key]['native_active_assembly']=L.attach(self_module(),key)
 show(key)


def self_module():return sys.modules[__name__]
def qualify_native_mesh(ob):
    import native_lumber_sources as L
    if ob.get('native_derived_LOD'):
        import importlib.util
        spec=importlib.util.spec_from_file_location('lumber_saved_wheel_audit',ROOT/'wheel_lods.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module.audit_saved_subset(ob)
    role='skin' if ob.get('native_lumber_role')=='skin' else 'rigid'
    exact=L.audit_exact(ob,role,None if role=='skin' else int(ob['native_lumber_source_index']))
    return {'passed':True,'actual_native_source_audit':exact,'native_playback_qualified':False}


def qualify_native_modifier(ob):
    """Only the untouched weighted cable SKMS admits a live native modifier."""
    import native_lumber_sources as L
    import native_mechanisms as N
    L.require(ob.get('retained_native_dependency') and ob.get('native_lumber_role')=='skin',
              'Only the exact retained Lumber skin is qualified')
    L.require(len(ob.modifiers)==1 and ob.modifiers[0].type=='ARMATURE','Unexpected modifier stack')
    modifier=ob.modifiers[0];arm=modifier.object
    L.require(arm and arm.type=='ARMATURE' and arm.get('native_lumber_reference_root'),'Missing retained reference armature')
    L.require(modifier.show_viewport and modifier.show_render and modifier.use_vertex_groups and not modifier.use_bone_envelopes,
              'Native modifier evaluation flags changed')
    L.require(not arm.animation_data and not arm.constraints,'Unexpected live rig action/constraint')
    L.require(all(not bone.constraints and all(abs(bone.matrix_basis[r][c]-float(r==c))<1e-7
        for r in range(4) for c in range(4)) for bone in arm.pose.bones),'Native skin reference pose changed')
    L.require(all(abs(arm.matrix_world[r][c]-float(r==c))<1e-7 for r in range(4) for c in range(4)),
              'Native skin armature whole transform changed')
    exact=L.audit_exact(ob,'skin');bones=N.audit_reference_bones(L.TARGET,arm.name)
    L.require(all(b['public_reference_projection_matches'] and b['actual_parent']==b['expected_parent'] for b in bones['bones']),
              'Native skin reference hierarchy changed')
    return {'passed':True,'route':'Exact native SKMS topology, positions, UV, material, normals and weights; unposed original reference forest',
        'source_audit':exact,'reference_bones':bones,'native_playback_qualified':False,'modifier_baked':False}


def build_lod(H,key,state,source,destination,lod,profile):
 import importlib.util
 spec=importlib.util.spec_from_file_location('persia_lumber_lods',ROOT/'lods.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module.build(H,key,state,source,destination,lod,profile)
def write_anchors():
 (ROOT/'evidence').mkdir(parents=True,exist_ok=True)
 (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n')
 (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n')
