"""Source/package checks for runner integration; never substitutes for Unity execution."""
import ast
import argparse
import hashlib
import json
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--csharp',action='store_true',help='Also parse C# syntax (requires tree-sitter and tree-sitter-c-sharp).')
args=parser.parse_args()

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'game/Assets/TokenRun'
sources={'Runner.fbx': ROOT/'art/runner/TokenRun_Runner_Rigged.fbx'}
for name in ['Idle','Run','Jump']:
    sources[name+'.fbx']=ROOT/'art/runner/animations'/(name+'.fbx')
for name,source in sources.items():
    target=ASSETS/'Art/Runner'/name
    assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest(),name
    assert target.read_bytes().startswith(b'Kaydara FBX Binary'),name
manifest=json.loads((ROOT/'game/Packages/manifest.json').read_text())
assert manifest['dependencies']['com.unity.modules.animation']=='1.0.0'
editor=json.loads((ASSETS/'Editor/TokenRun.Editor.asmdef').read_text())
assert 'TokenRun.Runtime' in editor['references']
for path in (ROOT/'tools').glob('*runner*.py'):
    ast.parse(path.read_text(),filename=str(path))
print('PASS: 4 FBX hashes/headers, animation module, Editor assembly reference, and runner tool Python syntax.')
if args.csharp:
    import tree_sitter
    import tree_sitter_c_sharp
    csharp=tree_sitter.Parser(tree_sitter.Language(tree_sitter_c_sharp.language()))
    paths=list(ASSETS.rglob('*.cs'))
    for path in paths:
        tree=csharp.parse(path.read_bytes())
        assert not tree.root_node.has_error,'C# syntax error: '+str(path)
    print(f'PASS: {len(paths)} C# files parsed without syntax errors (not compilation or Unity API validation).')
print('Unity compilation, import, prefab generation and PlayMode remain UNVERIFIED.')
