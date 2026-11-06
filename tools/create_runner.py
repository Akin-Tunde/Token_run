import bpy, math, json
from mathutils import Vector
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'art'/'runner'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,c,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=.38
 return m
teal=mat('Teal armor',(.008,.57,.59)); navy=mat('Navy undersuit',(.035,.055,.12)); orange=mat('Orange accents',(1,.27,.015)); visor=mat('Dark visor',(.018,.025,.055),.45); white=mat('Shoe soles',(.78,.84,.86)); skin=mat('Face',(.78,.43,.23))
parts=[]
def ell(name,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=loc)
 o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o); return o
def limb(name,a,b,r,m):
 mid=(Vector(a)+Vector(b))/2; d=Vector(b)-Vector(a)
 o=ell(name,mid,(r,r,d.length/2+r*.35),m); o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); return o
# Z up, character faces -Y; feet sit at ground level.
ell('Pelvis',(0,0,.89),(.225,.14,.19),navy)
ell('Suit torso',(0,0,1.19),(.26,.145,.32),navy)
ell('Chest armor',(0,-.08,1.29),(.255,.115,.19),teal)
ell('Abdominal armor',(0,-.105,1.08),(.145,.06,.18),teal)
ell('Belt',(0,0,.94),(.235,.158,.065),navy)
ell('Buckle',(0,-.157,.945),(.055,.02,.035),orange)
limb('Neck',(0,0,1.44),(0,0,1.53),.085,navy)
ell('Helmet',(0,0,1.77),(.275,.235,.29),teal)
ell('Face visible below visor',(0,-.194,1.63),(.15,.065,.10),skin)
ell('Visor rim',(0,-.202,1.80),(.242,.065,.16),navy)
ell('Visor',(0,-.24,1.805),(.218,.045,.13),visor)
ell('Helmet crown',(0,.005,2.015),(.085,.15,.035),navy)
for s in [-1,1]:
 ell('Helmet orange side',(s*.255,0,1.76),(.035,.11,.105),orange)
 hip=(s*.13,0,.87); knee=(s*.18,-.005,.51); ankle=(s*.20,0,.17)
 limb('Thigh suit',hip,knee,.12,navy); limb('Shin suit',knee,ankle,.10,navy)
 limb('Thigh armor',(s*.18,-.075,.83),(s*.205,-.075,.62),.072,teal)
 ell('Knee accent',(s*.18,-.09,.51),(.105,.035,.075),orange)
 ell('Boot',(s*.20,-.065,.13),(.14,.225,.125),navy)
 ell('Sole',(s*.20,-.075,.045),(.147,.235,.045),white)
 ell('Boot toe',(s*.20,-.195,.105),(.135,.105,.075),teal)
 ell('Boot strap',(s*.20,-.105,.205),(.13,.055,.03),orange)
 shoulder=(s*.265,0,1.40); elbow=(s*.43,0,1.18); wrist=(s*.57,-.005,1.00)
 limb('Upper arm',shoulder,elbow,.085,navy); limb('Forearm',elbow,wrist,.078,navy)
 ell('Shoulder armor',(s*.285,-.005,1.39),(.115,.12,.11),teal)
 limb('Wrist cuff',(s*.525,0,1.06),(s*.55,0,1.025),.082,orange)
 ell('Glove',(s*.60,-.005,.94),(.078,.065,.11),navy)
 ell('Thumb',(s*.54,-.045,.945),(.035,.04,.065),navy)
# Join visual geometry; preserve material slots. No implied rigging.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join(); model=bpy.context.object; model.name='TokenRun_Runner_Unrigged'
bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
model['status']='Unrigged procedural reference interpretation'; model['reference']='reference.png supplied by user'
# Reference kept inside blend for later modeling work.
img=bpy.data.images.load(str(out/'reference.png')); img.pack()
bpy.ops.object.empty_add(type='IMAGE',location=(0,.6,1.03)); ref=bpy.context.object; ref.name='Reference image (hidden in render)'; ref.data=img; ref.empty_display_size=2.06; ref.rotation_euler=(math.pi/2,0,0); ref.hide_render=True; ref.hide_viewport=True
# Studio preview, separate from exported character.
def area(name,pos,power,size):
 bpy.ops.object.light_add(type='AREA',location=pos); l=bpy.context.object; l.name=name; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-3,-4,5),450,4); area('Fill',(3,-2,3),220,3); area('Rim',(1,3,4),500,3)
bpy.ops.object.camera_add(location=(2.7,-6.5,2.6)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.02))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.5
scene=bpy.context.scene; scene.camera=cam; scene.render.engine='CYCLES'; scene.cycles.samples=8; scene.render.threads_mode='FIXED'; scene.render.threads=4; scene.render.resolution_x=480; scene.render.resolution_y=600; scene.render.resolution_percentage=100
scene.world.color=(.15,.15,.15); scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(out/'runner-preview.png')
scene.view_settings.view_transform='AgX'
bpy.ops.object.select_all(action='DESELECT'); model.select_set(True); bpy.context.view_layer.objects.active=model
bpy.ops.wm.save_as_mainfile(filepath=str(out/'TokenRun_Runner.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'TokenRun_Runner.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
tris=sum(len(p.vertices)-2 for p in model.data.polygons)
(out/'model-info.json').write_text(json.dumps({'triangles':tris,'height_m':round(model.dimensions.z,3),'rigged':False,'animated':False,'materials':len(model.data.materials)},indent=2))
bpy.ops.render.render(write_still=True)
