"""Mill distant sources retain masonry, bearing posts and the real feed eye."""
import json,math,bpy
import state_geometry as G

def _tri(q):return sum(len(p.vertices)-2 for p in q.data.polygons)

def build_lod(H,key,state,source,destination,level,profile):
    R=H.R;G.simplify(R,source,destination,level,profile)
    originals={o.get('healthy_source',o.name):o for o in source.all_objects if o.type=='MESH'}
    for q in list(destination.all_objects):
        if q.type!='MESH':continue
        original=originals[q['healthy_source']]
        if 'StoreApproachPaver' in original.name:
            index=int(original.name.split('StoreApproachPaver')[1].split('__')[0])
            if level==2 or index not in (0,3):G.remove(q);continue
        annulus=original.get('lod_annulus_spec')
        if annulus:
            d=json.loads(annulus);x,y=d['center_xy'];rings=d['rings_radius_z'];sides=8 if level==1 else 6
            vertices=[(x+r*math.cos(i*math.tau/sides),y+r*math.sin(i*math.tau/sides),z) for r,z in rings for i in range(sides)]
            faces=[]
            for ring in range(4):
                for i in range(sides):faces.append((ring*sides+i,ring*sides+(i+1)%sides,((ring+1)%4)*sides+(i+1)%sides,((ring+1)%4)*sides+i))
            new=R.mesh(key+'_'+state+'_LOD'+str(level)+'_QuernRunner',vertices,faces,d['surface'],destination,'finish','props')
            for p in original.keys():new[p]=original[p]
            new['healthy_source']=original.get('healthy_source',original.name);new['source_state']=state;new['lod_level']=level
            new['lod_replacement_basis']='Closed eight/six-sided annulus retains exact source eye radius, horizontal bearing/top planes and peg seat; no automatic collapse across the feed eye'
            G.remove(q);continue
        raw=original.get('lod_lathe_spec')
        if not raw or original.get('fracture'):continue
        d=json.loads(raw);sides=6 if level==1 else 4
        new=R.lathe(key+'_'+state+'_LOD'+str(level)+'_'+original.name.split('_A1_')[-1],d['center'],d['rings'],d['surface'],destination,sides=sides)
        if _tri(new)>=_tri(q):G.remove(new);continue
        for p in original.keys():new[p]=original[p]
        new['healthy_source']=original.get('healthy_source',original.name);new['source_state']=state;new['lod_level']=level
        new['lod_replacement_basis']='Original lathe rings and center retained with six/four angular sides; source profile and bearing heights unchanged'
        G.remove(q)
    # Only complete surviving courses are merged. Destruction never restores
    # a lost brick or roof: source presence is checked before making a proxy.
    if level==1:
        present={(int(o['mill_vault_bond_row']),int(o['mill_vault_bond_segment'])):o for o in source.all_objects if 'mill_vault_bond_row' in o}
        x,y,w,d=H.STORE
        for row in (0,4):
            for segment in range(18):
                pieces=[present.get((r,segment)) for r in range(row,row+4)]
                if any(o is None or o.get('fracture') for o in pieces):continue
                q=R.vault(key+'_'+state+'_LOD1_VaultBond_'+str(row)+'_'+str(segment),x,
                    y-d/2+row*d/8+.006,y-d/2+(row+4)*d/8-.006,H.SPRING,
                    1.180,.645,.025,'brick',destination,segments=1,along=1,
                    angle0=segment*math.pi/18+.003,angle1=(segment+1)*math.pi/18-.003)
                for prop in pieces[0].keys():q[prop]=pieces[0][prop]
                q['healthy_source']='MILL_BOND_PROXY|'+key+'|'+str(row)+'|'+str(segment)
                q['source_state']=state;q['lod_level']=1
                q['lod_source_parts']=json.dumps([o.get('healthy_source',o.name) for o in pieces])
                q['lod_replacement_basis']='Four intact adjacent longitudinal courses share one distant masonry unit; original curved cross-section and roof outline retained'
