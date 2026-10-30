"""Render selected saved-source compositions; no model edits or master save."""
from pathlib import Path
import sys,bpy
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import recipe as H,presentation as P

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['A1a:healthy','A2a:healthy','A3a:healthy','A4a:healthy']
    for arg in args:
        key,state=arg.split(':');s=P.setup();s.render.resolution_x=s.render.resolution_y=640;s.cycles.samples=12
        print('RENDER_START',key,state,flush=True)
        # P.render establishes the camera/material; use smaller inspection output.
        H.show(key,state);s=P.setup();P.fit_camera(key,state);s.render.resolution_x=s.render.resolution_y=640;s.cycles.samples=12
        s.render.filepath=str(ROOT/'previews'/f'{key}_{state}_LOD0_blue.png');bpy.ops.render.render(write_still=True)
        print('RENDER_DONE',s.render.filepath,flush=True)
