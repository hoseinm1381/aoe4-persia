"""Profile-driven building source compositions, never native state wiring.

Each family/body must supply a reviewed structural profile; no automatic generic
failure bay is accepted. Healthy architecture remains in its family recipe.
"""
import bpy,json
import state_geometry as G

STATES=['healthy',*[f'damage_{n}' for n in range(1,6)],'ruins','preview','targeting']

def destination(H,key,state,lod=0):
    c=H.R.collection(H.R.PREFIX+key+'_'+state+'_LOD'+str(lod),bpy.data.scenes[H.R.SCENE].collection)
    c.hide_render=c.hide_viewport=True;return c

def damage(H,key,n,profile):
    R=H.R;state='damage_'+str(n);c=destination(H,key,state);c.hide_viewport=False
    source=sorted(H.root(key).all_objects,key=lambda o:o.name);failure=profile['damage'];work=None;cutter=None
    if n<=4:
        work=R.collection(R.PREFIX+key+'_TemporaryFracture',bpy.data.scenes[R.SCENE].collection)
        cutter=G.corner_cutter(R,work,key+'_StateCutter',failure['corner_plus_x_front_y'],failure['notch_extents'][n-1])
    changed=[]
    for ob in source:
        if ob.type!='MESH':continue
        q=G.clone(ob,c,state);group=ob.get('structural_group','');role=ob.get('role','')
        # Native dependencies have their own lifecycle; never bisect a rigged
        # mechanism. The retained native graph/pose set is a separate source.
        if q.get('retained_native_dependency'):continue
        if n<=4 and group in failure['groups'] and role not in ['ground']:
            before=len(q.data.vertices);q=G.subtract(R,q,cutter,profile.get('fracture_surface_overrides',{}).get(ob.get('surface')))
            if q is None or len(q.data.vertices)!=before:changed.append(ob.name)
        elif n==5 and group in failure['heavy_failure_group_caps'] and role!='ground':
            cap=failure['heavy_failure_group_caps'][group]
            if role in ['architecture','roofs']:
                surface=profile.get('fracture_surface_overrides',{}).get(ob.get('surface'),'brick' if ob.get('surface')=='plaster' else None)
                q=G.cut(R,q,(0,0,cap),(.018,.023,1),surface=surface)
                if q and role=='architecture':G.broken_cap(q,750+len(changed))
            else:G.remove(q)
            changed.append(ob.name)
    if cutter:G.remove(cutter);bpy.data.collections.remove(work)
    area=failure['debris_area_xy'];ground=failure['debris_ground_z']
    G.rubble(R,c,key+'_'+state+'_Debris',area,ground,5+n*6,420+n,scale=.4 if n<=2 else 1)
    c['authored_damage_level']=n;c['native_hp_threshold']='not supplied or inferred';c['failure_profile']=json.dumps(failure);c['changed_source_parts']=json.dumps(changed);c.hide_viewport=True

def ruins(H,key,profile):
    R=H.R;c=destination(H,key,'ruins');ruin=profile['ruins'];source=sorted(H.root(key).all_objects,key=lambda o:o.name)
    for i,ob in enumerate(source):
        if ob.type!='MESH':continue
        role=ob.get('role');group=ob.get('structural_group','')
        if ob.get('retained_native_dependency'):continue
        if role=='ground':G.clone(ob,c,'ruins');continue
        if group in ruin.get('preserve_intact_groups',[]):
            G.clone(ob,c,'ruins');continue
        if role!='architecture' or group in ruin.get('remove_groups',[]):continue
        q=G.clone(ob,c,'ruins');cap=ruin.get('group_caps',{}).get(group,ruin['default_cap'])
        surface=profile.get('fracture_surface_overrides',{}).get(ob.get('surface'),'brick' if ob.get('surface')=='plaster' else None)
        q=G.cut(R,q,(0,0,cap),(.025,.02,1),surface=surface)
        if q:G.broken_cap(q,2200+i)
    G.rubble(R,c,key+'_ruins_Debris',ruin['debris_area_xy'],ruin['debris_ground_z'],ruin.get('debris_count',58),860)
    # Fallen members are grounded, with family-authored endpoints. They are new
    # editable source pieces associated with removed roof/beam groups.
    for i,row in enumerate(ruin.get('fallen_members',[])):
        ob=R.beam(key+'_ruins_FallenMember'+str(i),row['a'],row['b'],row['width'],row.get('surface','timber'),c,'finish','debris')
        ob['collapse_source']=row['source_group'];ob['grounding_basis']=row['grounding_basis']
        if row.get('ground_support_healthy_source'):ob['ground_support_healthy_source']=row['ground_support_healthy_source']
    for i,row in enumerate(ruin.get('fallen_slabs',[])):
        ob=R.block(key+'_ruins_FallenSlab'+str(i),row['center'],row['size'],row.get('surface','roof'),c,'finish','debris',rotation=row.get('rotation',0))
        ob['collapse_source']=row['source_group'];ob['grounding_basis']=row['grounding_basis']
        if row.get('ground_support_healthy_source'):ob['ground_support_healthy_source']=row['ground_support_healthy_source']
    c['ruin_profile']=json.dumps(ruin)

def construction(H,key):
    R=H.R;healthy=list(H.root(key).all_objects)
    for stage,included in [('foundation',['foundation']),('walls',['foundation','walls']),('vaults',['foundation','walls','vaults']),('finish',None)]:
        c=R.collection(R.PREFIX+key+'_construct_'+stage,bpy.data.scenes[R.SCENE].collection);c.hide_render=c.hide_viewport=True
        sources={o.name:o for o in healthy if o.type=='MESH'}
        chosen={n for n,o in sources.items() if included is None or o.get('construction_stage') in included};dependencies=[]
        # An upper floor/wall assembly may require a lower roof bearing earlier
        # than its nominal stage. Include the actual named support recursively;
        # do not clone an unsupported upper storey or invent temporary geometry.
        changed=True
        while changed:
            changed=False
            for contact in H.CONTRACTS:
                if contact['body']!=key:continue
                axis=contact.get('axis','bottom-top')
                if axis=='bottom-top':dependent,support=contact['a'],contact['b']
                elif axis=='top-bottom':dependent,support=contact['b'],contact['a']
                else:continue  # Lateral adjacency alone does not assert load.
                if dependent in chosen and support not in chosen:
                    if support not in sources:raise RuntimeError('Missing named construction support '+support)
                    chosen.add(support);dependencies.append({'dependent':dependent,'support':support,'contact':contact['name']});changed=True
        for name in sorted(chosen):G.clone(sources[name],c,'construct_'+stage)
        c['source_assembly_stage']=stage;c['native_progress_threshold']='not supplied or inferred'
        c['included_support_dependencies']=json.dumps(dependencies)

def placement(H,key,profile):
    for state in ['preview','targeting']:
        c=destination(H,key,state)
        for ob in H.root(key).all_objects:
            if ob.type!='MESH':continue
            if state=='targeting' and any(t in ob.name for t in profile['targeting_omit_name_fragments']):continue
            G.clone(ob,c,state)
        c['native_placement_rendering']='unverified; authored source composition proposal'

def build(H,key,profile):
    missing=set(['damage','ruins','targeting_omit_name_fragments','lod_omit_name_fragments'])-profile.keys()
    if missing:raise RuntimeError('Missing family state profile sections: '+str(missing))
    for n in range(1,6):damage(H,key,n,profile)
    ruins(H,key,profile);construction(H,key);placement(H,key,profile)
    ratios=[]
    for state in STATES:
        source=destination(H,key,state)
        for lod in [1,2]:
            dest=destination(H,key,state,lod)
            if hasattr(H,'build_lod'):H.build_lod(H,key,state,source,dest,lod,profile)
            else:G.simplify(H.R,source,dest,lod,profile)
    return ratios
