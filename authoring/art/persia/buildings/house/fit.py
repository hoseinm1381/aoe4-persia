"""Fit source compositions to the measured native model-space body envelope.

Native stamp/marker transforms remain unchanged and are recorded by inventory.
This is not a placement/walkability or native rendering qualification.
"""
import json,bpy
from pathlib import Path
from mathutils import Vector
import recipe as H
R=H.R
INVENTORY=H.ROOT.parents[3]/'research/persia_buildings/inventory'

def apply(key):
    models=json.loads((H.ROOT/'native-contracts.json').read_text())['models']
    suffix=f'sul_house_control_{key[-1]}_age0{key[1]}.rgm'
    logical,row=next((p,d) for p,d in models.items() if p.endswith('/'+suffix))
    ref=row['healthy_primary_bounds'];cols=[c for c in bpy.data.scenes[R.SCENE].collection.children if c.name.startswith(R.PREFIX+key+'_')]
    obs=[o for c in cols for o in c.all_objects if o.type=='MESH'];lo=[min(R.bounds(o)[0][i] for o in obs) for i in range(3)];hi=[max(R.bounds(o)[1][i] for o in obs) for i in range(3)]
    scale=[];offset=[];pad=.025
    for axis in [0,1]:
        s=min(1,(ref['max'][axis]-ref['min'][axis]-2*pad)/(hi[axis]-lo[axis]));lower=ref['min'][axis]+pad-s*lo[axis];upper=ref['max'][axis]-pad-s*hi[axis]
        t=max(lower,min(0,upper));scale.append(s);offset.append(t)
    scale.append(min(1,(ref['max'][2]-pad)/hi[2]));offset.append(0)
    for o in obs:
        for v in o.data.vertices:v.co=Vector(tuple(v.co[i]*scale[i]+offset[i] for i in range(3)))
        o.data.update()
    transform={'scale':scale,'offset':offset}
    H.ANCHORS[key]['source_to_fit']=transform
    result={'body':key,'source_model':logical,'model_sha256':row['native_rgm_sha256'],'native_model_bounds':ref,'nominal_bounds':{'min':lo,'max':hi},'source_to_fit':transform,'method':'All source states and LODs share the exact same baked transform; native actor markers/stamps unchanged.','native_gates':'placement/walkability/rendering unverified'}
    (H.ROOT/'evidence'/('fit-'+key+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
