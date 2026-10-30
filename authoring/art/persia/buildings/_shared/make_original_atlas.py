"""Original editable family atlas sources. Refuses to overwrite manual pixels."""
from pathlib import Path
import sys,json,hashlib,random,re
from PIL import Image,ImageDraw
from atlas_source import generate
ART=Path(__file__).resolve().parent.parent
MAPS=['albedo','normal','roughness','metalness','owner_mask']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(slug,seed):
    if not re.fullmatch('[a-z_]+',slug) or slug=='house':raise ValueError('Use an explicitly owned non-House family slug')
    root=ART/slug
    if not (root/'recipe.py').is_file():raise ValueError('Family recipe must exist before painting its surfaces')
    out=root/'textures';out.mkdir(exist_ok=True);receipt=out/'original-atlas-source.json'
    existing=[out/(n+'.png') for n in MAPS if (out/(n+'.png')).exists()]
    if existing:
        if not receipt.is_file():raise RuntimeError('Existing image has no owned-generation receipt; preserve and inspect before repainting')
        known=json.loads(receipt.read_text())['image_sha256']
        for p in existing:
            if sha(p)!=known.get(p.name):raise RuntimeError('Manual/external texture edit detected: '+str(p))
    generate(root,seed)
    # A continuous granular clay surface works for earthen flat/vaulted roofs.
    # Tilework or timber roof anatomy belongs in each original family recipe.
    rr=random.Random(seed+710);roof=Image.new('RGB',(512,512));pixels=roof.load()
    for y in range(512):
        for x in range(512):
            n=rr.randrange(-7,8);pixels[x,y]=(167+n,135+n,94+n)
    d=ImageDraw.Draw(roof)
    for j in range(110):
        x,y=rr.randrange(512),rr.randrange(512);r=rr.randrange(1,5);d.ellipse((x,y,x+r,y+r),fill=(150,120,82))
    albedo=Image.open(out/'albedo.png').convert('RGB');albedo.paste(roof,(1024,512));albedo.save(out/'albedo.png',optimize=True)
    normal=Image.open(out/'normal.png').convert('RGB');normal.paste(Image.new('RGB',(512,512),(128,128,255)),(1024,512));normal.save(out/'normal.png',optimize=True)
    files={n+'.png':sha(out/(n+'.png')) for n in MAPS}
    receipt.write_text(json.dumps({'schema':'persia-original-atlas/1','family':slug,'seed':seed,'size':[2048,2048],
                                  'source_files':{'_shared/atlas_source.py':sha(ART/'_shared/atlas_source.py'),'_shared/make_original_atlas.py':sha(Path(__file__))},
                                  'image_sha256':files,'original_painted_pixels':True,'stock_or_photographic_pixels_used':False,
                                  'owner_colour':'Neutral source textile plus owner mask; red/blue/yellow is a preview shader parameter, not baked albedo.',
                                  'manual_edit_policy':'Retain edited PNG originals. Repainting refuses changed image hashes; geometry rebuilds consume these retained images directly.',
                                  'native_shader':'unverified; source-only'},indent=2)+'\n')
    print('ORIGINAL_FAMILY_ATLAS_READY',slug)

if __name__=='__main__':main(sys.argv[1],int(sys.argv[2]))
