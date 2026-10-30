"""Inspect all source compositions; presentation helpers never enter asset counts."""
import bpy,json
from pathlib import Path
import asset_runner as R,presentation as V
def solid_views():
 s=bpy.context.scene;old=(s.render.resolution_x,s.render.resolution_y);s.render.resolution_x=640;s.render.resolution_y=640
 target=(0,0,6) if 'AliQapu' in R.PREFIX else (-.28,0,1.9);dist=24 if 'AliQapu' in R.PREFIX else 14
 helper=bpy.data.collections.get('Presentation_'+R.PREFIX[3:-1]);hidden=helper.hide_viewport if helper else None
 if helper:helper.hide_viewport=True
 a=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
 for name,pos in [('front',(target[0],-30,target[2])),('back',(target[0],30,target[2])),('left',(-30,target[1],target[2])),('right',(30,target[1],target[2])),('top',(target[0],target[1],35)),('bottom',(target[0],target[1],-35))]:
  R.view(pos=pos,center=target,distance=dist,solid=True);s.render.filepath=str(R.ROOT/'previews'/('solid-'+name+'.png'))
  with bpy.context.temp_override(area=a,region=next(r for r in a.regions if r.type=='WINDOW')):bpy.ops.render.opengl(write_still=True,view_context=True)
 if helper:helper.hide_viewport=hidden
 s.render.resolution_x,s.render.resolution_y=old
def all_reviews():
 R.show_state();solid_views()
 for state in ['healthy']+[f'damage_{i}' for i in range(1,6)]+['ruins']+['construct_'+x for x in ('foundation','walls','vaults','finish')]:V.render(state,state)
 V.render('owner-red',owner='red');V.render('owner-yellow',owner='yellow');V.render('rear',reverse=True)
 for level in (1,2):V.render('lod'+str(level),lod=level)
 R.show_state();R.material().node_tree.nodes['OWNER_COLOUR'].outputs[0].default_value=(.035,.22,.48,1)
 R.view(center=(0,0,6) if 'AliQapu' in R.PREFIX else (-.28,0,1.9),distance=24 if 'AliQapu' in R.PREFIX else 14,solid=False)
 R.save();print('ALL_REVIEW_IMAGES_READY')
