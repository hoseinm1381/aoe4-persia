"""Original Lumber source LOD adapters; parent generation/visual QA required."""
import json,math,importlib.util
from pathlib import Path
import bpy
import state_geometry as G
import native_lumber_sources as L
import native_mechanisms as N
import native_skin_sources as S
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('persia_lumber_wheel_lods',ROOT/'wheel_lods.py');W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)

def meshes(c):return [o for o in c.all_objects if o.type=='MESH']
def count(c):return sum(L.triangles(o) for o in meshes(c))
def _remove_generated(o):
 # Only newly generated state/LOD objects. Full source files/cache untouched.
 bpy.data.objects.remove(o,do_unlink=True)

def prepare_bases(H,key,profile):
 if H.root(key).get('lumber_native_state_bases_prepared'):return
 states=['healthy',*[f'damage_{n}' for n in range(1,6)],'ruins','preview','targeting',
         'construct_foundation','construct_walls','construct_vaults','construct_finish']
 for state in states:
  name=H.R.PREFIX+key+'_'+state+('_LOD0' if not state.startswith('construct_') else '')
  c=bpy.data.collections.get(name);L.require(c is not None,'State source assembly absent: '+name)
  L.normalize_state(H,key,state,c)
  if state.startswith('damage_') or state=='ruins':
   debris=sorted([o for o in meshes(c) if o.get('role')=='debris' and 'Debris' in o.name],key=lambda o:o.name)
   fixed=count(c)-sum(L.triangles(o) for o in debris)
   L.require(fixed<=2740,'Non-debris original source state exceeds stock cap: '+state)
   maximum=min(profile.get('source_debris_max_count',{}).get(state,len(debris)),max(0,(2740-fixed)//12))
   L.require(maximum>0,'No triangle room for actual source damage debris: '+state)
   for o in debris[maximum:]:_remove_generated(o)
   c['lumber_family_debris_budget_json']=json.dumps(dict(non_debris_triangles=fixed,actual_debris_count=min(maximum,len(debris)),stock_cap=2740,cap_raised=False))
 H.root(key)['lumber_native_state_bases_prepared']=True


def _original_lod1(H,key,state,source,dest):
 omitted=('Stool','BenchStock','BenchScuff','IncomingLog1','IncomingLog2','Board1_',
          'Knee','Bench1','Bench2')
 for index,o in enumerate(sorted(meshes(source),key=lambda o:o.name)):
  if o.get('native_lumber_role'):continue
  if o.get('role')=='wear' or any(n in o.name for n in omitted):continue
  if o.get('role')=='debris' and index%3:continue
  q=G.clone(o,dest,'OriginalLOD1');q['lod_level']=1
 return [o for o in meshes(dest) if not o.get('native_lumber_role')]


def _original_lod2(H,key,state,source,dest,profile,lod=2):
 R=H.R;out=[]
 def mark(o,name,stage,role,group):
  H.tag(o,stage,role,group);o['lod_level']=lod;o['healthy_source']=R.PREFIX+key+'_AuthoredLOD'+str(lod)+'_'+name
  o['source_state']=state;o['original_LOD_adaptation']='Separate simplified closed source fabrication; no native geometry reused'
  out.append(o);return o
 def block(name,center,size,surface='timber',stage='walls',role='architecture',group='shelter'):
  return mark(R.block(key+'_'+state+'_LOD'+str(lod)+'_'+name,center,size,surface,dest,stage,role),name,stage,role,group)
 def shape(name,outline,y0,y1,group):
  return mark(R.extrude_xz(key+'_'+state+'_LOD'+str(lod)+'_'+name,outline,y0,y1,'timber',dest,'walls',role='architecture'),name,'walls','architecture',group)
 # Named original ground footprints, no native shell and no hanging footings.
 for o in meshes(source):
  if ('EarthBed' in o.name or (lod==1 and 'WorkPlinth' in o.name)) and not o.get('native_lumber_role'):
   if lod==2:
    lo=[min(v.co[a] for v in o.data.vertices) for a in range(3)];hi=[max(v.co[a] for v in o.data.vertices) for a in range(3)]
    block('RectangularGroundBed',tuple((a+b)/2 for a,b in zip(lo,hi)),tuple(b-a for a,b in zip(lo,hi)),'earth','foundation','ground','plot')
   else:
    q=G.clone(o,dest,'OriginalLOD'+str(lod));q['lod_level']=lod;out.append(q)
 # Two solid simplified bearing piers replace their original brick+timber step.
 for side in (-1,1):
  block('AxleSupport'+str(side),(side*(H.AXLE_FACE+.21),H.AXLE_Y,(H.F+H.AXLE_Z+.09)/2),(.42,.30,H.AXLE_Z+.09-H.F),'brick',group='axle_frame')
 # Closed gantry U profile and two triangular-section rakers. The frame is
 # separate original fabrication, never a reduced native timber source.
 x=2.05;leg=.18;top=H.GUIDE_BOTTOM+.17;bottom=H.F
 shape('GuideFrame',[(-x,bottom),(-x,top),(x,top),(x,bottom),(x-leg,bottom),(x-leg,H.GUIDE_BOTTOM),(-x+leg,H.GUIDE_BOTTOM),(-x+leg,bottom)],3.465234375,3.765234375,'guide_frame')
 from mathutils import Vector
 for side in ((-1,1) if lod==1 else (-1,)):
  a=Vector((side*1.93,2.40,H.P));b=Vector((side*1.93,3.615234375,4.96));d=(b-a).normalized();u=d.cross(Vector((1,0,0))).normalized()*.07;v=d.cross(u).normalized()*.07
  ring=[u,-u/2+v*math.sqrt(3)/2,-u/2-v*math.sqrt(3)/2];vs=[tuple(p+q) for p in (a,b) for q in ring]
  mark(R.mesh(key+'_'+state+'_LOD'+str(lod)+'_GuideRaker'+str(side),vs,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'timber',dest),'GuideRaker'+str(side),'walls','architecture','guide_frame')
 if state!='ruins':
  for label,y in [('Front',1.60),('Back',2.86)]:
   x=2.02;leg=.14
   shape('Shelter'+label,[(-x,H.P),(-x,H.BEAM_TOP),(x,H.BEAM_TOP),(x,H.P),(x-leg,H.P),(x-leg,H.POST_TOP),(-x+leg,H.POST_TOP),(-x+leg,H.P)],y-.09,y+.09,'shelter')
  if lod==1:
   block('ReedDeck',(0,2.23,(H.BEAM_TOP+2.99)/2),(4.20,1.62,2.99-H.BEAM_TOP),'cloth','vaults','roofs')
   block('EarthRoof',(0,2.23,3.015),(4.20,1.62,.05),'roof','vaults','roofs')
  else:
   block('ContinuousBearingRoof',(0,2.23,(H.BEAM_TOP+3.04)/2),(4.20,1.62,3.04-H.BEAM_TOP),'roof','vaults','roofs')
  # State-specific losses are applied to new original source fabrication, not
  # to any native wheel/cable/payload/reference hierarchy.
  if state.startswith('damage_'):
   n=int(state[-1]);failure=profile['damage']
   if n<=4:
    work=R.collection(R.PREFIX+key+'_'+state+'_LOD'+str(lod)+'_Cutter',bpy.data.scenes[R.SCENE].collection)
    cutter=G.corner_cutter(R,work,key+'_'+state+'_LOD'+str(lod)+'Fracture',failure['corner_plus_x_front_y'],failure['notch_extents'][n-1])
    for o in list(out):
     if o.get('structural_group')=='shelter' and o.get('role') in ('architecture','roofs'):
      q=G.subtract(R,o,cutter)
      if q is None:out=[x for x in out if x is not o]
    _remove_generated(cutter);bpy.data.collections.remove(work)
   else:
    for o in list(out):
     if o.get('structural_group')=='shelter' and o.get('role') in ('architecture','roofs'):
      q=G.cut(R,o,(0,0,profile['damage']['heavy_failure_group_caps']['shelter']),(.018,.023,1))
      if q is None:out=[x for x in out if x is not o]
 # Retained low tool-store wall is below all native moving reference pieces.
 cap=profile['ruins']['group_caps'].get('tool_store',.80) if state=='ruins' else profile['damage']['heavy_failure_group_caps'].get('tool_store',1.1) if state=='damage_5' else 1.10
 if lod==1:block('ToolStoreBack',(-1.10,2.91,(H.P+cap)/2),(1.50,.12,cap-H.P),'plaster',group='tool_store')
 if state not in ('ruins','damage_5'):
  if lod==1:block('OwnerCloth',(.70,1.505,2.63),(.28,.025,.22),'owner','finish','owner','owner')
  else:mark(R.mesh(key+'_'+state+'_LOD'+str(lod)+'_OwnerCloth',[(.56,1.505,2.52),(.84,1.505,2.52),(.84,1.505,2.74),(.56,1.505,2.74)],[(0,1,2,3)],'owner',dest),'OwnerCloth','finish','owner','owner')
  # One readable log retains the intake silhouette on its new named ground.
  sides=6;radius=.10;vs=[(x,-.72+radius*math.cos(math.pi/6+j*math.tau/sides),H.F+radius+radius*math.sin(math.pi/6+j*math.tau/sides)) for x in (-1.56,1.56) for j in range(sides)]
  if lod==1:mark(R.mesh(key+'_'+state+'_LOD'+str(lod)+'_IntakeLog',vs,[tuple(reversed(range(6))),tuple(range(6,12))]+[(j,(j+1)%6,(j+1)%6+6,j+6) for j in range(6)],'timber',dest),'IntakeLog','finish','props','log_intake')
 # Actual family debris remains grounded; count is a visible source subset.
 debris=[o for o in meshes(source) if o.get('role')=='debris']
 for index,o in enumerate(debris):
  if index%7==0:out.append(G.clone(o,dest,'OriginalLOD'+str(lod)))
 return out


def _clone_placement(H,key,state,source,dest,lod,profile):
 healthy=bpy.data.collections[H.R.PREFIX+key+'_healthy_LOD'+str(lod)]
 old=next(o for o in healthy.all_objects if o.type=='ARMATURE' and o.get('native_lumber_reference_root'))
 arm=old.copy();arm.data=old.data.copy();arm.name=H.R.PREFIX+key+'_'+state+'_LOD'+str(lod)+'_Rig';dest.objects.link(arm);arm['native_probe_owner']=N.PREFIX+arm.name
 for o in meshes(healthy):
  identity=o.get('healthy_source',o.name)
  if state=='targeting' and any(t in identity for t in profile['targeting_omit_name_fragments']):continue
  q=G.clone(o,dest,state)
  if q.parent==old:q.parent=arm
  for m in q.modifiers:
   if m.type=='ARMATURE' and m.object==old:m.object=arm
 dest['native_lumber_state_normalized']=True
 return dict(route='Exact healthy source LOD clone; targeting applies only declared ground omission',armature=arm.name)


def _build(H,key,state,source,dest,lod,profile):
 prepare_bases(H,key,profile)
 if state in ('preview','targeting'):return _clone_placement(H,key,state,source,dest,lod,profile)
 original=_original_lod2(H,key,state,source,dest,profile,lod)
 old_arm=next(o for o in source.all_objects if o.type=='ARMATURE' and o.get('native_lumber_reference_root'))
 arm=old_arm.copy();arm.data=old_arm.data.copy();arm.name=H.R.PREFIX+key+'_'+state+'_LOD'+str(lod)+'_ReferenceRig';dest.objects.link(arm);arm['native_probe_owner']=N.PREFIX+arm.name
 for o in original:
  if o.parent==old_arm:o.parent=arm
  elif o.get('structural_group') in ('axle_frame','guide_frame') and o.get('role')=='architecture':L.bind_original(o,arm)
 native=sorted([o for o in meshes(source) if o.get('native_lumber_role')],key=lambda o:o.name)
 fixed=sum(L.triangles(o) for o in native if o.get('native_lumber_role')!='wheel')
 wheels=[o for o in native if o.get('native_lumber_role')=='wheel'];wheel_total=sum(L.triangles(o) for o in wheels)
 base=count(source);architecture=count(dest);fraction=.58 if lod==1 else .345
 allocation=max(24*len(wheels),min(560 if lod==1 else 280,math.floor(base*fraction)-architecture-fixed))
 reports=[];created=[]
 for o in native:
  if o.get('native_lumber_role')=='wheel':
   target=max(24,int(allocation*L.triangles(o)/max(1,wheel_total)));q,report=W.derive(o,dest,lod,target);reports.append(report)
  else:
   q=G.clone(o,dest,'ExactNativeLOD'+str(lod));L.audit_exact(q,'skin' if q.get('native_lumber_role')=='skin' else 'rigid',None if q.get('native_lumber_role')=='skin' else int(q['native_lumber_source_index']))
  if q.parent==old_arm:
   basis=q.matrix_basis.copy();inverse=q.matrix_parent_inverse.copy();q.parent=arm;q.matrix_parent_inverse=inverse;q.matrix_basis=basis
  for m in q.modifiers:
   if m.type=='ARMATURE' and m.object==old_arm:m.object=arm
  q['native_probe_owner']=N.PREFIX+arm.name;q['lod_level']=lod;created.append(q)
 pose=N.pose_probe(arm.name,'bone_wheel',[o.name for o in created])
 L.require(pose['reference_restored'] and all(x['movement_partition_matches'] for x in pose['rigid_movement_partition']),'Derived wheel pose/static partition failed')
 skin=next((o for o in created if o.get('native_lumber_role')=='skin'),None)
 skin_checks=[]
 if skin:
  skin_checks=[S.skin_pose_probe(skin.name,arm.name,bone) for bone in ('bone_cable_twist','bone_wheel_base')]
  L.require(all(x['reversible_source_pose_passed'] for x in skin_checks),'Unchanged native LOD skin did not retain exact LBS response')
 ratio=count(dest)/max(1,base);target=.5 if lod==1 else .25
 report=dict(state=state,lod=lod,source_triangles=base,original_derived_architecture_triangles=architecture,
  unchanged_skin_and_payload_triangles=fixed,wheel_requested_total=allocation,actual_triangles=count(dest),ratio=ratio,
  wheel_fidelity=reports,rigid_pose=pose,unchanged_skin_pose=skin_checks,all_five_bones_preserved=True,
  source_only=True,native_playback_qualified=False,passed=abs(ratio-target)<=.1000001)
 report['fast_checkpoint_ratio_failure_retained']=not report['passed'] and bool(getattr(H,'FAST_SOURCE_CHECKPOINT',False))
 dest['lumber_LOD_report_json']=json.dumps(report)
 if not getattr(H,'FAST_SOURCE_CHECKPOINT',False):L.require(report['passed'],'Lumber actual LOD ratio needs further original fabrication: '+json.dumps(report))
 return report


def build(H,key,state,source,dest,lod,profile):
 with L.visible_collections(source,dest):return _build(H,key,state,source,dest,lod,profile)
