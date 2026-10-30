"""Family-authored source LODs; real Blender generation/review belongs to parent.

Only exact unchanged source geometry may use an intact-profile proxy. Changed
arches, vaults, steps and native mechanisms never use a healthy reconstruction.
"""
import hashlib
import json
import math
import bpy
import bmesh
import state_geometry as G

FAMILY = 'dock'


def _bounds(R,ob):
    a,b=R.bounds(ob);return tuple(a),tuple(b)


def geometry_key(R,ob):
    points=[tuple(float(x).hex() for x in ob.matrix_world@v.co) for v in ob.data.vertices]
    faces=sorted(tuple(sorted(points[i] for i in p.vertices)) for p in ob.data.polygons)
    return hashlib.sha256(json.dumps([sorted(points),faces],separators=(',',':')).encode()).hexdigest()


def mark_curve(R,ob,kind,**spec):
    ob['lod_curve_spec']=json.dumps(dict(spec,kind=kind),sort_keys=True)
    ob['lod_reference_geometry_sha256']=geometry_key(R,ob)
    return ob


def mark_run(R,ob,kind,run,index,count,axis=0,**spec):
    ob['lod_run_spec']=json.dumps(dict(spec,kind=kind,run=run,index=index,count=count,axis=axis),sort_keys=True)
    ob['lod_reference_geometry_sha256']=geometry_key(R,ob)
    return ob


def _intact(R,ob):
    return (not ob.get('retained_native_dependency') and not ob.get('fracture')
            and ob.get('lod_reference_geometry_sha256')==geometry_key(R,ob))


def _box(R,ob):
    if len(ob.data.vertices)!=8:return False
    lo,hi=_bounds(R,ob)
    return all(all(min(abs((ob.matrix_world@v.co)[i]-lo[i]),abs((ob.matrix_world@v.co)[i]-hi[i]))<1e-6
                   for i in range(3)) for v in ob.data.vertices)


def _triangles(collection):
    return sum(len(p.vertices)-2 for o in collection.all_objects if o.type=='MESH' for p in o.data.polygons)


def _identity(ob):
    return ob.get('healthy_source',ob.name)


def _properties(parts,q,key,state,level,kind):
    template=parts[0]
    for name in template.keys():q[name]=template[name]
    ids=sorted(_identity(o) for o in parts)
    token=hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:20]
    q['healthy_source']='PERSIA_LOD|'+FAMILY+'|'+key+'|'+kind+'|LOD'+str(level)+'|'+token
    q['lod_source_parts']=json.dumps(ids)
    q['lod_level']=level;q['source_state']=state
    q['lod_replacement_basis']=kind+'; actual surviving source only'
    # Vertex indices from an LOD0 bisect cannot address a topology proxy.
    if 'fracture_cap_vertex_indices' in q:del q['fracture_cap_vertex_indices']
    return q


def _transform(spec):
    x,y=spec.get('origin',(0.,0.));turn=spec.get('turn',0)
    if turn==1:return lambda u,v,z:(x-v,y+u,z)
    if turn==-1:return lambda u,v,z:(x+v,y-u,z)
    if turn==2:return lambda u,v,z:(x-u,y-v,z)
    return lambda u,v,z:(x+u,y+v,z)


def _curve(H,key,state,ob,destination,level,serial):
    if not ob.get('lod_curve_spec') or not _intact(H.R,ob):return None
    R=H.R;s=json.loads(ob['lod_curve_spec']);T=_transform(s)
    name=key+'_'+state+'_LOD'+str(level)+'_Curve'+str(serial)
    surface=ob.get('surface','brick')
    if s['kind']=='arch':
        q=R.archwall(name,s['cx'],s['y0'],s['y1'],s['z0'],s['outer_w'],s['height'],
                    s['inner_w'],s['spring'],s['rise'],surface,destination,
                    segments=8 if level==1 else 4,transform=T)
    elif s['kind']=='vault':
        q=R.vault(name,s['cx'],s['y0'],s['y1'],s['z0'],s['rx'],s['rz'],s['thickness'],
                  surface,destination,segments=10 if level==1 else 6,along=1,transform=T)
    elif s['kind']=='vault_end':
        n=10 if level==1 else 6
        outline=[(-s['rx'],s['z0']),(s['rx'],s['z0'])]
        outline +=[(s['rx']*math.cos(i*math.pi/n),s['z0']+s['rz']*math.sin(i*math.pi/n)) for i in range(1,n)]
        q=R.extrude_xz(name,outline,s['y0'],s['y1'],surface,destination,'vaults',T)
    elif s['kind']=='lathe':
        q=R.lathe(name,s['center'],s['rings'],surface,destination,sides=10 if level==1 else 6,
                  stage=ob.get('construction_stage','finish'),role=ob.get('role','props'))
    else:raise ValueError('Unknown authored curve kind '+s['kind'])
    return _properties([ob],q,key,state,level,'Intact'+s['kind'])


def _same_bounds(a,b):
    return all(abs(x-y)<1e-5 for lo,hi in zip(a,b) for x,y in zip(lo,hi))


def _planar_survivor(R,q):
    before=_bounds(R,q)
    bm=bmesh.new();bm.from_mesh(q.data)
    try:
        # Geometric boundaries and UV material regions stay. Never collapse
        # a broken crest or run a convex proxy over an exposed arch opening.
        bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,use_dissolve_boundaries=False,
                                verts=list(bm.verts),edges=list(bm.edges),delimit={'UV'})
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(q.data)
    finally:bm.free()
    q.data.update()
    if not _same_bounds(before,_bounds(R,q)):raise ValueError('Surviving proxy changed bounds '+q.name)
    # No retile: existing exposed-core UVs must remain their own material regions.


def _union_surviving_steps(H,key,state,parts,destination,level,run):
    R=H.R;bounds=[_bounds(R,o) for o in parts]
    before=(tuple(min(a[i] for a,b in bounds) for i in range(3)),
            tuple(max(b[i] for a,b in bounds) for i in range(3)))
    hidden=destination.hide_viewport;destination.hide_viewport=False
    try:
        bpy.context.view_layer.update()
        q=G.clone(parts[0],destination,'LOD'+str(level)+'_ActualSteps')
        for index,part in enumerate(parts[1:]):
            operand=G.clone(part,destination,'LOD'+str(level)+'_StepOperand'+str(index))
            G.boolean(q,operand,'UNION');G.remove(operand)
        _planar_survivor(R,q)
    finally:
        destination.hide_viewport=hidden;bpy.context.view_layer.update()
    if not _same_bounds(before,_bounds(R,q)):raise ValueError('Actual step union changed source extrema '+run)
    _properties(parts,q,key,state,level,'ActualStepUnion'+run)
    q['lod_replacement_basis']='Exact union of actual surviving steps; no healthy reconstruction; strict planar/UV-preserving dissolve only'
    return q


def _chunks(parts,count):
    count=min(len(parts),count)
    return [parts[len(parts)*i//count:len(parts)*(i+1)//count] for i in range(count)]


def _box_proxy(H,key,state,parts,destination,level,kind,serial):
    R=H.R;bounds=[_bounds(R,o) for o in parts]
    lo=[min(a[i] for a,b in bounds) for i in range(3)]
    hi=[max(b[i] for a,b in bounds) for i in range(3)]
    q=R.block(key+'_'+state+'_LOD'+str(level)+'_'+kind+str(serial),
              tuple((lo[i]+hi[i])/2 for i in range(3)),tuple(hi[i]-lo[i] for i in range(3)),
              parts[0].get('surface','stone'),destination,
              parts[0].get('construction_stage','walls'),parts[0].get('role','architecture'))
    return _properties(parts,q,key,state,level,kind)


def _runs(objects,kind):
    groups={}
    for ob in objects:
        if ob.get('retained_native_dependency') or not ob.get('lod_run_spec'):continue
        spec=json.loads(ob['lod_run_spec'])
        if spec['kind']==kind:groups.setdefault(spec['run'],[]).append((spec,ob))
    for parts in groups.values():parts.sort(key=lambda row:row[0]['index'])
    return groups


def _contiguous_boxes(H,rows):
    chains=[];chain=[];R=H.R
    for spec,ob in rows:
        if not (_intact(R,ob) and _box(R,ob)):
            if chain:chains.append(chain);chain=[]
            continue
        if chain:
            previous_spec,previous=chain[-1];a,A=_bounds(R,previous);b,B=_bounds(R,ob);axis=spec['axis']
            same=(spec['index']==previous_spec['index']+1 and abs(b[axis]-A[axis])<1e-6)
            same=same and all(abs(a[i]-b[i])<1e-6 and abs(A[i]-B[i])<1e-6 for i in range(3) if i not in (axis,2))
            same=same and abs(a[2]-b[2])<1e-6
            if not same:chains.append(chain);chain=[]
        chain.append((spec,ob))
    if chain:chains.append(chain)
    return chains



def _exact_box_runs(H,key,state,objects,destination,level,consumed):
    R=H.R;used=set();serial=0
    for axis in (0,1):
        chains={}
        for ob in objects:
            if ob.name in consumed or ob.name in used or ob.get('role') not in ('architecture','roofs','fittings'):continue
            if not (_intact(R,ob) and _box(R,ob)):continue
            lo,hi=_bounds(R,ob)
            signature=(ob.get('surface'),ob.get('structural_group'),ob.get('role'),ob.get('construction_stage'),
                tuple((float(lo[i]).hex(),float(hi[i]).hex()) for i in range(3) if i!=axis))
            chains.setdefault(signature,[]).append((lo,hi,ob))
        for rows in chains.values():
            rows.sort(key=lambda row:row[0][axis]);runs=[];run=[]
            for row in rows:
                if run and row[0][axis]-run[-1][1][axis]>1e-6:runs.append(run);run=[]
                run.append(row)
            if run:runs.append(run)
            for run in runs:
                if len(run)<2:continue
                parts=[ob for lo,hi,ob in run]
                q=_box_proxy(H,key,state,parts,destination,level,'ExactCollinearBoxRun'+str(axis),serial)
                q['lod_replacement_basis']='Exact union envelope of touching unchanged boxes with identical cross-section; no corner, opening or real gap filled'
                used.update(o.name for o in parts);serial+=1
    return used


def _parapet_rings(H,key,state,objects,destination,level,consumed):
    R=H.R;used=set();serial=0
    for run,rows in _runs(objects,'parapet_ring').items():
        if any(o.name in consumed for s,o in rows):continue
        if len(rows)!=4 or [s['index'] for s,o in rows]!=[0,1,2,3]:continue
        if not all(_intact(R,o) and _box(R,o) for s,o in rows):continue
        parts=[o for s,o in rows];bounds=[_bounds(R,o) for o in parts]
        lo=[min(a[i] for a,b in bounds) for i in range(3)]
        hi=[max(b[i] for a,b in bounds) for i in range(3)];t=rows[0][0]['thickness']
        outer=[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]
        inner=[(lo[0]+t,lo[1]+t),(hi[0]-t,lo[1]+t),(hi[0]-t,hi[1]-t),(lo[0]+t,hi[1]-t)]
        vertices=[(x,y,z) for points in (outer,inner) for z in (lo[2],hi[2]) for x,y in points]
        faces=[]
        for i in range(4):
            j=(i+1)%4
            faces.extend([(j,i,i+8,j+8),(i+4,j+4,j+12,i+12),
                          (i,j,j+4,i+4),(j+8,i+8,i+12,j+12)])
        q=R.mesh(key+'_'+state+'_LOD'+str(level)+'_ExactParapetRing'+str(serial),
                  vertices,faces,parts[0].get('surface','plaster'),destination,'vaults','roofs')
        _properties(parts,q,key,state,level,'ExactIntactParapetRing'+run)
        q['lod_replacement_basis']='Exact complete unchanged four-rail parapet ring; shared closed corner faces removed, courtyard/roof void and full outer bounds retained'
        used.update(o.name for o in parts);serial+=1
    return used

def _finish(H,key,state,objects,destination,level,profile,consumed):
    consumed=set(consumed)
    consumed|=_parapet_rings(H,key,state,objects,destination,level,consumed)
    consumed|=_exact_box_runs(H,key,state,objects,destination,level,consumed)
    R=H.R;omissions=profile.get('lod_omit_name_fragments',{}).get(str(level),[])
    serial=0;debris_index=0
    for ob in objects:
        if ob.name in consumed:continue
        native=ob.get('retained_native_dependency')
        if not native:
            if ob.get('role') in ('fine_detail','wear') or any(text in ob.name for text in omissions):continue
            if ob.get('role')=='debris':
                # Fallen source members/slabs retain their function/silhouette.
                keep='Fallen' in ob.name or debris_index%(3 if level==1 else 9)==0
                debris_index+=1
                if not keep:continue
            q=_curve(H,key,state,ob,destination,level,serial)
            if q is not None:serial+=1;continue
        q=G.clone(ob,destination,'LOD'+str(level));q['lod_level']=level
        if not native and ob.get('lod_curve_spec'):
            _planar_survivor(R,q)
            _properties([ob],q,key,state,level,'ExistingFracturedCurve')
        # Low-impact props are omitted as complete supported groups by profile.
        # No architecture or damaged solid receives an unconstrained collapse.
    destination['family_lod_policy']=FAMILY+' original family proxies; actual survivors preserved'
    destination['family_lod_ratio']=_triangles(destination)/max(1,_triangles(H.root(key,state,0)))
    destination['native_lod_distance']='unqualified; no gameplay or native distance change'


def _deck(H,key,state,objects,destination,level):
    consumed=set();serial=0
    for run,rows in sorted(_runs(objects,'deck_plank').items()):
        for chain in _contiguous_boxes(H,rows):
            for offset in range(0,len(chain),2 if level==1 else 4):
                actual=[o for spec,o in chain[offset:offset+(2 if level==1 else 4)]]
                q=_box_proxy(H,key,state,actual,destination,level,'ContinuousDeckStrip',serial)
                q['lod_replacement_basis']='Only touching intact existing deck boards; gaps/missing boards split strips; quay support grid unchanged'
                consumed.update(o.name for o in actual);serial+=1
    return consumed


def _timber_stairs(H,key,state,objects,destination,level):
    R=H.R;consumed=set()
    for run,rows in sorted(_runs(objects,'timber_stair').items()):
        spec=rows[0][0];parts=[o for s,o in rows]
        # A complete exact source unit is mandatory: altered treads/stringers
        # remain actual survivor meshes, never a newly regenerated healthy stair.
        expected=spec['count']+2
        if len(parts)!=expected or not all(_intact(R,o) for o in parts):continue
        s=spec['stair'];n=7 if level==1 else 4
        x,y0,y1,width,z0,z1=(s[k] for k in ('x','y0','y1','width','z0','z1'))
        th=s['tread_thickness'];run_y=(y1-y0)/n;rise=(z1-z0)/n
        profile=[]
        for i in range(n):
            z=z0+(i+1)*rise-th
            profile.extend([(y0+i*run_y,z),(y0+(i+1)*run_y,z)])
        knee=y0+(th+s['web_depth'])/(z1-z0)*(y1-y0)
        profile.extend([(y1,z1-th-s['web_depth']),(knee,z0),(y0,z0)])
        stringers=[]
        for side in (-1,1):
            xx=x+side*(width/2-.06)
            q=R.extrude_xz(key+'_'+state+'_LOD'+str(level)+'_Stringer'+str(side),
                          profile,xx-.045,xx+.045,'timber',destination,'walls',
                          lambda u,v,z:(v,u,z))
            _properties(parts,q,key,state,level,'MatchedTimberStringer'+str(side))
            q['lod_actual_stair_count']=n;stringers.append(q)
        for i in range(n):
            top=z0+(i+1)*rise
            q=R.block(key+'_'+state+'_LOD'+str(level)+'_Tread'+str(i),
                      (x,y0+(i+.5)*run_y,top-th/2),(width,run_y,th),'timber',destination,'walls','architecture')
            _properties(parts,q,key,state,level,'MatchedTimberTread'+str(i))
            q['lod_actual_stair_count']=n
            q['lod_local_bearing_contract']=json.dumps({'tread_bottom':top-th,
                'stringer_ledge':top-th,'y_interval':[y0+i*run_y,y0+(i+1)*run_y],
                'source_supports':[_identity(o) for o in parts if 'Stringer' in o.name]})
        consumed.update(o.name for o in parts)
    return consumed


def _rafters(H,objects,level):
    omit=set()
    for run,rows in _runs(objects,'canopy_rafter').items():
        count=rows[0][0]['count']
        if len(rows)!=count or not all(_intact(H.R,o) for spec,o in rows):continue
        keep={0,count-1,(count-1)//2}
        if level==1:keep|={(count-1)//4,3*(count-1)//4}
        omit.update(o.name for spec,o in rows if spec['index'] not in keep)
    return omit


def _mooring(H,key,state,objects,destination,level):
    used=set()
    for run,rows in _runs(objects,'mooring_unit').items():
        if len(rows)!=3 or not all(_intact(H.R,o) for spec,o in rows):continue
        parts=[o for spec,o in rows];foot=next(o for o in parts if 'Foot' in o.name)
        post=next(o for o in parts if 'Post' in o.name);cap=next(o for o in parts if 'Cap' in o.name)
        a,A=_bounds(H.R,foot);b,B=_bounds(H.R,post);c,C=_bounds(H.R,cap)
        # Foot, narrow neck and cap remain visible; a twelve-vertex closed
        # profile replaces three intersecting little boxes. Grounding and
        # source extrema remain, and a damaged unit cannot use this proxy.
        vertices=[]
        for lo,hi,z in ((a,A,a[2]),(b,B,A[2]),(c,C,C[2])):
            vertices.extend([(lo[0],lo[1],z),(hi[0],lo[1],z),(hi[0],hi[1],z),(lo[0],hi[1],z)])
        faces=[(3,2,1,0),(8,9,10,11)]
        for ring in range(2):
            for i in range(4):
                j=(i+1)%4;faces.append((ring*4+i,ring*4+j,(ring+1)*4+j,(ring+1)*4+i))
        q=H.R.mesh(key+'_'+state+'_LOD'+str(level)+'_MooringProxy'+run,vertices,faces,'timber',destination,'finish','props')
        _properties(parts,q,key,state,level,'IntactMooringProfile'+run);q['surface']='timber'
        q['lod_replacement_basis']='Complete unchanged mooring unit; same grounded foot, narrow neck and cap extrema in a closed three-ring distant profile'
        used.update(o.name for o in parts)
    return used


def build_lod(H,key,state,source,destination,level,profile):
    if level not in (1,2):raise ValueError('Dock LOD must be1 or2')
    H.R.configure(H.ROOT,FAMILY)
    if destination.all_objects:raise ValueError('LOD destination is not empty')
    objects=sorted([o for o in source.all_objects if o.type=='MESH'],key=lambda o:o.name)
    consumed=_deck(H,key,state,objects,destination,level)
    consumed|=_timber_stairs(H,key,state,objects,destination,level)
    consumed|=_rafters(H,objects,level)
    consumed|=_mooring(H,key,state,objects,destination,level)
    _finish(H,key,state,objects,destination,level,profile,consumed)

