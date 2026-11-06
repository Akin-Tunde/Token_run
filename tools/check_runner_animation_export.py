"""Reimport each clip independently and sample actual skinned playback."""
import bpy
import json
import math
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'art'/'runner'
results={}
for name,expected in [('Idle',61),('Run',25),('Jump',31)]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps=30
    bpy.ops.import_scene.fbx(filepath=str(OUT/'animations'/(name+'.fbx')))
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    assert len(rigs)==1,name
    rig=rigs[0]
    assert rig.animation_data and rig.animation_data.action,name
    action=rig.animation_data.action
    start,end=map(round,action.frame_range)
    assert end-start==expected-1,(name,start,end)
    body=next(o for o in bpy.context.scene.objects if o.name.startswith('Runner_Suit_Continuous'))
    def snapshot(frame):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        graph=bpy.context.evaluated_depsgraph_get()
        evaluated=body.evaluated_get(graph); mesh=evaluated.to_mesh()
        points=[v.co.copy() for v in mesh.vertices]; evaluated.to_mesh_clear()
        root=rig.pose.bones['Root'].matrix.translation.copy()
        return points,root
    first,root=snapshot(start)
    motion=0; root_drift=0
    for frame in range(start,end+1):
        points,r=snapshot(frame)
        delta=max((a-b).length for a,b in zip(first,points))
        assert math.isfinite(delta) and delta<1.5,(name,frame,delta)
        motion=max(motion,delta); root_drift=max(root_drift,(r-root).length)
    last,_=snapshot(end)
    seam=max((a-b).length for a,b in zip(first,last))
    assert motion>.001,(name,motion)
    assert root_drift<1e-5,(name,root_drift)
    if name!='Jump': assert seam<1e-4,(name,seam)
    results[name]={'fbx_reimported':True,'frames':[start,end],'max_mesh_motion_m':round(motion,5),'loop_mesh_seam_m':round(seam,7),'max_root_drift_m':round(root_drift,7)}
(OUT/'animation-export-check.json').write_text(json.dumps({'clips':results,'unity_tested':False},indent=2))
print('ANIMATION EXPORT CHECK PASSED:',json.dumps(results))
