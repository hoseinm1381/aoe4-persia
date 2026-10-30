"""Read installed stock sources; all receipts/decodes stay in the asset folder."""
from pathlib import Path
import ast, collections, hashlib, json, os, sqlite3, statistics, struct, subprocess, sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
TEMP=Path('F:/aoe_4_temp/Temp_before_github_push')
REPO=Path('F:/aoe_4_temp/community_civilization_pack_garrison_aoe4')
EXT=Path(os.environ['APPDATA'])/'Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'
ARCH=EXT/'bin/sga-archiver.exe'; CORE=EXT/'bin/core/garrison-core.exe'
GAME=Path('E:/Games/steamapps/common/Age of Empires IV')
ATTRIB=GAME/'cardinal/archives/Attrib.sga'; DATA=GAME/'cardinal/archives/Data.sga'
DB=Path(os.environ['LOCALAPPDATA'])/'Garrison/Kit/game-assets.sqlite3'
CFG=DB.with_name('game-assets.local.json')
OUT=ROOT/'evidence'; CACHE=OUT/'stock'; DECODE=CACHE/'decode'

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def cli(args):
    p=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(f'{args}: {p.stdout[-1500:]} {p.stderr[-1500:]}')
    return p.stdout
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def extract(arc,member):
    p=CACHE/'native'/member
    if not p.exists():
        p.parent.mkdir(parents=True,exist_ok=True);cli([ARCH,'extract-member',arc,member,p])
    return p
def xml(member):
    p=extract(ATTRIB,member);dest=p.with_suffix('.xml')
    if not dest.exists():cli([ARCH,'decode-rgd',p,dest])
    return ET.parse(dest).getroot()
def snapshot():
    names=cli(['git','-C',REPO,'ls-files','-z','assets','art','tools','development.json','development-data/current-084-v1/index.json.gz','development-data/current-084-v1/index-current.json.gz','community_civilization_pack.aoe4mod']).split('\0')
    return {'head':cli(['git','-C',REPO,'rev-parse','HEAD']).strip(),
            'git_status':cli(['git','-C',REPO,'status','--porcelain=v1']),
            'files':{n:sha(REPO/n) for n in names if n and (REPO/n).is_file()}}
def load_function(path,name,env):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    if name=='selectors':
        source=ast.unparse(node)
        old="elif any((c['property'] != 'life_cycle_state' for c in cond)):\n            state = 'unknown'\n            upper.update(s['members'])"
        replacement="elif _healthy_conditions(cond):\n            state = 'healthy_known_comparison'\n            lower.update(s['members'])\n            upper.update(s['members'])\n        elif any((c['property'] != 'life_cycle_state' for c in cond)):\n            state = 'unknown'\n            upper.update(s['members'])"
        assert old in source
        node=ast.parse(source.replace(old,replacement)).body[0]
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),env)
    return env[name]
def ref(node):
    v={n.get('Key'):n.get('Value') for n in node}
    if v.get('$PBGNAME') and v.get('$PBGMAP'):return v['$PBGMAP'].replace('\\','/')+'/'+v['$PBGNAME']
def attach_member(value,names):
    leaf=value.rsplit('/',1)[-1]+'.rgd'
    matches=[n for n in names if n.startswith('attrib/attachments/') and n.endswith('/'+leaf)]
    if len(matches)==1:return matches[0]
    p=[n for n in matches if '/races/core/' in n or '/civilizations/'+value.split('/')[2]+'/' in n]
    if len(p)==1:return p[0]
    raise ValueError((value,matches))
def healthy_conditions(cond):
    # Native completed pre-collapse state: lifecycle healthy; collapse flag false.
    # The stock arrays OR lifecycle alternatives and additionally test collapse.
    if any(c['op']!=2 or c['flag'] not in (0,1) or c['property'] not in ('life_cycle_state','has_collapsed_ruins') for c in cond):return False
    lifecycle=[c for c in cond if c['property']=='life_cycle_state']
    positive=[c for c in lifecycle if c['flag']==0]
    negative=[c for c in lifecycle if c['flag']==1]
    return (not positive or any(c['value']=='healthy' for c in positive)) and all(c['value']!='healthy' for c in negative) and all(c['value']=='false' and c['flag']==0 for c in cond if c['property']=='has_collapsed_ruins')
def main():
    assert ROOT.resolve().is_relative_to(TEMP.resolve())
    for p in (TEMP,REPO):assert p.is_dir() and not p.is_symlink() and not p.is_junction()
    OUT.mkdir(parents=True,exist_ok=True)
    baseline=OUT/'repository-baseline.json'
    if not baseline.exists():write(baseline,snapshot())
    sys.path.insert(0,str(EXT))
    from garrison_shared import relic_chunky as rc
    schema=extract(GAME/'engine/archives/reflect.sga','reflect.db')
    env={'Path':Path,'struct':struct,'ET':ET,'relic_chunky':rc,'WORK':schema.parent}
    NativeTree=load_function(REPO/'tools/release_010/integration_native.py','NativeTree',env)
    env2={'rc':rc,'struct':struct,'_healthy_conditions':healthy_conditions};selectors=load_function(REPO/'tools/castle_next/selector_probe_castle.py','selectors',env2)
    listed=json.loads(cli([ARCH,'list',ATTRIB]));names={r['path'].lower() for r in listed['members']}
    # The original Persian actor's parent supplies effective placement dimensions.
    parent=xml('attrib/ebps/races/core/buildings/building_wonder_age1.rgd')
    placement=[]
    for branch in ('default','campaign'):
        b=parent.find(f"RGDNode[@Key='{branch}']")
        if b is None:continue
        for n in b.iter('RGDNode'):
            if n.get('Key') in ('footprint_scale','simbox','simbox_size','size','construction_stamp','animator_attachments'):
                placement.append({'variant':branch,'xml':ET.tostring(n,encoding='unicode')})
    write(OUT/'native-placement.json',{'parent':'building_wonder_age1','fields':placement})
    actors={
      'imperial_academy':'attrib/ebps/races/chinese/buildings/building_landmark_age1_academy_chi/building_landmark_age1_academy_control_chi.rgd',
      'dome_of_faith':'attrib/ebps/races/sultanate/buildings/building_landmark_age1_quwwat_ul_islam_sul/building_landmark_age1_quwwat_ul_islam_control_sul.rgd',
      'council_hall':'attrib/ebps/races/english/buildings/building_landmark_age1_westminster_hall_eng/building_landmark_age1_westminster_hall_eng.rgd'}
    models={};draws={}
    for key,actor in actors.items():
        b=xml(actor).find("RGDNode[@Key='default']"); entries=[]
        refs=[ref(n) for n in b.iter('RGDNode') if n.get('Key')=='attachments' and ref(n)]
        for value in sorted(set(refs)):
            member=attach_member(value,names);ab=xml(member).find("RGDNode[@Key='default']")
            if ab is None:continue
            stamps=[n.get('Value').replace('\\','/').lower()+'.bin' for n in ab.iter('RGDNode') if n.get('Key')=='stamp' and n.get('Value')]
            direct=[n.get('Value').replace('\\','/').lower() for n in ab.iter('RGDNode') if n.get('Key')=='animator' and n.get('Value')]
            for logical in direct:
                logical=logical.removesuffix('.rgm')+'.rgm';entries.append({'attachment':member,'stamp':None,'model':logical})
            for stamp in stamps:
                tree=NativeTree(extract(DATA,stamp))
                for o in tree.objects.values():
                    if o['type']!='StampBlueprint' or o['owner']:continue
                    arr=tree.field(o,o['fields']['m_blueprints'])
                    for i in range(arr['count']):
                        slot=arr['data_address']+8*i;obj=tree.by_offset.get(slot+struct.unpack('<q',tree.bytes(slot,8))[0])
                        if obj and obj['type']=='VisualStampBlueprint':
                            model=tree.field(obj,obj['fields']['m_blueprint']).get('text')
                            if model:entries.append({'attachment':member,'stamp':stamp,'model':model.replace('\\','/').lower().removesuffix('.rgm')+'.rgm'})
        draws[key]={'actor':actor,'entries':entries};print('GRAPH',key,len(entries),flush=True)
    with sqlite3.connect('file:'+DB.as_posix()+'?mode=ro',uri=True) as db:
        for logical in sorted({e['model'] for v in draws.values() for e in v['entries']}):
            token=hashlib.sha1(logical.encode()).hexdigest()[:12];folder=DECODE/token
            found=list(folder.rglob('decoded-static.json')) if folder.exists() else []
            if found:p=found[0]
            else:
                try:r=json.loads(cli([CORE,'convert','decode-static','--logical-path',logical,'--config',CFG,'--index',DB,'--output-root',folder]))
                except RuntimeError as error:
                    if any(t in logical for t in ('/splats/','/outskirt_marker/')) and 'no same-stem RRGeometry provider' in str(error):
                        models[logical]={'triangles':0,'upper_triangles':0,'raw':0,'method':'terrain splat or functional marker without authored same-stem RRGeometry; excluded from authored mesh metric','excluded_nonmesh':True}
                        print('DECAL_NOT_MESH',logical,flush=True);continue
                    raise
                p=Path(r['manifest_path'])
            doc=json.loads(p.read_text(encoding='utf-8'))
            assert doc.get('geometry',{}).get('groups'),(logical,doc.get('blockers'))
            actual=doc['provider_contract']['model']['logical_path']
            ar=db.execute('select archive_path from resolved_assets where lower(logical_path)=?',(actual.lower(),)).fetchone()
            rgm=extract(Path(ar[0]),actual);m=selectors(rgm,doc)
            if m['lower']!=m['upper']:
                write(OUT/('selector-diagnostic-'+token+'.json'),m)
            models[logical]={'triangles':m['lower'],'upper_triangles':m['upper'],'raw':m['raw'],'manifest':str(p),'manifest_sha256':sha(p),'native_rgm':str(rgm),'native_rgm_sha256':sha(rgm),'method':m['method'],'groups':len(doc['geometry']['groups'])}
            print('MEASURE',m['lower'],m['upper'],logical,flush=True)
    for key,v in draws.items():
        v['healthy_lod0_triangles']=sum(models[e['model']]['triangles'] for e in v['entries'])
        v['healthy_lod0_upper_triangles']=sum(models[e['model']]['upper_triangles'] for e in v['entries'])
    counts=sorted(v['healthy_lod0_triangles'] for v in draws.values())
    result={'status':'measured_native_default_healthy_with_bounded_props','actors':draws,'models':models,'budget':{'target':statistics.median(counts),'cap':max(counts),'counts':counts,'policy':'Use proven healthy lower bounds for conservative median/cap; unknown prop selectors retained as intervals, never promoted to exact counts.'},'limits':'Static native selector/attachment evidence, not engine rendering; repeated stamp model instances counted separately. Some small prop drawgroups are merged by the public decoder; exact numeric selector membership remains bounded.'}
    write(OUT/'stock-budget.json',result);print('BUDGET',json.dumps(result['budget']),flush=True)

if __name__=='__main__':main()
