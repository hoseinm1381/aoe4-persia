import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import asset_runner as R
def check():
 errors=[];c=bpy.data.collections.get(R.PREFIX+'healthy_LOD0')
 if not c:return {},['healthy composition missing']
 columns=[o for o in c.all_objects if o.name.endswith('ColumnShaft')]
 if len(columns)!=18:errors.append('eighteen physical column shafts required')
 vs=[];fs=[]
 for o in c.all_objects:
  if o.type!='MESH':continue
  off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in p.vertices) for p in o.data.polygons)
 tree=BVHTree.FromPolygons(vs,fs,all_triangles=False)
 hit,_,_,_=tree.ray_cast(Vector((0,-6.5,1.3)),Vector((0,1,0)),13)
 if hit is not None:errors.append('central through-gateway blocked at '+str(tuple(hit)))
 floor=bpy.data.objects[R.PREFIX+'TerraceFloor'];bottom=bpy.data.objects[R.PREFIX+'BasinBottom']
 ft=BVHTree.FromPolygons([v.co for v in floor.data.vertices],[tuple(p.vertices) for p in floor.data.polygons],all_triangles=False)
 pocket,_,_,_=ft.ray_cast(Vector((0,-3.1,5)),Vector((0,0,-1)),2)
 if pocket is None or not 4.14<pocket.z<4.17:errors.append('basin slab pocket must be below terrace surface')
 if R.bounds(bottom)[1][2]>=4.22:errors.append('basin liner is not recessed')
 for name in ('Chest0','Chest1'):
  if R.bounds(bpy.data.objects[R.PREFIX+name])[0][1]>=-6.20:errors.append('activity group hidden behind facade '+name)
 severe=bpy.data.collections.get(R.PREFIX+'damage_5_LOD0')
 if severe:
  for o in severe.all_objects:
   src=o.get('healthy_source','')
   if src in [R.PREFIX+'CoreRoof',R.PREFIX+'CoreFloor5'] and R.bounds(o)[1][0]>1.351:errors.append('upper slab remains above collapsed wall '+o.name)
   if src==R.PREFIX+'SideOwnerCloth1':errors.append('cloth remains above collapsed side wall')
 return {'column_shafts':len(columns),'through_gateway_open':hit is None,'severe_damage_support_checked':severe is not None},errors
