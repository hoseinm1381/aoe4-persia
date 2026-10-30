"""Small reusable Blender source-art runner. No native export/build operations."""
from pathlib import Path
import bpy,bmesh,json,math,random
from mathutils import Vector,Matrix

ROOT=Path(__file__).resolve().parent
PREFIX='PS_SamarkandBazaar_'
TILES=['plaster','brick','stone','timber','owner','cloth','roof','earth','leaves','rubble','ink','paper','metal','grime','carving','pottery']
COLOURS=[(.65,.54,.37,1),(.42,.19,.10,1),(.42,.37,.27,1),(.17,.10,.05,1),(.12,.32,.52,1),(.43,.31,.15,1),(.48,.34,.19,1),(.28,.20,.12,1),(.18,.23,.08,1),(.36,.25,.14,1),(.06,.05,.04,1),(.65,.54,.32,1),(.20,.18,.13,1),(.23,.18,.11,1),(.68,.55,.36,1),(.49,.23,.12,1)]

def collection(name,parent):
    c=bpy.data.collections.get(name)
    if not c:c=bpy.data.collections.new(name)
    if c.name not in parent.children:parent.children.link(c)
    return c

def setup_scene():
    s=bpy.data.scenes.get('PS_SamarkandBazaar')
    if not s:
        original=bpy.data.scenes.get('Scene') or bpy.context.scene
        record={'scene':original.name,'world':original.world.name if original.world else None,
                'objects':[{'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'mesh_vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in original.objects]}
        (ROOT/'evidence').mkdir(exist_ok=True)
        if not (ROOT/'evidence/original-scene.json').exists():(ROOT/'evidence/original-scene.json').write_text(json.dumps(record,indent=2)+'\n')
        s=bpy.data.scenes.new('PS_SamarkandBazaar')
    bpy.context.window.scene=s
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s['scope']='Editable source art only; native export, cook and mod integration deferred'
    s['native_footprint_scale']='Read evidence/native-owners.json; unchanged gameplay source'
    s['visual_envelope_basis']='Read evidence/fit-contract.json; source fit only; native clearance deferred'
    s.render.engine='CYCLES';s.cycles.samples=32
    s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100
    s.view_settings.view_transform='AgX'
    if not s.world or s.world.name=='World':
        w=bpy.data.worlds.get(PREFIX+'World') or bpy.data.worlds.new(PREFIX+'World');s.world=w
        w.use_nodes=True;w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.42,.49,.56,1)
        w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45
    return s

def material():
    name=PREFIX+'SharedAtlas'
    mat=bpy.data.materials.get(name)
    if mat:return mat
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(.65,.54,.36,1)
    n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputMaterial');out.location=(800,100)
    bs=n.new('ShaderNodeBsdfPrincipled');bs.location=(540,100);l.new(bs.outputs['BSDF'],out.inputs['Surface'])
    tex={}
    for i,kind in enumerate(('albedo','normal','roughness','metalness','owner_mask')):
        im=bpy.data.images.load(str(ROOT/'textures'/(kind+'.png')),check_existing=True)
        im.name=PREFIX+kind
        if kind!='albedo':im.colorspace_settings.name='Non-Color'
        t=n.new('ShaderNodeTexImage');t.image=im;t.name=kind;t.label=kind;t.location=(-700,350-i*210)
        t.interpolation='Linear';tex[kind]=t
    rgb=n.new('ShaderNodeRGB');rgb.name='OWNER_COLOUR';rgb.label='Preview owner colour - source only';rgb.location=(-410,450)
    rgb.outputs[0].default_value=(.035,.22,.48,1)
    multiply=n.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1;multiply.location=(-120,310)
    l.new(tex['albedo'].outputs['Color'],multiply.inputs[1]);l.new(rgb.outputs[0],multiply.inputs[2])
    channel=n.new('ShaderNodeSeparateColor');channel.location=(-400,-430);l.new(tex['owner_mask'].outputs['Color'],channel.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.location=(230,230)
    l.new(channel.outputs['Red'],mix.inputs[0]);l.new(tex['albedo'].outputs['Color'],mix.inputs[1]);l.new(multiply.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    normal=n.new('ShaderNodeNormalMap');normal.location=(250,-50);normal.inputs['Strength'].default_value=.45
    l.new(tex['normal'].outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],bs.inputs['Normal'])
    l.new(tex['roughness'].outputs[0],bs.inputs['Roughness']);l.new(tex['metalness'].outputs[0],bs.inputs['Metallic'])
    mat['owner_contract']='Source R mask and Blender preview only. Native structure shader binding/cook deferred.'
    return mat

def mesh(name,verts,faces,surface,col,stage='walls',role='architecture',meta=None):
    full=PREFIX+name
    if full in bpy.data.objects:raise ValueError('Recipe output already exists: '+full)
    data=bpy.data.meshes.new(full+'_mesh');data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free();data.update()
    o=bpy.data.objects.new(full,data);col.objects.link(o);data.materials.append(material())
    o['source_asset']='SamarkandBazaar';o['surface']=surface;o['construction_stage']=stage;o['role']=role
    if meta:
        for k,v in meta.items():o[k]=v
    o.color=COLOURS[TILES.index(surface)]
    uv=data.uv_layers.new(name='UVMap');k=TILES.index(surface);tx=k%4;ty=3-k//4
    # A per-face projection maps each surface to its own padded atlas tile.
    for p in data.polygons:
        axis=max(range(3),key=lambda j:abs(p.normal[j]));axes=[i for i in range(3) if i!=axis]
        values=[data.vertices[data.loops[i].vertex_index].co for i in p.loop_indices]
        low=[min(v[a] for v in values) for a in axes];high=[max(v[a] for v in values) for a in axes]
        scale=max(high[0]-low[0],high[1]-low[1],.001)
        for i,v in zip(p.loop_indices,values):
            u=.04+.92*(v[axes[0]]-low[0])/scale;v2=.04+.92*(v[axes[1]]-low[1])/scale
            uv.data[i].uv=((tx+u)/4,(ty+v2)/4)
    uv1=data.uv_layers.new(name='UVMap1')
    for a,b in zip(uv.data,uv1.data):b.uv=a.uv
    return o

def block(name,center,size,surface,col,stage='walls',role='architecture',rotation=0):
    x,y,z=center;a,b,c=(q/2 for q in size)
    verts=[(sx*a,sy*b,sz*c) for sx,sy,sz in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
    ca,sa=math.cos(rotation),math.sin(rotation)
    verts=[(x+vx*ca-vy*sa,y+vx*sa+vy*ca,z+vz) for vx,vy,vz in verts]
    return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],surface,col,stage,role)

def extrude_xz(name,outline,y0,y1,surface,col,stage='walls',transform=None,role='architecture'):
    n=len(outline);verts=[(x,y,z) for y in (y0,y1) for x,z in outline]
    if transform:verts=[transform(*v) for v in verts]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,surface,col,stage,role)

def archwall(name,cx,y0,y1,z0,outer_w,height,inner_w,spring,rise,surface,col,segments=24,transform=None):
    out=[(cx-outer_w/2,z0),(cx-outer_w/2,z0+height),(cx+outer_w/2,z0+height),(cx+outer_w/2,z0),(cx+inner_w/2,z0)]
    for i in range(segments+1):
        a=i*math.pi/segments;dx=inner_w/2*math.cos(a)
        if rise>=inner_w/2:
            off=(rise*rise-(inner_w/2)**2)/inner_w;radius=inner_w/2+off
            lift=math.sqrt(max(0,radius*radius-(abs(dx)+off)**2))
        else:lift=rise*math.sin(a)
        out.append((cx+dx,z0+spring+lift))
    out.append((cx-inner_w/2,z0))
    return extrude_xz(name,out,y0,y1,surface,col,transform=transform)

def vault(name,cx,y0,y1,z0,rx,rz,thickness,surface,col,segments=32,along=4,transform=None,angle0=0,angle1=math.pi,stage='vaults'):
    verts=[];faces=[]
    for shell in (0,1):
        for j in range(along+1):
            y=y0+(y1-y0)*j/along
            for i in range(segments+1):
                a=angle0+(angle1-angle0)*i/segments
                verts.append((cx+(rx+shell*thickness)*math.cos(a),y,z0+(rz+shell*thickness)*math.sin(a)))
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
    if transform:verts=[transform(*v) for v in verts]
    return mesh(name,verts,faces,surface,col,stage)

def lathe(name,center,rings,surface,col,sides=24,stage='finish',role='props',cap=True):
    x,y,z=center;verts=[];faces=[]
    for radius,h in rings:
        for i in range(sides):
            a=2*math.pi*i/sides;verts.append((x+radius*math.cos(a),y+radius*math.sin(a),z+h))
    for j in range(len(rings)-1):
        for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
    if cap:faces += [tuple(reversed(range(sides))),tuple((len(rings)-1)*sides+i for i in range(sides))]
    return mesh(name,verts,faces,surface,col,stage,role)

def beam(name,a,b,width,surface,col,stage='finish',role='props'):
    a,b=Vector(a),Vector(b);direction=(b-a).normalized();up=Vector((0,0,1))
    if abs(direction.dot(up))>.95:up=Vector((1,0,0))
    u=direction.cross(up).normalized()*width/2;v=direction.cross(u).normalized()*width/2
    verts=[tuple(p+su*u+sv*v) for p in (a,b) for su,sv in ((-1,-1),(1,-1),(1,1),(-1,1))]
    return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],surface,col,stage,role)

def bounds(o):
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]

def show_state(state='healthy',lod=0):
    s=bpy.data.scenes['PS_SamarkandBazaar']
    for c in s.collection.children:
        if c.name.startswith(PREFIX):c.hide_render=c.hide_viewport=(c.name!=f'{PREFIX}{state}_LOD{lod}')
    bpy.context.window.scene=s

def view(pos=(18,-23,18),center=(0,0,2.2),distance=23,solid=True):
    q=(Vector(center)-Vector(pos)).to_track_quat('-Z','Y')
    for a in bpy.context.screen.areas:
        if a.type=='VIEW_3D':
            space=a.spaces.active;space.region_3d.view_rotation=q
            space.region_3d.view_location=center;space.region_3d.view_distance=distance;space.region_3d.view_perspective='ORTHO'
            space.shading.type='SOLID' if solid else 'MATERIAL'
            space.shading.color_type='OBJECT';space.shading.light='STUDIO';space.shading.show_shadows=True
            space.overlay.show_overlays=False
    for o in bpy.context.selected_objects:o.select_set(False)

def save():
    scene=bpy.data.scenes['PS_SamarkandBazaar']
    original=bpy.data.scenes.get('Scene')
    blocks={scene}
    if original:blocks.add(original)
    # Library write exports only this asset scene and its dependencies. It never
    # saves the other asset's scene or changes the live file session.
    bpy.data.libraries.write(str(ROOT/"samarkand_bazaar.blend"),blocks,path_remap='RELATIVE_ALL',fake_user=True,compress=True)
    print('SOURCE_SAVED',str(ROOT/"samarkand_bazaar.blend"))


def retile_surface(ob):
    # Planar per-face projection avoids wrapped UV interpolation across a large n-gon.
    me=ob.data;k=TILES.index(ob.get('surface','brick'));tx=k%4;ty=3-k//4
    for poly in me.polygons:
        axis=max(range(3),key=lambda j:abs(poly.normal[j]));axes=[i for i in range(3) if i!=axis]
        coords=[me.vertices[me.loops[i].vertex_index].co for i in poly.loop_indices]
        low=[min(v[a] for v in coords) for a in axes];high=[max(v[a] for v in coords) for a in axes];scale=max(high[0]-low[0],high[1]-low[1],.001)
        for li,v in zip(poly.loop_indices,coords):
            uv=((tx+.04+.92*(v[axes[0]]-low[0])/scale)/4,(ty+.04+.92*(v[axes[1]]-low[1])/scale)/4)
            for layer in me.uv_layers:layer.data[li].uv=uv
