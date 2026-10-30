"""Original deterministic source atlas, not a sampled or copied game texture."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'textures'
TILES=['plaster','brick','stone','timber','owner','cloth','roof','earth',
       'leaves','rubble','ink','paper','metal','grime','carving','pottery']
BASE=[(198,180,141),(152,92,62),(149,137,109),(87,62,40),
      (204,198,174),(171,144,97),(170,137,94),(122,104,73),
      (94,108,59),(151,126,93),(50,47,38),(205,189,140),
      (94,88,70),(113,99,72),(211,193,151),(165,100,64)]

def main():
    OUT.mkdir(parents=True,exist_ok=True);S=512;N=2048;rng=np.random.default_rng(72871)
    alb=Image.new('RGB',(N,N));rough=Image.new('L',(N,N));height=Image.new('L',(N,N));pat=Image.new('RGB',(N,N));metal=Image.new('L',(N,N))
    for k,(kind,base) in enumerate(zip(TILES,BASE)):
        noise=rng.normal(0,2.1,(S,S,1));low=rng.random((16,16))
        soft=np.array(Image.fromarray((low*255).astype('uint8')).resize((S,S),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(11)))
        grain=(soft[:,:,None]/255-.5)*18+noise
        pixels=np.clip(np.array(base)[None,None,:]+grain,0,255).astype('uint8')
        t=Image.fromarray(pixels);a=ImageDraw.Draw(t)
        h=Image.new('L',(S,S),128);hd=ImageDraw.Draw(h)
        rr=Image.fromarray(np.clip(211+noise[:,:,0]*2,0,255).astype('uint8'))
        if kind=='brick':
            for row in range(16):
                yy=row*32;a.rectangle((0,yy,S,yy+3),fill=(115,91,65));hd.rectangle((0,yy,S,yy+3),fill=94)
                for xx in range(-64,S+64,128):
                    x=xx+(64 if row%2 else 0);a.rectangle((x,yy,x+3,yy+32),fill=(113,89,63));hd.rectangle((x,yy,x+3,yy+32),fill=94)
                    a.line((x+5,yy+5,x+120,yy+5),fill=(174,116,80),width=2)
        if kind in ('stone','rubble'):
            for row in range(4):
                yy=row*128;a.line((0,yy,S,yy),fill=(107,102,82),width=3);hd.line((0,yy,S,yy),fill=90,width=4)
                for xx in range(-96,S+96,192):
                    x=xx+(96 if row%2 else 0);a.line((x,yy,x,yy+128),fill=(107,102,82),width=3)
        if kind=='roof':
            for yy in range(0,S,32):
                a.line((0,yy,S,yy),fill=(135,104,74),width=3);hd.line((0,yy,S,yy),fill=103,width=3)
            for xx in range(0,S,96):a.line((xx,0,xx,S),fill=(178,145,101),width=2)
        if kind=='timber':
            for j in range(90):
                x=int(rng.integers(0,S));a.line((x,0,x+int(rng.integers(-8,9)),S),fill=(65+j%20,48+j%12,31+j%10),width=1+j%2)
            for x in (128,256,384):a.line((x,0,x,S),fill=(50,39,29),width=4)
        if kind in ('cloth','owner'):
            for x in range(0,S,5):a.line((x,0,x,S),fill=tuple(max(0,c-7) for c in base),width=1)
            for yy in range(0,S,7):a.line((0,yy,S,yy),fill=tuple(min(255,c+4) for c in base),width=1)
            if kind=='cloth':
                for yy in (28,45,466,483):a.line((0,yy,S,yy),fill=(101,83,52),width=6)
        if kind=='paper':
            for y in range(55,470,31):
                a.line((35,y,470-int(rng.integers(0,80)),y-1),fill=(110,92,60),width=2)
        if kind=='leaves':
            for j in range(130):
                x,y=map(int,rng.integers(0,S,2));a.ellipse((x,y,x+13,y+35),fill=(66+j%30,82+j%30,37+j%15))
        if kind in ('plaster','carving','pottery'):
            for j in range(150):
                x,y=map(int,rng.integers(0,S,2));r=int(rng.integers(1,5));a.ellipse((x,y,x+r,y+r),fill=tuple(max(0,c-13) for c in base))
        if kind=='carving':
            for x in range(48,S,96):
                a.ellipse((x-23,230,x+23,276),outline=(160,139,102),width=6)
                a.ellipse((x-11,242,x+11,264),fill=(190,170,130))
        if kind in ('earth','grime'):
            for j in range(550):
                x,y=map(int,rng.integers(0,S,2));c=(103+j%26,88+j%20,62+j%17);a.ellipse((x,y,x+int(j%5+1),y+int(j%4+1)),fill=c)
        xy=(k%4*S,k//4*S);alb.paste(t,xy);rough.paste(rr,xy);height.paste(h,xy)
        if kind=='owner':
            mask=Image.new('RGB',(S,S),(255,0,0));md=ImageDraw.Draw(mask)
            # Sparse worn fibres, not a baked player palette.
            for j in range(330):
                x,y=map(int,rng.integers(0,S,2));md.line((x,y,x+2,y+int(j%6+1)),fill=(150,0,0),width=1)
            pat.paste(mask,xy)
        if kind=='metal':metal.paste(Image.new('L',(S,S),170),xy)
    h=np.array(height,dtype=np.float32)/255;dy,dx=np.gradient(h);n=np.dstack((-dx*.6,-dy*.6,np.ones_like(h)));n/=np.linalg.norm(n,axis=2)[:,:,None]
    normal=Image.fromarray(np.clip((n*.5+.5)*255,0,255).astype('uint8'))
    for name,im in [('albedo',alb),('normal',normal),('roughness',rough),('metalness',metal),('owner_mask',pat)]:im.save(OUT/(name+'.png'),optimize=True)
    (OUT/'atlas-layout.json').write_text(json.dumps({'size':N,'tile_size':S,'tiles':{name:[i%4,i//4] for i,name in enumerate(TILES)},'authorship':'Original deterministic painted atlas from make_atlas.py; no external image dependency','owner_mask':'R owner colour, G/B zero; neutral albedo; source-only preview'},indent=2)+'\n')
    print('ATLAS_READY',N,len(TILES))

if __name__=='__main__':main()
