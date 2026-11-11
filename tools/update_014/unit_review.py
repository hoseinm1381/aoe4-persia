import argparse
from collections import defaultdict
from functools import lru_cache
import gzip,hashlib,json,os,struct,sys,zipfile
from pathlib import Path

import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bake_landmarks import rc,mv,rr,rgba,digest,encode

BODIES={
    'assassin':('assassin','abb_spy'),
    'zamburak':('zamburak','abb_camel_combined_bow_age04'),
    'zamburak_upgrade':('zamburak','abb_camel_combined_bow_age04_upgrade'),
    'savar_castle':('savar','byz_horse_combined_armor_age03'),
    'savar_imperial':('savar','byz_horse_combined_armor_age04'),
}
ROOT='art/persia/release_100/units'
MASTER='authoring/art/persia/units'
BARY=np.array([[1/3,1/3,1/3],[.6,.2,.2],[.2,.6,.2],[.2,.2,.6]])


def read(p):
    return json.loads(p.read_bytes())


def normalize(path):
    return path.replace('\\','/').lower()


def parts(geometry):
    for mesh in (x for x in rc.walk(rc.parse(geometry).roots) if x.tag==b'MESH'):
        for lod,chunk in enumerate(x for x in mesh.children if x.tag==b'LOD '):
            for g in (x for x in chunk.children if x.tag==b'GEOM'):
                head=next(x.payload for x in g.children if x.tag==b'GOHD')
                names=[]
                offset=0
                for _ in range(4):
                    name,offset=rc.read_lp_string(head,offset)
                    names.append(name)
                vertex,index=[x for x in g.children if x.tag==b'GEOB']
                v,i=vertex.payload,index.payload
                n,_,stride,_=struct.unpack_from('<4I',v)
                count,_,size,_=struct.unpack_from('<4I',i)
                assert size in (2,4) and count%3==0 and len(v)==16+n*stride and len(i)==16+count*size
                xyz=np.ndarray((n,3),'<f2',v,16,(stride,2)).astype(np.float32)
                uv=np.ndarray((n,2),'<f2',v,28,(stride,2)).astype(np.float32)
                face=np.frombuffer(i,'<u'+str(size),count,offset=16).reshape(-1,3)
                assert face.max()<n and np.isfinite(xyz).all()
                yield lod,names,vertex,xyz,uv,face


def sample(part):
    _,_,_,xyz,uv,face=part
    pt=xyz[face]
    area=np.linalg.norm(np.cross(pt[:,1]-pt[:,0],pt[:,2]-pt[:,0]),axis=1)/2
    coords=np.einsum('sa,fad->fsd',BARY,uv[face]).reshape(-1,2)
    return coords,np.repeat(area/4,4)


def pixels(coords,shape):
    h,w=shape[:2]
    return (np.floor(coords[...,1]*h).astype('int64')%h,np.floor(coords[...,0]*w).astype('int64')%w)


def owner_coverage(geometry,mask):
    sums=defaultdict(lambda:np.zeros(2))
    for row in parts(geometry):
        uv,area=sample(row)
        values=mask[pixels(uv,mask.shape)]
        sums[row[0]]+= (float(area[values>=128].sum()),float(area.sum()))
    return [round(float(a/b*100),2) for _,(a,b) in sorted(sums.items())]


def baseline_member(repo, name):
    snapshot = repo / 'docs/update_014/native-baseline.zip'
    if snapshot.is_file():
        with zipfile.ZipFile(snapshot) as z:
            if name in z.namelist():
                return z.read(name)
    return (repo / 'inputs/native' / name).read_bytes()


def baseline_manifest(repo):
    prior = repo / 'docs/update_014/baseline-members.json.gz'
    if not prior.is_file():
        prior = repo / 'docs/FINAL_MEMBER_MANIFEST.json.gz'
    return json.loads(gzip.decompress(prior.read_bytes()))['members']


def material_data(root,stem,manifest):
    raw=baseline_member(root.parent.parent, stem+'.rrmaterial')
    assert manifest[stem+'.rrmaterial']['sha256']==digest(raw),stem
    slots=mv.material_slots(raw)
    return raw,slots


def audit(repo,stage):
    root=repo/'inputs/native'
    manifest=baseline_manifest(repo)
    all_rows={}
    scopes={tuple(v):k for k,v in BODIES.items()}
    for family in ('assassin','zamburak','savar'):
        for geom in sorted((root/ROOT/family).rglob('*.rrgeom')):
            member=geom.relative_to(root).as_posix()
            native=baseline_member(repo,member)
            assert manifest[member]['sha256']==digest(native),member
            stem=member.removesuffix('.rrgeom')
            mat,slots=material_data(root,stem,manifest)
            asset=geom.parent.name
            maps=slots['textures']
            decoded={}
            for k,v in maps.items():
                if k in ('albedoTexture','patternTex','normalMap','metalTex'):
                    member=normalize(v)
                    p=root/member
                    if p.exists():
                        raw=p.read_bytes()
                        assert manifest[member]['sha256']==digest(raw),member
                        decoded[k]=rgba(raw)
            layout_file=repo/MASTER/family/'textures'/asset/'sources.json'
            layout=read(layout_file) if layout_file.is_file() else {}
            body=scopes.get((family,asset))
            row={'asset':asset,'family':family,'maps':{k:list(v.shape[:2]) for k,v in decoded.items()},
                 'geometry':stem+'.rrgeom','material':stem+'.rrmaterial','lods':[]}
            tiles=layout.get('tiles',{})
            grid=layout.get('atlas_grid',4)
            mask=decoded.get('patternTex')
            if body:
                print('BODY',body,'tiles',tiles,flush=True)
            for part in parts(native):
                lod,names,_,xyz,uv,faces=part
                corners=uv[faces]
                d1=corners[:,1]-corners[:,0];d2=corners[:,2]-corners[:,0]
                triangle_uv=np.abs(d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])
                item=dict(lod=lod+1,part=names,faces=len(faces),nonfinite_uv=int((~np.isfinite(uv)).sum()),
                          outside_uv=int(((uv<0)|(uv>1)).any(1).sum()),collapsed_uv_faces=int((triangle_uv<1.e-10).sum()),
                          min_uv=uv.min(0).tolist(),max_uv=uv.max(0).tolist())
                if mask is not None and np.isfinite(uv).all():
                    xy,area=sample(part)
                    pi=pixels(xy,mask.shape)
                    values=mask[pi]
                    item['coverage']=round(float(area[values[:,0]>=128].sum()/area.sum()*100),3)
                    if body and tiles:
                        ts=(np.floor(xy*grid).astype(int)%grid)
                        by_tile={}
                        for name,(tx,ty) in tiles.items():
                            # sources.json grid uses authoring UV coordinates, v up.
                            in_tile=(ts[:,0]==tx)&(ts[:,1]==grid-1-ty)
                            if area[in_tile].sum()/area.sum()>.004:
                                by_tile[name]=[round(float(area[in_tile].sum()/area.sum()*100),2),
                                               round(float(area[in_tile&(values[:,0]>=128)].sum()/area.sum()*100),2)]
                        item['tile_area_and_owner']=by_tile
                row['lods'].append(item)
                if body:
                    print(lod+1,names[:2],len(faces),item['coverage'],item.get('tile_area_and_owner'),
                          'UV',item['nonfinite_uv'],item['outside_uv'],item['collapsed_uv_faces'],flush=True)
            all_rows[stem]=row
    (stage/'uv-baseline.json').write_text(json.dumps(all_rows,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('repo',type=Path)
    p.add_argument('stage',type=Path)
    args=p.parse_args()
    audit(args.repo,args.stage)
