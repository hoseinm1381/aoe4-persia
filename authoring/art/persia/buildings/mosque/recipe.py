"""Unbuilt ordinary Persian Mosque draft; exact existing Ottoman A3/A4 owners.

An original neighborhood prayer building, subordinate to Shah Masjid Wonder.
Projected stamp coordinates only. No native integration or motion is authored.
"""
from pathlib import Path
import sys
import json
import math
import bpy

ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parent/'_shared'
if str(SHARED) not in sys.path:sys.path.insert(0,str(SHARED))
import source_runner as R
R.configure(ROOT,'mosque')

F=.16
CURRENT='A3'
ANCHORS={}
CONTRACTS=[]
ASSEMBLIES={}
TEXTURE_INPUTS={k:str(ROOT/'textures'/(k+'.png')) for k in ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC={'resolution':[2048,2048],'original_pixels_required':True,'status':'paths only; parent generates original family atlas'}
ACTOR='ps_building_unit_religious_control_sul'
VARIANT_EVIDENCE={'campaign':'existing_private_compiled_variant','default':'existing_private_compiled_variant',
 'cordoba':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant',
 'xp3':'official_parent_inheritance_candidate_not_a_separately_serialized_private_variant'}
STAMP_MATRIX=[[-1.,0.,0.,0.],[0.,-1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
NATIVE={
 'A3':{'age':3,'triangles':105265,'budget_target':106082,'budget_cap':208921,
       'primary_resource_bounds':[[-6.046875,-5.81640625,-1.6005859375],[6.046875,5.6015625,9.71875]],
       'primary_stamp_bounds':[[-6.046875,-5.6015625,-1.6005859375],[6.046875,5.81640625,9.71875]],
       'conditional_compound_bounds':[[-7.4661189859,-8.3109178132,-1.6005859375],[7.9625428780,8.6953136002,9.71875]]},
 'A4':{'age':4,'triangles':124677,'budget_target':104592,'budget_cap':241534,
       'primary_resource_bounds':[[-6.02734375,-5.8125,-1.5986328125],[6.02734375,5.54296875,11.7578125]],
       'primary_stamp_bounds':[[-6.02734375,-5.54296875,-1.5986328125],[6.02734375,5.8125,11.7578125]],
       'conditional_compound_bounds':[[-7.4661189859,-8.3109178132,-1.5986328125],[7.9625428780,8.6953136002,11.7578125]]},
}
for _k,_n in NATIVE.items():
    _a=str(_n['age']).zfill(2)
    _n['model']='art/civilizations/ottoman/structures/monastery/ott_monastery_control_age'+_a+'/ott_monastery_control_age'+_a+'.rgm'
    _n['source_uses']=[dict(actor=ACTOR,variant=v,variant_evidence_class=e,
      attachment='attachments/attachment_lists/civilizations/ottoman/buildings/unit_religious_ott/tier'+str(_n['age'])+'_unit_religious_control_ott',
      attachment_category='default',inventory_category='default',stamp='art/stamps/civ_ott/ott_monastery_age_'+_a+'.bin',stamp_instance_index=0)
      for v,e in VARIANT_EVIDENCE.items()]
REVIEW_BOUNDS=[[-5.60,-5.10,-.06],[5.60,5.50,6.60]]
PLANS={
 3:{'program':'low three-bay barrel-roof prayer hall, western shade arcade and ablution court',
    'hall':(0.,3.15,7.60,4.00,3.05),'roof':'three_vaults','arcade_side':-1},
 4:{'program':'offset low-domed prayer chamber, lower west winter hall and eastern court portico',
    'hall':(.85,3.05,4.40,4.40,3.60),'roof':'low_dome','arcade_side':1},
}
NATIVE_STATE_CONTRACT={
 'life_cycle_values':['construct_'+str(i).zfill(2) for i in range(0,100,5)]+['healthy']+['damage_'+str(i) for i in range(1,6)]+['ruins','preview','targeting'],
 'conditional_properties':['has_collapsed_ruins','has_collapsed_damage1','has_collapsed_damage2','has_collapsed_damage3','has_collapsed_damage4','has_collapsed_damage5','life_cycle_state_previous','burn_state','jin_debuff','debug_static_rig_name'],
 'shared_layout_graph_contexts':{'preview':['off','planned','targeting','targeting_invalid'],'regicide_crown_state':['on'],'gold_ink_longer_pulse':['off'],'building_heal_buff_state':['on']},
 'physics_actions':'Original RGO collapse/repair/static-rig actions exist; no new animation clips are authored.',
 'primary_skeleton_present':False,
 'inventory_reference':'research/persia_buildings/inventory/FAMILY_NATIVE_STATE_CONTRACTS.json',
 'status':'Exact inventory contexts, not proof that every auxiliary ability is reachable. Native visibility/effects/repair and additional component mappings remain parent work; no HP thresholds inferred.',
}
NATIVE_DEPENDENCIES={
 'layout':'art/civilizations/common/layouts/archetypes/layout_monastery/layout_monastery.rgm',
 'native_layout_skeleton':True,'layout_markers':9,
 'existing_props':['stone_bench','tree_small_garden','sagebush_row'],
 'marker_frame':'Bone-local until native skeleton/pose evaluation; never asserted world-space sockets.',
 'policy':'Retain original layout, religious effects, physics/repair graph owners, markers and legal attachments; no new motion/rig.',
 'clearance_status':'Unqualified: rest geometry is not native footprint, monk exit, interaction marker, terrain placement or runtime clearance proof.',
}


def age():return NATIVE[CURRENT]['age']


def root(key=None,state='healthy',lod=0):
    R.configure(ROOT,'mosque');key=key or CURRENT
    if key not in NATIVE:raise ValueError('Only existing Mosque A3/A4 are admitted')
    return R.collection(R.PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)


def col(role):
    parent=root();return R.collection(R.PREFIX+CURRENT+'_healthy_'+role,parent)


def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role;ob['draft_uninspected']=True
    ob['authored_coordinate_space']='projected stamp-space; adapter pending'
    if group:ob['structural_group']=group
    return ob


def B(name,center,size,surface='plaster',stage='walls',role='architecture',group=''):
    if any(v<=0 for v in size):raise ValueError('Nonpositive part: '+name)
    return tag(R.block(CURRENT+'_'+name,center,size,surface,col(role),stage,role),stage,role,group)


def wall(name,x,y,w,d,h,surface='plaster',bottom=F,group=''):
    return B(name,(x,y,bottom+h/2),(w,d,h),surface,'walls','architecture',group)


def contact(name,child,parent,axis='bottom-top',target=0.,tolerance=.003):
    CONTRACTS.append(dict(body=CURRENT,name=name,a=child.name,b=parent.name,axis=axis,target=target,tolerance=tolerance))


def setup():
    R.configure(ROOT,'mosque');s=R.setup_scene()
    s['historical_basis']='Original neighborhood mosque informed by layered Persian mosque history; not Shah Masjid in miniature. See README.'
    R.view(pos=(15,-20,16),center=(0.,.3,2.3),distance=20,solid=True)


def foundation(key='A3'):
    global CURRENT
    if key not in NATIVE:raise ValueError('Unknown measured body')
    CURRENT=key;setup()
    if root().all_objects:raise ValueError('Owned body exists; explicit owned reset required')
    ground=B('MosqueEarthBed',(0.,.20,.05),(11.20,10.60,.22),'earth','foundation','ground','court_ground')
    court=B('AblutionCourt',(0.,-1.95,F+.04),(7.30,5.75,.08),'stone','foundation','ground','court_ground')
    contact('CourtOnGround',court,ground)
    low,high=NATIVE[key]['primary_stamp_bounds']
    margins=[REVIEW_BOUNDS[0][0]-low[0],REVIEW_BOUNDS[0][1]-low[1],high[0]-REVIEW_BOUNDS[1][0],high[1]-REVIEW_BOUNDS[1][1],high[2]-REVIEW_BOUNDS[1][2]]
    if min(margins)<0:raise ValueError('Draft review bounds exceed primary healthy rest envelope')
    ANCHORS[key]=dict(ground_top=F,native_body_key=key,native_model=NATIVE[key]['model'],existing_visual_age=age(),source_uses=NATIVE[key]['source_uses'],
      authored_space='projected stamp-space; this half-turn matrix is its own inverse',
      projected_resource_to_stamp_matrix=STAMP_MATRIX,stamp_to_projected_resource_matrix=STAMP_MATRIX,
      authoring_bounds_proposal=REVIEW_BOUNDS,native_primary_stamp_bounds=NATIVE[key]['primary_stamp_bounds'],
      conditional_compound_bounds=NATIVE[key]['conditional_compound_bounds'],envelope_proposal_margins=margins,
      entry=[0.,-4.90,F],ablution=[-.15,-2.10,F+.08],
      qibla_orientation='Original composition axis only; not a claim of a real-world geographic bearing in the game map.',
      dependencies=NATIVE_DEPENDENCIES,native_states=NATIVE_STATE_CONTRACT,
      native_clearance_status=NATIVE_DEPENDENCIES['clearance_status'],visual_inspection='Not performed; parent builds and reviews serially')
    ASSEMBLIES[key]={'ground':ground,'court':court}
    print('FOUNDATION_DRAFT',key,'ordinary mosque proposal inside primary rest envelope')


def hall_back_with_niche(x,y,w,d,h,bottom,group):
    """The prayer focus is a recessed niche within a split back wall."""
    t=.24;back=y+d/2;outer=1.35;pw=(w-outer)/2
    piers=[]
    for side in (-1,1):piers.append(wall(group+'_BackPier'+str(side),x+side*(outer/2+pw/2),back-t/2,pw,t,h,bottom=bottom,group=group))
    niche=tag(R.archwall(CURRENT+'_'+group+'_MihrabArch',x,back-t,back,bottom,outer,h,.86,1.75,.36,'brick',col('architecture'),segments=16),'walls','architecture',group)
    bed=B(group+'_MihrabRecessBack',(x,back-.035,bottom+1.25),(outer,.07,2.50),'plaster','walls','architecture',group)
    bed['recess_depth_source']=.17
    ASSEMBLIES[CURRENT]['mihrab']=dict(center=[x,back-t,bottom],source_recess_depth=.17,orientation='authored rear wall, no geographic qibla assertion')
    return piers+[niche]


def first_room():
    x,y,w,d,h=PLANS[age()]['hall'];bottom=F+.12;t=.24;group='prayer_hall'
    floor=B('PrayerHallFloor',(x,y,F+.06),(w,d,.12),'stone','foundation','ground',group)
    back=hall_back_with_niche(x,y,w,d,h,bottom,group)
    sides=[]
    for side in (-1,1):sides.append(wall('PrayerSide'+str(side),x+side*(w/2-t/2),y,t,d-.48,h,bottom=bottom,group=group))
    supports=[]
    bays=3 if age()==3 else 1
    outer=w/bays
    for i in range(bays):
        xx=x-w/2+(i+.5)*outer
        opening=1.60 if age()==3 else 2.10
        arch=tag(R.archwall(CURRENT+'_PrayerFrontArch'+str(i),xx,y-d/2,y-d/2+t,bottom,outer,h,opening,2.00 if age()==3 else 2.24,.50,'brick',col('architecture'),segments=20),'walls','architecture',group)
        contact('PrayerArchFoot'+str(i),arch,floor);supports.append(arch)
    ASSEMBLIES[CURRENT]['hall']=dict(x=x,y=y,w=w,d=d,h=h,bottom=bottom,top=bottom+h,floor=floor,back=back,sides=sides,front=supports)
    print('FIRST_ROOM_DRAFT',CURRENT,'real prayer openings, thick side walls and a recessed mihrab')


def square_transition(x,y,half,inner,z,thick=.22,sides=32):
    """Closed square-to-circular roof ring; genuine open center under the dome."""
    verts=[]
    for zz in (z,z+thick):
        for mode in ('outer','inner'):
            for i in range(sides):
                a=2*math.pi*i/sides;c,s=math.cos(a),math.sin(a)
                radius=half/max(abs(c),abs(s)) if mode=='outer' else inner
                verts.append((x+radius*c,y+radius*s,zz))
    n=sides;faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                      (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return tag(R.mesh(CURRENT+'_SquareToDomeRoofRing',verts,faces,'brick',col('roofs'),'vaults','roofs'),'vaults','roofs','prayer_hall')


def low_dome(x,y,z):
    # A closed hollow shell with annular foot; no overlapping bottom disks and
    # no full sphere or unseated drum. Radius/height are authored art dimensions.
    profile=[(1.90,0),(1.90,.24),(1.82,.54),(1.58,.96),(1.17,1.31),(.53,1.54),(.045,1.58),
             (.045,1.45),(.48,1.40),(1.07,1.19),(1.46,.86),(1.69,.44),(1.76,.22),(1.76,0)]
    sides=32;verts=[]
    for r,zz in profile:
        for i in range(sides):
            a=2*math.pi*i/sides;verts.append((x+r*math.cos(a),y+r*math.sin(a),z+zz))
    faces=[]
    for j in range(len(profile)):
        k=(j+1)%len(profile)
        for i in range(sides):faces.append((j*sides+i,j*sides+(i+1)%sides,k*sides+(i+1)%sides,k*sides+i))
    return tag(R.mesh(CURRENT+'_LowPrayerDome',verts,faces,'roof',col('roofs'),'vaults','roofs'),'vaults','roofs','prayer_hall')


def hall_roof():
    a=ASSEMBLIES[CURRENT]['hall'];x,y,w,d,z=a['x'],a['y'],a['w'],a['d'],a['top']
    if age()==3:
        bay=w/3
        for i in range(3):
            xx=x-w/2+(i+.5)*bay
            p=R.vault(CURRENT+'_PrayerVault'+str(i),xx,y-d/2,y+d/2,z,(bay-.24)/2,.66,.12,'roof',col('roofs'),segments=24,along=4,stage='vaults')
            tag(p,'vaults','roofs','prayer_hall')
            contact('PrayerVaultFront'+str(i),p,a['front'][i])
            for j,b in enumerate(a['back']):
                lo,hi=R.bounds(b)
                if hi[0]>=xx-bay/2 and lo[0]<=xx+bay/2:contact('PrayerVaultBack'+str(i)+'_'+str(j),p,b)
    else:
        transition=square_transition(x,y,w/2,1.72,z)
        for i,p in enumerate(a['sides']+a['back']+a['front']):contact('DomeRoofRingBearing'+str(i),transition,p)
        dome=low_dome(x,y,z+.22);contact('DomeOnTransition',dome,transition)
        ASSEMBLIES[CURRENT]['dome']=dome


def low_west_hall():
    if age()<4:return
    x,y,w,d,h=-2.95,3.05,3.20,4.40,2.55;bottom=F+.12;t=.22;g='winter_hall'
    floor=B('WinterHallFloor',(x,y,F+.06),(w,d,.12),'stone','foundation','ground',g)
    back=wall('WinterHallBack',x,y+d/2-t/2,w,t,h,bottom=bottom,group=g)
    wall('WinterHallWest',x-w/2+t/2,y,t,d-.44,h,bottom=bottom,group=g)
    # East wall is shared with the main chamber; it is not duplicated here.
    front=tag(R.archwall(CURRENT+'_WinterHallArch',x,y-d/2,y-d/2+t,bottom,w,h,1.40,1.70,.42,'brick',col('architecture'),segments=18),'walls','architecture',g)
    contact('WinterHallArchFoot',front,floor)
    p=R.vault(CURRENT+'_WinterHallVault',x,y-d/2,y+d/2,bottom+h,(w-.24)/2,.42,.12,'roof',col('roofs'),segments=24,along=4,stage='vaults')
    tag(p,'vaults','roofs',g);contact('WinterVaultFront',p,front);contact('WinterVaultBack',p,back)


def court_arcade():
    side=PLANS[age()]['arcade_side'];x=side*4.77;y=-1.05;w=1.25;d=4.80;h=2.28;bottom=F+.08;g='court_portico'
    floor=B('PorticoFloor',(x,y,F+.04),(w,d,.08),'stone','foundation','ground',g)
    outer=wall('PorticoOuter',x+side*(w/2-.10),y,.20,d,h,bottom=bottom,group=g)
    roofparts=[]
    for i in range(3):
        yy=y-d/2+(i+.5)*d/3;front=x-side*w/2
        arch=tag(R.archwall(CURRENT+'_PorticoArch'+str(i),yy,front-.10,front+.10,bottom,d/3,h,1.12,1.55,.38,'brick',col('architecture'),segments=16,transform=lambda u,v,z:(v,u,z)),'walls','architecture',g)
        contact('PorticoArchFoot'+str(i),arch,floor)
        slab=B('PorticoRoof'+str(i),(x,yy,bottom+h+.08),(w,d/3,.16),'roof','vaults','roofs',g)
        contact('PorticoRoofArch'+str(i),slab,arch);contact('PorticoRoofOuter'+str(i),slab,outer);roofparts.append(slab)
    ASSEMBLIES[CURRENT]['portico']=dict(x=x,y=y,side=side,floor=floor,roofparts=roofparts)


def front_prayer_portico():
    if age()<4:return
    x,y,w,d=-.75,.25,7.60,1.20;bottom=F+.10;h=2.70;g='prayer_portico'
    floor=B('PrayerPorticoFloor',(x,y,F+.05),(w,d,.10),'stone','foundation','ground',g)
    top=bottom+h
    rearposts=[]
    for j in range(4):
        xx=x-w/2+.12+j*(w-.24)/3
        p=wall('PrayerPorticoRearPost'+str(j),xx,y+d/2-.10,.18,.18,h-.18,'timber',bottom,g)
        contact('PrayerPorticoRearPostFoot'+str(j),p,floor);rearposts.append(p)
    rearbeam=B('PrayerPorticoRearBearingBeam',(x,y+d/2-.10,top-.09),(w,.20,.18),'timber','vaults','architecture',g)
    for j,p in enumerate(rearposts):contact('PrayerPorticoRearBeamBearing'+str(j),rearbeam,p)
    for i in range(3):
        xx=x-w/2+(i+.5)*w/3
        p=tag(R.archwall(CURRENT+'_PrayerPorticoArch'+str(i),xx,y-d/2,y-d/2+.22,bottom,w/3,h,1.80,1.82,.42,'brick',col('architecture'),segments=18),'walls','architecture',g)
        contact('PrayerPorticoArchFoot'+str(i),p,floor)
        # Independent rear posts/beam carry each slab even opposite a genuine
        # open prayer entrance; a masonry facade AABB is not a rear support.
        slab=B('PrayerPorticoRoof'+str(i),(xx,y,bottom+h+.09),(w/3,d,.18),'roof','vaults','roofs',g)
        contact('PrayerPorticoRoofFront'+str(i),slab,p)
        contact('PrayerPorticoRoofRear'+str(i),slab,rearbeam)


def architecture():
    hall_roof();low_west_hall();court_arcade();front_prayer_portico()
    print('ARCHITECTURE_DRAFT',CURRENT,'low neighborhood hierarchy; no minarets/four-iwan royal copy')


def bench(name,x,y):
    z0=F+.08;top=z0+.51
    seat=B(name+'Seat',(x,y,top-.05),(1.60,.42,.10),'stone','finish','props','ablution')
    for side in (-1,1):
        leg=B(name+'Foot'+str(side),(x+side*.55,y,(z0+top-.10)/2),(.20,.34,top-.10-z0),'stone','finish','props','ablution')
        contact(name+'LegSeat'+str(side),leg,seat,'top-bottom');contact(name+'LegCourt'+str(side),leg,ASSEMBLIES[CURRENT]['court'])


def props():
    # An open faceted basin with actual interior and solid bottom. No opaque
    # blue disk, pump, flowing water or unqualified effect is substituted.
    p=R.lathe(CURRENT+'_AblutionBasin',(-.15,-2.10,F+.08),[(.98,0),(.98,.11),(.93,.41),(.77,.41),(.77,.12)],'stone',col('props'),sides=8,role='props')
    tag(p,'finish','props','ablution');contact('BasinOnCourt',p,ASSEMBLIES[CURRENT]['court'])
    bench('AblutionBenchLeft',-2.18,-3.30);bench('AblutionBenchRight',2.15,-3.30)
    # Small folded/reed-like mats stay within the prayer floor and do not turn
    # into decorative figurative imagery or invented calligraphic text.
    a=ASSEMBLIES[CURRENT]['hall']
    for i in range(3):
        xx=a['x']+(i-1)*.70
        q=B('PrayerMat'+str(i),(xx,a['y'],F+.126),(.52,1.10,.012),'cloth','finish','props','prayer_hall')
        contact('MatOnPrayerFloor'+str(i),q,a['floor'])
    print('PROPS_DRAFT',CURRENT,'open ablution vessel, supported benches and quiet prayer mats')


def detail():
    # Reserved owner cloth hangs on the exterior side-portico fascia, leaving
    # prayer/mihrab surfaces free of fabricated inscriptions or secular labels.
    p=ASSEMBLIES[CURRENT]['portico'];side=p['side'];x=p['x']-side*(1.25/2+.012)
    q=B('PorticoOwnerCloth',(x,p['y'],F+.08+2.28+.08),(.024,.85,.13),'owner','finish','owner','court_portico')
    q['mounting_parent']=p['roofparts'][1].name
    for j in range(5):
        B('EntryBeddedPaver'+str(j),(0.,-4.55+j*.32,F+.09),(.80,.27,.02),'stone','foundation','ground','court_path')
    # Quiet contact wear at the basin/entry only, never ruin-like damage painted
    # uniformly over a healthy sacred building.
    for j in range(3):B('AblutionTrafficWear'+str(j),(-.20+j*.18,-3.03,F+.084),(.24,.31,.008),'grime','finish','wear','court_ground')
    print('DETAIL_DRAFT',CURRENT,'modest exterior owner cloth, bedded approach and localized working wear')


def show(key='A3',state='healthy',lod=0):
    R.configure(ROOT,'mosque')
    if key not in NATIVE:raise ValueError('Unknown measured body')
    scene=bpy.data.scenes[R.SCENE]
    for c in scene.collection.children:
        if c.name.startswith(R.PREFIX):c.hide_render=c.hide_viewport=c.name!=R.PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=scene;R.view(pos=(15,-20,16),center=(0.,.3,2.3),distance=20,solid=True)


def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_BUILT_UNINSPECTED',key)


def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')


def reset_owned(key=None):
    if key is not None and key not in NATIVE:raise ValueError('Unknown measured body')
    prefix='PSB_mosque_'+(key+'_' if key else '')
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):
            data=ob.data if ob.type=='MESH' else None;bpy.data.objects.remove(ob,do_unlink=True)
            if data and not data.users:bpy.data.meshes.remove(data)
    for c in list(bpy.data.collections):
        if c.name.startswith(prefix):bpy.data.collections.remove(c)
    if key:
        ANCHORS.pop(key,None);ASSEMBLIES.pop(key,None);CONTRACTS[:]=[c for c in CONTRACTS if c['body']!=key]
    else:ANCHORS.clear();ASSEMBLIES.clear();CONTRACTS.clear()


def build_lod(H,key,state,source,destination,level,profile):
    """Parent-only family LOD source adapter; no healthy mesh mutation."""
    import importlib.util
    spec=importlib.util.spec_from_file_location("mosque_authored_lods",ROOT/"lods.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.build_lod(H,key,state,source,destination,level,profile)
