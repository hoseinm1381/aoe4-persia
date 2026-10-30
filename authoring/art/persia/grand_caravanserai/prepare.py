"""Read-only repo/source baseline and installed native owner trace. Writes only this folder."""
from pathlib import Path
import importlib.util,json,hashlib,os,sqlite3,struct,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'gundeshapur'
TEMP=ROOT.parents[2]
REPO=Path('F:/aoe_4_temp/community_civilization_pack_garrison_aoe4')

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(name,value):
    p=ROOT/'evidence'/name;p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def main():
    # No missing-junction fallback and no permanent-path mutation.
    assert TEMP==Path('F:/aoe_4_temp/Temp_before_github_push')
    for p in [TEMP,REPO,PREV,ROOT]:
        assert p.is_dir() and not p.is_symlink() and not p.is_junction(),str(p)
        assert str(p.resolve()).lower().startswith('f:\\aoe_4_temp\\')
    spec=importlib.util.spec_from_file_location('prior_preflight',PREV/'preflight.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
    P.ROOT=ROOT;P.OUT=ROOT/'evidence';P.CACHE=P.OUT/'native-owners';P.DECODE=P.OUT/'owner-decode'
    if not (P.OUT/'repository-baseline.json').exists():write('repository-baseline.json',P.snapshot())
    if not (P.OUT/'gundeshapur-baseline.json').exists():
        paths=[p for p in PREV.rglob('*') if p.is_file() and ('evidence' not in p.parts and 'previews' not in p.parts and '__pycache__' not in p.parts)]
        write('gundeshapur-baseline.json',{str(p.relative_to(PREV)):sha(p) for p in paths})
    budget=json.loads((PREV/'evidence/stock-budget.json').read_text())
    write('stock-budget.json',{'budget':budget['budget'],'evidence_file':str(PREV/'evidence/stock-budget.json'),'sha256':sha(PREV/'evidence/stock-budget.json'),'limits':budget['limits'],'copied_decodes':False})
    sys.path.insert(0,str(P.EXT));from garrison_shared import relic_chunky as rc
    schema=P.extract(P.GAME/'engine/archives/reflect.sga','reflect.db')
    env={'Path':Path,'struct':struct,'ET':ET,'relic_chunky':rc,'WORK':schema.parent}
    NT=P.load_function(REPO/'tools/release_010/integration_native.py','NativeTree',env)
    names={r['path'].lower() for r in json.loads(P.cli([P.ARCH,'list',P.ATTRIB]))['members']}
    actor=REPO/'assets/attrib/instances/ebps/persia/ps_building_landmark_age1_trade_persia.xml';tree=ET.parse(actor).getroot()
    parent=P.xml('attrib/ebps/races/core/buildings/building_wonder_age1.rgd')
    variants=[]
    default=ET.fromstring(ET.tostring(tree))
    for variant in list(default.findall('variant')):default.remove(variant)
    for key,element in [('default',default),('campaign',tree.find("variant[@name='campaign']"))]:
        if element is None:element=tree.find('variant')
        # Direct campaign overrides and actual inherited parent fields retained separately.
        variants.append({'variant':key,'private_attachments':sorted({n.get('value') for n in element.iter('instance_reference') if n.get('name') in ('attachments','animator_attachments')}),'private_footprint':[ET.tostring(n,encoding='unicode') for n in element.iter('group') if n.get('name')=='footprint_scale'],'official_parent_footprint':[ET.tostring(n,encoding='unicode') for b in parent if b.get('Key')==key for n in b.iter('RGDNode') if n.get('Key')=='footprint_scale']})
    entries=[]
    for logical in sorted({n.get('value') for n in tree.iter('instance_reference') if n.get('name')=='attachments'}):
        member=P.attach_member(logical.replace('\\','/'),names);ab=P.xml(member)
        stamps=sorted({n.get('Value').replace('\\','/').lower()+'.bin' for n in ab.iter('RGDNode') if n.get('Key')=='stamp' and n.get('Value')})
        models=sorted({n.get('Value').replace('\\','/').lower().removesuffix('.rgm')+'.rgm' for n in ab.iter('RGDNode') if n.get('Key')=='animator' and n.get('Value')})
        for stamp in stamps:
            nt=NT(P.extract(P.DATA,stamp))
            for ob in nt.objects.values():
                if ob['type']!='StampBlueprint' or ob['owner']:continue
                arr=nt.field(ob,ob['fields']['m_blueprints'])
                for i in range(arr['count']):
                    slot=arr['data_address']+8*i;o=nt.by_offset.get(slot+struct.unpack('<q',nt.bytes(slot,8))[0])
                    if o and o['type']=='VisualStampBlueprint':
                        model=nt.field(o,o['fields']['m_blueprint']).get('text')
                        if model:models.append(model.replace('\\','/').lower().removesuffix('.rgm')+'.rgm')
        entries.append({'attachment':logical,'native_member':member,'stamps':stamps,'models':sorted(set(models))})
    write('native-owners.json',{'private_actor':str(actor),'actor_sha256':sha(actor),'parent':'building_wonder_age1','variants':variants,'owners':entries,'functional_markers':'Read only, not replaced or scaled; native clearance test deferred'})
    # Decode only the primary Han model, other tier owners traced without media duplication.
    candidates=[x for e in entries for x in e['models'] if 'ott' in x and 'landmark' in x]
    decoded=[]
    for logical in candidates:
        token=hashlib.sha1(logical.encode()).hexdigest()[:12];folder=P.DECODE/token
        paths=list(folder.rglob('decoded-static.json')) if folder.exists() else []
        if paths:p=paths[0]
        else:
            r=json.loads(P.cli([P.CORE,'convert','decode-static','--logical-path',logical,'--config',P.CFG,'--index',P.DB,'--output-root',folder]));p=Path(r['manifest_path'])
        d=json.loads(p.read_text());groups=d['geometry']['groups'];points=[v for g in groups for v in g['positions']]
        decoded.append({'model':logical,'decoded_manifest':str(p),'groups':[{'name':g['name'],'triangles':g['triangle_count'],'bounds_min':[min(v[i] for v in g['positions']) for i in range(3)],'bounds_max':[max(v[i] for v in g['positions']) for i in range(3)]} for g in groups],'bounds_min':[min(v[i] for v in points) for i in range(3)],'bounds_max':[max(v[i] for v in points) for i in range(3)]})
    write('current-visual-envelope.json',{**decoded[0],'chosen_art_bounds':{'x':[-6.1,6.1],'y':[-6.3,6.1],'z':[-.08,5.8]},'limit':'All decoded lifecycle/LOD geometry envelope, not native clearance or active-only healthy bounding box. Gameplay remains 8x8.','no_build':True})
    write('storage-check.json',{'passed':True,'temp':str(TEMP.resolve()),'repo':str(REPO.resolve()),'legacy_workspace_json':'Absent by current GitHub layout. STORAGE.md is current; obsolete junction guard not run.','core':str(P.CORE),'core_exists':P.CORE.is_file(),'archive_exists':P.ARCH.is_file(),'python':sys.executable})
    print(json.dumps({'owners':entries,'decoded_models':len(decoded),'budget':budget['budget']},indent=2))
if __name__=='__main__':main()
