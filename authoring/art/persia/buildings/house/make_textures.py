"""House-specific original painted surfaces. No photographs/game texture samples."""
from pathlib import Path
import sys,json,random
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'_shared'))
from atlas_source import generate

def main():
    generate(ROOT,270110)
    p=ROOT/'textures/albedo.png';im=Image.open(p).convert('RGB');tile=im.crop((0,0,512,512));px=tile.load()
    # The wall's lower UV edge carries soil splash, fading gradually upward.
    for y in range(512):
        shade=max(0,(y-408)/104)*.18
        for x in range(512):
            r,g,b=px[x,y];px[x,y]=(int(r*(1-shade)),int(g*(1-shade)),int(b*(1-shade*.8)))
    rr=random.Random(713);d=ImageDraw.Draw(tile)
    for j in range(22):
        x=rr.randrange(512);y=rr.randrange(80,460)
        pts=[(x,y)]
        for k in range(rr.randrange(2,5)):x+=rr.randrange(-5,6);y+=rr.randrange(3,11);pts.append((x,y))
        d.line(pts,fill=(168,150,119),width=1)
    im.paste(tile,(0,0))
    # Earth roofs: granular clay, slight uneven wear, no modern tile-grid pattern.
    roof=Image.new('RGB',(512,512));pixels=roof.load()
    for y in range(512):
        for x in range(512):
            n=rr.randrange(-7,8);pixels[x,y]=(167+n,135+n,94+n)
    rd=ImageDraw.Draw(roof)
    for j in range(110):
        x,y=rr.randrange(512),rr.randrange(512);r=rr.randrange(1,5)
        rd.ellipse((x,y,x+r,y+r),fill=(150,120,82))
    im.paste(roof,(2*512,512));im.save(p,optimize=True)
    # Override roof normals to a quiet earthen surface, not the generic tile grid.
    normal=Image.open(ROOT/'textures/normal.png').convert('RGB');normal.paste(Image.new('RGB',(512,512),(128,128,255)),(2*512,512));normal.save(ROOT/'textures/normal.png',optimize=True)
    (ROOT/'textures/house-authorship.json').write_text(json.dumps({'source':'make_textures.py plus retained _shared/atlas_source.py','original_painting':True,'changes':['soil splash gradient and tiny plaster cracks','granular clay roof, no tile grid'],'native_shader_validation':'deferred'},indent=2)+'\n')
    print('HOUSE_TEXTURES_READY')

if __name__=='__main__':main()
