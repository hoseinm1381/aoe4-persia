"""Compact review sheets assembled from the current Blender renders."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'previews'
FONT=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22);SMALL=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)

def sheet(filename,title,entries,columns=3,cell=(600,570)):
    w,h=cell;rows=math.ceil(len(entries)/columns);im=Image.new('RGB',(w*columns,rows*h+72),(30,29,27));d=ImageDraw.Draw(im)
    d.text((20,14),title,fill=(242,229,204),font=FONT)
    d.text((20,43),'Editable source study | Blender preview | Native game integration deferred',fill=(174,170,161),font=SMALL)
    for i,(name,label) in enumerate(entries):
        img=Image.open(OUT/(name+'.png')).convert('RGB');img.thumbnail((w-12,h-44),Image.Resampling.LANCZOS)
        x=i%columns*w;y=i//columns*h+72;im.paste(img,(x+(w-img.width)//2,y+32));d.text((x+14,y+5),label,fill='white',font=SMALL)
    im.save(OUT/filename,optimize=True)

def main():
    states=['healthy',*[f'damage_{i}' for i in range(1,6)],'ruins']
    sheet('01-states.png','Gundeshapur | healthy, progressive damage and ruins',[(f'state_{s}',s.replace('_',' ').title()) for s in states]+[('ruins_reverse','Ruins | opposite view')],4,(500,470))
    sheet('02-construction.png','Gundeshapur | ordered construction assemblies',[(f'construction_{s}',f'{i+1}. '+label) for i,(s,label) in enumerate([('foundation','Foundation and ground'),('walls','Walls, piers and scaffold'),('vaults','Vaults and dome'),('finish','Plaster, textiles and working props')])],2,(750,690))
    sheet('03-owner-colours.png','Gundeshapur | one shared owner mask',[(f'owner_{c}',c.title()+' | neutral masonry') for c in ('red','blue','yellow')],3,(650,600))
    lod=json.loads((ROOT/'evidence/lod-budget.json').read_text());healthy=json.loads((ROOT/'evidence/source-checks.json').read_text())['states'][0]['triangles']
    counts={0:healthy,**{r['level']:r['triangles'] for r in lod if r['state']=='healthy'}}
    sheet('04-courtyard-and-lods.png','Gundeshapur | working academy and reduced detail',[(n,label) for n,label in [('working_courtyard','Teaching, herbs and supplies'),('teaching_detail','Documents, mats and writing desk'),('herb_service_detail','Jars, herb drying and baskets')]]+[(f'lod_{l}',f'LOD {l} | {counts[l]:,} triangles') for l in (0,1,2)],3,(650,600))
    sheet('05-orthographic.png','Gundeshapur | six-direction solid inspection',[(f'ortho_{s}',s.title()) for s in ('front','back','left','right','top','bottom')],3,(600,560))
    sheet('06-damage-detail.png','Gundeshapur | partial wing collapse and grounded ruins',[(s,label) for s,label in [('state_damage_4','Damage 4 | fractured subsidiary vault'),('damage_5_reverse','Damage 5 | main iwan retained'),('state_ruins','Ruins | approximately 29% healthy height'),('ruins_reverse','Ruins | vault and dome fragments')]],2,(750,690))
    # Atlas review is a contact layout, not an edited texture source.
    im=Image.new('RGB',(1500,1080),(30,29,27));d=ImageDraw.Draw(im);d.text((18,10),'Shared 2048 x 2048 atlas | original procedural texture sources',font=FONT,fill='white')
    for i,n in enumerate(('albedo','normal','roughness','metalness','owner_mask')):
        a=Image.open(ROOT/'textures'/(n+'.png')).convert('RGB');a.thumbnail((480,480));x=i%3*500;y=i//3*510+52;im.paste(a,(x+10,y+30));d.text((x+12,y+3),n,font=SMALL,fill='white')
    im.save(OUT/'07-atlas.png',optimize=True)
if __name__=='__main__':main()
