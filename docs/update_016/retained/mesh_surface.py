import json,struct
from lifecycle_repair import readback, stage, rc
from garrison_shared import model_variants as mv
import numpy as np
def s(chunk):
    return rc.pack_document([rc.pack_chunk(chunk.kind,chunk.tag,chunk.payload,version=chunk.version,name=chunk.name)])
def mesh(raw):
    for group in rc.walk(rc.parse(raw).roots):
        if group.tag!=b'GEOM':continue
        h,=tuple(c for c in group.children if c.tag==b'GOHD')
        v,i=[c.payload for c in group.children if c.tag==b'GEOB']
        n,_,vs,_=struct.unpack_from('<4I',v)
        t,_,isize,_=struct.unpack_from('<4I',i)
        xyz=np.ndarray((n,3),'<f2',v,16,(vs,2)).astype(float)
        uv=np.ndarray((n,2),'<f2',v,28,(vs,2)).astype(float)
        idx=np.frombuffer(i,'<u'+str(isize),t,offset=16).reshape(-1,3)
        yield group,rc.read_lp_string(h.payload,0)[0],xyz,uv,idx
def samples(p,grid):
    a=np.zeros((grid,grid))
    for _,name,xyz,uv,idx in mesh(p.read_bytes()):
        if name.startswith(('almaliq_','s0')) and name not in ('almaliq_healthy','s00p00','s01p00'):continue
        points=xyz[idx]; area=np.linalg.norm(np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]),axis=1)*.5
        xy=np.floor((uv[idx].mean(1)%1)*grid).astype(int)
        np.add.at(a,(xy[:,1],xy[:,0]),area)
    return np.round(a/a.sum()*100,1).tolist()
if __name__=='__main__':
 for civ,paths in [('persia',[('art/ps100/b/keep_a3/m',4)]),('vietnam',[(p.relative_to(readback('vietnam')).with_suffix('').as_posix(),4) for p in (readback('vietnam')/'art/scenario').rglob('model.rrmaterial') if any(x in p.as_posix() for x in ('/cc040/','/cc070/','/cccastle/imperial_citadel','/cc050/imperial_citadel'))])]:
  b=readback(civ)
  for stem,g in paths:
   raw=(b/(stem+'.rrmaterial')).read_bytes()
   c=rc.parse(raw).roots[0]
   t=mv.material_slots(s(c))['textures']
   print(civ,stem,t.get('albedoTexture'),samples(b/(stem+'.rrgeom'),g))
