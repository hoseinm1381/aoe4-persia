"""Pure recipe-plan arithmetic; never creates Blender geometry."""
from pathlib import Path
import ast, json, math, sys, types, hashlib
ROOT=Path(__file__).resolve().parent

class Ob(dict):
 def __init__(self,name,vertices,faces):
  super().__init__();self.name=name;self.vertices=vertices;self.faces=faces;self.type='MESH'
  self.data=types.SimpleNamespace(polygons=[types.SimpleNamespace(vertices=f) for f in faces])
class Collection:
 def __init__(self,name):self.name=name;self.objects=[];self.children=[]
 @property
 def all_objects(self):return self.objects+[o for c in self.children for o in c.all_objects]
class Runner:
 def __init__(self):
  self.PREFIX='PSB_lumber_camp_';self.SCENE='PSB_lumber_camp';self.collections={};self.objects={}
  self.scene=Scene();self.scene.collection=Collection('scene')
 def configure(self,*a):pass
 def setup_scene(self):return self.scene
 def collection(self,name,parent):
  if name not in self.collections:self.collections[name]=Collection(name);parent.children.append(self.collections[name])
  return self.collections[name]
 def mesh(self,name,vertices,faces,surface,col,stage='walls',role='architecture'):
  o=Ob(self.PREFIX+name,vertices,faces);self.objects[o.name]=o;col.objects.append(o);o['surface']=surface;return o
 def block(self,name,center,size,surface,col,stage='walls',role='architecture'):
  vertices=[tuple(center[i]+sign[i]*size[i]/2 for i in range(3)) for sign in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
  return self.mesh(name,vertices,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],surface,col,stage,role)
 def beam(self,name,a,b,width,surface,col,stage='walls',role='architecture'):
  sub=lambda a,b:tuple(x-y for x,y in zip(a,b));cross=lambda a,b:(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
  norm=lambda a:tuple(x/math.sqrt(sum(q*q for q in a)) for x in a)
  d=norm(sub(b,a));up=(1,0,0) if abs(d[2])>.95 else (0,0,1);u=norm(cross(d,up));v=norm(cross(d,u))
  vertices=[tuple(p[i]+su*u[i]*width/2+sv*v[i]*width/2 for i in range(3)) for p in (a,b) for su,sv in ((-1,-1),(1,-1),(1,1),(-1,1))]
  return self.mesh(name,vertices,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],surface,col,stage,role)
class Scene(dict):pass

def bounds(ob):return [[min(v[i] for v in ob.vertices) for i in range(3)],[max(v[i] for v in ob.vertices) for i in range(3)]]
def main():
 runner=Runner();bpy=types.SimpleNamespace(data=types.SimpleNamespace(objects=runner.objects),context=types.SimpleNamespace())
 tree=ast.parse((ROOT/'recipe.py').read_text());tree.body=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]
 # Top-level imports only are replaced by a pure, non-Blender geometry recorder.
 module=types.ModuleType('draft_recipe');module.__dict__.update(dict(__file__=str(ROOT/'recipe.py'),Path=Path,sys=sys,math=math,json=json,bpy=bpy,R=runner))
 sys.modules[module.__name__]=module;exec(compile(tree,'recipe-plan','exec'),module.__dict__)
 for name in ('foundation','first_room','architecture','props','detail'):getattr(module,name)()
 objects=runner.scene.collection.all_objects;total=sum(sum(len(f)-2 for f in o.faces) for o in objects)
 rows=[dict(name=o.name,triangles=sum(len(f)-2 for f in o.faces),bounds=bounds(o),role=o['role'],stage=o['construction_stage'],group=o['structural_group']) for o in objects]
 errors=[];contacts=[]
 axes={'bottom-top':(2,False),'top-bottom':(2,True),'right-left':(0,True),'left-right':(0,False),'front-back':(1,False),'back-front':(1,True)}
 for c in module.CONTRACTS:
  a,A=bounds(runner.objects[c['a']]);b,B=bounds(runner.objects[c['b']]);i,rev=axes[c['axis']]
  gap=A[i]-b[i] if rev else a[i]-B[i];overlap=[min(A[j],B[j])-max(a[j],b[j]) for j in range(3) if j!=i]
  passed=abs(gap-c['target'])<=c['tolerance'] and min(overlap)>=-c['tolerance'];row=dict(c,planned_gap=gap,planned_overlap=overlap,passed=passed);contacts.append(row)
  if not passed:errors.append(row)
 if total>1136:errors.append(dict(architecture_triangles=total,cap=1136))
 low=(-2.28125,-1.365234375,-2.4375);high=(2.28125,4.28125,5.7265625)
 for o in objects:
  if any(v[a]<low[a]-1e-8 or v[a]>high[a]+1e-8 for v in o.vertices for a in range(3)):
   errors.append(dict(object=o.name,error='Original recipe plan outside retained donor reference envelope'))
 document=dict(schema='ccp.persia.lumber-original-plan/v1',qualification='Pure recipe coordinate/triangle arithmetic only; no Blender generation, normals, closed-solid ray tests or visual acceptance',
  recipe_sha256=hashlib.sha256((ROOT/'recipe.py').read_bytes()).hexdigest(),original_architecture_triangles=total,native_functional_triangles=1604,healthy_total=total+1604,stock_cap=2740,
  members=rows,planned_scalar_contacts=contacts,planned_interfaces=module.ANCHORS['A1']['numerical_interfaces'],anchors=module.ANCHORS,
  passed_pure_arithmetic=not errors,errors=errors,parent_generated_verification_required=True)
 (ROOT/'geometry-context.json').write_text(json.dumps(document,indent=2)+'\n')
 print(json.dumps({k:document[k] for k in ('original_architecture_triangles','native_functional_triangles','healthy_total','stock_cap','passed_pure_arithmetic','errors')}))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
