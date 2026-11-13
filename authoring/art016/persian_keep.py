"""Paint the Keep's masonry and glazed parapets, retaining its lifecycle meshes."""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image
from lifecycle_repair import stage,repos,readback,put
from mesh_surface import mesh,s,rc,mv
sys.path.insert(0,str(repos/'aoe4-korea/tools'))
from art037.srgb_landmarks import encode_srgb_bc1
from art016.repair import encode_bc3
from garrison_shared import rrtex_decoder as rr
from io import BytesIO

def decode(path,work):
    rr.decode_rrtex(path,work,validate_stream=True)
    return np.array(Image.open(work).convert('RGBA'))

def levels(image):
    for i in range(max(image.size).bit_length()):
        size=tuple(max(1,d>>i) for d in image.size)
        channels=tuple(c.resize(size,Image.Resampling.BOX) for c in image.split())
        with BytesIO() as stream:
            Image.merge('RGBA',channels).save(stream,format='DDS',pixel_format='DXT5')
            yield *size,stream.getvalue()[128:]

def native_texture(pixels,key,name,base,out,template):
    image=Image.fromarray(pixels)
    image.save(out/(name+'-'+key+'.png'))
    fmt=19 if key=='albedo' else 22
    data=encode_srgb_bc1(template,name,image) if fmt==19 else encode_bc3(template,name.removesuffix('.rrtex'),list(levels(image)))
    return data

def patch_keep():
    stage_out=stage/'persia'
    masters=stage_out/'masters';masters.mkdir(parents=True,exist_ok=True)
    base=readback('persia')
    member='art/ps100/b/keep_a3/m.rrmaterial'
    raw=(base/member).read_bytes()
    tex=mv.material_slots(raw)['textures']
    prior={k:base/tex[k].replace(chr(92),'/') for k in ('albedoTexture','patternTex')}
    img=decode(prior['albedoTexture'],stage_out/'original-albedo.dds')
    old=decode(prior['patternTex'],stage_out/'original-pattern.dds')
    out=img.copy()
    mask=np.zeros_like(out);mask[:,:,:]=0
    n=img.shape[0]//4
    rng=np.random.default_rng(317)
    x,y=np.meshgrid(np.arange(n),np.arange(n))
    for (u,v),color in {(0,3):(167,105,65),(2,3):(114,113,101),(2,2):(51,108,111),(0,2):(139,139,139),(3,3):(78,49,34),(3,2):(123,106,87),(1,3):(156,93,67)}.items():
        rows=slice((3-v)*n,(4-v)*n); cols=slice(u*n,(u+1)*n)
        original=img[rows,cols,:3].astype(float).mean(2)
        grain=(original-np.median(original))*.75+rng.normal(0,2,original.shape)
        if (u,v)==(0,3):
            stagger=(x+(y//32%2)*24)%48
            joints=(y%32<2)|(stagger<2)
            grain+=np.where(joints,-30,8*np.sin((x+y)/45))
        if (u,v)==(2,2):
            diamond=(abs(x%32-16)+abs(y%32-16))<11
            grain+=np.where(diamond,25,-8)
        out[rows,cols,:3]=np.clip(np.array(color)+grain[:,:,None],0,255).astype(np.uint8)
        if (u,v)==(0,2):mask[rows,cols,0]=255
        if (u,v)==(0,3):
            # A repeating glazed frieze follows the upper band of the wall atlas.
            painted=(y>=82)&(y<109)
            motif=((x//12+y//6)%4)==0
            mask[rows,cols,0][painted]=255
            band=np.where(motif,166,125).astype(np.uint8)
            out[rows,cols,:3][painted]=band[painted,None]
    coverage=[]
    for _,name,xyz,uv,faces in mesh((base/member.replace('.rrmaterial','.rrgeom')).read_bytes()):
        if name!='s00p00': continue
        p=xyz[faces];area=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)*.5
        bary=np.array([[1/3,1/3,1/3],[.6,.2,.2],[.2,.6,.2],[.2,.2,.6]])
        samples=np.einsum('sa,fad->fsd',bary,uv[faces]).reshape(-1,2)
        i=np.floor(samples*img.shape[0]).astype(int)%img.shape[0]
        i[:,1]=img.shape[0]-1-i[:,1]
        area=np.repeat(area/4,4)
        coverage.append(float(area[mask[i[:,1],i[:,0],0]>127].sum()/area.sum()))
    names={'albedoTexture':'art/ps116/keep/masonry.rrtex','patternTex':'art/ps116/keep/glazed-owner.rrtex'}
    template=(repos/'aoe4-korea/inputs/native/art/kr036/architecture/gyeongbok_palace.rrtex').read_bytes()
    for key,pixels in [('albedoTexture',out),('patternTex',mask)]:
        image=Image.fromarray(pixels)
        image.save(masters/(('masonry' if key=='albedoTexture' else 'glazed-owner')+'.png'))
        member_name=names[key]
        data=encode_srgb_bc1(template,member_name,image) if key=='albedoTexture' else encode_bc3(prior[key].read_bytes(),member_name.removesuffix('.rrtex'),list(levels(image)))
        put('persia',member_name,data)
    edited=mv.rewrite_material(raw,{k:v.replace('/',chr(92)) for k,v in names.items()},{})
    assert all(mv.material_slots(edited)['textures'][k].replace(chr(92),'/')==v for k,v in names.items())
    put('persia',member,edited)
    (masters/'keep-coverage.json').write_text(json.dumps({'healthy_owner_surface_fraction':coverage[0]},indent=2))
    print('Keep owner surface',coverage[0],flush=True)

if __name__=='__main__':patch_keep()

