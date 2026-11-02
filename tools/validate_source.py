"""Structural audit only: does not compile C# or validate Unity behavior."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks=0
def check(value,message):
 global checks
 assert value,message
 checks+=1
for path in (root/'game').rglob('*.asmdef'):
 check(bool(json.loads(path.read_text())['name']),str(path))
m=json.loads((root/'game/Packages/manifest.json').read_text())
for name in ['com.unity.inputsystem','com.unity.render-pipelines.universal','com.unity.test-framework','com.unity.ugui','com.unity.modules.physics','com.unity.modules.audio']:
 check(name in m['dependencies'],name)
scene=(root/'game/Assets/TokenRun/Scenes/MoonLaunch.unity').read_text()
check('0c8d44607a354236969e23999058f3b1' in scene,'scene bootstrap GUID')
meta=(root/'game/Assets/TokenRun/Scripts/CourseBootstrap.cs.meta').read_text()
check('0c8d44607a354236969e23999058f3b1' in meta,'script GUID')
for name in ['RunnerMotor','RunnerInput','RaceState','RaceDirector','CourseTrigger','ObstacleMotion','FollowCamera','CourseBootstrap']:
 check((root/f'game/Assets/TokenRun/Scripts/{name}.cs').is_file(),name)
for name in ['README.md','AGENTS.md','docs/PHASE_1_PLAN.md','docs/DEPENDENCIES.md']:
 check((root/name).is_file(),name)
check('MoonLaunch.unity' in (root/'game/ProjectSettings/EditorBuildSettings.asset').read_text(),'build scene')
print(f'PASS: {checks} structural checks. Unity compilation, tests and gameplay remain UNVERIFIED.')
