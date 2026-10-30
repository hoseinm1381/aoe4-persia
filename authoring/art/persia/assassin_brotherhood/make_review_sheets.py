"""Compact labeled sheets from actual Blender captures; never substitute diagrams for proof."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'previews'
def sheet(name,items,cols=3):
 w=460;h=440;rows=(len(items)+cols-1)//cols
 im=Image.new('RGB',(w*cols,h*rows),(35,37,39));d=ImageDraw.Draw(im)
 try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 except OSError:font=ImageFont.load_default()
 for i,(label,file) in enumerate(items):
  p=OUT/(file+'.png');assert p.is_file(),p
  src=Image.open(p).convert('RGB');src.thumbnail((w-12,h-45))
  x=i%cols*w;y=i//cols*h;im.paste(src,(x+(w-src.width)//2,y+32+(h-40-src.height)//2));d.text((x+12,y+8),label,font=font,fill=(237,230,209))
 im.save(OUT/(name+'.jpg'),quality=90);print('SHEET',name)
def main():
 states=['healthy']+[f'damage_{i}' for i in range(1,6)]+['ruins']
 sheet('01-states',[(s.replace('_',' ').title(),'state_'+s) for s in states])
 sheet('02-construction',[(s.title(),'construction_'+s) for s in ('foundation','walls','vaults','finish')],2)
 sheet('03-lods',[(f'LOD {i}','lod_'+str(i)) for i in range(3)])
 sheet('04-owner-colours',[(s.title(),'owner_'+s) for s in ('blue','red','yellow')])
 sheet('05-solid-views',[(s.title(),'ortho_'+s) for s in ('front','back','left','right','top','bottom')])
if __name__=='__main__':main()
