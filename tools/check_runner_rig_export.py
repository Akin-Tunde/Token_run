"""Independently reimport rigged FBX and check skeleton, skinning, and deformation."""
import bpy
import json
from pathlib import Path
from mathutils import Quaternion, Vector
import math

out=Path(__file__).resolve().parents[1]/'art'/'runner'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(out/'TokenRun_Runner_Rigged.fbx'))
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert len(rigs)==1
rig=rigs[0]
required=['Hips','Spine','Chest','Neck','Head']
required += [part+'.'+side for side in ['L','R'] for part in ['Shoulder','UpperArm','LowerArm','Hand','UpperLeg','LowerLeg','Foot','Toes']]
assert all(name in rig.data.bones for name in required)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==26
max_influences=0
for obj in meshes:
    assert any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers),obj.name
    groups={g.index for g in obj.vertex_groups if g.name in rig.data.bones and rig.data.bones[g.name].use_deform}
    for v in obj.data.vertices:
        weights=[g.weight for g in v.groups if g.group in groups and g.weight>1e-6]
        assert weights and abs(sum(weights)-1)<1e-4,(obj.name,v.index,weights)
        max_influences=max(max_influences,len(weights))
assert max_influences<=4
body=next(o for o in meshes if o.name.startswith('Runner_Suit_Continuous'))
def points():
    bpy.context.view_layer.update()
    evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh(); result=[v.co.copy() for v in mesh.vertices]; evaluated.to_mesh_clear(); return result
rest=points()
p=rig.pose.bones['LowerLeg.L']; p.rotation_mode='QUATERNION'
axis=p.bone.matrix_local.to_3x3().inverted() @ Vector((1,0,0))
p.rotation_quaternion=Quaternion(axis,math.radians(60))
posed=points()
delta=max((a-b).length for a,b in zip(rest,posed))
assert .05<delta<1.0,delta
result={'fbx_reimported_in_blender':True,'required_humanoid_bones_present':True,'bones':len(rig.data.bones),'skinned_meshes':len(meshes),'max_influences':max_influences,'weight_sums_valid':True,'reimported_knee_deformation_m':round(delta,4),'unity_humanoid_import_tested':False}
(out/'rig-export-check.json').write_text(json.dumps(result,indent=2))
print('RIG EXPORT CHECK PASSED:',json.dumps(result))
