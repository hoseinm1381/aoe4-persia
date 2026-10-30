"""Assemble unchanged QA renders on a labelled neutral canvas."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
def sheet(items,name):
    w,h=420,450;im=Image.new('RGB',(w*3,h*2),(43,46,48));d=ImageDraw.Draw(im)
    for j,(filename,label) in enumerate(items):
        src=Image.open(ROOT/'previews'/filename).convert('RGBA');src.thumbnail((w,h-40));x=j%3*w+(w-src.width)//2;y=j//3*h+38
        im.paste(src,(x,y),src);d.text((j%3*w+14,j//3*h+10),label,font=FONT,fill=(235,230,219))
    path=ROOT/'previews'/name;im.save(path);print(path)
if __name__=='__main__':sheet([(f'{k}_{s}_LOD0_blue.png',label) for k,s,label in [('A1a','healthy','Age I courtyard'),('A2a','healthy','Age II vaulted range'),('A3a','healthy','Age III loft / upper vent'),('A4a','healthy','Age IV shaded upper floor'),('A4c','healthy','Age IV alternate plan'),('A1a','ruins','Age I ruins')]],'01-pilot-review.png')
