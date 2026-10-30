"""Retain compact verified native measurement inputs; no stock media copies."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
INV=ROOT.parents[3]/'research/persia_buildings/inventory'

def main():
    models=json.loads((INV/'house-models.json').read_text());rows={}
    for logical,row in models.items():
        if '/sul_house_control_' not in logical:continue
        rows[logical]={k:row[k] for k in ['native_rgm_sha256','healthy_lod0','healthy_primary_bounds','rig_contract'] if k in row}
        rows[logical]['native_selector_sets']=[{'name':s['set'],'predicates':s.get('predicates',[])} for s in row.get('selectors',{}).get('selector_sets',[])]
    fits=json.loads((INV/'house-fit-contracts.json').read_text())
    compact_fits=[{k:v for k,v in row.items() if k not in ['manifest','manifest_sha256']} for row in fits['rows']]
    doc={'schema':'persia-house-measurement-contract/1','coordinate_projection':fits['coordinate_projection'],'transform_order':fits['transform_order'],'models':rows,'stamp_body_mappings':compact_fits,'native_runtime_qualification':False}
    (ROOT/'native-contracts.json').write_text(json.dumps(doc,indent=2)+'\n')
    budgets=json.loads((INV/'HOUSE_TRIANGLE_BUDGETS.json').read_text())
    (ROOT/'evidence/stock-budgets.json').write_text(json.dumps(budgets,indent=2)+'\n')
    roster=json.loads((INV/'FAMILY_INVENTORY.json').read_text())['families']['house']
    (ROOT/'family.json').write_text(json.dumps({'family':'House','source_art_only':True,'status':'In development; see actual build/readback/review receipts','native_consumers':roster,'expected_body_keys':[f'A{a}{c}' for c in 'abc' for a in range(1,5)],'expected_source_compositions_per_body':31,'source_recipe_dependencies':['recipe.py','states.py','fit.py','checks.py','build_source.py','make_textures.py','native-contracts.json','../_shared/source_runner.py','../_shared/atlas_source.py'],'historical_references':'../../../../research/persia_buildings/history/HOUSE_PILOT_EVIDENCE.md','native_hp_thresholds':None,'native_visual_bindings':'unchanged; later integration required'},indent=2)+'\n')
    for name in ['HOUSE_LIFECYCLE_CONTRACT.json','HOUSE_PREVIEW_TARGETING_CONTRACT.json']:
        d=json.loads((INV/name).read_text());(ROOT/'evidence'/name.lower()).write_text(json.dumps(d,indent=2)+'\n')
    print('COMPACT_CONTRACTS_READY',len(rows),'models',len(compact_fits),'stamp mappings')

if __name__=='__main__':main()
