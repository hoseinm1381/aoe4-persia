"""Hash-checked single-pass family sheets from the current quick render batch."""
from pathlib import Path
import json,hashlib,sys,math
from PIL import Image,ImageDraw
ART=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(slug):
    root=ART/slug;out=root/'previews/quick';doc=json.loads((root/'evidence/quick-render-receipt.json').read_text())
    if not doc.get('passed') or doc['saved_file_sha256']!=sha(root/(slug+'.blend')):raise RuntimeError('Stale quick render master')
    for row in doc['frames']:
        if sha(out/row['file'])!=row['sha256']:raise RuntimeError('Changed review frame '+row['file'])
    by_label={r['label']:r for r in doc['frames']};keys=json.loads((root/'family.json').read_text())['expected_body_keys'];sheets=[]
    def sheet(name,items,columns,tile=220):
        canvas=Image.new('RGB',(columns*tile,math.ceil(len(items)/columns)*(tile+24)),(42,45,45));draw=ImageDraw.Draw(canvas)
        for i,(label,row) in enumerate(items):
            x=(i%columns)*tile;y=(i//columns)*(tile+24);draw.text((x+5,y+4),label,fill=(235,235,227))
            im=Image.open(out/row['file']).convert('RGBA');im.thumbnail((tile,tile));canvas.paste(im,(x+(tile-im.width)//2,y+24+(tile-im.height)//2),im)
        canvas.save(out/name);sheets.append({'file':name,'sha256':sha(out/name)})
    items=[]
    for key in keys:
        for suffix in ('healthy_blue','damage_5_material','ruins_material','healthy_LOD1_state_solid','healthy_LOD2_state_solid','construct_walls_state_solid','construct_vaults_state_solid'):
            label=key+'_'+suffix;items.append((label,by_label[label]))
    sheet('family-review.png',items,7)
    sheet('owners.png',[(key+' '+colour,by_label[key+'_healthy_'+colour]) for key in keys for colour in ('blue','red','yellow')],3)
    for key in keys:
        sheet('solid-'+key+'.png',[(direction,by_label[key+'_solid_'+direction]) for direction in ('front','back','left','right','top','bottom')],3,320)
        rows=[r for r in doc['frames'] if r['body']==key and r['label'].endswith('_state_solid')]
        sheet('states-'+key+'.png',[(r['label'],r) for r in rows],5,190)
    (root/'evidence/quick-review-sheets.json').write_text(json.dumps({'passed':True,'saved_file_sha256':doc['saved_file_sha256'],
        'hash_verified_frames':len(doc['frames']),'sheets':sheets,'visual_review_completed':False},indent=2)+'\n')
    print('QUICK_SHEETS',slug,len(sheets),len(doc['frames']))
if __name__=='__main__':main(sys.argv[1])
