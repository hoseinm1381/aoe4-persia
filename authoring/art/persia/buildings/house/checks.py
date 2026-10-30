"""Actual mesh/UV/contact gates for the House source master."""
import bpy,bmesh,math,json,hashlib,struct
from pathlib import Path
import recipe as H
R=H.R

def tris(obs):return sum(len(p.vertices)-2 for o in obs if o.type=='MESH' for p in o.data.polygons)

def digest(o):
    # Canonical oriented surfaces + vertex multiset ignore harmless Boolean
    # element ordering, while retaining winding, UV seams and duplicate counts.
    def q(x):return round(float(x),5) or 0.0
    vertices=[tuple(q(x) for x in v.co) for v in o.data.vertices];faces=[]
    for p in o.data.polygons:
        loops=[vertices[o.data.loops[i].vertex_index]+tuple(q(x) for layer in o.data.uv_layers for x in layer.data[i].uv) for i in p.loop_indices]
        faces.append(min(tuple(loops[j:]+loops[:j]) for j in range(len(loops))))
    data=[sorted(vertices),[layer.name for layer in o.data.uv_layers],sorted(faces)]
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()

def contacts():
    result=[]
    contracts=H.CONTRACTS or json.loads((H.ROOT/'evidence/contact-contracts.json').read_text())
    for c in contracts:
        a=bpy.data.objects.get(c['a']);b=bpy.data.objects.get(c['b'])
        if a is None or b is None:result.append({**c,'passed':False,'error':'missing contact object'});continue
        alo,ahi=R.bounds(a);blo,bhi=R.bounds(b)
        gap=alo[2]-bhi[2] if c['axis']=='bottom-top' else ahi[2]-blo[2]
        overlap=[min(ahi[i],bhi[i])-max(alo[i],blo[i]) for i in [0,1]]
        result.append({**c,'measured_gap':gap,'projected_xy_overlap':overlap,'passed':abs(gap-c['target'])<=c['tolerance'] and min(overlap)>=-c['tolerance']})
    return result

def coplanar_roof_overlaps(collection):
    """Visible upper roof/deck rectangular faces only; not buried joinery."""
    groups={};bad=[]
    for o in collection.all_objects:
        if o.type!='MESH' or not (o.get('role')=='roofs' or 'PorchFloor' in o.name):continue
        for p in o.data.polygons:
            if p.normal.z<.99999 or len(p.vertices)!=4:continue
            axis=max(range(3),key=lambda i:abs(p.normal[i]))
            if abs(p.normal[axis])<.99999:continue
            pts=[o.data.vertices[j].co for j in p.vertices]
            if max(v[axis] for v in pts)-min(v[axis] for v in pts)>1e-6:continue
            a,b=[i for i in range(3) if i!=axis]
            row=(o.name,min(v[a] for v in pts),max(v[a] for v in pts),min(v[b] for v in pts),max(v[b] for v in pts))
            group=(axis,1 if p.normal[axis]>0 else -1,round(pts[0][axis],5))
            for old in groups.get(group,[]):
                overlap=max(0,min(old[2],row[2])-max(old[1],row[1]))*max(0,min(old[4],row[4])-max(old[3],row[3]))
                if old[0]!=row[0] and overlap>.0025:bad.append({'a':old[0],'b':row[0],'area':overlap,'axis':axis,'plane':group[2]})
            groups.setdefault(group,[]).append(row)
    return bad

def perimeter_wall_overlaps(collection):
    """Exact exterior X-plane overlap between courtyard boundary and rooms."""
    bad=[];obs=[o for o in collection.all_objects if o.type=='MESH']
    for boundary in obs:
        if not any(n in boundary.name for n in ['BoundaryEast','BoundaryWest']):continue
        sign=1 if 'BoundaryEast' in boundary.name else -1
        def faces(ob):
            result=[]
            for p in ob.data.polygons:
                if p.normal.x*sign<.99999 or len(p.vertices)!=4:continue
                vs=[ob.data.vertices[i].co for i in p.vertices]
                result.append((round(vs[0].x,5),min(v.y for v in vs),max(v.y for v in vs),min(v.z for v in vs),max(v.z for v in vs)))
            return result
        for wall in obs:
            if wall.get('role')!='architecture' or not wall.get('structural_group','').startswith('room_'):continue
            for a in faces(boundary):
                for b in faces(wall):
                    area=max(0,min(a[2],b[2])-max(a[1],b[1]))*max(0,min(a[4],b[4])-max(a[3],b[3]))
                    if a[0]==b[0] and area>.0025:bad.append({'a':boundary.name,'b':wall.name,'area':area,'plane_x':a[0]})
    return bad

def run(key='A1a',complete=False,write=True):
    errors=[];rows=[]
    cols=[c for c in bpy.data.scenes[R.SCENE].collection.children if c.name.startswith(R.PREFIX+key+'_')]
    expected={R.PREFIX+key+'_'+s+'_LOD'+str(l) for s in ['healthy',*[f'damage_{i}' for i in range(1,6)],'ruins','preview','targeting'] for l in [0,1,2]}
    expected|={R.PREFIX+key+'_construct_'+s for s in ['foundation','walls','vaults','finish']}
    if complete:
        for n in sorted(expected-{c.name for c in cols}):errors.append('missing composition '+n)
    for c in cols:
        obs=[o for o in c.all_objects if o.type=='MESH'];points=[v.co for o in obs for v in o.data.vertices]
        rows.append({'collection':c.name,'triangles':tris(obs),'parts':len(obs),'bounds_min':[min(v[i] for v in points) for i in range(3)] if points else None,'bounds_max':[max(v[i] for v in points) for i in range(3)] if points else None})
        for o in obs:
            if o.data.users!=1:errors.append('shared mesh '+o.name)
            if any(abs(v)>1e-6 for v in (*o.location,*o.rotation_euler)) or any(abs(v-1)>1e-6 for v in o.scale):errors.append('unapplied transform '+o.name)
            if len(o.data.uv_layers)!=2:errors.append('UV layers '+o.name)
            for layer in o.data.uv_layers:
                if any(not all(math.isfinite(v) and -.0001<=v<=1.0001 for v in a.uv) for a in layer.data):errors.append('invalid UV '+o.name)
            bm=bmesh.new();bm.from_mesh(o.data)
            if any(not e.is_manifold for e in bm.edges):errors.append('open topology '+o.name)
            if any(e.is_manifold and not e.is_contiguous for e in bm.edges):errors.append('inconsistent face winding '+o.name)
            if any(f.calc_area()<1e-10 for f in bm.faces):errors.append('zero-area face '+o.name)
            if bm.calc_volume(signed=True)<=0:errors.append('inward/zero volume '+o.name)
            bm.free()
    measured=[c for c in contacts() if c['body']==key]
    for c in measured:
        if not c['passed']:errors.append('contact '+c['name'])
    construction_exact=None
    placement_exact=[]
    damage_progression=[]
    overlaps=coplanar_roof_overlaps(H.root(key))+perimeter_wall_overlaps(H.root(key))
    errors.extend('coplanar overlap '+o['a']+' / '+o['b'] for o in overlaps)
    if complete:
        previous_debris=0
        def parts(coll):return {o.get('healthy_source',o.name):o for o in coll.all_objects if o.type=='MESH'}
        for n in range(1,6):
            coll=bpy.data.collections.get(R.PREFIX+key+'_damage_'+str(n)+'_LOD0')
            if coll is None:continue
            fallen=sum(o.get('role')=='debris' for o in coll.all_objects)
            okay=fallen>0 and fallen>=previous_debris;previous_debris=fallen
            damage_progression.append({'level':n,'grounded_debris_parts':fallen,'passed':okay})
            if not okay:errors.append('missing/nonprogressive damage debris '+str(n))
        third=bpy.data.collections.get(R.PREFIX+key+'_damage_3_LOD0');fourth=bpy.data.collections.get(R.PREFIX+key+'_damage_4_LOD0')
        if third and fourth:
            third_parts=parts(third);fourth_parts=parts(fourth)
            changed_roofs=[name for name,o in third_parts.items() if o.get('structural_group')=='room_1' and o.get('role')=='roofs' and (name not in fourth_parts or digest(o)!=digest(fourth_parts[name]))]
            if not changed_roofs:errors.append('damage4 service roof failure missed this body')
            damage_progression.append({'transition':'3 to 4','changed_service_roof_parts':changed_roofs,'passed':bool(changed_roofs)})
        hc=H.root(key);cc=bpy.data.collections.get(R.PREFIX+key+'_construct_finish')
        if cc:
            construction_exact={o.name:digest(o) for o in hc.all_objects if o.type=='MESH'}=={o.get('healthy_source'):digest(o) for o in cc.all_objects if o.type=='MESH'}
            if not construction_exact:errors.append('construction finish differs from healthy')
        for lod in [0,1,2]:
            healthy=bpy.data.collections.get(R.PREFIX+key+'_healthy_LOD'+str(lod))
            def source_identity(o):return '__authored_stair_proxy' if o.get('structural_group')=='stair' and 'SimplifiedStair' in o.name else o.get('healthy_source',o.name)
            want={source_identity(o):digest(o) for o in healthy.all_objects if o.type=='MESH'}
            for state in ['preview','targeting']:
                coll=bpy.data.collections.get(R.PREFIX+key+'_'+state+'_LOD'+str(lod))
                if coll is None:continue
                actual={source_identity(o):digest(o) for o in coll.all_objects if o.type=='MESH'}
                expected_map={n:d for n,d in want.items() if state=='preview' or not any(t in n for t in ['_EarthBed','_CourtBase'])}
                okay=actual==expected_map
                placement_exact.append({'state':state,'lod':lod,'passed':okay,'parts':len(actual)})
                if not okay:errors.append('placement membership/geometry differs '+state+' LOD'+str(lod))
        for row in rows:
            name=row['collection']
            if name.endswith(('LOD1','LOD2')):
                base=bpy.data.collections.get(name[:-1]+'0');ratio=row['triangles']/tris(base.all_objects)
                target=.5 if name.endswith('LOD1') else .25;row['lod_ratio']=ratio
                if abs(ratio-target)>.095:errors.append('LOD ratio '+name+': '+str(round(ratio,4)))
        native=json.loads((H.ROOT/'native-contracts.json').read_text())['models']
        suffix=f'sul_house_control_{key[-1]}_age0{key[1]}.rgm';contract=next(v for p,v in native.items() if p.endswith('/'+suffix))
        envelope=contract['healthy_primary_bounds'];budget=json.loads((H.ROOT/'evidence/stock-budgets.json').read_text())['budgets_by_age'][key[1]]
        cap=budget['cap_guaranteed_native_maximum_triangles']
        for row in rows:
            if row['triangles']>cap:errors.append('stock composition cap '+row['collection'])
            if row['bounds_min'] and any(row['bounds_min'][i]<envelope['min'][i]-1e-5 or row['bounds_max'][i]>envelope['max'][i]+1e-5 for i in range(3)):errors.append('native model envelope '+row['collection'])
    original=json.loads((H.ROOT/'evidence/original-scene.json').read_text());s=bpy.data.scenes.get(original['scene'])
    observed={'scene':s.name,'world':s.world.name if s.world else None,'objects':[{'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'mesh_vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in s.objects]} if s else None
    if observed!=original:errors.append('unrelated default scene changed')
    images=[]
    for kind in ['albedo','normal','roughness','metalness','owner_mask']:
        im=bpy.data.images.get(R.PREFIX+kind);ok=bool(im and list(im.size)==[2048,2048] and Path(bpy.path.abspath(im.filepath)).is_file())
        if not ok:errors.append('unresolved 2048 texture '+kind)
        images.append({'map':kind,'passed':ok})
    doc={'key':key,'passed':not errors,'complete_requested':complete,'construction_exact_healthy_restore':construction_exact,'placement_checks':placement_exact,'damage_progression':damage_progression,'coplanar_overlap_defects':overlaps,'errors':errors,'compositions':rows,'contacts':measured,'textures':images,'native_gates':'deferred; source checks only'}
    if write:(H.ROOT/'evidence'/('checks-'+key+'.json')).write_text(json.dumps(doc,indent=2)+'\n')
    print('HOUSE_CHECK',key,not errors,len(errors),json.dumps(errors[:12]));return doc

def manifest():
    native_labels={f'construct_{n:02}':'construct_'+('foundation' if n<=20 else 'walls' if n<=55 else 'vaults' if n<=90 else 'finish') for n in range(0,100,5)}
    native_labels.update({s:s for s in ['healthy',*[f'damage_{n}' for n in range(1,6)],'ruins','preview','targeting']})
    doc={'schema':'persia-building-source/1','family':'House','source_art_only':True,'native_hp_thresholds':None,'native_state_source_assembly_proposal':native_labels,'native_construction_progress_wiring':'Deferred. Labels are exact native strings; source assembly grouping is an authored proposal, not runtime proof.','placement_sources':'Preview reuses healthy composition; targeting omits authored plot base. Native ghost tint/placement rendering remains unverified.','selector_aliases_are_not_states':['sel_base','sel_ruins_disappear','gen7'],'compositions':{}}
    doc['geometry_digest_method']='Q5 canonical oriented polygon surfaces including every UV layer and vertex multiset; element ordering ignored, winding and duplicate counts retained.'
    for c in bpy.data.scenes[R.SCENE].collection.children:
        if not c.name.startswith(R.PREFIX):continue
        doc['compositions'][c.name]={'parts':[{'name':o.name,'healthy_source':o.get('healthy_source',o.name),'role':o.get('role'),'group':o.get('structural_group'),'stage':o.get('construction_stage'),'triangles':tris([o]),'geometry_uv_digest_q5':digest(o)} for o in c.all_objects if o.type=='MESH']}
    (H.ROOT/'state-manifest.json').write_text(json.dumps(doc,indent=2)+'\n');return doc
