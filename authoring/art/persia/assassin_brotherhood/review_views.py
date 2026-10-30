"""Viewport-first source inspection; cameras are added only for final presentation."""
import bpy,json
from pathlib import Path
import asset_runner as R

def capture(name,pos=(18,-23,18),center=(0,0,2.4),distance=19,solid=True):
 helper=bpy.data.collections.get('Presentation_'+R.PREFIX[3:-1]);old=helper.hide_viewport if helper else None
 if helper:helper.hide_viewport=True
 R.view(pos,center,distance,solid)
 s=bpy.context.scene;s.render.resolution_x=1100;s.render.resolution_y=950
 s.render.image_settings.file_format='PNG';s.render.filepath=str(R.ROOT/'previews'/f'{name}.png')
 a=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in a.regions if r.type=='WINDOW')
 with bpy.context.temp_override(area=a,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
 if helper:helper.hide_viewport=old
 print('VIEW_CAPTURED',name)

def six(prefix='ortho'):
 for name,pos in [('front',(0,-30,2.4)),('back',(0,30,2.4)),('left',(-30,0,2.4)),('right',(30,0,2.4)),('top',(0,0,35)),('bottom',(0,0,-35))]:capture(prefix+'_'+name,pos=pos)

def capture_set():
 from states_recipe import STATES
 center=(0,0,2.4) if 'Bazaar' in R.PREFIX else (0,-2,2.4)
 distance=19 if 'Bazaar' in R.PREFIX else 12
 for state in STATES:
  R.show_state(state);capture('state_'+state,center=center,distance=distance,solid=False)
 for stage in ('foundation','walls','vaults','finish'):
  for c in bpy.data.scenes[R.PREFIX[:-1]].collection.children:
   if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+'construct_'+stage
  capture('construction_'+stage,center=center,distance=distance,solid=False)
 for lod in (0,1,2):
  R.show_state('healthy',lod);capture('lod_'+str(lod),center=center,distance=distance,solid=False)
 R.show_state()
 colours={'blue':(.035,.22,.48,1),'red':(.60,.035,.018,1),'yellow':(.85,.56,.025,1)}
 for name,value in colours.items():
  R.material().node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=value;capture('owner_'+name,center=center,distance=distance,solid=False)
 R.material().node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=colours['blue']
 for name,pos in [('front',(0,-30,2.4)),('back',(0,30,2.4)),('left',(-30,-2,2.4)),('right',(30,-2,2.4)),('top',(0,-2,35)),('bottom',(0,-2,-35))]:capture('ortho_'+name,pos=pos,center=center,distance=distance)
 capture('detail_entry',pos=(8,-12,9),center=(0,-4.2,1.6),distance=7 if 'Bazaar' in R.PREFIX else 5,solid=False)
 R.show_state();R.view(center=center,distance=distance,solid=False)

def step_receipt(step,comparison,anchors):
 s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH' and o.name.startswith(R.PREFIX)]
 out={'step':step,'objects':[o.name for o in obs],'triangles':sum(len(p.vertices)-2 for o in obs for p in o.data.polygons),'anchors':anchors,'comparison':comparison,'scope':'source art only'}
 (R.ROOT/'evidence'/('step-'+step+'.json')).write_text(json.dumps(out,indent=2)+'\n')
 return out
