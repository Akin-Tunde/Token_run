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
# Validate stable Unity metadata and actual assembly names.
assets=root/'game/Assets/TokenRun'
check(not list(assets.rglob('*.meta.meta')),'recursive .meta files')
guids=set()
for path in assets.rglob('*.meta'):
 lines=path.read_text().splitlines()
 guid=next((line.split(': ',1)[1] for line in lines if line.startswith('guid: ')),None)
 check(bool(guid) and guid not in guids,str(path)+' GUID must be unique')
 guids.add(guid)
 original=Path(str(path)[:-5])
 check(original.exists(),str(path)+' orphan metadata')
runtime=json.loads((assets/'Scripts/TokenRun.Runtime.asmdef').read_text())
check('UnityEngine.UI' in runtime['references'],'UGUI uses UnityEngine.UI assembly')
check('Unity.ugui' not in runtime['references'],'invalid UI assembly reference')
check((assets/'Tests/PlayMode/CoursePlayTests.cs').is_file(),'gameplay tests')
print(f'PASS: {checks} structural checks. Unity compilation, tests and gameplay remain UNVERIFIED.')
