"""Assemble existing source inspection pixels; never generate missing evidence."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw,ImageFont
ART=Path(__file__).resolve().parent.parent
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)

def sheet(root,items,name,cols=3,size=(330,365)):
    w,h=size;im=Image.new('RGB',(w*cols,h*((len(items)+cols-1)//cols)),(43,46,48));d=ImageDraw.Draw(im)
    for i,(file,label) in enumerate(items):
        p=root/'previews'/file
        if not p.is_file():raise FileNotFoundError(p)
        src=Image.open(p).convert('RGBA');src.thumbnail((w,h-32));x=i%cols*w+(w-src.width)//2;y=i//cols*h+28;im.paste(src,(x,y),src);d.text((i%cols*w+8,i//cols*h+6),label,font=FONT,fill=(235,230,219))
    out=root/'previews'/name;im.save(out);print(out);return {'file':name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_frames':[f for f,l in items]}

def main(slug,mode='healthy'):
    if mode in ('coverage','closeups'):
        root=ART/slug;receipt=json.loads((root/('evidence/render-'+mode+'-receipt.json')).read_text());frames=receipt['frames']
        if receipt['saved_file_sha256']!=hashlib.sha256((root/(slug+'.blend')).read_bytes()).hexdigest():raise RuntimeError('Stale source frames')
        for f in frames:
            if hashlib.sha256((root/'previews'/f['file']).read_bytes()).hexdigest()!=f['sha256']:raise RuntimeError('Changed source frame '+f['file'])
        results=[]
        if mode=='closeups':results.append(sheet(root,[(f['file'],f['view']['name'].replace('_',' ')) for f in frames],'closeups.png',2,(480,512)))
        else:
            for key in json.loads((root/'family.json').read_text())['expected_body_keys']:
                rows=[f for f in frames if f['composition'].startswith('PSB_'+slug+'_'+key+'_')]
                results.append(sheet(root,[(f['file'],f['composition'].replace('PSB_'+slug+'_','')) for f in rows],'coverage-'+key+'.png',3))
        (root/('evidence/review-sheets-'+mode+'.json')).write_text(json.dumps({'saved_file_sha256':receipt['saved_file_sha256'],'sheets':results,'visual_review_required':True},indent=2)+'\n')
        return
    if mode!='healthy':raise ValueError('Unknown sheet mode')
    root=ART/slug;receipt=json.loads((root/'evidence/render-healthy-receipt.json').read_text());frames=receipt['frames'];results=[]
    for key in json.loads((root/'family.json').read_text())['expected_body_keys']:
        rows=[f for f in frames if f['composition']=='PSB_'+slug+'_'+key+'_healthy_LOD0']
        solids=[(f['file'],key+' / '+f['direction']) for f in rows if f['direction']!='game']
        colors=[(f['file'],key+' / owner '+f['colour']) for f in rows if f['direction']=='game']
        results.append(sheet(root,solids,'solid-'+key+'.png',3,(300,328)));results.append(sheet(root,colors,'colour-'+key+'.png'))
    items=[(f['file'],f['composition'].split('_healthy')[0].replace('PSB_'+slug+'_','')) for f in frames if f['direction']=='game' and f['colour']=='blue']
    results.append(sheet(root,items,'healthy-bodies.png',min(3,len(items))))
    (root/'evidence/review-sheets.json').write_text(json.dumps({'saved_file_sha256':receipt['saved_file_sha256'],'sheets':results,'visual_review_required':True},indent=2)+'\n')

if __name__=='__main__':main(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'healthy')
