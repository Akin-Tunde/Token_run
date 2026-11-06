"""Independently reopen the saved Blender asset and reimport its FBX."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

out = Path(__file__).resolve().parents[1] / 'art' / 'runner'
bpy.ops.wm.open_mainfile(filepath=str(out/'TokenRun_Runner.blend'))
body = bpy.data.objects.get('Runner_Suit_Continuous')
assert body is not None and len(body.data.polygons) > 0
assert not any(o.type == 'ARMATURE' for o in bpy.context.scene.objects)
source_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
source_triangles = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in source_meshes)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(out/'TokenRun_Runner.fbx'))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
triangles = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
assert len(meshes) == len(source_meshes), (len(meshes), len(source_meshes))
assert triangles == source_triangles, (triangles, source_triangles)
points = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
height = max(v.z for v in points)-min(v.z for v in points)
assert 1.9 < height < 2.1, height
assert triangles <= 6000, triangles
result = {'blend_reopened': True, 'fbx_reimported_in_blender': True,
          'mesh_count': len(meshes), 'triangles': triangles,
          'height_m': round(height, 4), 'within_6000_triangle_budget': True,
          'unity_import_tested': False}
(out/'export-check.json').write_text(json.dumps(result, indent=2))
print('EXPORT CHECK PASSED:', json.dumps(result))
