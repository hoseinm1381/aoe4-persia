"""Parent-run rigid-wheel-only derivatives; source references remain untouched."""
import json, math, hashlib
from pathlib import Path

CONTACT_TRIANGLES={0:101,3:336}
LIMITS={1:dict(surface=.04,uv=.005),2:dict(surface=.10,uv=.01)}
PRIMARY_DECIMATE_SOURCES=[
 'https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/modifiers/intern/MOD_decimate.cc',
 'https://github.com/blender/blender/blob/blender-v5.2-release/source/blender/bmesh/tools/bmesh_decimate_collapse.cc#L224-L228']

def require(value,message):
 if not value:raise RuntimeError(message)
def digest(ob):
 data=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],
  uv={layer.name:[list(x.uv) for x in layer.data] for layer in ob.data.uv_layers},
  parent=ob.parent.name if ob.parent else None,parent_bone=ob.parent_bone,world=[list(r) for r in ob.matrix_world])
 return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
def protected_points(source):
 points=[v.co.copy() for v in source.data.vertices];ids=set()
 for axis in range(3):
  ids.add(min(range(len(points)),key=lambda i:points[i][axis]));ids.add(max(range(len(points)),key=lambda i:points[i][axis]))
 # Geometric Y/Z rim samples, not a physical rotation-axis assertion.
 cy,cz=-.02499248780077369,2.097864985466003
 for j in range(16):
  angle=math.tau*j/16;ids.add(max(range(len(points)),key=lambda i:(points[i].y-cy)*math.cos(angle)+(points[i].z-cz)*math.sin(angle)))
 index=int(source['native_lumber_source_index'])
 if index in CONTACT_TRIANGLES:ids.update(source.data.polygons[CONTACT_TRIANGLES[index]].vertices)
 return [points[i] for i in sorted(ids)]

def _tree(obj):
 from mathutils.bvhtree import BVHTree
 obj.data.calc_loop_triangles();tris=[tuple(t.vertices) for t in obj.data.loop_triangles]
 return BVHTree.FromPolygons([v.co for v in obj.data.vertices],tris,all_triangles=True),tris

def fidelity(source,derived,level,locked):
 from mathutils import Vector
 from mathutils.geometry import barycentric_transform
 source_tree,source_tris=_tree(source);derived_tree,derived_tris=_tree(derived)
 def samples(ob):
  return [v.co for v in ob.data.vertices]+[sum((ob.data.vertices[i].co for i in t.vertices),Vector())/3 for t in ob.data.loop_triangles]
 directional=[]
 for obj,tree in ((source,derived_tree),(derived,source_tree)):
  distances=[]
  for p in samples(obj):
   hit=tree.find_nearest(p);require(hit is not None,'Empty source/derived wheel surface');distances.append(hit[3])
  directional.append(max(distances,default=0))
 source_bounds=[[min(v.co[a] for v in source.data.vertices),max(v.co[a] for v in source.data.vertices)] for a in range(3)]
 derived_bounds=[[min(v.co[a] for v in derived.data.vertices),max(v.co[a] for v in derived.data.vertices)] for a in range(3)]
 extrema=max(abs(x-y) for a,b in zip(source_bounds,derived_bounds) for x,y in zip(a,b))
 protected=max((derived_tree.find_nearest(p)[3] for p in locked),default=0)
 source.data.calc_loop_triangles();source_loops=[tuple(t.loops) for t in source.data.loop_triangles]
 uv_max=0;worst=[]
 for layer in derived.data.uv_layers:
  original=source.data.uv_layers.get(layer.name);require(original is not None,'Derived wheel created/lost UV identity')
  for loop in derived.data.loops:
   p=derived.data.vertices[loop.vertex_index].co;hit=source_tree.find_nearest(p);distance=hit[3]
   nearby=source_tree.find_nearest_range(p,distance+1e-5)
   errors=[]
   for q,normal,ti,d in nearby:
    a,b,c=[source.data.vertices[i].co for i in source_tris[ti]]
    values=[Vector((*original.data[i].uv,0)) for i in source_loops[ti]]
    expected=barycentric_transform(q,a,b,c,*values)
    errors.append(max(abs(layer.data[loop.index].uv[i]-expected[i]) for i in (0,1)))
   require(errors,'No geometric source correspondence for derived UV')
   error=min(errors);uv_max=max(uv_max,error)
   if error>LIMITS[level]['uv']:worst.append(dict(layer=layer.name,loop=loop.index,error=error))
 result=dict(sampled_source_to_derived_max_metres=directional[0],sampled_derived_to_source_max_metres=directional[1],
  sampling='All vertices plus triangle centroids in both directions; not a continuous Hausdorff bound',
  maximum_bounds_extrema_error_metres=extrema,maximum_protected_rim_or_bearing_surface_error_metres=protected,
  maximum_nearest_surface_UV_component_error=uv_max,UV_correspondence='Minimum barycentric UV discrepancy among nearest coincident reference surfaces within1e-5m',
  worst_UV_corners=worst[:8],limits=dict(LIMITS[level],extrema=1e-5,protected=1e-5),
  source_mesh_digest=digest(source),derived_mesh_digest=digest(derived),actual_triangles=len(derived.data.loop_triangles))
 result['passed']=max(directional)<=LIMITS[level]['surface'] and uv_max<=LIMITS[level]['uv'] and extrema<=1e-5 and protected<=1e-5
 return result

def derive(source,destination,level,target_triangles):
 import bpy, importlib.util
 from mathutils import Vector
 module_path=Path(__file__).with_name('wheel_face_subset.py')
 spec=importlib.util.spec_from_file_location('lumber_exact_face_subset',module_path);F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
 require(source.get('native_lumber_role')=='wheel' and level in (1,2),'Only separate rigid wheel source copies may be adapted')
 require(not source.modifiers,'Wheel source must be exact rigid geometry')
 before=digest(source);locked=protected_points(source);source.data.calc_loop_triangles()
 old_triangles=list(source.data.loop_triangles)
 positions=[list(v.co) for v in source.data.vertices];faces=[list(t.vertices) for t in old_triangles]
 selected,selection=F.select(positions,faces,[list(p) for p in locked],.039 if level==1 else .099)
 used=sorted({i for ti in selected for i in faces[ti]});remap={old:i for i,old in enumerate(used)}
 mesh=bpy.data.meshes.new(source.data.name+'__ExactFaceSubsetLOD'+str(level))
 mesh.from_pydata([positions[i] for i in used],[],[[remap[i] for i in faces[ti]] for ti in selected]);mesh.update()
 q=source.copy();q.data=mesh;q.name=source.name+'__OriginalDerivedWheelLOD'+str(level);destination.objects.link(q)
 for material in source.data.materials:mesh.materials.append(material)
 for polygon,ti in zip(mesh.polygons,selected):polygon.material_index=source.data.polygons[old_triangles[ti].polygon_index].material_index
 for layer in source.data.uv_layers:
  dst=mesh.uv_layers.new(name=layer.name)
  for polygon,ti in zip(mesh.polygons,selected):
   for outloop,inloop in zip(polygon.loop_indices,old_triangles[ti].loops):dst.data[outloop].uv=layer.data[inloop].uv
 # Native raw per-vertex normals remain exact for each retained source vertex.
 raw=source.data.attributes.get('native_reference_normal')
 require(raw is not None,'Exact raw native wheel normals missing')
 attr=mesh.attributes.new('native_reference_normal','FLOAT_VECTOR','POINT')
 for row,old in zip(attr.data,used):row.vector=raw.data[old].vector
 native_corners=[tuple(source.data.corner_normals[li].vector) for ti in selected for li in old_triangles[ti].loops]
 mesh.normals_split_custom_set(native_corners);mesh.update()
 q['healthy_source']=source.get('healthy_source',source.name);q['source_state']='LOD'+str(level)
 q['native_derived_LOD']=True;q['native_original_vertices_preserved']=False;q['native_reference_geometry_preserved']=False
 q['derived_from_native_source_mesh_digest']=before;q['derived_from_native_full_reference']=source.get('native_original_full_reference_library','')
 q['native_source_adaptation']='Exact selected native source faces in a separate open-sheet distance LOD; native LOD0/palette/weights untouched'
 q['derived_source_triangle_indices_json']=json.dumps(selected);q['derived_source_vertex_indices_json']=json.dumps(used)
 if 'native_source_vertex_indices_json' in q:
  q['derived_parent_source_vertex_indices_json']=q['native_source_vertex_indices_json'];del q['native_source_vertex_indices_json']
 report=fidelity(source,q,level,locked)
 actual_normals=[n.vector for n in mesh.corner_normals]
 angles=[math.degrees(math.acos(max(-1,min(1,Vector(a).normalized().dot(b.normalized()))))) for a,b in zip(native_corners,actual_normals)]
 report['derived_normal_count']=len(actual_normals)
 report['maximum_retained_source_custom_normal_angle_degrees']=max(angles,default=0)
 report['derived_normals_finite_and_unit']=len(actual_normals)==len(mesh.loops) and all(all(math.isfinite(x) for x in n) and abs(n.length-1)<1e-4 for n in actual_normals)
 report.update(level=level,target_triangles=target_triangles,target_is_advisory_only=True,original_triangles=len(old_triangles),
  retained_materials_exact=[m.as_pointer() for m in mesh.materials]==[m.as_pointer() for m in source.data.materials],
  same_native_bone_parent=q.parent==source.parent and q.parent_bone==source.parent_bone,
  exact_source_face_selection=selection,skin_weights_or_palette_modified=False,clips_created=False,
  geometry_interpolated=False,UV_interpolated=False,intentional_open_source_sheets=True,
  UV_qualification='Exact original native corner values on retained source triangles, plus nearest-surface comparison; no atlas/seam interpolation')
 require(digest(source)==before,'Original native wheel reference mutated')
 q['derived_wheel_fidelity_report_json']=json.dumps(report)
 q['derived_wheel_fidelity_qualified']=report['passed'] and report['retained_materials_exact'] and report['same_native_bone_parent'] and report['derived_normals_finite_and_unit'] and report['maximum_retained_source_custom_normal_angle_degrees']<=.1
 require(q['derived_wheel_fidelity_qualified'],'Derived wheel fidelity failed: '+json.dumps(report))
 return q,report


def audit_saved_subset(q):
 """Recompute saved derived geometry/appearance/coverage from original native data.

 No qualified boolean, saved fidelity report or hash of generated mesh is trusted.
 Metadata selects a candidate source/face subset; every selected datum is checked.
 """
 import importlib.util
 import numpy as np
 import native_lumber_sources as L
 import native_source_appearance as A
 from mathutils import Vector
 spec=importlib.util.spec_from_file_location('lumber_saved_face_subset',Path(__file__).with_name('wheel_face_subset.py'));F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
 require(q.type=='MESH' and q.get('native_lumber_role')=='wheel','Only rigid wheel derived source allowed')
 index=int(q.get('native_lumber_source_index',-1));level=int(q.get('lod_level',str(q.get('source_state',''))[-1:]))
 require(index in L.WHEEL and level in (1,2),'Unknown original wheel/LOD identity')
 plan,binding,sources=L._sources();record,group,native_used,tris=sources[index]
 require(L.N._sha(binding['native_rrgeom_local_path'])==binding['native_rrgeom_sha256'],'Original RRGeom changed')
 require(q.get('native_source_geometry_sha256')==binding['native_rrgeom_sha256'],'Derived wheel source provenance mismatch')
 selected=json.loads(q['derived_source_triangle_indices_json']);used=json.loads(q['derived_source_vertex_indices_json'])
 require(selected==sorted(set(selected)) and selected and all(type(i)==int and 0<=i<len(tris) for i in selected),'Invalid native face subset indices')
 require(used==sorted({i for ti in selected for i in tris[ti]}),'Native subset vertex identity does not match faces')
 remap={old:i for i,old in enumerate(used)};faces=[[remap[i] for i in tris[ti]] for ti in selected]
 require([list(p.vertices) for p in q.data.polygons]==faces and len(q.data.vertices)==len(used),'Saved wheel subset topology changed')
 source_positions=[group['positions'][i] for i in native_used]
 positions=np.asarray(source_positions,float);actual=np.asarray([list(v.co) for v in q.data.vertices],float)
 pe=float(np.max(np.abs(actual-positions[used])));require(pe<1e-7,'Saved wheel native source positions changed')
 raw=q.data.attributes.get('native_reference_normal');require(raw is not None and len(raw.data)==len(used),'Saved raw wheel normals missing')
 ne=max(abs(row.vector[a]-group['normals'][native_used[old]][a]) for row,old in zip(raw.data,used) for a in range(3))
 require(ne<1e-7,'Saved wheel exact raw normals changed')
 uv_error=0
 require(set(layer.name for layer in q.data.uv_layers)==set(group['uv_layers']),'Saved wheel UV layer identity changed')
 for layer in q.data.uv_layers:
  values=group['uv_layers'][layer.name]
  uv_error=max(uv_error,max(abs(layer.data[loop.index].uv[a]-values[native_used[used[loop.vertex_index]]][a]) for loop in q.data.loops for a in (0,1)))
 require(uv_error<1e-7,'Saved wheel native corner UV changed')
 angular=max(A.angular_error_degrees(n.vector,group['normals'][native_used[used[loop.vertex_index]]]) for n,loop in zip(q.data.corner_normals,q.data.loops))
 require(angular<=A.NORMAL_ANGULAR_LIMIT_DEGREES,'Saved wheel actual custom normal fidelity failed')
 require(len(q.data.materials)==1 and {p.material_index for p in q.data.polygons}=={0},'Saved wheel material slot join changed')
 material=q.data.materials[0];identity=A.material_identity({k:material[k] for k in material.keys()},plan)
 require(identity['name']=='crane','Saved native wheel material identity changed')
 # Independent numeric coverage from immutable native inputs and ACTUAL saved
 # vertices/faces, not the generator's saved report or declared measurements.
 source_tri=positions[np.asarray(tris,int)]
 samples=np.concatenate((positions,source_tri.mean(axis=1),(source_tri[:,0]+source_tri[:,1])/2,(source_tri[:,1]+source_tri[:,2])/2,(source_tri[:,2]+source_tri[:,0])/2))
 ids=set()
 for axis in range(3):ids.update((int(positions[:,axis].argmin()),int(positions[:,axis].argmax())))
 cy,cz=-.02499248780077369,2.097864985466003
 for j in range(16):
  angle=math.tau*j/16;ids.add(int(np.argmax((positions[:,1]-cy)*math.cos(angle)+(positions[:,2]-cz)*math.sin(angle))))
 if index in CONTACT_TRIANGLES:ids.update(tris[CONTACT_TRIANGLES[index]])
 saved_tri=actual[np.asarray(faces,int)];distance=F.point_triangle_distances(samples,saved_tri).min(axis=1)
 protected=F.point_triangle_distances(positions[sorted(ids)],saved_tri).min(axis=1)
 extrema=float(np.max(np.abs(np.asarray((positions.min(axis=0),positions.max(axis=0)))-np.asarray((actual.min(axis=0),actual.max(axis=0))))))
 maximum=float(max(distance,default=0));protected_max=float(max(protected,default=0))
 require(maximum<=LIMITS[level]['surface'] and protected_max<=1e-5 and extrema<=1e-5,'Saved wheel source surface/protected/bounds fidelity failed')
 require(not q.modifiers and not q.vertex_groups,'Derived rigid source unexpectedly has modifiers/weights')
 require(q.parent is not None and q.parent.type=='ARMATURE' and q.parent_bone==record['native_parent_bone'],'Saved wheel native rigid parent binding changed')
 return dict(passed=True,source_index=index,lod=level,actual_triangles=len(faces),native_rrgeom_sha256=binding['native_rrgeom_sha256'],
  exact_source_triangle_indices=selected,position_max_error=pe,UV_max_error=uv_error,raw_normal_max_error=ne,
  maximum_custom_normal_angle_degrees=angular,material_identity=identity,sampled_source_to_saved_max_metres=maximum,
  protected_point_max_metres=protected_max,maximum_bounds_error_metres=extrema,
  saved_to_native_surface_error_metres=0.0,saved_to_native_basis='Every checked triangle is an exact original native source triangle',
  original_LOD0_and_native_weights_unchanged=True,intentional_open_source_sheets=True,
  proof='Recomputed exact source membership, mesh data and numeric coverage; saved qualified flags/reports not trusted')
