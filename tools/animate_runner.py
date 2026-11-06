"""Create original in-place FK clips and Blender playback evidence."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Quaternion

OUT=Path(__file__).resolve().parents[1]/'art'/'runner'
CLIPS=OUT/'animations'; CLIPS.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'TokenRun_Runner_Rigged.blend'))
rig=bpy.data.objects['TokenRun_Humanoid']
scene=bpy.context.scene; scene.render.fps=30
meshes=[o for o in scene.objects if o.type=='MESH']
soles=[o for o in meshes if o.name.startswith('Boot sole')]
assert len(soles)==2
rig.animation_data_create()

def rotate(name,axis,degrees):
    p=rig.pose.bones[name]
    local=p.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
    p.rotation_quaternion = p.rotation_quaternion @ Quaternion(local,math.radians(degrees))

def hips_height(z):
    p=rig.pose.bones['Hips']
    p.location=p.bone.matrix_local.to_3x3().inverted() @ Vector((0,0,z))

def sole_bottom():
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    points=[]
    for obj in soles:
        evaluated=obj.evaluated_get(graph); mesh=evaluated.to_mesh()
        points.extend((evaluated.matrix_world @ v.co).z for v in mesh.vertices)
        evaluated.to_mesh_clear()
    return min(points)

def reset():
    for p in rig.pose.bones:
        p.rotation_mode='QUATERNION'; p.rotation_quaternion=Quaternion(); p.location=(0,0,0); p.scale=(1,1,1)

actions=[]; report={'fps':30,'root_motion':False,'unity_playback_tested':False,'clips':{}}
for name,end,loop in [('Idle',61,True),('Run',25,True),('Jump',31,False)]:
    action=bpy.data.actions.new(name); action.use_fake_user=True
    rig.animation_data.action=action
    floor_samples=[]; root_samples=[]; rotations=[]
    for frame in range(1,end+1):
        scene.frame_set(frame); reset()
        t=(frame-1)/(end-1); phase=2*math.pi*t
        for side,sign in [('L',1),('R',-1)]:
            rotate('UpperArm.'+side,(0,1,0),sign*20)
            rotate('LowerArm.'+side,(1,0,0),-12)
        if name=='Idle':
            rotate('Chest',(1,0,0),1.2*math.sin(phase))
            rotate('Head',(0,0,1),2*math.sin(phase))
            for side in ['L','R']: rotate('LowerArm.'+side,(1,0,0),-2*(1-math.cos(phase)))
        elif name=='Run':
            rotate('Spine',(1,0,0),8)
            for side,offset in [('L',0),('R',math.pi)]:
                p=phase+offset; swing=math.sin(p)
                hip=-30*swing
                knee=12+54*max(0,-swing)
                rotate('UpperLeg.'+side,(1,0,0),hip)
                rotate('LowerLeg.'+side,(1,0,0),knee)
                rotate('Foot.'+side,(1,0,0),-hip-knee)
                rotate('UpperArm.'+side,(1,0,0),24*swing)
                rotate('LowerArm.'+side,(1,0,0),-42-8*swing)
            rotate('Chest',(0,0,1),4*math.sin(phase))
            # Keep the lowest sole on the ground. Root stays fixed for controller movement.
            hips_height(.008-sole_bottom())
        else:
            # Anticipation -> takeoff -> airborne tuck -> landing -> recovery.
            keys=[(0,0,0),(0.16,-20,40),(0.3,8,8),(0.5,-20,55),(0.7,-14,35),(0.84,-24,48),(1,0,0)]
            for a,b in zip(keys,keys[1:]):
                if a[0]<=t<=b[0]:
                    u=(t-a[0])/(b[0]-a[0]); u=u*u*(3-2*u)
                    hip=a[1]+(b[1]-a[1])*u; knee=a[2]+(b[2]-a[2])*u; break
            for side in ['L','R']:
                rotate('UpperLeg.'+side,(1,0,0),hip)
                rotate('LowerLeg.'+side,(1,0,0),knee)
                rotate('Foot.'+side,(1,0,0),-hip-knee)
                rotate('UpperArm.'+side,(1,0,0),-35*math.sin(math.pi*t))
                rotate('LowerArm.'+side,(1,0,0),-25*math.sin(math.pi*t))
            # Only grounded anticipation / recovery adjust pelvis. Actual jump arc is gameplay-owned.
            if t<=.3 or t>=.7: hips_height(.008-sole_bottom())
        bpy.context.view_layer.update()
        for p in rig.pose.bones:
            p.keyframe_insert('rotation_quaternion',frame=frame,group=p.name)
            p.keyframe_insert('location',frame=frame,group=p.name)
        floor_samples.append(sole_bottom())
        root_samples.append(tuple(rig.pose.bones['Root'].location))
        rotations.append([tuple(p.rotation_quaternion) for p in rig.pose.bones])
    action.use_frame_range=True; action.frame_start=1; action.frame_end=end
    assert all(sum(abs(v) for v in xyz)<1e-8 for xyz in root_samples)
    if loop:
        seam=max(abs(a-b) for qa,qb in zip(rotations[0],rotations[-1]) for a,b in zip(qa,qb))
        assert seam<1e-5,(name,seam)
        assert max(abs(z-.008) for z in floor_samples)<.001,(name,min(floor_samples),max(floor_samples))
    else: seam=None
    assert all(math.isfinite(z) for z in floor_samples)
    scene.frame_start=1; scene.frame_end=end; scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True)
    for obj in meshes: obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.fbx(filepath=str(CLIPS/(name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0)
    report['clips'][name]={'frames':[1,end],'seconds':(end-1)/30,'loop':loop,'rotation_seam_error':seam,'min_sole_z':round(min(floor_samples),5),'max_sole_z':round(max(floor_samples),5),'root_translation_zero':True}
    actions.append(action)

# Open into Idle, with all actions retained in the Action Editor.
rig.animation_data.action=actions[0]; scene.frame_start=1; scene.frame_end=61; scene.frame_set(1)
rig['usage']='Choose Idle, Run or Jump in the Action Editor. In-place FK clips, 30 FPS. Root motion disabled.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TokenRun_Runner_Animated.blend'))
(OUT/'animation-check.json').write_text(json.dumps(report,indent=2))

# Compact workbench playback frames for visual inspection, not runtime performance evidence.
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD'; scene.world.color=(.06,.07,.09)
scene.render.resolution_x=320; scene.render.resolution_y=400; scene.render.resolution_percentage=100
scene.camera.location=(2.5,-6.5,2.3)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
for action in actions:
    rig.animation_data.action=action
    folder=CLIPS/action.name; folder.mkdir(exist_ok=True)
    end=int(action.frame_end)
    for frame in range(1,end,2):
        scene.frame_set(frame); scene.render.filepath=str(folder/f'{frame:03}.png')
        bpy.ops.render.render(write_still=True)
print('ANIMATION CHECK PASSED:',json.dumps(report))
