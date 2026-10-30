"""Original configuration guards and seats; native inputs remain unchanged."""
import json
import native_equipment as E

def adapt(case,state,lod,body_objects,native,collection,gear_collection):
 import bpy
 import source_runner as R
 R.configure(E.ROOT.parent,'outpost')
 code=('B' if case['body_key']=='A1Basic' else 'F')+'_'+case['emplacement'][:2]+'_'+state.replace('damage_','D').replace('construct_','C')+'_'+str(lod)
 original=[];contacts=[]
 def block(name,center,size,surface,group):
  ob=R.block(code+'_'+name,center,size,surface,collection,'finish','architecture')
  ob['construction_stage']='finish';ob['structural_group']=group;ob['source_configuration']=case['id'];ob['source_state']=state
  ob['source_LOD']=str(lod);ob['original_authored_configuration_architecture']=True
  original.append(ob);return ob
 references=list(native['component_objects']);is_arrow=case['emplacement']=='arrowslits'
 failed_platform=state in ('damage_5','ruins')
 if is_arrow or failed_platform:
  gear_collection.hide_render=gear_collection.hide_viewport=True
  native['inactive_reference_component_objects']=references;native['active_component_objects']=[]
  native['native_reference_component_triangles']=native['actual_visible_equipment_triangles'];native['actual_visible_equipment_triangles']=0
  native['active_reference_policy']='Exact native arrow architecture retained inactive; original slitted guards active' if is_arrow else 'Native lifecycle-selected weapon compound retained inactive; authored heavy source omits intact compound to avoid surviving-wall/entry collisions'
  native['source_choice_not_native_visibility_or_clip']=True
 else:native['active_component_objects']=references;native['inactive_reference_component_objects']=[]
 guard_allowed=state in ('healthy','preview','targeting','damage_1','damage_2','damage_3','damage_4','construct_finish')
 if is_arrow and guard_allowed:
  basic=case['body_key']=='A1Basic';pos=1.76 if basic else 1.28;half=1.685 if basic else 1.11
  bottom=6.65 if basic else 5.52;hole0=7.25 if basic else 6.65;hole1=7.85 if basic else 7.25;top=7.99 if basic else 7.72
  surface='timber' if basic else 'plaster';slot=half*.38;gap=.08
  for face in range(4):
   def piece(name,x0,x1,z0,z1):
    tangent=(x0+x1)/2;depth=.12
    center=(tangent,pos,(z0+z1)/2) if face==0 else (pos,-tangent,(z0+z1)/2) if face==1 else (-tangent,-pos,(z0+z1)/2) if face==2 else (-pos,tangent,(z0+z1)/2)
    size=(x1-x0,depth,z1-z0) if face%2==0 else (depth,x1-x0,z1-z0)
    return block('Guard'+str(face)+name,center,size,surface,'original_arrow_guards')
   lower=piece('Sill',-half,half,bottom,hole0)
   piece('Left',-half,-slot-gap/2,hole0,hole1);piece('Middle',-slot+gap/2,slot-gap/2,hole0,hole1);piece('Right',slot+gap/2,half,hole0,hole1)
   piece('Lintel',-half,half,hole1,top)
   contacts.append(dict(object=lower.name,bottom=bottom,bearing='Existing original upper breastwork top6.65' if basic else 'Existing original GalleryDeck top5.52',qualification='Named numerical seating; actual contact test deferred'))
 if not is_arrow and not failed_platform and native['active_component_objects']:
  floor=3.40 if case['body_key']=='A1Basic' else 5.52
  for name in native['active_component_objects']:
   ob=bpy.data.objects[name]
   if 'springald' not in ob['native_source_name'] and ('cannon' not in ob['native_source_name'] or len(ob.data.polygons)==60):continue
   points=[ob.matrix_world@v.co for v in ob.data.vertices];low=min(p.z for p in points)
   if low<=floor+1e-5:continue
   # Exact connected native bottom faces yield individual carrier-foot seats,
   # avoiding a generic platform across the access hatch or whole gallery.
   faces=[p for p in ob.data.polygons if all(abs(points[i].z-low)<1e-5 for i in p.vertices)]
   adjacency={}
   for polygon in faces:
    keys=[tuple(round(points[i][a],6) for a in (0,1)) for i in polygon.vertices]
    for key in keys:adjacency.setdefault(key,set()).update(keys)
   remaining=set(adjacency);feet=[]
   while remaining:
    todo=[remaining.pop()];seen=set(todo)
    while todo:
     for key in adjacency[todo.pop()]-seen:seen.add(key);remaining.discard(key);todo.append(key)
    feet.append(seen)
   for i,foot in enumerate(feet):
    lo=[min(p[a] for p in foot)-.008 for a in (0,1)];hi=[max(p[a] for p in foot)+.008 for a in (0,1)]
    if min(hi[a]-lo[a] for a in (0,1))<.025:continue
    seat=block('Seat'+str(len(original)),((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(floor+low)/2),(hi[0]-lo[0],hi[1]-lo[1],low-floor),'stone','original_carrier_plinths')
    contacts.append(dict(object=seat.name,native_carrier=ob.name,seat_bottom=floor,seat_top=low,height=low-floor,
     native_bottom_face_xy=[list(p) for p in sorted(foot)],qualification='Exact native bottom-face plane and existing gallery deck datum; pivots unchanged, contact verification deferred'))
 count=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in original)
 return dict(original_authored_objects=[o.name for o in original],active_original_guard_triangles=count if is_arrow else 0,
  active_original_plinth_triangles=count if not is_arrow else 0,active_original_adaptation_triangles=count,
  inactive_native_reference_triangles=native.get('native_reference_component_triangles',0),contacts=contacts,
  native_vertices_bones_pivots_clips_changed=False,
  heavy_source_choice='Intact compound omitted from visible heavy/ruin source; exact native lifecycle alternative remains inactive and inspectable; no reviewed safe yard arrangement or invented collapse animation' if failed_platform and references else None,
  early_guard_damage_refinement='Guard panels retained on surviving original bearer; individual guard fractures not additionally authored in this quick correction' if is_arrow else None)
