"""Compact review sheets from the current Blender preview set."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'previews'
def sheet(name,items,columns=3):
    w=480;h=460;rows=(len(items)+columns-1)//columns;im=Image.new('RGB',(columns*w,rows*h+70),'#e9e0cf');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    d.text((18,17),'GRAND CARAVANSERAI / '+name.replace('_',' '),font=font,fill='#3c3226')
    for i,(file,label) in enumerate(items):
        p=OUT/(file+'.png') if not file.startswith('../') else OUT/file
        with Image.open(p) as pic:
            pic=pic.convert('RGB');pic.thumbnail((w-16,h-50));x=(i%columns)*w+(w-pic.width)//2;y=70+(i//columns)*h;im.paste(pic,(x,y));d.text(((i%columns)*w+12,y+h-40),label,font=font,fill='#3c3226')
    im.save(OUT/(name+'.png'),optimize=True)
def main():
    sheet('01_states',[(f'state_{s}',s.replace('_',' ').title()) for s in ['healthy','damage_1','damage_2','damage_3','damage_4','damage_5','ruins']])
    sheet('02_construction',[(f'construction_{s}',s.title()) for s in ['foundation','walls','vaults','finish']],2)
    sheet('03_owner_colours',[(f'owner_{c}',c.title()+' / same R mask') for c in ['red','blue','yellow']])
    sheet('04_courtyard_and_lods',[('working_courtyard','Working court'),('unloading_detail','Unloading and cargo'),('water_detail','Water / fodder'),('lod_0','LOD0'),('lod_1','LOD1 ~50%'),('lod_2','LOD2 ~25%')])
    sheet('05_orthographic',[(f'ortho_{s}',s.title()) for s in ['front','back','left','right','top','bottom']])
    sheet('06_damage_detail',[('state_damage_4','Subsidiary fractured vault'),('damage_5_reverse','Partial wing collapse'),('ruins_reverse','Low grounded ruins')])
    sheet('07_atlas',[(f'../textures/{s}.png',s.replace('_',' ').title()) for s in ['albedo','normal','roughness','metalness','owner_mask']])
    print('CONTACT_SHEETS_READY')
if __name__=='__main__':main()
