"""Bake six distinct Persian landmark finishes into the shipped UV layouts."""
from __future__ import annotations

import argparse
from collections import defaultdict
import gzip
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import struct
import sys
import zlib

import numpy as np
from PIL import Image

from runtime import EXT
sys.path.insert(0, str(EXT))
from garrison_shared import model_variants as mv, relic_chunky as rc, rrtex_decoder as rr

TILE = 512
MODEL = 'art/ps100/l'
ART = 'art/persia/landmarks_013'
# Plaster, brick, stone, timber, dyed cloth, fixed cloth, roof, earth, glaze, carved detail.
PALETTES = {
    'ali_qapu_palace': ('c2a07a','a46442','a69a82','66402c','766a58','9b4637','306d73','80664c','255871','b18a51'),
    'assassin_brotherhood': ('a89b80','845844','726a60','493429','645e55','785348','4c615b','675644','3d5d5b','8d7655'),
    'grand_caravanserai': ('bca27b','a96b43','928471','644634','78654e','93473d','996043','827052','397677','b79059'),
    'gundeshapur': ('b9af8d','a56c52','8f8e7d','624735','716a55','636e45','365a76','70664e','2f716d','a8945c'),
    'samarkand_bazaar': ('c6b08a','a36345','a39a83','6b4333','7e705a','a44548','297c84','857151','245b87','c09b58'),
    'shah_abbas_siege_factory': ('b5a081','855b42','7e7666','533b2b','6b6558','8b683c','635244','705a43','41625b','a18253'),
}
ROOF_DYE = {
    'ali_qapu_palace': .84, 'assassin_brotherhood': .92, 'grand_caravanserai': .91,
    'gundeshapur': .83, 'samarkand_bazaar': .65, 'shah_abbas_siege_factory': .79,
}
MATERIALS = ('plaster','brick','stone','timber','owner','cloth','roof','earth',
             'leaves','rubble','ink','paper','metal','grime','carving','pottery')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def rgba(raw):
    chunks={x.tag:x for x in rc.walk(rc.parse(raw).roots)}
    manifest=chunks[b'TMAN'].payload
    data=chunks[b'TDAT'].payload
    rr._validate_stream_table(manifest,data)
    _,levels=rr._decode_mips(data)
    levels.sort(key=lambda m:m.level)
    fmt=struct.unpack_from('<I',manifest,20)[0]
    dxgi,_=rr._select_dxgi(fmt,chunks[b'TXTR'].decoded_name,levels[0])
    # BC3 UNORM and its sRGB interpretation store the same block data.
    return np.asarray(Image.open(BytesIO(rr._dds(levels,77 if dxgi==78 else dxgi))).convert('RGBA')).copy()


def encode(template, member, pixels, srgb=False):
    doc=rc.parse(template)
    fmt=19 if srgb else 22
    assert struct.unpack_from('<I',next(c.payload for c in rc.walk(doc.roots) if c.tag==b'TMAN'),20)[0]==fmt
    if srgb:
        assert any(c.tag==b'TSRI' for c in rc.walk(doc.roots))
    h,w=pixels.shape[:2]
    count=max(w,h).bit_length()
    src=Image.fromarray(pixels)
    if srgb:
        x=pixels.astype(np.float32)/255
        linear=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
        channels=[Image.fromarray(linear[:,:,i]) for i in range(3)]
    else:
        channels=src.split()
    data=bytearray(struct.pack('<I',6))
    counts,sizes=[],[]
    for level in reversed(range(count)):
        size=(max(1,w>>level),max(1,h>>level))
        if level==0:
            image=src
        elif srgb:
            sample=np.stack([np.asarray(ch.resize(size,Image.Resampling.BOX)) for ch in channels],axis=2)
            rgb=np.where(sample<=.0031308,12.92*sample,1.055*sample**(1/2.4)-.055)
            image=Image.fromarray(np.clip(np.rint(rgb*255),0,255).astype(np.uint8))
        else:
            image=Image.merge('RGBA',[ch.resize(size,Image.Resampling.BOX) for ch in channels])
        dds=BytesIO()
        image.save(dds,format='DDS',pixel_format='DXT1' if srgb else 'DXT5')
        blocks=dds.getvalue()
        assert blocks[84:88]==(b'DXT1' if srgb else b'DXT5')
        blocks=blocks[128:]
        mw,mh=size
        assert len(blocks)==((mw+3)//4)*((mh+3)//4)*(8 if srgb else 16)
        record=struct.pack('<4I',level,mw,mh,len(blocks))+blocks
        fragments=[record[i:i+65536] for i in range(0,len(record),65536)]
        counts.append(len(fragments))
        for chunk in fragments:
            packed=zlib.compress(chunk,9)
            packed=packed if len(packed)<len(chunk) else chunk
            data.extend(packed)
            sizes.append(struct.pack('<2I',len(chunk),len(packed)))
    manifest=(struct.pack('<8IBII',6,w,h,1,2,fmt,count,2,0,1,count)
              +struct.pack('<'+'I'*count,*counts)+b''.join(sizes))
    rr._validate_stream_table(manifest,bytes(data))
    name=member.removesuffix('.rrtex').replace('/','\\').encode()+b'\0'
    raw=rc.rebuild(doc,lambda c:manifest if c.tag==b'TMAN' else bytes(data) if c.tag==b'TDAT'
                   else rc.Rename(name) if c.tag==b'TXTR' else None)
    return raw


def byte(values):
    return np.clip(np.rint(values),0,255).astype(np.uint8)


def field(rng,size,scale):
    low=rng.integers(0,256,(scale,scale),dtype=np.uint8)
    return np.asarray(Image.fromarray(low).resize((size,size),Image.Resampling.BICUBIC),np.float32)/255-.5


def paint(name,source,old_mask):
    """Bake pigment, mineral variation, relief and roughness per material tile."""
    rng=np.random.default_rng(91341+list(PALETTES).index(name))
    y,x=np.mgrid[0:TILE,0:TILE]
    u,v=(x+.5)/TILE,(y+.5)/TILE
    colors=[np.array(list(bytes.fromhex(c)),np.float32) for c in PALETTES[name]]
    plaster,brick,stone,timber,neutral,cloth,roof,earth,glaze,carving=colors
    palette=(plaster,brick,stone,timber,neutral,cloth,roof,earth,
             np.array([79,86,52]),stone*.83,glaze,plaster*.86,np.array([77,72,64]),
             earth*.72,carving,brick*.88)
    h=TILE*4
    albedo=np.empty((h,h,3),np.uint8)
    relief=np.empty((h,h),np.float32)
    roughness=np.empty((h,h),np.uint8)
    metallic=np.zeros((h,h),np.uint8)
    mask=np.zeros((h,h),np.uint8)
    normal=np.empty((h,h,3),np.uint8)
    for i,kind in enumerate(MATERIALS):
        ix,iy=i%4,i//4
        crop=(ix*TILE,iy*TILE,(ix+1)*TILE,(iy+1)*TILE)
        sl=np.s_[iy*TILE:(iy+1)*TILE,ix*TILE:(ix+1)*TILE]
        orig=np.asarray(source.crop(crop).convert('L'),np.float32)
        grain=rng.normal(0,2.6,(TILE,TILE)).astype(np.float32)
        weather=field(rng,TILE,8)
        fine=field(rng,TILE,43)
        variation=(orig-np.median(orig))*.50+weather*25+fine*12+grain
        height=fine*.30+weather*.13+grain*.012
        color=np.broadcast_to(palette[i],(TILE,TILE,3)).copy().astype(np.float32)
        rough=184+weather*16+fine*8
        if kind in ('brick','stone','rubble','roof'):
            rows,columns=(13,13) if kind=='roof' else (19,12) if kind=='brick' else (11,8)
            row=np.floor(v*rows).astype(int)
            shifted=u*columns+(row%2)*.5
            col=np.floor(shifted).astype(int)
            fx,fy=shifted%1,v*rows%1
            edge=np.minimum(np.minimum(fx,1-fx),np.minimum(fy,1-fy))
            grout=np.clip(edge/(.072 if kind=='roof' else .067),0,1)
            block=rng.uniform(-17,16,(rows,columns+1))[row,col]
            variation+=(block-22*(1-grout)+6*np.sin(np.pi*fy)*grout)
            height+=grout*.86+np.sin(np.pi*fy)*.31
            rough=183+18*(1-grout)+weather*19
            if kind=='roof':
                accent=((row+col)%7==0) | (row%7==0)
                if name in ('ali_qapu_palace','gundeshapur','samarkand_bazaar'):
                    color[accent]=glaze*.82+carving*.18
                    accent_core=accent&(fx>.29)&(fx<.71)&(fy>.34)&(fy<.66)
                    color[accent_core]=carving
                rough-=18*grout
                # Inset owner-colour glaze / fabric panels. Grout and the
                # detailed borders retain the architectural palette.
                margin=(1-ROOF_DYE[name])/4
                dye=(fx>margin)&(fx<1-margin)&(fy>margin)&(fy<1-margin)
                if name in ('gundeshapur','samarkand_bazaar'):
                    dye &= ~(accent & (fx>.24)&(fx<.76)&(fy>.31)&(fy<.69))
                mask[sl]=255*dye
        elif kind in ('timber','owner','cloth','paper'):
            if kind=='timber':
                bend=np.sin(v*16+weather*3)*.012
                grainline=np.cos((u+bend)*np.pi*116+fine*1.8)
                seams=np.abs(((u*5)%1)-.5)>.476
                variation+=grainline*6-19*seams
                height+=grainline*.18-1.0*seams
                rough=167+fine*17+15*seams
                if name=='assassin_brotherhood':
                    # Raised structural timber carries the dyed finish.
                    mask[sl]=255*(~seams)
            else:
                weave=(np.cos(u*2*np.pi*104)+np.sin(v*2*np.pi*113))*.5
                variation+=weave*5
                height+=weave*.19
                rough=198+weather*12
                if kind=='owner':
                    mask[sl]=np.maximum(np.asarray(old_mask.crop(crop)),np.where((u>.025)&(u<.975)&(v>.025)&(v<.975),239,0)).astype(np.uint8)
        elif kind in ('ink','carving'):
            a=(u*8)%1-.5
            b=(v*8)%1-.5
            diamond=np.abs(a)+np.abs(b)
            inlay=(diamond>.25)&(diamond<.34)
            center=(a*a+b*b)<.023
            color[inlay]=carving*.92 if kind=='ink' else glaze
            color[center]=glaze*.77 if kind=='carving' else plaster*.91
            height+=inlay*.58+center*.25
            variation-=8*(diamond>.44)
            rough=156+weather*16
        elif kind=='plaster':
            variation+=field(rng,TILE,21)*10
            pores=(fine<-.25)
            height-=pores*.22
            rough=197+weather*15
            if name=='assassin_brotherhood':
                mask[sl]=255*((v%(.25)<.062)&(u>.12)&(u<.88))
        elif kind=='metal':
            fine_lines=np.sin(u*2*np.pi*25+fine*3)
            variation+=fine_lines*6
            height+=fine_lines*.14
            rough=145+weather*19
            metallic[sl]=byte(176+weather*34)
        elif kind in ('earth','grime'):
            variation+=field(rng,TILE,74)*12
            rough=211+fine*18
        rgb=byte(color+variation[:,:,None])
        m=mask[sl]>=128
        luma=rgb.astype(np.float32)@np.array([.2126,.7152,.0722],np.float32)
        rgb[m]=byte(np.clip(luma[m]*.58+24,38,118))[:,None]
        albedo[sl]=rgb
        relief[sl]=height
        roughness[sl]=byte(rough)
        dy,dx=np.gradient(height)
        n=np.dstack((-dx*.50,-dy*.50,np.ones_like(dx)))
        n/=np.linalg.norm(n,axis=2)[:,:,None]
        normal[sl]=byte((n*.5+.5)*255)
    return albedo,normal,roughness,metallic,mask,relief


def get_chunks(raw):
    return [c for c in rc.walk(rc.parse(raw).roots) if c.tag==b'MESH']


def surfaces(raw):
    bary=np.array([[1/3,1/3,1/3],[.6,.2,.2],[.2,.6,.2],[.2,.2,.6]])
    for mesh in get_chunks(raw):
        for lod,chunk in enumerate(x for x in mesh.children if x.tag==b'LOD '):
            for g in (x for x in chunk.children if x.tag==b'GEOM'):
                head=next(x.payload for x in g.children if x.tag==b'GOHD')
                name,at=rc.read_lp_string(head,0)
                _,at=rc.read_lp_string(head,at)
                effect,at=rc.read_lp_string(head,at)
                stream,_=rc.read_lp_string(head,at)
                assert effect=='unit' and stream=='UnitDataStream'
                v,i=[c.payload for c in g.children if c.tag==b'GEOB']
                n,_,stride,_=struct.unpack_from('<4I',v)
                count,_,isize,_=struct.unpack_from('<4I',i)
                assert stride==28 and isize in (2,4)
                xyz=np.ndarray((n,3),'<f2',v,16,(stride,2)).astype(np.float32)
                uv=np.ndarray((n,2),'<f2',v,28,(stride,2)).astype(np.float32)
                faces=np.frombuffer(i,'<u'+str(isize),count,offset=16).reshape(-1,3)
                points=xyz[faces]
                area=np.linalg.norm(np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]),axis=1)*.5
                uv_points=np.einsum('sa,fad->fsd',bary,uv[faces]).reshape(-1,2)
                height=(points[:,:,1] @ bary.T).ravel()
                yield name,lod,uv_points,np.repeat(area/4,4),height


def coverage(geometry, mask):
    result=defaultdict(lambda:np.zeros(3))
    h,w=mask.shape
    for name,lod,uv,area,height in surfaces(geometry):
        xi=np.floor(uv[:,0]*w).astype(np.int64)%w
        yi=np.floor(uv[:,1]*h).astype(np.int64)%h
        owner=mask[yi,xi]>=128
        result[(name[:3],lod)]+= (area.sum(),area[owner].sum(),area[owner&(height<.38)].sum())
    return {f'{state}-LOD{lod+1}':{'owner_percent':round(float(100*col/total),2),
                                  'near_ground_owner_percent':round(float(100*low/total),3)}
            for (state,lod),(total,col,low) in sorted(result.items()) if total}


def generate(repo,out):
    native=repo/'inputs/native'
    prior=repo/'docs/update_013'
    baseline=json.loads(gzip.decompress((prior/'baseline-members.json.gz').read_bytes()))['members']
    template=(native/ART/'ali_qapu_palace/albedo.rrtex').read_bytes()
    result={}
    for name in PALETTES:
        folder=f'{MODEL}/{name}/m'
        material=(prior/'materials'/(name+'.rrmaterial')).read_bytes()
        geometry=(native/(folder+'.rrgeom')).read_bytes()
        assert baseline[folder+'.rrmaterial']['sha256']==digest(material)
        assert baseline[folder+'.rrgeom']['sha256']==digest(geometry)
        old=mv.material_slots(material)
        maps={}
        for slot in ('albedoTexture','normalMap','metalTex','patternTex'):
            member=old['textures'][slot].replace('\\','/').lower()
            raw=(native/member).read_bytes()
            assert baseline[member]['sha256']==digest(raw)
            maps[slot]=raw
        # Work in the original authored PNG orientation. Native textures are
        # stored flipped, while the released UV0 remains in file space.
        albedo_src=Image.fromarray(rgba(maps['albedoTexture'])[::-1,:,:3]).resize((TILE*4,TILE*4),Image.Resampling.BICUBIC)
        original_mask=rgba(maps['patternTex'])
        mask_src=Image.fromarray(original_mask[::-1,:,0]).resize(albedo_src.size,Image.Resampling.NEAREST)
        a,n,r,m,mask,height=paint(name,albedo_src,mask_src)
        # Native unit shader: normal=(emissive, Ny, AO, Nx),
        # metal=(metalness, dielectric, height, roughness).
        mat_maps=np.asarray(Image.fromarray(rgba(maps['metalTex'])[::-1]).resize(albedo_src.size)).copy()
        norm_maps=np.asarray(Image.fromarray(rgba(maps['normalMap'])[::-1]).resize(albedo_src.size)).copy()
        norm_maps[:,:,1]=n[:,:,1]
        norm_maps[:,:,3]=n[:,:,0]
        norm_maps[:,:,2]=np.minimum(norm_maps[:,:,2],byte(246+np.clip(height,-1,0)*19))
        mat_maps[:,:,0]=m
        mat_maps[:,:,2]=byte(128+height*23)
        mat_maps[:,:,3]=r
        pat=np.zeros((*mask.shape,4),np.uint8)
        pat[:,:,0]=mask
        author=out/'authoring/landmarks_013'/name
        author.mkdir(parents=True,exist_ok=True)
        for label,im in [('albedo',a),('normal',n),('roughness',r),('metalness',m),('pattern',pat[:,:,:3])]:
            Image.fromarray(im).save(author/(label+'.png'),compress_level=4)
        emitted={}
        masks=None
        for slot,role,image in [('albedoTexture','albedo',a),('normalMap','normal',norm_maps),
                                ('metalTex','surface',mat_maps),('patternTex','owner',pat)]:
            member=f'{ART}/{name}/{role}.rrtex'
            raw=encode(template if slot=='albedoTexture' else maps[slot],member,image[::-1],
                       srgb=slot=='albedoTexture')
            target=out/'overlay'/member
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
            decoded=rgba(raw)
            assert decoded.shape[:2]==image.shape[:2]
            if slot=='patternTex':
                assert decoded[:,:,1:].max()==0
                masks=decoded[:,:,0]
            emitted[slot]=member
        rewritten=mv.rewrite_material(material,{k:v.replace('/','\\') for k,v in emitted.items()},{})
        assert mv.material_slots(rewritten)['parameters']==old['parameters']
        assert {k:v for k,v in mv.material_slots(rewritten)['textures'].items() if k not in emitted}=={k:v for k,v in old['textures'].items() if k not in emitted}
        changed=out/'overlay'/(folder+'.rrmaterial')
        changed.parent.mkdir(parents=True,exist_ok=True)
        changed.write_bytes(rewritten)
        before=coverage(geometry,original_mask[:,:,0])
        after=coverage(geometry,masks)
        healthy=[v['owner_percent'] for k,v in after.items() if k.startswith('s00')]
        assert len(healthy)==3 and all(5<=v<=25 for v in healthy),(name,healthy)
        result[name]={'material':folder+'.rrmaterial','textures':emitted,
                      'healthy_before':[v['owner_percent'] for k,v in before.items() if k.startswith('s00')],
                      'healthy_after':healthy,'all_states':after,'original_geometry_sha256':digest(geometry)}
        print(name,result[name]['healthy_before'],healthy,flush=True)
    (out/'coverage.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    generate(args.repo,args.output)
