"""Compact current inspection sheets; unchanged source render pixels."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;P=ROOT/'previews'
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
def sheet(items,name,columns=3,size=(310,340)):
    w,h=size;rows=(len(items)+columns-1)//columns
    im=Image.new('RGB',(columns*w,rows*h),(43,46,48));d=ImageDraw.Draw(im)
    for j,(filename,label) in enumerate(items):
        path=P/filename
        if not path.exists():raise FileNotFoundError(path)
        src=Image.open(path).convert('RGBA');src.thumbnail((w,h-30));x=j%columns*w+(w-src.width)//2;y=j//columns*h+28
        im.paste(src,(x,y),src);d.text((j%columns*w+8,j//columns*h+7),label,font=FONT,fill=(235,230,219))
    im.save(P/name);print(name)
if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'solid'
    if mode=='solid':
        for age in range(1,5):
            sheet([(f'solid_A{age}{body}_{d}.png',f'A{age}{body} {d}') for body in 'abc' for d in ['front','back','left','right','top','bottom']],f'solid_age{age}.png',6,(230,258))
    elif mode=='materials':
        sheet([(f'A{age}{body}_healthy_LOD0_blue.png',f'Age {age} / plan {body}') for age in range(1,5) for body in 'abc'],'02-all-healthy-bodies.png',3,(360,390))
        states=['healthy','damage_1','damage_2','damage_3','damage_4','damage_5','ruins']
        sheet([(f'{key}_{state}_LOD0_blue.png',f'{key} {state}') for key in ['A1a','A4a'] for state in states],'03-damage-sequences.png',7,(280,310))
        sheet([(f'{key}_construct_{stage}.png',f'{key} {stage}') for key in ['A1a','A4a'] for stage in ['foundation','walls','vaults','finish']],'04-construction.png',4,(300,330))
        sheet([(f'A{age}a_healthy_LOD{lod}_blue.png',f'Age {age} LOD{lod}') for age in range(1,5) for lod in [0,1,2]],'05-lods.png',3,(330,360))
        sheet([(f'{key}_healthy_LOD0_{colour}.png',f'{key} owner {colour}') for key in ['A1a','A4a'] for colour in ['blue','red','yellow']],'06-owner-colour.png',3,(330,360))
    elif mode=='coverage':
        for age in range(1,5):
            for body in 'abc':
                key=f'A{age}{body}'
                states=['healthy',*[f'damage_{n}' for n in range(1,6)],'ruins']
                items=[(f'coverage_{key}_{state}_LOD{lod}.png',f'{state} / LOD{lod}') for lod in [0,1,2] for state in states]
                items += [(f'coverage_{key}_construct_{stage}.png','construct '+stage) for stage in ['foundation','walls','vaults','finish']]
                items += [(f'coverage_{key}_{state}_LOD{lod}.png',f'{state} / LOD{lod}') for state in ['preview','targeting'] for lod in [0,1,2]]
                sheet(items,'coverage-'+key+'.png',7,(190,214))
