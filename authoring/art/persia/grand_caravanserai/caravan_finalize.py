"""Small durable finishing/repair pass used both live and during cold reconstruction."""
import bpy,bmesh,random
import asset_runner as R
from caravan_states import ragged
def refine_damage():
    for level in [3,4,5]:
        c=bpy.data.collections[R.PREFIX+'damage_'+str(level)+'_LOD0']
        for j,o in enumerate(c.all_objects):
            n=o.name
            if ('EastSouthButtress' in n or level==5 and ('_south_stub' in n or n.endswith('EastSouthEndWall') or any(t in n for t in ['EastBay0_Facade','EastBay1_Facade','EastBay0_Bearing','EastBay1_Bearing']))):ragged(o,800+j)
    # Capture exact source role/stage classification once, before construction clones.
    for o in bpy.data.collections[R.PREFIX+'healthy_LOD0'].all_objects:
        if 'DirtZone' in o.name or 'Paving_' in o.name:o['construction_stage']='finish'
def topology():
    issues=[]
    for o in bpy.data.scenes['PS_Caravanserai'].objects:
        if o.type!='MESH' or not o.name.startswith(R.PREFIX):continue
        bm=bmesh.new();bm.from_mesh(o.data)
        non=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-10 for f in bm.faces);vol=bm.calc_volume(signed=True)
        if non or deg or vol<=0:issues.append({'object':o.name,'nonmanifold':non,'degenerate':deg,'volume':vol})
        bm.free()
    return issues
