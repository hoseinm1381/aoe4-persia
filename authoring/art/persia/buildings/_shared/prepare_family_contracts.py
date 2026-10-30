"""Copy compact qualified measurement/consumer contracts, never game media.

This prepares source-art metadata. It neither chooses architecture nor changes
native consumers, gameplay tiers, markers or animation graphs.
"""
from pathlib import Path
import json,hashlib,sys
ART=Path(__file__).resolve().parent.parent
INVENTORY=ART.parents[2]/'research/persia_buildings/inventory'
ALIASES={'divan_commerce':'divan_economy','divan_war':'divan_military','shah_masjid':'shah_masjid_wonder'}
def read(name):return json.loads((INVENTORY/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(slug):
    if slug=='house':raise ValueError('House has its own qualified 12-body contracts')
    family=ALIASES.get(slug,slug);p=ART/slug;p.mkdir(exist_ok=True);(p/'evidence').mkdir(exist_ok=True);(p/'textures').mkdir(exist_ok=True);(p/'previews').mkdir(exist_ok=True)
    native=read('PRIMARY_BODY_HANDOFF.json')['families'][family]
    states=read('FAMILY_NATIVE_STATE_CONTRACTS.json')['families'][family]
    bounds=read('HEALTHY_REST_BOUNDS.json')
    budgets=read('ALL_FAMILY_TRIANGLE_BUDGETS.json')['families'][family]
    models={m['model']:m for m in states['models']}
    deps=read('MECHANISM_DEPENDENCIES.json')['dependencies']
    bodies={};keys=[]
    for b in native['bodies']:
        age=b['native_age_label_from_resource_name'];key='A'+str(age) if age else 'Shared'
        if family=='outpost':key+='Fortified' if 'upgrade_stone' in b['model'] else 'Basic'
        if key in bodies:raise ValueError('Ambiguous body key: '+slug+' '+key)
        m=models[b['model']];keys.append(key)
        bodies[key]={**b,'resource_age_is_not_gameplay_availability':True,'stamp_contracts':bounds['stamp_transform_bounds_by_model'][b['model']],
                     'actual_geometry_lifecycle_values':m['actual_geometry_lifecycle_values'],'geometry_property_values':m['geometry_string_property_values'],
                     'native_markers':m['native_markers'],'native_skeleton':m['native_skeleton'],
                     'animation_graphs':m['animation_graphs'],'mechanism_and_rig_action_references':m['mechanism_and_rig_action_references']}
    doc={'schema':'persia-building-source-contract/1','family':slug,'inventory_family':family,'body_keys':keys,'bodies':bodies,
         'coordinate_projection':bounds['coordinate_projection'],'native_stamp_transform_order':bounds['transform_order'],
         'mechanism_dependencies':{k:v for k,v in deps.items() if family in v['used_by_families']},
         'preservation':'Native actors, source consumers, gameplay footprints, markers, rigs and graph binaries are retained inputs; this source milestone does not rebind them.',
         'limits':'Rest/model/stamp coordinates only. Bounds are envelopes, not collision or posed swept volumes. Numeric HP thresholds are not inferred.',
         'input_contract_sha256':{n:sha(INVENTORY/n) for n in ['PRIMARY_BODY_HANDOFF.json','FAMILY_NATIVE_STATE_CONTRACTS.json','HEALTHY_REST_BOUNDS.json','MECHANISM_DEPENDENCIES.json','ALL_FAMILY_TRIANGLE_BUDGETS.json']}}
    (p/'native-contracts.json').write_text(json.dumps(doc,indent=2)+'\n')
    (p/'evidence/stock-budgets.json').write_text(json.dumps(budgets,indent=2)+'\n')
    info={'schema':'persia-building-source-family/1','family':slug,'expected_body_keys':keys,'native_consumers':'native-contracts.json bodies.*.source_uses; evidence classes retained',
          'source_art_only':True,'native_hp_thresholds':None,'visual_state_coverage':'To be authored and reviewed against each body lifecycle. No completion from metadata preparation.',
          'native_gates':'Garrison export/cook, native colour, animation, placement, transitions, destruction/repair, package/import and multiplayer are deferred.'}
    old=p/'family.json'
    if old.exists():
        previous=json.loads(old.read_text())
        for k,v in previous.items():
            if k not in info:info[k]=v
    old.write_text(json.dumps(info,indent=2)+'\n')
    print('FAMILY_CONTRACTS_PREPARED',slug,len(keys),'bodies',len(doc['mechanism_dependencies']),'mechanisms')

if __name__=='__main__':
    for slug in sys.argv[1:]:prepare(slug)
