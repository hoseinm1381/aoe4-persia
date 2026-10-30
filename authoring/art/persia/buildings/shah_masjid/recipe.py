"""DRAFT original Persia shah_masjid source art. Existing resources only.
No Blender execution was performed while authoring this file. Native motion,
footprints, selectors and gameplay remain external preserved dependencies.
"""
from pathlib import Path
import sys
import json
import math
import bpy

ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / '_shared'
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))
import source_runner as R
FAMILY = 'shah_masjid'
INVENTORY_FAMILY = 'shah_masjid_wonder'
PREFIX = 'PSB_' + FAMILY + '_'
R.configure(ROOT, FAMILY)
INVENTORY = ROOT.parents[3] / 'research/persia_buildings/inventory'
KEYS = ('A1','A2','A3','A4')
F = .08
CURRENT = KEYS[0]
ANCHORS, CONTRACTS, ASSEMBLIES = {}, [], {}
TEXTURE_INPUTS = {k: str(ROOT/'textures'/(k+'.png')) for k in
                  ('albedo','normal','roughness','metalness','owner_mask')}
TEXTURE_SPEC = {'size':[2048,2048], 'original_pixels_required':True,
                'status':'guarded make_textures.py override; parent must apply/reload/rebuild',
                'fixed_glaze_slots':['roof','carving'],'owner_colour_slot':'owner'}

def _native_records():
    handoff=json.loads((INVENTORY/'PRIMARY_BODY_HANDOFF.json').read_text(encoding='utf-8'))
    rest=json.loads((INVENTORY/'HEALTHY_REST_BOUNDS.json').read_text(encoding='utf-8'))
    compounds=json.loads((INVENTORY/'SOURCE_CATEGORY_COMPOUND_BOUNDS.json').read_text(encoding='utf-8'))
    dependencies=json.loads((INVENTORY/'MECHANISM_DEPENDENCIES.json').read_text(encoding='utf-8'))
    result={}
    for b in handoff['families'][INVENTORY_FAMILY]['bodies']:
        key='A'+str(b['native_age_label_from_resource_name'])
        if key not in KEYS: raise ValueError('Unexpected native resource age: '+key)
        uses=b['source_uses']
        private=[u for u in uses if u['variant_evidence_class']=='existing_private_compiled_variant']
        candidates=[u for u in uses if u['variant_evidence_class']!='existing_private_compiled_variant']
        stamps=rest['stamp_transform_bounds_by_model'][b['model']]
        if len(stamps)!=1:raise ValueError('Multiple stamp transforms require explicit parent mapping')
        attachments={u['attachment'] for u in private}
        cases=[{k:c.get(k) for k in ('actor','variant','variant_evidence_class','attachment',
                    'attachment_category','inventory_category','healthy_definite_category_rest_bounds',
                    'healthy_possible_category_rest_bounds')}
               for c in compounds['category_cases']
               if c.get('family')==INVENTORY_FAMILY and c.get('attachment') in attachments
               and c.get('variant') in {u['variant'] for u in private}]
        result[key]={'age':b['native_age_label_from_resource_name'],'model':b['model'],
                     'source_uses':uses,'private_compiled_source_uses':private,
                     'official_parent_candidates':candidates,
                     'native_model_sha256':b['native_model_sha256'],
                     'native_geometry_sha256':b['native_geometry_sha256'],
                     'healthy_lod0_triangle_interval':b['healthy_lod0_triangle_interval'],
                     'resource_bounds':b['healthy_definite_rest_bounds'],
                     'stamp':stamps[0], 'complete_category_bounds':cases,
                     'native_animation_graphs':b['native_animation_graphs'],
                     'dependencies':[{'model':path,'native_model_sha256':m['native_model_sha256'],
                        'native_owner_graphs':m['native_owner_graphs'],
                        'pose_and_sweep_status':m['pose_and_sweep_status'],
                        'native_skeleton':m['native_skeleton'],
                        'markers':m['markers'],'marker_contract':m['marker_contract']}
                       for path,m in dependencies['dependencies'].items()
                       if INVENTORY_FAMILY in m['used_by_families']]}
    if set(result)!=set(KEYS):raise ValueError('Existing body roster incomplete')
    return result
NATIVE = _native_records()

def age(): return NATIVE[CURRENT]['age']

def activate():
    if R.ROOT!=ROOT or R.SLUG!=FAMILY:R.configure(ROOT,FAMILY)

def root(key=None,state='healthy',lod=0):
    activate();key=key or CURRENT
    if key not in KEYS:raise ValueError('Only exact native body keys admitted')
    return R.collection(PREFIX+key+'_'+state+'_LOD'+str(lod),R.setup_scene().collection)

def col(role):return R.collection(PREFIX+CURRENT+'_healthy_'+role,root())

def tag(ob,stage,role,group=''):
    ob['body_key']=CURRENT;ob['construction_stage']=stage;ob['role']=role
    ob['structural_group']=group;ob['draft_uninspected']=True
    ob['authored_space']='measured native stamp space; resource inverse not yet applied'
    return ob

def B(name,center,size,surface='plaster',stage='walls',role='architecture',group=''):
    if any(v<=0 for v in size):raise ValueError('Nonpositive geometry '+name)
    activate()
    return tag(R.block(CURRENT+'_'+name,center,size,surface,col(role),stage,role),stage,role,group)

def contact(name,a,b,axis='bottom-top',target=0.,tolerance=.003):
    CONTRACTS.append({'body':CURRENT,'name':name,'a':a.name,'b':b.name,
                      'axis':axis,'target':target,'tolerance':tolerance})

def wall(name,x,y,w,d,h,bottom=F,group=''):
    return B(name,(x,y,bottom+h/2),(w,d,h),'plaster','walls','architecture',group)

def _inverse_rigid(m):
    r=[[m[j][i] for j in range(3)] for i in range(3)]
    return [r[i]+[-sum(r[i][j]*m[j][3] for j in range(3))] for i in range(3)]+[[0,0,0,1]]

def foundation(key=KEYS[0]):
    global CURRENT
    if key not in KEYS:raise ValueError('No invented age/body: '+str(key))
    CURRENT=key;activate();R.setup_scene()
    if root().all_objects:raise ValueError('Owned body exists; reset explicitly')
    native=NATIVE[key];env=ENVELOPES[age()]
    lo,hi=env;raw=native['stamp']['healthy_definite_stamp_space_rest_bounds']
    if any(lo[i]<raw['min'][i]-1e-6 or hi[i]>raw['max'][i]+1e-6 for i in range(3)):
        raise ValueError('Proposed envelope exceeds measured primary healthy body')
    ground=B('EarthBed',((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+F)/2),
             (hi[0]-lo[0],hi[1]-lo[1],F-lo[2]),'earth','foundation','ground','ground')
    ASSEMBLIES[key]={'ground':ground,'rooms':{}}
    ANCHORS[key]={'ground_top':F,'native_body_key':key,'inventory_family':INVENTORY_FAMILY,'native_model':native['model'],'authored_space':'measured native stamp-space; inverse resource projection required exactly once',
       'chosen_horizontal_bounds':[lo[:2],hi[:2]],'authoring_bounds_proposal':env,
       'native_stamp_rest_bounds':raw,'native_resource_bounds':native['resource_bounds'],
       'resource_to_stamp':native['stamp']['blender_matrix_row_major'],
       'stamp_to_resource':_inverse_rigid(native['stamp']['blender_matrix_row_major']),
       'source_uses':native['source_uses'],'private_compiled_source_uses':native['private_compiled_source_uses'],
       'official_parent_candidates':native['official_parent_candidates'],
       'native_dependencies':native['dependencies'],
       'native_animation_graphs':native['native_animation_graphs'],
       'native_model_sha256':native['native_model_sha256'],
       'native_geometry_sha256':native['native_geometry_sha256'],
       'healthy_lod0_triangle_interval':native['healthy_lod0_triangle_interval'],'complete_category_bounds':native['complete_category_bounds'],
       'terrain_origin_note':'native origin retained; no Z recenter from buried geometry minimum; .08 source surface is provisional',
       'clearance_status':'Only conservative rest-body envelope; native exits/markers/weapon motion unqualified',
       'door_dimensions':'original source proposals, not measured stock doorways',
       'visual_status':'unbuilt and uninspected in Blender'}
    print('FOUNDATION_DRAFT',FAMILY,key)

def _P(name,origin,xyz,size,surface='plaster',stage='walls',role='architecture',group='',turn=0):
    x,y=origin;u,v,z=xyz
    if turn==1:cx,cy=x-v,y+u;sx,sy,sz=size[1],size[0],size[2]
    elif turn==-1:cx,cy=x+v,y-u;sx,sy,sz=size[1],size[0],size[2]
    elif turn==2:cx,cy=x-u,y-v;sx,sy,sz=size
    else:cx,cy=x+u,y+v;sx,sy,sz=size
    return B(name,(cx,cy,z),(sx,sy,sz),surface,stage,role,group)

def room(name,spec,doors=(0.,),roof='flat',arched=False,bottom=F,turn=0,door_leaf=True):
    x,y,w,d,h=spec;t=.24;g=name;P=lambda label,xyz,size,mat='plaster',stage='walls',role='architecture':_P(
        name+'_'+label,(x,y),xyz,size,mat,stage,role,g,turn)
    back=P('Back',(0,d/2-t/2,bottom+h/2),(w,t,h))
    sides=[P('Side'+str(s),(s*(w/2-t/2),0,bottom+h/2),(t,d-2*t,h)) for s in (-1,1)]
    dh=min(2.02,h-.32);ow=min(1.02,w*.54)
    edges=[(-w/2,None)];front=[];last=-w/2
    for i,u in enumerate(sorted(doors)):
        half=(ow+.34)/2
        if u-half<last-1e-7 or u+half>w/2:raise ValueError('Door module does not fit '+name)
        if u-half>last:front.append(P('FrontSolid'+str(i),((last+u-half)/2,-d/2+t/2,bottom+h/2),(u-half-last,t,h)))
        if arched:
            transform=(lambda a,b,z:(x-b,y+a,z)) if turn==1 else ((lambda a,b,z:(x+b,y-a,z)) if turn==-1 else ((lambda a,b,z:(x-a,y-b,z)) if turn==2 else (lambda a,b,z:(x+a,y+b,z))))
            arch=tag(R.archwall(CURRENT+'_'+name+'_Arch'+str(i),u,-d/2,-d/2+t,bottom,
                      ow+.34,h,ow,dh-.25,.25,'plaster',col('architecture'),segments=14,transform=transform),
                      'walls','architecture',g);front.append(arch)
        else:
            for s in (-1,1):front.append(P('Jamb'+str(i)+'_'+str(s),(u+s*(ow/2+.085),-d/2+t/2,bottom+h/2),(.17,t,h)))
            front.append(P('Head'+str(i),(u,-d/2+t/2,bottom+(dh+h)/2),(ow,t,h-dh)))
        if door_leaf:leaf=P('Door'+str(i),(u,-d/2+t*.80,bottom+dh/2),(ow*.88,.055,dh),'timber','finish','fittings')
        last=u+half
    if last<w/2:front.append(P('FrontEnd',((last+w/2)/2,-d/2+t/2,bottom+h/2),(w/2-last,t,h)))
    floor=P('Floor',(0,0,bottom+.04),(w-.24,d-.24,.08),'timber' if FAMILY=='dock' else 'stone','foundation','architecture')
    record={'spec':spec,'back':back,'sides':sides,'front':front,'floor':floor,'bottom':bottom,'turn':turn}
    ASSEMBLIES[CURRENT]['rooms'][name]=record
    return record

def roof_room(name,kind='flat'):
    a=ASSEMBLIES[CURRENT]['rooms'][name];x,y,w,d,h=a['spec'];bottom=a['bottom'];turn=a['turn'];top=bottom+h
    P=lambda label,xyz,size,mat='roof',stage='vaults',role='roofs':_P(name+'_'+label,(x,y),xyz,size,mat,stage,role,name,turn)
    if kind=='vault':
        rx=(w-.22)/2;rise=.45
        transform=(lambda u,v,z:(x-v,y+u,z)) if turn==1 else ((lambda u,v,z:(x+v,y-u,z)) if turn==-1 else ((lambda u,v,z:(x-u,y-v,z)) if turn==2 else (lambda u,v,z:(x+u,y+v,z))))
        cap=tag(R.vault(CURRENT+'_'+name+'_Vault',0,-d/2,d/2,top,rx,rise,.10,'brick',
                      col('roofs'),segments=20,along=3,transform=transform),'vaults','roofs',name)
        for s in (-1,1):
            out=[(-rx,top),(rx,top)]+[(rx*math.cos(j*math.pi/20),top+rise*math.sin(j*math.pi/20)) for j in range(1,20)]
            tag(R.extrude_xz(CURRENT+'_'+name+'_VaultEnd'+str(s),out,s*d/2-.04,s*d/2+.04,
                            'plaster',col('roofs'),'vaults',transform),'vaults','roofs',name)
    else:
        cap=P('RoofBed',(0,0,top+.09),(w,d,.18),'brick')
        for s in (-1,1):
            P('ParapetSide'+str(s),(s*(w/2-.07),0,top+.26),(.14,d,.16),'plaster')
            P('ParapetEnd'+str(s),(0,s*(d/2-.07),top+.26),(w-.28,.14,.16),'plaster')
    for i,bearing in enumerate([a['back']]+a['sides']+a['front']):
        contact(name+'_RoofBearing'+str(i),cap,bearing)
    a['roof']=cap
    return cap

def canopy(name,x,y,w,d,h,posts=3):
    g=name;beam_h=.18;rafter_h=.12;posttop=F+h-beam_h-rafter_h
    feet=[];poles=[]
    for row,yy in enumerate((y-d/2+.10,y+d/2-.10)):
        rowposts=[]
        for i in range(posts):
            xx=x-w/2+.10+i*(w-.20)/(posts-1)
            foot=B(name+'_Foot'+str(row)+'_'+str(i),(xx,yy,F+.04),(.24,.24,.08),'stone','foundation','architecture',g)
            pole=B(name+'_Post'+str(row)+'_'+str(i),(xx,yy,(F+.08+posttop)/2),(.12,.12,posttop-F-.08),'timber','walls','architecture',g)
            contact(name+'_PoleFoot'+str(row)+'_'+str(i),pole,foot);rowposts.append(pole);poles.append(pole)
        beam=B(name+'_Beam'+str(row),(x,yy,posttop+beam_h/2),(w,.18,beam_h),'timber','vaults','architecture',g)
        for i,pole in enumerate(rowposts):contact(name+'_BeamPost'+str(row)+'_'+str(i),beam,pole)
        feet.append(beam)
    rafters=[]
    for i in range(7):
        xx=x-w/2+.12+i*(w-.24)/6
        joist=B(name+'_Rafter'+str(i),(xx,y,F+h-rafter_h/2),(.09,d,rafter_h),'timber','vaults','fittings',g)
        for j,beam in enumerate(feet):contact(name+'_RafterBearing'+str(i)+'_'+str(j),joist,beam)
        rafters.append(joist)
    cap=B(name+'_Roof',(x,y,F+h+.055),(w+.10,d+.10,.11),'brick','vaults','roofs',g)
    for i,joist in enumerate(rafters):contact(name+'_RoofRafter'+str(i),cap,joist)
    return {'roof':cap,'posts':poles,'height':h}

def textile(name,x,y,z,w=.92):
    beam=B(name+'_Support',(x,y,z),(w+.18,.08,.08),'timber','finish','fittings','owner')
    cloth=B(name+'_Cloth',(x,y-.04,z-.23),(w,.025,.38),'owner','finish','owner','owner')
    contact(name+'_Suspended',cloth,beam,'top-bottom')
    return cloth

def show(key=KEYS[0],state='healthy',lod=0):
    activate();s=bpy.data.scenes[R.SCENE]
    for c in s.collection.children:
        if c.name.startswith(PREFIX):c.hide_render=c.hide_viewport=c.name!=PREFIX+key+'_'+state+'_LOD'+str(lod)
    bpy.context.window.scene=s
    R.view(pos=(14,-18,14),center=VIEW_CENTER,distance=VIEW_DISTANCE,solid=True)

def build_body(key):
    foundation(key);first_room();architecture();props();detail();show(key)
    print('HEALTHY_DRAFT_UNINSPECTED',FAMILY,key)

def write_anchors():
    (ROOT/'anchors.json').write_text(json.dumps(ANCHORS,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/contact-contracts.json').write_text(json.dumps(CONTRACTS,indent=2)+'\n',encoding='utf-8')

def reset_owned(key=None):
    if key is not None and key not in KEYS:raise ValueError('Unknown body')
    owned=PREFIX+(key+'_' if key else '')
    for ob in list(bpy.data.objects):
        if ob.name.startswith(owned):
            data=ob.data if ob.type=='MESH' else None;bpy.data.objects.remove(ob,do_unlink=True)
            if data and not data.users:bpy.data.meshes.remove(data)
    for c in list(bpy.data.collections):
        if c.name.startswith(owned):bpy.data.collections.remove(c)
    if key:
        ANCHORS.pop(key,None);ASSEMBLIES.pop(key,None);CONTRACTS[:]=[c for c in CONTRACTS if c['body']!=key]
    else:ANCHORS.clear();ASSEMBLIES.clear();CONTRACTS.clear()



# These are exact existing donor-resource keys under one existing Age4 Wonder
# actor. They are NOT four historical periods of the Royal Mosque's existence.
ENVELOPES={1:[[-5.65,-5.18,-.08],[5.65,5.55,6.90]],
           2:[[-5.70,-5.65,-.08],[5.70,5.55,8.95]],
           3:[[-5.70,-5.65,-.08],[5.70,5.55,8.95]],
           4:[[-5.75,-5.70,-.08],[5.75,5.70,10.15]]}
VIEW_CENTER=(0.,.3,2.8)
VIEW_DISTANCE=23.
PLAN={1:{'court_w':4.60,'front':-2.50,'back':1.20,'hall_h':2.85,'qibla_h':3.50,'entry_h':2.70,
         'side_h':2.60,'portal_h':3.15,'portal_y':-3.90,'dome_z':.70,'dome_r':.70,'portal_top':4.55,'sanctuary_top':5.20,'arcades':1,'roof_bays':1,'side_courts':False},
      2:{'court_w':5.00,'front':-2.85,'back':1.30,'hall_h':3.35,'qibla_h':3.95,'entry_h':2.90,
         'side_h':2.85,'portal_h':3.40,'portal_y':-4.35,'dome_z':.80,'dome_r':.75,'portal_top':5.40,'sanctuary_top':6.05,'arcades':2,'roof_bays':2,'side_courts':True},
      3:{'court_w':5.20,'front':-2.95,'back':1.40,'hall_h':3.55,'qibla_h':4.10,'entry_h':3.00,
         'side_h':3.00,'portal_h':3.50,'portal_y':-4.35,'dome_z':.84,'dome_r':.77,'portal_top':5.65,'sanctuary_top':6.35,'arcades':3,'roof_bays':3,'side_courts':True},
      4:{'court_w':5.20,'front':-3.05,'back':1.45,'hall_h':3.80,'qibla_h':4.35,'entry_h':3.10,
         'side_h':3.15,'portal_h':3.65,'portal_y':-4.40,'dome_z':.88,'dome_r':.80,'portal_top':5.95,'sanctuary_top':6.75,'arcades':3,'roof_bays':3,'side_courts':True}}
CARVING_REGIONS={'field':(0.,0.,.60,1.),'border':(.65,0.,.78,1.),
                 'shaft':(.84,0.,1.,1.),'drum':(0.,0.,.60,.16)}


def _trans(origin,angle):
    ca,sa=math.cos(angle),math.sin(angle);x,y=origin
    return lambda u,v,z:(x+u*ca-v*sa,y+u*sa+v*ca,z)


def _TB(name,origin,angle,xyz,size,mat,stage='walls',role='architecture',group=''):
    return tag(R.block(CURRENT+'_'+name,_trans(origin,angle)(*xyz),size,mat,col(role),stage,role,angle),stage,role,group)


def _tile_uv(surface,u,v):
    # UV Y is opposite image row numbering. Four-percent tile gutters are kept.
    k=R.TILES.index(surface)
    return ((k%4+.04+.92*u)/4,(3-k//4+.04+.92*v)/4)


def _region_uv(surface,u,v,region=None):
    if surface=='carving':
        a,b,c,d=CARVING_REGIONS[region or 'field']
        u,v=a+(c-a)*u,b+(d-b)*v
    return _tile_uv(surface,u,v)


def _region_faces(ob,surface='carving',region='field'):
    # All islands, including narrow edge faces, stay in their assigned region.
    me=ob.data
    for poly in me.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]));axes=[i for i in range(3) if i!=axis]
        points=[me.vertices[me.loops[li].vertex_index].co for li in poly.loop_indices]
        low=[min(p[i] for p in points) for i in axes]
        scale=max(.0001,*(max(p[i] for p in points)-low[j] for j,i in enumerate(axes)))
        for li,p in zip(poly.loop_indices,points):
            uv=_region_uv(surface,(p[axes[0]]-low[0])/scale,(p[axes[1]]-low[1])/scale,region)
            for layer in me.uv_layers:layer.data[li].uv=uv
    ob['preserve_custom_source_uv']=True;ob['glaze_region']=region


def _longitude_uv(ob,origin,rings,sides,surface='roof',smooth=True,region=None):
    """Continuous single-wrap longitude/height, with a per-loop UV seam.

    This maps the ORIGINAL lathe topology. The shared LOD adapter must preserve
    custom UVs through Decimate and never retile damaged caps to this surface.
    Smooth only curved side polygons; end caps remain flat. Recalculated
    outward winding is supplied by source_runner.mesh, not inverted here.
    """
    me=ob.data;low=rings[0][1];height=rings[-1][1]-low
    if height<=0 or len(me.polygons)!=(len(rings)-1)*sides+2:
        raise ValueError('Unexpected original lathe topology for continuous mapping')
    for j in range(len(rings)-1):
        for i in range(sides):
            poly=me.polygons[j*sides+i]
            # Use vertex identity rather than loop order: recalc_face_normals
            # is allowed to reverse a face. Last-face vertex0 gets U=1, not0.
            for li in poly.loop_indices:
                vi=me.loops[li].vertex_index;ri,ci=divmod(vi,sides)
                u=1. if i==sides-1 and ci==0 else ci/sides
                uv=_region_uv(surface,u,(rings[ri][1]-low)/height,region)
                for layer in me.uv_layers:layer.data[li].uv=uv
            poly.use_smooth=bool(smooth) and abs(poly.normal[2])<.9999
    max_radius=max(r for r,z in rings)
    for poly in me.polygons[(len(rings)-1)*sides:]:
        poly.use_smooth=False
        for li in poly.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            uv=_region_uv(surface,.5+(co[0]-origin[0])/(2*max_radius),
                                .5+(co[1]-origin[1])/(2*max_radius),region)
            for layer in me.uv_layers:layer.data[li].uv=uv
    ob['preserve_custom_source_uv']=True
    ob['uv_mapping']='continuous longitude/height; seam per loop; flat radial caps'
    ob['uv_tile']=surface;ob['uv_longitude_sides']=sides
    ob['glaze_region']=region or ('field' if surface=='carving' else 'whole roof tile')
    ob['uv_height_range']=[origin[2]+low,origin[2]+rings[-1][1]]
    me.update()


def _iwan_face_uv(ob,origin,angle,w,h,surface,region='field',z0=F,horizontal=False):
    # One coherent planar facade field across arch segments; side reveals keep
    # their existing nondegenerate per-face mapping. Do not stretch a complete
    # motif separately across every tiny voussoir-like arch face.
    _region_faces(ob,surface,region)
    me=ob.data;ca,sa=math.cos(angle),math.sin(angle)
    for poly in me.polygons:
        if abs(-sa*poly.normal[0]+ca*poly.normal[1])<.90:continue
        for li in poly.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            local_x=(co[0]-origin[0])*ca+(co[1]-origin[1])*sa
            u,v=(local_x+w/2)/w,(co[2]-z0)/h
            uv=_region_uv(surface,v if horizontal else u,u if horizontal else v,region)
            for layer in me.uv_layers:layer.data[li].uv=uv
    ob['preserve_custom_source_uv']=True
    ob['uv_mapping']='coherent facade field; existing side-reveal islands retained'


def _vault_uv(ob,segments,along,surface='carving',region='field',trim=False):
    _region_faces(ob,surface,region)
    me=ob.data;n=(segments+1)*(along+1)
    for poly in me.polygons:
        # On a narrow applied arch ribbon, front/rear annular strips get a
        # continuous border across their radial width and whole arch length.
        if trim:
            ids=[me.loops[li].vertex_index for li in poly.loop_indices]
            if len({(vi%n)//(segments+1) for vi in ids})!=1:continue
        elif poly.index>=2*segments*along:continue
        for li in poly.loop_indices:
            vi=me.loops[li].vertex_index;shell,offset=divmod(vi,n)
            longitudinal,arc=divmod(offset,segments+1)
            uv=_region_uv(surface,shell if trim else arc/segments,
                          arc/segments if trim else longitudinal/along,region)
            for layer in me.uv_layers:layer.data[li].uv=uv
    ob['preserve_custom_source_uv']=True;ob['glaze_region']=region


def _pointed_branch(rx,rise,t):
    """Original cubic ogive: vertical spring tangent, inflected pointed crown.

    Kenyon B.050/B.058 document pointed arches; SAHARA/Harby indexes ogee.
    Control points are an original game reduction, not surveyed mosque radii.
    """
    u=1.-t
    return rx*(u*u*u+3*u*u*t+.75*u*t*t),rise*(1.80*u*u*t+2.04*u*t*t+t*t*t)


def _pointed_profile(rx,rise,segments):
    if segments<4 or segments%2:raise ValueError('Pointed profile needs even segments >=4')
    right=[_pointed_branch(rx,rise,i/(segments//2)) for i in range(segments//2+1)]
    return right+[(-x,z) for x,z in reversed(right[:-1])]


def _pointed_archwall(name,cx,y0,y1,z0,outer_w,height,inner_w,spring,rise,
                      surface,collection,segments=20,transform=None):
    if min(inner_w,spring,rise)<=0 or inner_w>=outer_w or spring+rise>=height:
        raise ValueError('Invalid original pointed aperture '+name)
    outline=[(cx-outer_w/2,z0),(cx-outer_w/2,z0+height),
             (cx+outer_w/2,z0+height),(cx+outer_w/2,z0),(cx+inner_w/2,z0)]
    outline += [(cx+x,z0+spring+z) for x,z in _pointed_profile(inner_w/2,rise,segments)]
    outline.append((cx-inner_w/2,z0))
    ob=R.extrude_xz(name,outline,y0,y1,surface,collection,transform=transform)
    ob['arch_profile']='original symmetric inflected cubic pointed ogive; actual clear aperture'
    ob['pointed_aperture']=[cx,inner_w,z0+spring,z0+spring+rise]
    return ob


def _pointed_vault(name,cx,y0,y1,z0,rx,rz,thickness,surface,collection,
                   segments=20,along=2,transform=None,stage='vaults'):
    """Closed pointed shell sharing the exact aperture's cubic profile/topology."""
    vertices=[];faces=[]
    for shell in (0,1):
        profile=_pointed_profile(rx+shell*thickness,rz+shell*thickness,segments)
        for j in range(along+1):
            y=y0+(y1-y0)*j/along
            vertices.extend((cx+x,y,z0+z) for x,z in profile)
    n=(segments+1)*(along+1)
    for sh in (0,1):
        for j in range(along):
            for i in range(segments):
                a=sh*n+j*(segments+1)+i;faces.append((a,a+1,a+segments+2,a+segments+1))
    for j in (0,along):
        for i in range(segments):
            a=j*(segments+1)+i;faces.append((a,a+1,a+1+n,a+n))
    for i in (0,segments):
        for j in range(along):
            a=j*(segments+1)+i;faces.append((a,a+segments+1,a+segments+1+n,a+n))
    if transform:vertices=[transform(*v) for v in vertices]
    ob=R.mesh(name,vertices,faces,surface,collection,stage,'roofs')
    ob['arch_profile']='same cubic pointed ogive as true aperture; crown is a real geometric crease'
    return ob


def _arch_trim(name,origin,angle,y,opening,spring,rise,width=.085,base=F,group='',sill=None,pointed=True):
    """Supported jamb strips + closed curved tile ribbon, never fake lettering."""
    t=.026;T=_trans(origin,angle);jambs=[]
    for side in (-1,1):
        jamb=_TB(name+'_Jamb'+str(side),origin,angle,
                 (side*(opening/2+width/2),y-t/2,base+spring/2),(width,t,spring),
                 'carving','finish','detail',group)
        center=_trans(origin,angle)(side*(opening/2+width/2),0.,0.)[:2]
        _iwan_face_uv(jamb,center,angle,width,spring,'carving','border',base)
        contact(name+'_JambSill'+str(side),jamb,sill if sill else ASSEMBLIES[CURRENT]['ground'])
        jambs.append(jamb)
    vault_function=_pointed_vault if pointed else R.vault
    arch=tag(vault_function(CURRENT+'_'+name+'_ArchRibbon',0.,y-t,y,base+spring,
               opening/2,rise,width,'carving',col('details'),segments=20,along=1,
               transform=T,stage='finish'),'finish','detail',group)
    _vault_uv(arch,20,1,'carving','border',trim=True)
    for side,jamb in enumerate(jambs):contact(name+'_SpringSeat'+str(side),arch,jamb)
    return arch


def _muqarnas_hood(name,origin,angle,w,d,t,h,opening,spring,rise,bearings):
    """Original coarse seated semi-dome; not a traced muqarnas cell survey.

    Kenyon B.054 describes tiers springing from a back/side horizontal band.
    UNESCO identifies the deep portal's half-dome and angled courtyard route.
    Eight sectors/five receding tiers are a deliberate editable game reduction.
    """
    T=_trans(origin,angle);full_rx=opening/2;full_rise=rise;front=-d/2+t;depth=d-2*t
    # Preserve the v2 entrance's lower spring-height route. The new, taller
    # pointed head starts lower, but the hood occupies only its upper segment.
    # Its front section still follows that SAME actual cubic, not a second arch.
    old_clear=F+h-.46-min(.90,opening*.47)
    zbase=max(F+spring+.10,old_clear+.10)
    offset=zbase-(F+spring);a,b=0.,1.
    for unused in range(52):
        m=(a+b)/2
        if _pointed_branch(full_rx,full_rise,m)[1]<offset:a=m
        else:b=m
    start_t=(a+b)/2;rx=_pointed_branch(full_rx,full_rise,start_t)[0]
    rise=full_rise-offset
    def hood_curve(v):
        x,z=_pointed_branch(full_rx,full_rise,start_t+(1-start_t)*v)
        return x,z-offset
    sectors=8;levels=(0.,.22,.45,.68,.86)
    band_h=.10;band_out=.10;seat=.045
    verts=[]
    # Continuous spring ledge follows the semi-elliptical back/side boundary.
    # Its inner .045 seats the first cells; outer .10 enters the rear masonry.
    for radial in (0,1):
        r=rx-seat if radial==0 else rx+band_out
        dy=depth-seat if radial==0 else depth+band_out
        for z in (zbase-band_h,zbase):
            verts.extend(T(r*math.cos(i*math.pi/sectors),
                           front+dy*math.sin(i*math.pi/sectors),z) for i in range(sectors+1))
    k=sectors+1;faces=[]
    for i in range(sectors):
        j=i+1
        faces.extend([(i,j,j+k,i+k),(i+2*k,i+3*k,j+3*k,j+2*k),
                      (i,j,j+2*k,i+2*k),(i+k,i+3*k,j+3*k,j+k)])
    for i in (0,sectors):faces.append((i,i+2*k,i+3*k,i+k))
    band=tag(R.mesh(CURRENT+'_'+name+'_MuqarnasSpringBand',verts,faces,'carving',
                   col('architecture'),'vaults','architecture'),'vaults','architecture',name)
    _region_faces(band,'carving','border')
    # Solid side shoulders bridge the ledge to the actual full-height flanks.
    shoulder=(w/2-.24)-rx
    if shoulder<=0:raise ValueError('Muqarnas shoulder has no masonry seat')
    bridges=[]
    for side in (-1,1):
        bridge=_TB(name+'_MuqarnasSideSeat'+str(side),origin,angle,
            (side*(rx+shoulder/2),0.,zbase-band_h/2),(shoulder,depth,band_h),
            'brick','vaults','architecture',name)
        # Local side face at x=+/-(w/2-.24) meets the full-height flank.
        bridge['local_bearing_contract']=json.dumps({'outer_x':side*(w/2-.24),
            'flank_inner_x':side*(w/2-.24),'y_interval':[front,front+depth],
            'z_interval':[zbase-band_h,zbase],'kind':'side shoulder into full-height masonry flank'})
        flank=bearings[2 if side<0 else 3]
        contact(name+'_MuqarnasShoulderFlank'+str(side),bridge,flank,
                target=(zbase-band_h)-(F+h))
        contact(name+'_MuqarnasSpringShoulder'+str(side),band,bridge,target=-band_h)
        bridges.append(bridge)
    # A continuous closed masonry backing supports every individually editable
    # tile cell. Its same pointed front section meets the real opening crown.
    stations=[]
    for v in levels:
        x,z=hood_curve(v);stations.append((x,z))
    # Buried outer masonry toe enters the horizontal ledge .04. The continuous
    # backing itself has a bearing; ornament does not carry the masonry hood.
    hood_stations=[(rx+.025,-.09)]+stations
    base=[]
    for x,z in hood_stations:
        base.extend((x*math.cos(i*math.pi/sectors),
                     front+depth*(x/rx)*math.sin(i*math.pi/sectors),zbase+z+.05)
                    for i in range(sectors+1))
    apex=len(base);base.append((0.,front,zbase+rise+.05))
    count=len(base);vertices=[T(x,y,z+offset) for offset in (0.,.10) for x,y,z in base]
    faces=[]
    for shell in (0,1):
        off=shell*count
        for row in range(len(hood_stations)-1):
            for i in range(sectors):
                a=off+row*k+i;faces.append((a,a+1,a+1+k,a+k))
        for i in range(sectors):
            a=off+(len(hood_stations)-1)*k+i;faces.append((a,a+1,off+apex))
    boundary=[row*k for row in range(len(hood_stations))]+[apex]+[
        row*k+sectors for row in range(len(hood_stations)-1,-1,-1)]+list(range(sectors-1,0,-1))
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+count,a+count))
    backing=tag(R.mesh(CURRENT+'_'+name+'_MuqarnasSemiDomeBacking',vertices,faces,'brick',
                     col('roofs'),'vaults','roofs'),'vaults','roofs',name)
    contact(name+'_MuqarnasBackingSpring',backing,band,target=-.04)
    backing['hood_profile']='five receding semi-dome rings and one true pointed crown; continuous masonry behind cells'
    # Closed shallow concave cell soffits, never free hanging repeated cones.
    # Cell backs penetrate the backing .04 at corners and .085 at their recess.
    rings=stations+[(0.,rise)];cell_names=[]
    for row in range(len(rings)-1):
        r0,z0=rings[row];r1,z1=rings[row+1]
        for i in range(sectors):
            a0=i*math.pi/sectors;a1=(i+1)*math.pi/sectors
            def point(r,z,a):return (r*math.cos(a),front+depth*(r/rx)*math.sin(a),zbase+z-.02)
            polygon=[point(r0,z0,a0),point(r0,z0,a1)]
            polygon += [(0.,front,zbase+z1-.02)] if r1==0 else [point(r1,z1,a1),point(r1,z1,a0)]
            center=tuple(sum(p[j] for p in polygon)/len(polygon) for j in range(3))
            center=(center[0],center[1],center[2]+.045)
            low=polygon+[center];n=len(polygon);m=n+1
            vv=[T(x,y,z+offset) for offset in (0.,.11) for x,y,z in low];ff=[]
            for j in range(n):
                q=(j+1)%n;ff.extend([(j,q,n),(j+m,n+m,q+m),(j,j+m,q+m,q)])
            cell=tag(R.mesh(CURRENT+'_'+name+'_MuqarnasCell'+str(row)+'_'+str(i),vv,ff,
                     'carving',col('architecture'),'vaults','architecture'),'vaults','architecture',name)
            _region_faces(cell,'carving','border' if row%2==0 else 'field')
            cell['local_bearing_contract']=json.dumps({'backing_overlap_at_corners':.04,
                'backing_overlap_at_recess':.085,'spring_band_seating_overlap':.02 if row==0 else None,
                'tier':row,'sector':i,'kind':'closed faceted concave tile cell on continuous masonry backing'})
            support=band if row==0 else backing
            bottom=min(v[2] for v in vv);top=R.bounds(support)[1][2]
            # Exact scalar check plus local support data; scalar alone is not a
            # general surface-adjacency proof for the curved reduced hood.
            contact(name+'_MuqarnasCellSeat'+str(row)+'_'+str(i),cell,support,target=bottom-top)
            cell_names.append(cell.name)
    ANCHORS[CURRENT]['royal_portal_hood']={'spring_z':zbase,'clear_lower_passage_top_z':zbase-band_h,
        'preserved_v2_lower_spring_z':old_clear,'actual_pointed_aperture_curve_t_start':start_t,
        'local_depth_interval':[front,front+depth],'sector_count':sectors,'tier_count':len(rings)-1,
        'cells':cell_names,'continuous_backing':backing.name,'spring_band':band.name,
        'top_z':zbase+rise+.15,'source_links':['https://digital.kenyon.edu/baly/847/',
            'https://whc.unesco.org/en/list/115/'],
        'interpretation':'original eight-sector/five-tier coarse seated muqarnas semi-dome; no traced cells, inscriptions, surveyed profile or seventeenth-century revetment claim',
        'chronology_qualification':'Kenyon catalogue notes much vertical tile replaced in1930s; source reproduces documented recognizable form, not a claim of all original1611 fabric'}
    return backing


def _iwan(name,origin,w,d,h,opening,spring,rise,angle=0.,mat='carving'):
    t=min(.16,d/3);T=_trans(origin,angle);bearings=[]
    if mat=='carving':
        # A tall genuine recess leaves a restrained header, rather than a large
        # decorated blank slab above the arch. Original proportions, not survey.
        rise=min(1.24,opening*.67);spring=h-.46-rise
    for label,y0,y1 in [('Front',-d/2,-d/2+t),('Rear',d/2-t,d/2)]:
        ob=tag(_pointed_archwall(CURRENT+'_'+name+'_'+label,0.,y0,y1,F,w,h,opening,spring,rise,mat,
                    col('architecture'),segments=18,transform=T),'walls','architecture',name);bearings.append(ob)
        _iwan_face_uv(ob,origin,angle,w,h,mat)
    for side in (-1,1):
        bearings.append(_TB(name+'_Flank'+str(side),origin,angle,(side*(w/2-.12),0.,F+h/2),
                            (.24,d-2*t,h),'brick',group=name))
    cap_h=.10 if mat=='carving' else .16
    cap=_TB(name+'_Roof',origin,angle,(0.,0.,F+h+cap_h/2),(w,d,cap_h),'stone','vaults','roofs',name)
    for i,bearing in enumerate(bearings):contact(name+'_RoofBearing'+str(i),cap,bearing)
    if name=='AngledRoyalPortal':
        vault=_muqarnas_hood(name,origin,angle,w,d,t,h,opening,spring,rise,bearings)
    else:
        vault=tag(_pointed_vault(CURRENT+'_'+name+'_InnerVault',0.,-d/2+t,d/2-t,F+spring,opening/2,rise,.065,
                     mat,col('roofs'),segments=18,along=2,transform=T),'vaults','roofs',name)
        if mat=='carving':_vault_uv(vault,18,2,'carving','field')
    # A narrow projecting rim sits on the actual cap, framing the recessed
    # opening without a second coplanar facade shell or fake black doorway.
    if mat=='carving':
        rim=_TB(name+'_CrownCoping',origin,angle,(0.,-.010,F+h+.12),(w+.04,d+.02,.04),
                'stone','finish','detail',name)
        contact(name+'_CrownSeat',rim,cap)
        # These original narrow glazed edge strips sit against the solid piers.
        # They are a geometric reduction, not a reproduction of inscriptions.
        for side in (-1,1):
            strip=_TB(name+'_OuterTileReveal'+str(side),origin,angle,
                (side*(w/2-.065),-d/2-.018,F+h/2),(.13,.036,h),
                'carving','finish','detail',name)
            center=T(side*(w/2-.065),0.,0.)[:2]
            _iwan_face_uv(strip,center,angle,.13,h,'carving','border')
        frieze=_TB(name+'_GeometricHeaderFrieze',origin,angle,(0.,-d/2-.018,F+h-.11),
                    (w-.26,.036,.14),'carving','finish','detail',name)
        _iwan_face_uv(frieze,origin,angle,w-.26,.14,'carving','border',F+h-.18,horizontal=True)
        _arch_trim(name+'_OpeningTrim',origin,angle,-d/2,opening,spring,rise,group=name)
    ANCHORS[CURRENT].setdefault('iwans',{})[name]={'origin':origin,'rotation_radians':angle,
         'outer_wdh':[w,d,h],'clear_opening':[opening,spring,rise],
         'inner_vault_spring_z':F+spring,'roof_bottom_z':F+h,
         'framing':'genuine pointed cubic opening, matching trim and inner vault; royal entrance uses seated receding muqarnas hood; no text',
         'pointed_profile':'original inflected cubic: right control points (rx,0),(rx,.60rise),(.25rx,.68rise),(0,rise); mirror at apex',
         'pointed_sources':['https://digital.kenyon.edu/baly/843/','https://digital.kenyon.edu/baly/851/'],
         'source_status':'original compressed anatomy; no surveyed facade coordinates'}
    return {'roof':cap,'vault':vault,'origin':origin,'height':h}


def _sanctuary_windows(name,origin,angle,w,h):
    """Two real high openings; original number/spacing, not surveyed fabric."""
    module=.96;offset=min(.78,w/2-module/2-.08);t=.35
    # The old low openings were hidden behind the neighboring prayer roofs.
    # Keep even the lowest clear opening above the maximum new vault field.
    adjacent_roof=1.75+.06*age()+.18+.31
    sill_h=max(h-.95,adjacent_roof+.08)
    clear_h=min(.66,h-sill_h-.14);opening=min(.58,clear_h*1.35)
    spring=.68*clear_h;rise=.32*clear_h
    if clear_h<=.25:raise ValueError('Clerestory cannot fit above adjacent vaults')
    bearings=[];cursor=-w/2
    T=_trans(origin,angle)
    for index,x in enumerate((-offset,offset)):
        left=x-module/2
        if left>cursor:
            bearings.append(_TB(name+'_Pier'+str(index),origin,angle,
                ((cursor+left)/2,0.,F+h/2),(left-cursor,t,h),'plaster',group='sanctuary'))
        sill=_TB(name+'_SillWall'+str(index),origin,angle,(x,0.,F+sill_h/2),(module,t,sill_h),
                  'plaster',group='sanctuary')
        head=tag(R.archwall(CURRENT+'_'+name+'_HighWindow'+str(index),x,-t/2,t/2,F+sill_h,
                 module,h-sill_h,opening,spring,rise,'plaster',col('architecture'),segments=12,transform=T),
                 'walls','architecture','sanctuary')
        contact(name+'_WindowWallSeat'+str(index),head,sill);bearings.append(head)
        # Sill stone bears on masonry and remains below the actual clear void.
        stone=_TB(name+'_SillStone'+str(index),origin,angle,(x,0.,F+sill_h+.025),
                  (opening+.12,t+.08,.05),'stone','finish','detail','sanctuary')
        contact(name+'_SillStoneSeat'+str(index),stone,sill)
        trim_origin=T(x,0.,0.)[:2]
        _arch_trim(name+'_ClerestoryTrim'+str(index),trim_origin,angle,-t/2+.004,
                   opening,spring-.05,rise,.045,F+sill_h+.05,'sanctuary',stone,pointed=False)
        cursor=x+module/2
    if cursor<w/2:
        bearings.append(_TB(name+'_EndPier',origin,angle,((cursor+w/2)/2,0.,F+h/2),
                             (w/2-cursor,t,h),'plaster',group='sanctuary'))
    ANCHORS[CURRENT].setdefault('clerestories',{})[name]={
       'actual_clear_bottom_z':F+sill_h+.05,'actual_arch_top_z':F+sill_h+clear_h,
       'adjacent_vault_maximum_z':F+adjacent_roof,
       'minimum_roof_clearance':sill_h+.05-adjacent_roof,
       'status':'six original high windows with geometric trim; exact count/spacing is interpretation, not surveyed Royal Mosque fabric'}
    return bearings


def first_room():
    p=PLAN[age()];cy=p['back']+2.30;h=p['hall_h'];w=d=3.20;t=.35;g='sanctuary'
    bearings=_sanctuary_windows('SanctuaryBack',(0.,cy+d/2-t/2),math.pi,w,h)
    # Side modules do not collide with the front/back corner returns.
    for side in (-1,1):
        bearings+=_sanctuary_windows('SanctuarySide'+str(side),(side*(w/2-t/2),cy),side*math.pi/2,d-2*t,h)
    front=tag(_pointed_archwall(CURRENT+'_SanctuaryOpening',0.,cy-d/2,cy-d/2+t,F,w,h,1.85,
              h-.95,.55,'brick',col('architecture'),segments=20),'walls','architecture',g)
    floor=B('SanctuaryFloor',(0.,cy,F+.035),(w-2*t,d-2*t,.07),'stone','foundation','architecture',g)
    ASSEMBLIES[CURRENT]['sanctuary']={'cy':cy,'bearings':bearings+[front],'floor':floor}
    ANCHORS[CURRENT]['chronology']={'monument':'Royal Mosque of Isfahan, begun1611; completed early SafiI reign with later documented finishes',
       'native_resource_key':CURRENT,'not_historical_age':'Existing resource label does not date the Royal Mosque to934–1501 or create an earlier Wonder tier',
       'late_finish_policy':'completed17C identity accepted; geometric tile/dado influence may postdate1629; no falsely precise finished-in1629 claim'}
    print('FIRST_ROOM_DRAFT',CURRENT,'occupied sanctuary beneath the principal dome')


def _dome():
    p=PLAN[age()];a=ASSEMBLIES[CURRENT]['sanctuary'];cy=a['cy'];h=p['hall_h'];r=p['dome_r']
    roof=B('SanctuaryRoof',(0.,cy,F+h+.09),(3.20,3.20,.18),'stone','vaults','roofs','sanctuary')
    for i,bearing in enumerate(a['bearings']):contact('SanctuaryRoofBearing'+str(i),roof,bearing)
    a['roof']=roof
    base_z=F+h+.18
    trans=tag(R.lathe(CURRENT+'_DomeOctagonalTransition',(0.,cy,base_z),[(1.38*r,0),(1.38*r,.10),(1.10*r,.22)],
              'brick',col('roofs'),sides=8,stage='vaults',role='roofs'),'vaults','roofs','main_dome')
    contact('DomeTransitionSeat',trans,a['roof'])
    drum=tag(R.lathe(CURRENT+'_DomeDrum',(0.,cy,base_z+.22),[(1.10*r,0),(1.10*r,.42)],
              'carving',col('roofs'),sides=32,stage='vaults',role='roofs'),'vaults','roofs','main_dome')
    _longitude_uv(drum,(0.,cy,base_z+.22),[(1.10*r,0),(1.10*r,.42)],32,'carving',region='drum')
    contact('DomeDrumSeat',drum,trans)
    profile=[(1.06,0),(1.10,.16),(1.23,.38),(1.40,.75),(1.44,1.00),(1.38,1.25),
             (1.20,1.55),(.90,1.82),(.55,2.02),(.16,2.18),(.04,2.22)]
    rings=[(rr*r,z*p['dome_z']) for rr,z in profile]
    dome=tag(R.lathe(CURRENT+'_MainBulbousDome',(0.,cy,base_z+.64),rings,
             'roof',col('roofs'),sides=48,stage='vaults',role='roofs'),'vaults','roofs','main_dome')
    _longitude_uv(dome,(0.,cy,base_z+.64),rings,48)
    contact('DomeShellDrumSeat',dome,drum)
    crown_z=base_z+.64+2.22*p['dome_z']
    finial=tag(R.lathe(CURRENT+'_DomeFinial',(0.,cy,crown_z),[(.055,0),(.055,.08),(.09,.10),(.06,.17),(.018,.36)],
             'metal',col('details'),sides=12,stage='finish',role='detail'),'finish','detail','main_dome')
    contact('DomeFinialSeat',finial,dome)
    ANCHORS[CURRENT]['main_crown']={'base':base_z,'drum_top':base_z+.64,'finial_top':crown_z+.36,
          'maximum_diameter':2*1.44*r,'dome_diameter_to_short_court_ratio':2*1.44*r/min(p['court_w'],p['back']-p['front']),
          'uv_contract':'single longitude wrap, height-normalized roof tile; UVMap1 identical; smooth sides/flat caps; preserve UVs through state/LOD cloning',
          'interpretation':'controlled bulbous profile on square/octagonal/circular transition, not a sphere on a roof'}


def _minaret(name,x,y,height):
    # Two pairs belong to portal and sanctuary frontage, not four court corners.
    rings=[(.28,0),(.28,.20),(.19,.20),(.18,height-1.10),
           (.23,height-1.02),(.29,height-.92),(.29,height-.82),
           (.22,height-.82),(.22,height-.64),(.155,height-.64),
           (.155,height-.36),(.205,height-.36),(.205,height-.29),(.10,height-.16),(.02,height)]
    ob=tag(R.lathe(CURRENT+'_'+name,(x,y,F),rings,'carving',col('architecture'),sides=24,
                 stage='walls',role='architecture'),'walls','architecture','minaret_'+name)
    _longitude_uv(ob,(x,y,F),rings,24,'carving',region='shaft')
    contact(name+'_Foot',ob,ASSEMBLIES[CURRENT]['ground'])
    ANCHORS[CURRENT].setdefault('minarets',{})[name]={'xy':[x,y],'top':F+height,
       'profile':'lighter banded tapered shaft, .29 radius flared balcony/rim, distinct neck/capped upper stage; flat ledges and smooth shafts',
       'certainty':'original relative dimensions; exact historical minaret heights/diameters not asserted'}


def _vestibule():
    p=PLAN[age()];T=_trans((0.,p['portal_y']),math.pi/4)
    left=T(-.60,.43,0)[:2];right=T(.60,.43,0)[:2]
    court_left=(-.60,p['front']-.60);court_right=(.60,p['front']-.60)
    wall_h=min(p['entry_h']-.40,2.45)
    walls=[]
    for label,a,b in [('West',left,court_left),('East',right,court_right)]:
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        ob=tag(R.block(CURRENT+'_TurnVestibule'+label,((a[0]+b[0])/2,(a[1]+b[1])/2,F+wall_h/2),
                 (length,.18,wall_h),'brick',col('architecture'),'walls','architecture',math.atan2(dy,dx)),
                 'walls','architecture','entrance_turn');walls.append(ob)
    outline=[left,right,court_right,court_left];n=4
    verts=[(x,y,z) for z in (F+wall_h,F+wall_h+.16) for x,y in outline]
    faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    cap=tag(R.mesh(CURRENT+'_TurnVestibuleRoof',verts,faces,'stone',col('roofs'),'vaults','roofs'),
                 'vaults','roofs','entrance_turn')
    for i,bearing in enumerate(walls):contact('VestibuleRoofBearing'+str(i),cap,bearing)
    ANCHORS[CURRENT]['entrance_turn']={'portal_rotation_degrees':45,'portal_center':[0.,p['portal_y']],
        'vestibule_outline':outline,'court_rear_axis_y':p['front']-.60,
        'status':'original compact oblique connection inspired by Coste adjacency, not a traced/surveyed polygon'}


def _side_arcades():
    p=PLAN[age()];half=p['court_w']/2;front,back=p['front'],p['back'];mid=(front+back)/2
    # A real central lateral iwan plus smaller arch modules; three independently
    # authored low bays are compressed around it rather than equal detached gates.
    for side,sgn,angle in [('West',-1,math.pi/2),('East',1,-math.pi/2)]:
        _iwan(side+'Iwan',(sgn*(half+.45),mid),1.70,.90,p['side_h'],1.02,1.65,.38,angle)
        chamber=side+'DomedChamber'
        ch=room(chamber,(sgn*(half+1.70),mid,2.10,1.60,2.15+.08*age()),(0.,),arched=True,
                turn=1 if sgn<0 else -1,door_leaf=False)
        cap=roof_room(chamber)
        small=tag(R.lathe(CURRENT+'_'+chamber+'_Dome',(sgn*(half+1.70),mid,F+2.15+.08*age()+.18),
                  [(.64,0),(.66,.06),(.60,.17),(.42,.29),(.04,.38)],'brick',col('roofs'),sides=20,
                  stage='vaults',role='roofs'),'vaults','roofs',chamber)
        contact(chamber+'_DomeSeat',small,cap)
        # North-edge wings join the entrance iwan and the side arcade ends.
        fw=half-1.05
        if fw>.30:
            _iwan(side+'EntranceWing',(sgn*(1.05+fw/2),front-.42),fw,.84,1.75+.10*age(),
                   max(.25,fw-.24),1.12,.22,math.pi,mat='brick')
            wall(side+'EntranceWingBacking',sgn*(1.05+fw/2),front-.93,fw,.18,1.75+.10*age(),group='court_perimeter')
        # Two north/south residual bays, with independently sized plan lengths.
        for end,y0,y1 in [('Front',front,mid-.85),('Back',mid+.85,back)]:
            length=y1-y0
            if length<.30:continue
            count=min(p['arcades'],max(1,int(length/.45)))
            for i in range(count):
                span=length/count
                _iwan(side+end+'Arcade'+str(i),(sgn*(half+.42),y0+(i+.5)*span),span,.84,1.70+.10*age(),
                      max(.22,span-.22),1.10,.22,angle,mat='brick')
                wall(side+end+'ArcadeBacking'+str(i),sgn*(half+.93),y0+(i+.5)*span,.18,span,1.70+.10*age(),group='court_perimeter')


def _connected_vault_field(name,x,front,depth,base_z,bays):
    """One editable low connected masonry cover with subordinate bay crowns.

    Original roof reduction inspired by the plan's lower repeated prayer bays;
    this continuous cover and exact vault curvature are not surveyed fabric.
    """
    nx=12;ny=max(12,bays*10);half=.88;minimum=.06;rise=.25
    centers=[front+depth/2] if bays==1 else [front+.65+i*(depth-1.30)/(bays-1) for i in range(bays)]
    radius_y=depth/2-.08 if bays==1 else max(.80,(depth-1.30)/(bays-1)*.70)
    verts=[]
    for shell in (0,1):
        for j in range(ny+1):
            yy=front+.08+(depth-.16)*j/ny
            for i in range(nx+1):
                xx=-half+2*half*i/nx
                shape=max(max(0.,1-(xx/.86)**2-((yy-cy)/radius_y)**2)**.60 for cy in centers)
                z=base_z+(minimum+rise*shape if shell==1 else 0.)
                verts.append((x+xx,yy,z))
    count=(nx+1)*(ny+1);faces=[]
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i
            faces.append((a,a+nx+1,a+nx+2,a+1))
            faces.append((a+count,a+1+count,a+nx+2+count,a+nx+1+count))
    perimeter=[i for i in range(nx+1)]+[j*(nx+1)+nx for j in range(1,ny+1)]+[
                ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
    for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):faces.append((a,b,b+count,a+count))
    ob=tag(R.mesh(CURRENT+'_'+name+'_ConnectedVaultField',verts,faces,'brick',col('roofs'),'vaults','roofs'),
                'vaults','roofs',name)
    for poly in ob.data.polygons:
        # Continuous physical XY masonry mapping, not a full brick tile on every
        # grid quad. Curved upper field is smooth; lower face/edge walls are flat.
        poly.use_smooth=poly.normal[2]>.10
        if abs(poly.normal[2])<=.10:continue
        for li in poly.loop_indices:
            co=ob.data.vertices[ob.data.loops[li].vertex_index].co
            uv=_tile_uv('brick',(co[0]-x+half)/(2*half),(co[1]-front-.08)/(depth-.16))
            for layer in ob.data.uv_layers:layer.data[li].uv=uv
    ob['preserve_custom_source_uv']=True;ob['uv_mapping']='continuous vault-field XY masonry'
    ob['bay_centres_y']=centers
    ANCHORS[CURRENT].setdefault('connected_prayer_roofs',{})[name]={
       'bay_centres_y':centers,'base_z':base_z,'maximum_top_z':base_z+minimum+rise,
       'minimum_cover':minimum,'rise':rise,'status':'original shallow connected bay reduction; source roof construction not surveyed'}
    return ob


def _winter_halls():
    p=PLAN[age()];front=p['back']+.40;depth=3.50;cy=front+depth/2
    # A1 uses shortened one-bay prayer wings; the other resources use longer
    # halls and secondary courts. This is an original compression choice.
    if age()==1:depth=2.35;cy=front+depth/2
    for s in (-1,1):
        x=s*2.55;name=('West' if s<0 else 'East')+'WinterHall'
        room(name,(x,cy,1.90,depth,1.75+.06*age()),(0.,),arched=True,door_leaf=False)
        roof=roof_room(name)
        base_z=F+1.75+.06*age()+.18
        field=_connected_vault_field(name,x,front,depth,base_z,p['roof_bays'])
        contact(name+'_ConnectedVaultSeat',field,roof)
        if p['side_courts']:
            # Distinct narrow side voids; A3 west trace starts slightly forward,
            # reflecting original envelope reduction, not a claim of original phase.
            court_front=front-(.30 if age()==3 and s<0 else 0.)
            outside_x=s*5.30
            wall(name+'_OuterCourtWall',outside_x,(court_front+5.30)/2,.22,5.30-court_front,1.45,group='side_court')
            wall(name+'_CourtRear',s*4.45,5.30,1.70,.22,1.45,group='side_court')
            # A low occupied rear cell is a real room, not an empty decorative cap.
            cell=room(name+'_RearCell',(s*4.45,4.75,1.48,.88,1.62),(0.,),arched=True)
            roof_room(name+'_RearCell')
            ANCHORS[CURRENT].setdefault('secondary_courts',[]).append({'side':s,'x':[3.50,5.19],
                   'y':[court_front,4.30],'status':'compressed subordinate open trace, not the full22x44m historical court'})


def architecture():
    p=PLAN[age()];half=p['court_w']/2
    _dome()
    _iwan('QiblaIwan',(0.,p['back']+.50),3.20,1.00,p['qibla_h'],2.15,2.25,.65)
    _iwan('CourtEntranceIwan',(0.,p['front']-.30),2.10,.60,p['entry_h'],1.30,1.85,.45,math.pi)
    _side_arcades();_winter_halls()
    _iwan('AngledRoyalPortal',(0.,p['portal_y']),2.50,.86,p['portal_h'],1.60,1.95,.63,math.pi/4)
    _vestibule()
    T=_trans((0.,p['portal_y']),math.pi/4)
    for s in (-1,1):
        x,y,z=T(s*1.38,0.,F);_minaret('PortalMinaret'+str(s),x,y,p['portal_top'])
        _minaret('SanctuaryMinaret'+str(s),s*1.74,p['back']+.75,p['sanctuary_top'])
    # Warm court paving remains a visible negative shape, not a palace garden.
    pave=B('MainCourtPaving',(0.,(p['front']+p['back'])/2,F+.018),(p['court_w'],p['back']-p['front'],.036),
           'stone','foundation','ground','main_court')
    contact('CourtPavingGround',pave,ASSEMBLIES[CURRENT]['ground'])
    ANCHORS[CURRENT]['program']={'court':[-half,half,p['front'],p['back']],
        'four_iwan_names':['QiblaIwan','CourtEntranceIwan','WestIwan','EastIwan'],
        'resource_body_variation':'original court/occupied-hall/roof-bay/side-court programme; not four historic mosque ages'}
    print('ARCHITECTURE_DRAFT',CURRENT,'turned portal, four-iwan court, main dome and two minaret pairs')


def props():
    p=PLAN[age()];y=(p['front']+p['back'])/2
    base_z=F+.036
    base=B('AblutionBasinBase',(0.,y,base_z+.035),(1.15,.85,.07),'stone','foundation','props','court_basin')
    for label,x,yy,w,d in [('West',-.53,y,.09,.85),('East',.53,y,.09,.85),
             ('North',0.,y+.38,.97,.09),('South',0.,y-.38,.97,.09)]:
        rim=B('BasinRim'+label,(x,yy,base_z+.12),(w,d,.10),'stone','finish','props','court_basin')
        contact('BasinRimSeat'+label,rim,base)
    B('BasinDampInterior',(0.,y,base_z+.08),(.95,.65,.015),'ink','finish','props','court_basin')
    # Coste identifies the pulpit in the sanctuary, but these five risers and
    # textile dimensions are original functional reductions, not traced fabric.
    hall=ASSEMBLIES[CURRENT]['sanctuary'];cy=hall['cy'];floor=hall['floor'];floor_top=F+.07
    for index,yy in enumerate((cy-.80,cy-.30)):
        runner=B('SanctuaryPrayerRunner'+str(index),(0.,yy,floor_top+.007),(1.85,.38,.014),
                   'cloth','finish','props','sanctuary')
        contact('PrayerRunnerFloor'+str(index),runner,floor)
    for index in range(5):
        height=(index+1)*.10
        step=B('MinbarRiser'+str(index),(-.83,cy-.05+(index+.5)*.18,floor_top+height/2),
                 (.55,.18,height),'timber','finish','props','sanctuary')
        contact('MinbarRiserFloor'+str(index),step,floor)
    landing=B('MinbarStandingLanding',(-.83,cy+.975,floor_top+.25),(.55,.25,.50),
                'timber','finish','props','sanctuary')
    contact('MinbarLandingFloor',landing,floor)
    posts=[]
    for side in (-1,1):
        post=B('MinbarRearPost'+str(side),(-.83+side*.235,cy+1.06,floor_top+.80),(.08,.08,.60),
                 'timber','finish','props','sanctuary')
        contact('MinbarRearPostSeat'+str(side),post,landing);posts.append(post)
    rail=B('MinbarRearRail',(-.83,cy+1.06,floor_top+1.135),(.55,.10,.07),
             'timber','finish','props','sanctuary')
    for index,post in enumerate(posts):contact('MinbarRearRailSeat'+str(index),rail,post)
    # Ordinary prayer/circulation purpose does not need statues, huge gardens or
    # copied text. Native garden/bench attachments remain external contracts.
    ANCHORS[CURRENT]['sanctuary_occupation']={'prayer_runners':2,'minbar_risers':5,
       'certainty':'Coste pulpit location supports programme; exact dimensions/material/number of original source steps are interpretations'}
    print('PROPS_DRAFT',CURRENT,'restrained basin, open court and occupied prayer hall')


def detail():
    p=PLAN[age()]
    # Fixed cobalt/turquoise live in carving/roof atlas tiles. Owner tile is only
    # the small administrative textile; a player's color must not recolor dome.
    T=_trans((0.,p['portal_y']),math.pi/4);x,y,z=T(0.,-.46,F+p['portal_h']-.12)
    support=_TB('PortalOwnerSupport',(0.,p['portal_y']),math.pi/4,(0.,-.46,F+p['portal_h']-.12),
                (.92,.07,.07),'timber','finish','fittings','owner')
    cloth=_TB('PortalOwnerCloth',(0.,p['portal_y']),math.pi/4,(0.,-.50,F+p['portal_h']-.255),
               (.78,.02,.20),'owner','finish','owner','owner')
    contact('PortalOwnerSuspended',cloth,support,'top-bottom')
    ANCHORS[CURRENT]['atlas_semantics']={'roof':'fixed turquoise principal dome',
       'carving':'fixed cobalt/turquoise geometric portal/drum/minaret tile',
       'brick':'warm lower roofs and structural masonry','stone':'paving and restrained lower finish',
       'owner':'small separate textile only','text':'no fabricated calligraphy; geometric pattern only'}
    print('DETAIL_DRAFT',CURRENT,'original geometric tile hierarchy; no invented calligraphy')
