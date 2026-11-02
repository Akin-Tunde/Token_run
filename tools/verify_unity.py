"""Run real Unity checks; never treat a missing editor or empty test report as success."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--unity',default=os.environ.get('UNITY_EDITOR_PATH','Unity'))
parser.add_argument('--build',choices=['none','android','web','both'],default='none')
args=parser.parse_args()
editor=shutil.which(args.unity)
if not editor:
 print('BLOCKED: Unity Editor unavailable. No compilation, Unity tests or builds executed.')
 sys.exit(2)
output=root/'game/Builds/Validation'
output.mkdir(parents=True,exist_ok=True)
base=[editor,'-batchmode','-projectPath',str(root/'game')]
def execute(label,flags):
 command=base+flags+['-logFile',str(output/(label+'.log'))]
 result=subprocess.run(command,timeout=3600)
 if result.returncode:
  raise RuntimeError(f'{label} failed ({result.returncode}); inspect {output/(label+".log")}')
execute('setup',['-quit','-executeMethod','TokenRun.Editor.ProjectSetup.Configure'])
for mode in ['EditMode','PlayMode']:
 report=output/(mode+'.xml')
 report.unlink(missing_ok=True)
 execute(mode,['-runTests','-testPlatform',mode,'-testResults',str(report)])
 if not report.is_file(): raise RuntimeError(f'{mode}: no XML report generated')
 test_run=ET.parse(report).getroot()
 total=int(test_run.get('total','0')); passed=int(test_run.get('passed','0'))
 if total<=0 or passed!=total or test_run.get('result')!='Passed':
  raise RuntimeError(f'{mode}: not all tests passed: {ET.tostring(test_run,encoding="unicode")[:300]}')
 print(f'PASS: {mode}: {passed}/{total}')
for kind,target,method in [('android','Android','BuildAndroid'),('web','WebGL','BuildWeb')]:
 if args.build in [kind,'both']:
  execute(kind,['-quit','-buildTarget',target,'-executeMethod','TokenRun.Editor.ProjectSetup.'+method])
  print('PASS: '+kind+' build')
print('Unity checks finished. Actual device gameplay and performance still require manual testing.')
