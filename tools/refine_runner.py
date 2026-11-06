"""Refine the local runner blockout in Blender; no game or paid service changes."""
import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1] / 'art' / 'runner'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=.55, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m

navy = material('Navy flexible suit', (.025, .04, .095))
teal = material('Teal armor', (.008, .43, .44))
orange = material('Orange safety accents', (1, .24, .008))
glass = material('Visor', (.012, .018, .035), .2, .25)
sole = material('Light soles', (.72, .77, .79))
skin = material('Face', (.72, .37, .18))
models = []
body_parts = []

def mesh_object(name, verts, faces, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True
    return obj

def loft(name, rings, mat, segments=16):
    # Horizontal elliptical cross sections, closed with end caps.
    verts = []
    for x, y, z, rx, ry in rings:
        for j in range(segments):
            a = 2 * math.pi * j / segments
            verts.append((x + rx * math.cos(a), y + ry * math.sin(a), z))
    faces = []
    for i in range(len(rings)-1):
        for j in range(segments):
            a = i*segments+j
            b = i*segments+(j+1)%segments
            faces.append((a, b, b+segments, a+segments))
    faces += [tuple(reversed(range(segments))), tuple((len(rings)-1)*segments+j for j in range(segments))]
    return mesh_object(name, verts, faces, mat)

def ellipsoid(name, pos, scale, mat, seg=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=pos)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def activate(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def join(objects, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    return o

# A continuous flexible undersuit, including connected hands and boots.
body_parts.append(loft('Torso source', [
    (0,0,.83,.18,.12), (0,0,.9,.205,.135), (0,0,.98,.17,.12),
    (0,0,1.07,.17,.12), (0,0,1.18,.22,.14),
    (0,0,1.30,.255,.14), (0,0,1.39,.225,.12),
    (0,0,1.43,.105,.095), (0,0,1.52,.085,.08)], navy))
for s in (-1, 1):
    body_parts.append(loft('Leg source', [
        (s*.135,0,.9,.115,.12), (s*.15,0,.8,.12,.13),
        (s*.17,0,.66,.105,.115), (s*.18,-.025,.53,.088,.095),
        (s*.18,-.025,.48,.088,.095), (s*.19,0,.37,.1,.105),
        (s*.2,0,.23,.075,.08), (s*.2,0,.14,.07,.08)], navy))
    body_parts.append(loft('Arm source', [
        (s*.225,0,1.37,.09,.095), (s*.28,0,1.32,.09,.095),
        (s*.34,0,1.23,.077,.082), (s*.395,-.01,1.15,.067,.075),
        (s*.42,-.01,1.11,.067,.075), (s*.47,-.01,1.04,.075,.08),
        (s*.53,-.01,.95,.056,.065), (s*.55,-.01,.91,.055,.06)], navy))
    body_parts.append(ellipsoid('Mitten source', (s*.57,-.01,.87), (.068,.06,.095), navy, 16, 8))
    body_parts.append(ellipsoid('Thumb source', (s*.52,-.052,.87), (.04,.04,.055), navy, 12, 8))
    body_parts.append(ellipsoid('Foot source', (s*.2,-.07,.125), (.12,.19,.105), navy, 16, 8))

body = join(body_parts, 'Runner_Suit_Continuous')
activate(body)
remesh = body.modifiers.new('Fuse overlapping source volumes', 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = .014
remesh.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth = body.modifiers.new('Smooth anatomical joins', 'SMOOTH')
smooth.factor = .8
smooth.iterations = 4
bpy.ops.object.modifier_apply(modifier=smooth.name)
# QuadriFlow provides a connected quad starting mesh; deformation still needs testing.
bpy.ops.object.quadriflow_remesh(target_faces=1600, use_mesh_symmetry=True, use_preserve_sharp=False, use_preserve_boundary=False, seed=0)
models.append(body)

# A shaped front plate follows the chest instead of a sphere glued to the torso.
plate = loft('Chest abdominal armor', [
    (0,-.108,1.015,.11,.036), (0,-.117,1.10,.125,.045),
    (0,-.123,1.19,.18,.055), (0,-.12,1.28,.215,.064),
    (0,-.105,1.35,.19,.05), (0,-.09,1.375,.12,.035)], teal)
models.append(plate)
models.append(loft('Collar', [(0,0,1.43,.105,.095),(0,0,1.49,.10,.09)], navy))
models.append(loft('Belt', [(0,0,.955,.18,.132),(0,0,.99,.177,.13)], navy))
for s in (-1,1):
    models.append(ellipsoid('Belt orange tab', (s*.145,-.104,.974), (.035,.025,.035), orange, 12, 6))
    models.append(ellipsoid('Shoulder cap', (s*.245,-.005,1.355), (.105,.115,.075), teal,16,8))
    models.append(loft('Wrist cuff', [(s*.51,-.01,.982,.065,.073),(s*.53,-.01,.95,.063,.07)], orange,12))
    models.append(loft('Thigh teal panel', [(s*.16,-.09,.83,.075,.055),(s*.18,-.095,.7,.07,.05),(s*.18,-.09,.60,.04,.025)], teal,12))
    # Slim accent bands keep knees free to bend.
    models.append(loft('Knee orange band',[(s*.18,-.025,.54,.093,.101),(s*.18,-.025,.565,.095,.105)],orange,12))
    models.append(loft('Boot sole',[(s*.2,-.07,.008,.12,.21),(s*.2,-.07,.045,.13,.215),(s*.2,-.07,.065,.125,.205)],sole,16))
    models.append(ellipsoid('Boot toe panel',(s*.2,-.19,.10),(.115,.09,.055),teal,16,8))
    models.append(ellipsoid('Boot orange strap',(s*.2,-.11,.195),(.10,.055,.025),orange,12,6))

# Helmet material regions follow its surface: no floating crown or stripe shapes.
helmet = ellipsoid('Helmet shell',(0,0,1.735),(.265,.225,.285),teal,24,12)
helmet.data.materials.append(navy)
helmet.data.materials.append(orange)
for p in helmet.data.polygons:
    c = p.center
    if c.z > .16 and abs(c.x) < .065:
        p.material_index = 1
    elif c.z > .10 and .12 < abs(c.x) < .16 and c.y < -.07:
        p.material_index = 2
models.append(helmet)
models.append(ellipsoid('Face below visor',(0,-.196,1.605),(.15,.057,.085),skin,16,8))
models.append(ellipsoid('Visor surround',(0,-.197,1.745),(.233,.062,.145),navy,16,8))
models.append(ellipsoid('Visor glass',(0,-.229,1.75),(.215,.043,.127),glass,16,8))
for s in (-1,1):
    models.append(ellipsoid('Helmet ear accent',(s*.258,.005,1.72),(.019,.078,.085),orange,12,8))

# Pack the supplied image; retain it as an optional modeling reference.
img = bpy.data.images.load(str(OUT/'reference.png'))
img.pack()
bpy.ops.object.empty_add(type='IMAGE',location=(0,.65,1.01))
reference = bpy.context.object
reference.name = 'User reference (toggle visibility to compare)'
reference.data = img
reference.empty_display_size = 2.02
reference.rotation_euler = (math.pi/2,0,0)
reference.hide_render = True
reference.hide_viewport = True

for o in models:
    activate(o)
    if o != body:
        reduction = o.modifiers.new('Mobile shell simplification', 'DECIMATE')
        reduction.ratio = .65
        bpy.ops.object.modifier_apply(modifier=reduction.name)
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(o.data); bm.free()
    for polygon in o.data.polygons: polygon.use_smooth = True

def topology(o):
    bm=bmesh.new(); bm.from_mesh(o.data)
    seen=set(); components=0
    for v in bm.verts:
        if v in seen: continue
        components+=1; stack=[v]; seen.add(v)
        while stack:
            for edge in stack.pop().link_edges:
                for other in edge.verts:
                    if other not in seen: seen.add(other); stack.append(other)
    result={'components':components,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'quads':sum(len(f.verts)==4 for f in bm.faces),'faces':len(bm.faces)}
    bm.free(); return result

report={'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in models),'body_topology':topology(body),'rigged':False,'animated':False,'materials':6,'unity_import_verified':False,'note':'Continuous quad suit plus separate armor shells; skinning and deformation not yet validated.'}
if report['body_topology']['components'] != 1 or report['body_topology']['non_manifold_edges']:
    raise RuntimeError('Body failed connected manifold validation: '+str(report))
OUT.joinpath('model-info.json').write_text(json.dumps(report,indent=2))

scene=bpy.context.scene
def aim(obj,at): obj.rotation_euler=(Vector(at)-obj.location).to_track_quat('-Z','Y').to_euler()
for pos,power,size in [((-3,-4,5),350,4),((3,-2,3),180,3),((1,3,4),400,3)]:
    bpy.ops.object.light_add(type='AREA',location=pos)
    light=bpy.context.object; light.data.energy=power; light.data.shape='DISK'; light.data.size=size; aim(light,(0,0,1))
bpy.ops.object.camera_add(location=(2.4,-6.5,2.4))
camera=bpy.context.object; camera.name='Preview Camera'; aim(camera,(0,0,1.01)); camera.data.type='ORTHO'; camera.data.ortho_scale=2.35; scene.camera=camera
scene.render.engine='CYCLES'; scene.cycles.samples=8
scene.render.threads_mode='FIXED'; scene.render.threads=4
scene.render.resolution_x=480; scene.render.resolution_y=600; scene.render.resolution_percentage=100
scene.world.color=(.12,.12,.12); scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'
bpy.ops.object.select_all(action='DESELECT')
for o in models: o.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TokenRun_Runner.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'TokenRun_Runner.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
scene.render.filepath=str(OUT/'runner-preview.png'); bpy.ops.render.render(write_still=True)
camera.location=(0,-7,1.05); aim(camera,(0,0,1.01)); scene.render.filepath=str(OUT/'runner-front.png'); bpy.ops.render.render(write_still=True)
camera.location=(2.5,6,2.2); aim(camera,(0,0,1.01)); scene.render.filepath=str(OUT/'runner-back.png'); bpy.ops.render.render(write_still=True)
print('REFINEMENT VALIDATION:',json.dumps(report))
