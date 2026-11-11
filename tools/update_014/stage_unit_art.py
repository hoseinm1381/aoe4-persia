"""Stage scoped owner-color and UV0 corrections for the five Persian unit bodies."""
from collections import defaultdict
from io import BytesIO
import argparse
import gzip
import json
from pathlib import Path
import struct
import zlib

import numpy as np
from PIL import Image
from unit_review import baseline_manifest, baseline_member, BODIES, MASTER, ROOT, digest, encode, mv, normalize, owner_coverage, parts, rc, read, rgba, rr

OUT='art/persia/units_014'
CANNON=('zamburak','jpn_cannon_ozutsu')


def uv_area(uv, faces):
    coordinates=uv[faces]
    a,b=coordinates[:,1]-coordinates[:,0],coordinates[:,2]-coordinates[:,0]
    return a[:,0]*b[:,1]-a[:,1]*b[:,0]


def fix_uv(raw, grid, cannon=False):
    """Move only affected UV0 points inside their original atlas regions."""
    doc=rc.parse(raw)
    patches, fixes={},[]
    for lod,names,vertex,xyz,uv,faces in parts(raw):
        before=uv.copy()
        assert np.isfinite(uv).all()
        if cannon:
            uv[uv<0]=.5/1024
            uv[uv>1]=1-.5/1024
        bad=np.abs(uv_area(uv,faces))<1e-10
        # Try local half-texel increments, keeping good incident faces oriented
        # and preferring vertices at the collapsed edge over the opposite corner.
        initial=int(bad.sum())
        affected=set()
        while bad.any():
            old_area=uv_area(uv,faces)
            row=int(np.flatnonzero(bad)[0])
            triangle=faces[row]
            t=uv[triangle]
            distances=np.linalg.norm(t[:,None]-t[None,:],axis=2)+np.eye(3)
            pair=np.argmin(distances)//3,np.argmin(distances)%3
            duplicate=np.linalg.norm(t[pair[0]]-t[pair[1]])<1e-7
            candidates=[]
            for i,point in enumerate(triangle):
                if duplicate and i not in pair:
                    continue
                if not duplicate:
                    edge=t[(i+2)%3]-t[(i+1)%3]
                    if np.linalg.norm(edge)<1.e-7:
                        continue
                    along=xyz[triangle[(i+2)%3]]-xyz[triangle[(i+1)%3]]
                    offset=xyz[point]-xyz[triangle[(i+1)%3]]
                    along_norm=np.dot(along,along)
                    dev=np.linalg.norm(offset-along*np.dot(along,offset)/max(along_norm,1e-12))
                else:
                    edge=t[({0,1,2}-set(pair)).pop()]-t[i]
                    dev=np.linalg.norm(xyz[triangle[pair[0]]]-xyz[triangle[pair[1]]])
                ortho=np.array([-edge[1],edge[0]])/max(np.linalg.norm(edge),1.e-10)
                incident=np.flatnonzero(np.any(faces==point,axis=1))
                good=incident[~bad[incident]]
                original_tile=np.floor(uv[point]*grid)
                for step in (.75,1.25,2.,3.):
                    for sign in (-1,1):
                        candidate=(uv[point]+ortho*(sign*step/1024)).astype('<f2').astype(np.float32)
                        if (candidate<0).any() or (candidate>1).any() or not np.array_equal(np.floor(candidate*grid),original_tile):
                            continue
                        old=uv[point].copy()
                        uv[point]=candidate
                        area=uv_area(uv,faces)
                        uv[point]=old
                        if abs(area[row])<.8/(1024**2) or np.any(area[good]*old_area[good]<=0):
                            continue
                        repaired=np.count_nonzero(np.abs(area[incident])>=1e-10)
                        originally_good=len(good)
                        relative=np.sum(np.abs(area[good]-old_area[good])/np.maximum(np.abs(old_area[good]),1e-5))
                        candidates.append((-(repaired-originally_good),step*(1+.18*len(good))+relative*.14-dev*.01,
                                           int(point),float(candidate[0]),float(candidate[1])))
            if not candidates:
                raise ValueError((lod,names,triangle.tolist(),t.tolist()))
            _,_,point,u,v=min(candidates)
            uv[point]=(u,v)
            affected.add(point)
            next_bad=np.abs(uv_area(uv,faces))<1e-10
            assert next_bad.sum()<bad.sum()
            bad=next_bad
        changed=np.flatnonzero(np.any(before!=uv,axis=1))
        if len(changed):
            b=bytearray(vertex.payload)
            stride=struct.unpack_from('<I',b,8)[0]
            for i in changed:
                struct.pack_into('<2e',b,16+int(i)*stride+12,*uv[i])
            patches[vertex.offset]=bytes(b)
            fixes.append({'lod':lod+1,'component':names[0],'recovered_uv_faces':initial,
                          'vertices_changed':len(changed),'max_displacement_texels':round(float(np.linalg.norm(uv-before,axis=1).max()*1024),3)})
    if not patches:
        return raw,fixes
    fixed=rc.rebuild(doc,lambda x:patches.get(x.offset))
    before=list(rc.walk(doc.roots))
    after=list(rc.walk(rc.parse(fixed).roots))
    assert len(before)==len(after)
    for a,b in zip(before,after,strict=True):
        assert (a.tag,a.kind,a.name,a.version)==(b.tag,b.kind,b.name,b.version)
        if a.offset in patches:
            n,_,stride,_=struct.unpack_from('<4I',a.payload)
            assert a.payload[:16]==b.payload[:16]
            ax=np.frombuffer(a.payload,np.uint8,offset=16).reshape(n,stride)
            bx=np.frombuffer(b.payload,np.uint8,offset=16).reshape(n,stride)
            assert np.array_equal(ax[:,:12],bx[:,:12]) and np.array_equal(ax[:,16:],bx[:,16:])
        elif not a.children:
            assert a.payload==b.payload
    for _,_,_,_,uv,faces in parts(fixed):
        assert np.isfinite(uv).all() and (uv>=0).all() and (uv<=1).all()
        assert (np.abs(uv_area(uv,faces))>=1e-10).all()
    return fixed,fixes


def tile_region(shape,grid,xy):
    x,y=xy
    dim=shape[0]//grid
    top=(grid-1-y)*dim
    return np.s_[top:top+dim,x*dim:(x+1)*dim]


def recolor(key,pattern,albedo,layout):
    grid=4 if key=='assassin' else 8
    out=pattern.copy()
    rgb=albedo[:,:,:3].copy()
    region=tile_region(pattern.shape,grid,layout['tiles']['horse_owner' if key.startswith('savar') else 'indigo'])
    selected=out[region]
    cloth=rgb[region]
    w,h=cloth.shape[:2]
    x,y=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h)
    assert selected[:,:,1:3].max()==0, key
    old_red=selected[:,:,0].copy()
    luma=cloth.astype(float) @ np.array([.2126,.7152,.0722])
    if key=='assassin':
        # Color the central woven panel on the coat. Leave its borders indigo.
        bands=(y>.32)&(y<.625)
        # The original mesh UVs keep each tile inset from its border.
        mark=bands&(x>.018)&(x<.982)
        selected[:,:,0][mark]=252
    elif key.startswith('zamburak'):
        # Blue stock cloth gets a neutral dye base. Retain woven edge strips.
        mark=(x>.014)&(x<.986)&(y>.014)&(y<.986)
        selected[:,:,0][mark]=252
    else:
        # Keep player color across the broad horse cloth panel with dark
        # woven edging and interrupted trim. The mask repeats consistently
        # with the same tile wherever the stock-compatible LOD consumes it.
        border=(x<.16)|(x>.84)
        trim=(y>.37)&(y<.51)
        undecorated=border|trim
        selected[:,:,0][undecorated]=0
        off=undecorated&(old_red>=128)
        dark=(luma*.56)[:,:,None]+np.array([12,18,24])
        piping=(np.abs(x-.16)<.014)|(np.abs(x-.84)<.014)
        dark[piping]=luma[piping,None]*.58+np.array([53,34,14])
        cloth[off]=np.clip(dark[off],18,145).astype(np.uint8)
    owner=selected[:,:,0]>=128
    neutral=np.clip(luma*.78+24,51,153).astype(np.uint8)
    cloth[owner]=neutral[owner,None]
    return out,rgb


def mip_records(raw):
    chunks={x.tag:x for x in rc.walk(rc.parse(raw).roots)}
    rr._validate_stream_table(chunks[b'TMAN'].payload,chunks[b'TDAT'].payload)
    _,levels=rr._decode_mips(chunks[b'TDAT'].payload)
    return sorted(levels,key=lambda m:m.level)


def merge_blocks(baseline,new,changed,block_size,*,preserve_owner_channels=True):
    """Keep original BC blocks outside the edited cloth across the mip chain."""
    old=mip_records(baseline)
    draft=mip_records(new)
    records=[]
    for a,b in zip(old,draft,strict=True):
        assert (a.width,a.height,a.level)==(b.width,b.height,b.level)
        dim=(a.width,a.height)
        # BOX with high dynamic range retains any marked mip footprint.
        heat=np.array(Image.fromarray(changed.astype(np.float32)).resize(dim,Image.Resampling.BOX))>0
        bw,bh=(a.width+3)//4,(a.height+3)//4
        p=np.zeros((bh*4,bw*4),bool)
        p[:a.height,:a.width]=heat
        mark=p.reshape(bh,4,bw,4).any(axis=(1,3)).ravel()
        x=np.frombuffer(a.data,np.uint8).reshape(-1,block_size).copy()
        y=np.frombuffer(b.data,np.uint8).reshape(-1,block_size)
        if block_size==16 and preserve_owner_channels:
            # Leave any native BC3 block with nonzero green/blue endpoint
            # channels in place, including their lower-mip skin/hair pixels.
            endpoints=x[:,8:12].copy().view('<u2').reshape(-1,2)
            mark &= ~((endpoints & 0x07ff)!=0).any(axis=1)
        x[mark]=y[mark]
        records.append((a.level,a.width,a.height,x.tobytes()))
    data=bytearray(struct.pack('<I',6))
    counts,sizes=[],[]
    for level,w,h,pixels in reversed(records):
        raw=struct.pack('<4I',level,w,h,len(pixels))+pixels
        split=[raw[i:i+65536] for i in range(0,len(raw),65536)]
        counts.append(len(split))
        for ch in split:
            packed=zlib.compress(ch,9)
            packed=packed if len(packed)<len(ch) else ch
            data.extend(packed)
            sizes.append(struct.pack('<2I',len(ch),len(packed)))
    doc=rc.parse(new)
    old_header=next(c.payload for c in rc.walk(doc.roots) if c.tag==b'TMAN')
    count=len(counts)
    manifest=old_header[:41]+struct.pack('<'+'I'*count,*counts)+b''.join(sizes)
    rr._validate_stream_table(manifest,bytes(data))
    return rc.rebuild(doc,lambda c: manifest if c.tag==b'TMAN' else bytes(data) if c.tag==b'TDAT' else None)


def store(stage,name,data):
    file=stage/'overlay'/name
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_bytes(data)


def run(repo,stage):
    native=repo/'inputs/native'
    template=(native/'art/persia/landmarks_013/ali_qapu_palace/albedo.rrtex').read_bytes()
    manifest=baseline_manifest(repo)
    baseline=read(stage/'uv-baseline.json')
    assert len(baseline)==15
    assert all(not a['nonfinite_uv'] for r in baseline.values() for a in r['lods'])
    changed={}
    for key,(family,asset) in BODIES.items():
        stem=f'{ROOT}/{family}/{asset}/model'
        geometry=baseline_member(repo,stem+'.rrgeom')
        assert digest(geometry)==manifest[stem+'.rrgeom']['sha256']
        grid=4 if key=='assassin' else 8
        fixed,uv=fix_uv(geometry,grid)
        if fixed!=geometry:
            store(stage,stem+'.rrgeom',fixed)
        material=baseline_member(repo,stem+'.rrmaterial')
        assert digest(material)==manifest[stem+'.rrmaterial']['sha256']
        maps=mv.material_slots(material)
        source={slot:(native/normalize(maps['textures'][slot])).read_bytes() for slot in ('albedoTexture','patternTex')}
        albedo,pattern=(rgba(source[s]) for s in ('albedoTexture','patternTex'))
        layout=read(repo/MASTER/family/'textures'/asset/'sources.json')
        mask,color=recolor(key,pattern,albedo,layout)
        newpaths={'albedoTexture':f'{OUT}/{key}/albedo.rrtex','patternTex':f'{OUT}/{key}/owner.rrtex'}
        albedoraw=merge_blocks(source['albedoTexture'],encode(template,newpaths['albedoTexture'],color,srgb=True),
                               (albedo[:,:,:3]!=color).any(2),8)
        maskraw=merge_blocks(source['patternTex'],encode(source['patternTex'],newpaths['patternTex'],mask),
                             mask[:,:,0]!=pattern[:,:,0],16)
        mask_baked=rgba(maskraw)
        assert np.array_equal(mask_baked[:,:,1:],pattern[:,:,1:]),key
        after=owner_coverage(fixed,mask_baked[:,:,0])
        assert len(after)==3 and all(10<=x<=50 for x in after),(key,after)
        replacement=mv.rewrite_material(material,{s:p.replace('/','\\') for s,p in newpaths.items()},{})
        newslots=mv.material_slots(replacement)
        assert newslots['parameters']==maps['parameters']
        assert {k:v for k,v in newslots['textures'].items() if k not in newpaths}=={k:v for k,v in maps['textures'].items() if k not in newpaths}
        store(stage,stem+'.rrmaterial',replacement)
        store(stage,newpaths['albedoTexture'],albedoraw)
        store(stage,newpaths['patternTex'],maskraw)
        art=stage/'editable'/key
        art.mkdir(parents=True,exist_ok=True)
        Image.fromarray(rgba(albedoraw)[::-1,:,:3]).save(art/'albedo.png')
        Image.fromarray(mask_baked[::-1,:,:3]).save(art/'pattern.png')
        unchanged_maps={k:normalize(v) for k,v in maps['textures'].items() if k in ('normalMap','metalTex')}
        changed[key]={'family':family,'asset':asset,'stem':stem,'before':owner_coverage(geometry,pattern[:,:,0]),
                      'after':after,'uv_fixes':uv,'textures':newpaths,'preview_normal_and_metal':unchanged_maps}
        print(key,changed[key]['before'],after,uv,flush=True)
    family,asset=CANNON
    stem=f'{ROOT}/{family}/{asset}/model'
    old=baseline_member(repo,stem+'.rrgeom')
    assert digest(old)==manifest[stem+'.rrgeom']['sha256']
    fixed,uv=fix_uv(old,4,cannon=True)
    assert len(uv)==3
    store(stage,stem+'.rrgeom',fixed)
    changed['cannon']={'family':family,'asset':asset,'stem':stem,'uv_fixes':uv}
    (stage/'coverage.json').write_text(json.dumps(changed,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('repo',type=Path)
    p.add_argument('stage',type=Path)
    a=p.parse_args()
    run(a.repo,a.stage)
