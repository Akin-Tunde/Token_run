"""Add a local FK humanoid rig and reproducible bend checks to the runner."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Quaternion

OUT = Path(__file__).resolve().parents[1] / 'art' / 'runner'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'TokenRun_Runner.blend'))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
body = bpy.data.objects['Runner_Suit_Continuous']
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,0))
rig = bpy.context.object
rig.name = 'TokenRun_Humanoid'
rig.show_in_front = True
rig.data.name = 'TokenRun_Humanoid_Skeleton'
rig.data.edit_bones.remove(rig.data.edit_bones[0])

def bone(name, head, tail, parent=None, deform=True):
    b=rig.data.edit_bones.new(name)
    b.head=head; b.tail=tail; b.use_deform=deform
    if parent: b.parent=rig.data.edit_bones[parent]
    b.align_roll(Vector((0,-1,0)))
    return b

bone('Root',(0,0,0),(0,0,.18),deform=False)
bone('Hips',(0,0,.86),(0,0,1.0),'Root')
bone('Spine',(0,0,1.0),(0,0,1.17),'Hips')
bone('Chest',(0,0,1.17),(0,0,1.40),'Spine')
bone('Neck',(0,0,1.40),(0,0,1.51),'Chest')
bone('Head',(0,0,1.51),(0,0,1.94),'Neck')
for s,side in [(-1,'R'),(1,'L')]:
    bone('Shoulder.'+side,(s*.06,0,1.38),(s*.225,0,1.37),'Chest')
    bone('UpperArm.'+side,(s*.225,0,1.37),(s*.40,-.01,1.14),'Shoulder.'+side)
    bone('LowerArm.'+side,(s*.40,-.01,1.14),(s*.54,-.01,.94),'UpperArm.'+side)
    bone('Hand.'+side,(s*.54,-.01,.94),(s*.59,-.01,.81),'LowerArm.'+side)
    bone('UpperLeg.'+side,(s*.135,0,.87),(s*.18,-.025,.51),'Hips')
    bone('LowerLeg.'+side,(s*.18,-.025,.51),(s*.20,0,.17),'UpperLeg.'+side)
    bone('Foot.'+side,(s*.20,0,.17),(s*.20,-.16,.08),'LowerLeg.'+side)
    bone('Toes.'+side,(s*.20,-.16,.08),(s*.20,-.255,.08),'Foot.'+side)
bpy.ops.object.mode_set(mode='OBJECT')

# Bone heat on only the continuous flexible suit. Armor remains rigid by design.
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

def rigid_attach(obj, bone_name):
    obj.parent=rig
    group=obj.vertex_groups.new(name=bone_name)
    group.add(list(range(len(obj.data.vertices))),1.0,'REPLACE')
    modifier=obj.modifiers.new('Skeleton deformation','ARMATURE'); modifier.object=rig

for obj in meshes:
    if obj==body: continue
    name=obj.name.lower()
    center=obj.matrix_world @ (sum((Vector(v) for v in obj.bound_box),Vector())/8)
    side='L' if center.x>0 else 'R'
    if any(word in name for word in ('helmet','visor','face below')): target='Head'
    elif 'collar' in name: target='Neck'
    elif 'chest' in name: target='Chest'
    elif 'belt' in name: target='Hips'
    elif 'shoulder' in name: target='UpperArm.'+side
    elif 'wrist' in name: target='LowerArm.'+side
    elif 'thigh' in name or 'knee' in name: target='UpperLeg.'+side
    elif 'boot' in name: target='Foot.'+side
    else: raise RuntimeError('Unmapped shell: '+obj.name)
    rigid_attach(obj,target)

deform_names={b.name for b in rig.data.bones if b.use_deform}
max_influences=0; zero=[]; errors=[]
for obj in meshes:
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    deform_ids={g.index for g in obj.vertex_groups if g.name in deform_names}
    for v in obj.data.vertices:
        values=[g.weight for g in v.groups if g.group in deform_ids and g.weight>1e-6]
        max_influences=max(max_influences,len(values))
        if not values: zero.append((obj.name,v.index))
        elif abs(sum(values)-1)>1e-4: errors.append((obj.name,v.index,sum(values)))
assert not zero, 'Unweighted vertices: '+str(zero[:10])
assert not errors, 'Invalid weight sums: '+str(errors[:10])
assert max_influences<=4

def clear_pose():
    for p in rig.pose.bones:
        p.rotation_mode='QUATERNION'; p.rotation_quaternion=Quaternion(); p.location=(0,0,0); p.scale=(1,1,1)
    bpy.context.view_layer.update()

def rotate(name,world_axis,degrees):
    p=rig.pose.bones[name]
    axis=p.bone.matrix_local.to_3x3().inverted() @ Vector(world_axis)
    p.rotation_quaternion=Quaternion(axis,math.radians(degrees))

def evaluated_points():
    deps=bpy.context.evaluated_depsgraph_get()
    obj=body.evaluated_get(deps)
    mesh=obj.to_mesh()
    points=[obj.matrix_world @ v.co for v in mesh.vertices]
    obj.to_mesh_clear()
    return points

clear_pose(); rest=evaluated_points()
report={'bones':len(rig.data.bones),'deforming_bones':len(deform_names),'weighted_meshes':len(meshes),'unweighted_vertices':len(zero),'weight_sum_errors':len(errors),'max_influences':max_influences,'pose_checks':{},'unity_humanoid_mapping_tested':False,'animations_created':False,'rig_type':'FK humanoid, mitten hands; no IK controls'}
scene=bpy.context.scene
scene.render.resolution_x=480; scene.render.resolution_y=600; scene.cycles.samples=8
scene.render.threads_mode='FIXED'; scene.render.threads=4
camera=scene.camera
camera.location=(2.4,-6.5,2.4)
camera.rotation_euler=(Vector((0,0,1.01))-camera.location).to_track_quat('-Z','Y').to_euler()

# Save and export the clean rest pose, never a diagnostic bent pose.
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
for obj in meshes: obj.select_set(True)
bpy.context.view_layer.objects.active=rig
rig['usage']='Pose FK bones; Root is non-deforming. No animation clips or IK controls.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TokenRun_Runner_Rigged.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'TokenRun_Runner_Rigged.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False)

poses={
    'arms': [('UpperArm.L',(0,1,0),-20),('UpperArm.R',(0,1,0),20),('LowerArm.L',(1,0,0),-75),('LowerArm.R',(1,0,0),-75)],
    'stride': [('UpperLeg.L',(1,0,0),-35),('LowerLeg.L',(1,0,0),65),('UpperLeg.R',(1,0,0),25),('LowerLeg.R',(1,0,0),30),('UpperArm.L',(1,0,0),25),('UpperArm.R',(1,0,0),-25),('LowerArm.L',(1,0,0),-45),('LowerArm.R',(1,0,0),-45)],
}
for name, rotations in poses.items():
    clear_pose()
    for bone_name,axis,degrees in rotations: rotate(bone_name,axis,degrees)
    bpy.context.view_layer.update()
    posed=evaluated_points()
    displacement=max((a-b).length for a,b in zip(rest,posed))
    assert math.isfinite(displacement) and .05<displacement<1.5, (name,displacement)
    report['pose_checks'][name]={'max_vertex_displacement_m':round(displacement,4),'finite_and_bounded':True}
    scene.render.filepath=str(OUT/('rig-test-'+name+'.png'))
    bpy.ops.render.render(write_still=True)
clear_pose()
(OUT/'rig-check.json').write_text(json.dumps(report,indent=2))
print('RIG CHECK PASSED:',json.dumps(report))
