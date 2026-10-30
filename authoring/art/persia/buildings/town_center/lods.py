"""Town Center LODs: surviving-geometry first; never regenerate a lost healthy bay.

Executed only by the parent's serial Blender pipeline. Targets are approximately
.50/.25 of the detailed LOD0; actual ratios and visual quality must be measured.
"""
import json
import math
import bpy
import bmesh
import state_geometry as G


def _bounds(R,ob):
    a,b=R.bounds(ob);return tuple(a),tuple(b)


def _props(template,q,state,level):
    for k in template.keys():q[k]=template[k]
    q['source_state']=state;q['lod_level']=level
    q['healthy_source']=template.get('healthy_source',template.name)
    q['family_lod_policy']='Town Center authored profile; actual surviving source only'
    return q


def _box(R,ob):
    if ob.get('fracture') or ob.get('retained_native_dependency'):return False
    if len(ob.data.vertices)!=8:return False
    lo,hi=_bounds(R,ob)
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co
        if any(min(abs(p[i]-lo[i]),abs(p[i]-hi[i]))>1e-5 for i in range(3)):return False
    return all(hi[i]-lo[i]>1e-7 for i in range(3))


def _intact_height(R,ob,lo,hi):
    if ob.get('fracture'):return False
    a,b=_bounds(R,ob)
    return all(abs(a[i]-lo[i])<1e-4 and abs(b[i]-hi[i])<1e-4 for i in range(3))


def _triangles(collection):
    return sum(max(0,len(p.vertices)-2) for o in collection.all_objects if o.type=='MESH' for p in o.data.polygons)


def _mesh_triangles(ob):
    return sum(max(0,len(p.vertices)-2) for p in ob.data.polygons)


def _planar_survivor(R,ob):
    """Remove redundant internal subdivisions without moving a fracture edge.

    This intentionally uses a tiny coplanar tolerance rather than collapsing an
    arch's concave opening or its exposed broken crest. UVs are reprojected onto
    the same source surface after the topology operation.
    """
    bm=bmesh.new();bm.from_mesh(ob.data)
    try:
        bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,use_dissolve_boundaries=False,
            verts=list(bm.verts),edges=list(bm.edges),delimit=set())
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(ob.data)
    finally:bm.free()
    ob.data.update();R.retile_surface(ob)


def _same_bounds(before,after,tolerance=2e-5):
    return all(abs(a-b)<=tolerance for A,B in zip(before,after) for a,b in zip(A,B))


def _exact_surviving_stair(H,key,state,parts,destination,level,name):
    """Union ONLY the actual surviving steps, then dissolve hidden subdivisions.

    Damaged steps are not rebuilt from their healthy stair specification. Exact
    union retains missing steps, fracture caps, disconnected remnants and every
    exposed riser, while removing their shared internal faces. It does not add a
    ramp or restore a landing. Common atlas surface and group are required.
    """
    if not parts or any(o.get('retained_native_dependency') for o in parts):return False
    signatures={(o.get('surface'),o.get('role'),o.get('structural_group')) for o in parts}
    if len(signatures)!=1:return False
    R=H.R;bounds=[_bounds(R,o) for o in parts]
    before=(tuple(min(a[i] for a,b in bounds) for i in range(3)),
            tuple(max(b[i] for a,b in bounds) for i in range(3)))
    union_trace=[]
    # family_states creates distant destinations hidden in the viewport. A
    # Boolean operand in an excluded collection is absent from the evaluated
    # depsgraph: the modifier can silently leave only the first step. Temporarily
    # enable this task-owned destination and restore its exact flag in all cases.
    was_hidden=destination.hide_viewport
    destination.hide_viewport=False
    try:
        bpy.context.view_layer.update()
        q=G.clone(parts[0],destination,'LOD'+str(level)+'_SurvivingStair')
        for index,part in enumerate(parts[1:]):
            operand=G.clone(part,destination,'LOD'+str(level)+'_StairOperand'+str(index))
            G.boolean(q,operand,'UNION');G.remove(operand)
            union_trace.append({'part':part.name,'bounds':_bounds(R,q),'triangles':_mesh_triangles(q)})
        _planar_survivor(R,q)
    finally:
        destination.hide_viewport=was_hidden
        bpy.context.view_layer.update()
    if not _same_bounds(before,_bounds(R,q)):
        raise ValueError('Surviving stair union changed source bounds: '+json.dumps({
            'body':key,'state':state,'lod':level,'group':name,'before':before,'after':_bounds(R,q),
            'parts':[{'name':o.name,'bounds':b} for o,b in zip(parts,bounds)],'union_trace':union_trace}))
    _props(parts[0],q,state,level)
    # The healthy indices and bisect vertex numbers no longer address this mesh.
    if 'fracture_cap_vertex_indices' in q:del q['fracture_cap_vertex_indices']
    q['healthy_source']='TC_LOD_SURVIVOR|'+key+'|'+name+'|LOD'+str(level)
    q['lod_source_parts']=json.dumps([o.get('healthy_source',o.name) for o in parts])
    q['lod_replacement_basis']='Exact union of existing surviving step solids; coplanar internal subdivisions removed; no healthy regeneration'
    q['lod_surviving_source_triangles']=sum(_mesh_triangles(o) for o in parts)
    q['lod_surviving_proxy_triangles']=_mesh_triangles(q)
    return True


def _step_sample(R,ob):
    """Read an actual survivor's full rectangular foot and four upper corners.

    This admits the existing horizontally clipped stair prisms only. A lost
    corner, partial foot, nonrectangular breach or unsupported wedge falls back
    to the exact surviving union rather than being filled by an invented box.
    """
    lo,hi=_bounds(R,ob);vs=[tuple(ob.matrix_world@v.co) for v in ob.data.vertices]
    corners=[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]
    tops=[]
    for x,y in corners:
        column=[p[2] for p in vs if abs(p[0]-x)<2e-5 and abs(p[1]-y)<2e-5]
        if not column or abs(min(column)-lo[2])>2e-5 or max(column)-lo[2]<1e-5:return None
        tops.append(max(column))
    if abs(max(tops)-hi[2])>2e-5:return None
    return {'object':ob,'lo':lo,'hi':hi,'tops':tops}


def _coarse_chunks(parts,count):
    """Even major-riser bands; inputs are already one contiguous surviving run."""
    count=min(count,len(parts))
    return [parts[len(parts)*i//count:len(parts)*(i+1)//count] for i in range(count)]


def _surviving_stair(H,key,state,parts,destination,level,name):
    R=H.R;samples=[_step_sample(R,o) for o in parts]
    if not all(samples):return _exact_surviving_stair(H,key,state,parts,destination,level,name)
    signatures={(o.get('surface'),o.get('role'),o.get('structural_group')) for o in parts}
    if len(signatures)!=1 or any(o.get('retained_native_dependency') for o in parts):return False
    # Split at every missing step, real interval gap or changed footprint/base.
    # Distant geometry must not bridge a breach simply to meet a triangle ratio.
    runs=[];run=[]
    for sample in samples:
        if run:
            prev=run[-1]
            same=all(abs(sample['lo'][i]-prev['lo'][i])<2e-5 and abs(sample['hi'][i]-prev['hi'][i])<2e-5 for i in (0,))
            same=same and abs(sample['lo'][2]-prev['lo'][2])<2e-5
            adjoining=abs(sample['lo'][1]-prev['hi'][1])<2e-5
            consecutive=int(sample['object']['lod_stair_index'])==int(prev['object']['lod_stair_index'])+1
            if not (same and adjoining and consecutive):runs.append(run);run=[]
        run.append(sample)
    if run:runs.append(run)
    made=[];serial=0
    for run in runs:
        for chunk in _coarse_chunks(run,6 if level==1 else 3):
            # Sample the actual surviving crest, never the original healthy rise.
            # A few major risers replace the dense staircase. Upper corner slopes
            # carry the measured broken-cap character through this source LOD.
            crest=max(chunk,key=lambda row:row['hi'][2])
            lo=[min(s['lo'][i] for s in chunk) for i in range(3)]
            hi=[max(s['hi'][i] for s in chunk) for i in range(3)]
            verts=[(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2])]
            verts +=[(x,y,z) for (x,y,_),z in zip(verts,crest['tops'])]
            faces=[(0,3,2,1),(4,5,6),(4,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
            template=chunk[0]['object']
            q=R.mesh(key+'_'+state+'_LOD'+str(level)+'_SurvivingRiser'+str(serial),verts,faces,
                template.get('surface','stone'),destination,template.get('construction_stage','walls'),'architecture')
            _props(template,q,state,level)
            if 'fracture_cap_vertex_indices' in q:del q['fracture_cap_vertex_indices']
            q['healthy_source']='TC_LOD_SURVIVOR|'+key+'|'+name+'|Riser'+str(serial)+'|LOD'+str(level)
            q['lod_source_parts']=json.dumps([s['object'].get('healthy_source',s['object'].name) for s in chunk])
            q['lod_replacement_basis']='Six/three major surviving risers per connected run; actual survivor cap-corner samples and extrema, not healthy stair rise; gaps remain separate'
            q['lod_actual_crest_source']=crest['object'].name
            q['lod_riser_approximation']='Interior treads coarsened at distance within the surviving run bounds; LOD0 and actual loss state unchanged'
            made.append(q);serial+=1
    original=[_bounds(R,o) for o in parts];after=[_bounds(R,o) for o in made]
    extents=lambda rows:(tuple(min(a[i] for a,b in rows) for i in range(3)),tuple(max(b[i] for a,b in rows) for i in range(3)))
    if not _same_bounds(extents(original),extents(after)):
        raise ValueError('Coarse surviving stair changed source extrema: '+json.dumps({'body':key,'state':state,'lod':level,'group':name,'before':extents(original),'after':extents(after)}))
    return True


def _caps(H,key,state,objects,destination,level):
    R=H.R;groups={};consumed=set();serial=0
    for ob in objects:
        if not ob.get('lod_cap_run'):continue
        if not _box(R,ob):continue  # A fractured/jagged cap is cloned unchanged.
        lo,hi=_bounds(R,ob);axis=int(ob['lod_cap_axis']);cross=1-axis
        signature=(ob['lod_cap_run'],axis,round(lo[cross],5),round(hi[cross],5),round(lo[2],5),round(hi[2],5))
        groups.setdefault(signature,[]).append((lo,hi,ob))
    for sig,parts in sorted(groups.items()):
        axis=sig[1];parts.sort(key=lambda x:x[0][axis]);chains=[];chain=[]
        for part in parts:
            # Mortar joins are coarsened; a missing brick or fracture gap is not.
            if chain and part[0][axis]-chain[-1][1][axis]>.018:
                chains.append(chain);chain=[]
            chain.append(part)
        if chain:chains.append(chain)
        for chain in chains:
            step=(6 if state in ('damage_5','ruins') else (4 if key=='A1' else 3)) if level==1 else len(chain)
            for start in range(0,len(chain),step):
                chunk=chain[start:start+step];first=chunk[0][2]
                lo=[min(a[i] for a,b,o in chunk) for i in range(3)];hi=[max(b[i] for a,b,o in chunk) for i in range(3)]
                q=R.block(key+'_'+state+'_LOD'+str(level)+'_CapRun'+str(serial),tuple((lo[i]+hi[i])/2 for i in range(3)),
                    tuple(hi[i]-lo[i] for i in range(3)),first.get('surface','stone'),destination,
                    first.get('construction_stage','vaults'),'roofs')
                _props(first,q,state,level);q['lod_source_parts']=json.dumps([o.name for a,b,o in chunk])
                q['lod_gap_policy']='Only contiguous intact course; missing/boolean-cut units split runs'
                consumed.update(o.name for a,b,o in chunk);serial+=1
    return consumed


def _stairs(H,key,state,objects,destination,level):
    R=H.R;groups={};consumed=set()
    for ob in objects:
        if ob.get('lod_stair_group'):groups.setdefault(ob['lod_stair_group'],[]).append(ob)
    for name,parts in sorted(groups.items()):
        parts.sort(key=lambda o:int(o['lod_stair_index']));template=parts[0]
        spec=json.loads(template['lod_stair_spec']);count=int(template['lod_stair_count'])
        intact=(len(parts)==count and [int(o['lod_stair_index']) for o in parts]==list(range(count))
                and all(_box(R,o) for o in parts))
        # Explicitly reject shortened or damaged steps; do not restore ruins.
        if intact:
            for i,o in enumerate(parts):
                lo,hi=_bounds(R,o);expected=spec['bottom']+spec['rise']*(i+1)/count
                if abs(lo[2]-spec['bottom'])>1e-5 or abs(hi[2]-expected)>1e-5:intact=False;break
        if not intact:
            if _surviving_stair(H,key,state,parts,destination,level,name):consumed.update(o.name for o in parts)
            continue
        n=6 if level==1 else 3;run=(spec['y1']-spec['y0'])/n
        for i in range(n):
            h=spec['rise']*(i+1)/n
            q=R.block(key+'_'+state+'_LOD'+str(level)+'_'+name.split('_')[-1]+'_Step'+str(i),
                      (spec['x'],spec['y0']+(i+.5)*run,spec['bottom']+h/2),(spec['width'],run,h),
                      'stone',destination,'walls','architecture')
            _props(template,q,state,level);q['lod_steps']=n
            q['healthy_source']='TC_LOD_PROXY|'+key+'|'+name+'|Step'+str(i)+'|LOD'+str(level)
            q['lod_source_parts']=json.dumps([o.get('healthy_source',o.name) for o in parts])
            q['lod_replacement_basis']='Full intact stair bounds and final landing height preserved; closed stepped solid'
        consumed.update(o.name for o in parts)
    return consumed


def _curve(H,key,state,ob,destination,level,serial):
    R=H.R
    if ob.get('retained_native_dependency') or ob.get('fracture'):return None
    n=8 if level==1 else 4
    if ob.get('lod_arch_spec'):
        d=json.loads(ob['lod_arch_spec'])
        if not _intact_height(R,ob,(d['cx']-d['outer_w']/2,d['y0'],d['z0']),
                             (d['cx']+d['outer_w']/2,d['y1'],d['z0']+d['height'])):return None
        q=R.archwall(key+'_'+state+'_LOD'+str(level)+'_Arch'+str(serial),d['cx'],d['y0'],d['y1'],d['z0'],
             d['outer_w'],d['height'],d['inner_w'],d['spring'],d['rise'],d['surface'],destination,segments=n)
    elif ob.get('lod_vault_spec'):
        d=json.loads(ob['lod_vault_spec']);r=d['rx']+d['thickness'];top=d['z0']+d['rz']+d['thickness']
        if not _intact_height(R,ob,(d['cx']-r,d['y0'],d['z0']),(d['cx']+r,d['y1'],top)):return None
        q=R.vault(key+'_'+state+'_LOD'+str(level)+'_Vault'+str(serial),d['cx'],d['y0'],d['y1'],d['z0'],d['rx'],d['rz'],
             d['thickness'],d['surface'],destination,segments=10 if level==1 else 6,along=1)
    elif ob.get('lod_vault_end'):
        d=json.loads(ob['lod_vault_end']);lo,hi=_bounds(R,ob)
        if ob.get('fracture') or abs(lo[2]-d['z0'])>1e-5 or abs(hi[2]-(d['z0']+d['rz']))>1e-5:return None
        n=10 if level==1 else 6
        out=[(d['cx']-d['rx'],d['z0']),(d['cx']+d['rx'],d['z0'])]
        out +=[(d['cx']+d['rx']*math.cos(j*math.pi/n),d['z0']+d['rz']*math.sin(j*math.pi/n)) for j in range(1,n)]
        q=R.extrude_xz(key+'_'+state+'_LOD'+str(level)+'_VaultEnd'+str(serial),out,d['y0'],d['y1'],d['surface'],destination,'vaults')
    else:return None
    return _props(ob,q,state,level)


def _surviving_curve(H,key,state,ob,destination,level):
    """A proxy of the actual fractured mesh, with its breach edges unchanged."""
    if ob.get('retained_native_dependency'):return None
    if not any(ob.get(k) for k in ('lod_arch_spec','lod_vault_spec','lod_vault_end')):return None
    # The intact case was already handled by _curve. This path never invokes a
    # healthy shape generator, clips a regenerated arch, or modifies LOD0.
    R=H.R;before=_bounds(R,ob)
    q=G.clone(ob,destination,'LOD'+str(level)+'_SurvivingCurve')
    _planar_survivor(R,q)
    if not _same_bounds(before,_bounds(R,q)):
        raise ValueError('Surviving curved proxy changed source bounds: '+ob.name)
    _props(ob,q,state,level)
    if 'fracture_cap_vertex_indices' in q:del q['fracture_cap_vertex_indices']
    q['lod_replacement_basis']='Actual surviving curved mesh; only coplanar subdivisions dissolved; breach and crest retained'
    q['lod_surviving_source_triangles']=_mesh_triangles(ob)
    q['lod_surviving_proxy_triangles']=_mesh_triangles(q)
    return q


def build_lod(H,key,state,source,destination,level,profile):
    if level not in (1,2):raise ValueError('Town Center LOD must be1 or2')
    R=H.R;R.configure(H.ROOT,'town_center')
    if destination.all_objects:raise ValueError('LOD destination must be empty')
    objects=sorted([o for o in source.all_objects if o.type=='MESH'],key=lambda o:o.name)
    consumed=_caps(H,key,state,objects,destination,level)
    consumed|=_stairs(H,key,state,objects,destination,level)
    debris_index=0;curves=0
    for ob in objects:
        if ob.name in consumed:continue
        role=ob.get('role');group=ob.get('structural_group','')
        if not ob.get('retained_native_dependency'):
            if role in ('fine_detail','wear'):continue
            if level==2 and group in ('civic_props','water_station','received_supplies','public_notice') and role not in ('architecture','roofs'):continue
            if 'ApproachPaver' in ob.name and level==2:continue
            if ob.get('lod_joist_run'):
                count=int(ob['lod_joist_count']);i=int(ob['lod_joist_index'])
                keep={0,count-1,(count-1)//2}
                if level==1:keep|={(count-1)//4,3*(count-1)//4}
                if i not in keep:continue
            if role=='debris':
                stride=3 if level==1 else 18 if state=='ruins' else 7
                # Preserve readable fallen-member/slab identity; reduce the many
                # small loose masonry chips to a sparse grounded distant scatter.
                keep=(level==2 and 'Fallen' in ob.name) or debris_index%stride==0;debris_index+=1
                if not keep:continue
            q=_curve(H,key,state,ob,destination,level,curves)
            if q is not None:curves+=1;continue
            q=_surviving_curve(H,key,state,ob,destination,level)
            if q is not None:curves+=1;continue
        q=G.clone(ob,destination,'LOD'+str(level));q['lod_level']=level
        # Only independent curved props/debris may use collapse. Main walls,
        # roofs, doors, frames, posts, beams/ledgers and fracture boundaries stay.
        if role in ('props','debris') and _mesh_triangles(q)>28 and not q.get('retained_native_dependency'):
            mod=q.modifiers.new('TC distant curved prop','DECIMATE');mod.ratio=.50 if level==1 else .25
            mod.use_collapse_triangulate=True
            with bpy.context.temp_override(object=q,active_object=q,selected_objects=[q],selected_editable_objects=[q]):
                bpy.ops.object.modifier_apply(modifier=mod.name)
            R.retile_surface(q)
    a,b=_triangles(source),_triangles(destination)
    destination['family_lod_ratio']=b/a if a else 0
    destination['family_lod_target']=.50 if level==1 else .25
    destination['family_lod_scope']='Measured ratio required; topology/visual/source-only status remains unaccepted'
    destination['family_lod_damage_policy']='Actual surviving curved meshes; six/three sampled major surviving stair risers with loss gaps/extrema retained; no healthy regeneration; structural ledgers never omitted by substring'
    return {'body':key,'state':state,'lod':level,'source_triangles':a,'lod_triangles':b,'ratio':b/a if a else 0,
            'target':.50 if level==1 else .25,'authored_curve_proxies':curves}
