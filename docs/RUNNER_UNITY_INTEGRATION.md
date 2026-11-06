# Animated runner integration — 2026-11-06

Status: source integration prepared; Unity import, generated prefab, compilation and runtime playback are NOT verified. Phase 1 acceptance remains incomplete.

## Delivered source

- Four FBXs copied into `game/Assets/TokenRun/Art/Runner/`: the unanimated skinned runner and separate Idle, Run and Jump takes. Hashes match their Blender exports.
- `RunnerVisualSetup.Configure` imports a Generic Avatar, copies it to the clips, names the takes, enables Idle/Run looping, disables Jump looping, and creates an Animator Controller, six URP palette materials and a Resources prefab. Generic mode preserves the existing custom skeleton and FK clips without requiring humanoid retargeting. A Humanoid Avatar is not configured or claimed valid.
- Model facing is derived from the foot/toe bones, and import height is checked. A wrapper outside the FBX animation hierarchy owns orientation and ground correction. Setup requires the expected 26 skinned meshes and valid clip lengths; failure throws rather than silently generating an incomplete prefab.
- `CourseBootstrap` uses the generated prefab if available. Without it, the original capsule appears with an explanatory warning. The existing CharacterController remains the sole gameplay collider.
- `RunnerAnimation` selects idle/running from actual horizontal CharacterController velocity. Root motion is off. While airborne it samples the Jump clip's 30–70% region against the motor's ballistic phase, avoiding an animation-controlled jump delay or a fixed-duration loop. Walking off an edge uses the descending phase. Landing blends back to idle/run; restart and respawn reset animation state.
- The built-in Unity animation module is explicitly listed in the package manifest, and the Editor assembly references the runtime assembly used by the generated prefab.

No generated controller, material or prefab is represented as completed here: these must be produced and checked in Unity by the setup method. Model and script metadata GUIDs are supplied; Unity will populate default importer settings on initial import, then setup applies the explicit runner settings.

## Run in Unity

1. Finish installing an Editor and activate its license in Unity Hub. The pinned project remains Unity 6.3 LTS (`6000.3.0f1`); the user's 6.6 installation has not been validated against these dependencies. Preserve a project backup before any version upgrade.
2. Open `game/`, wait for Package Manager and inspect the Console.
3. Run **Token Run > Configure Phase 1**. It now also configures the runner. Restart if prompted for the Input System. The narrower **Token Run > Configure Animated Runner** command can regenerate only the character assets afterward.
4. Open `MoonLaunch.unity`, press Play and start the race. Check color/material rendering, facing, feet height, movement, blocked movement, jumping, falling, checkpoints, finish and replay.
5. Run EditMode and PlayMode suites. The new PlayMode scenario requires the generated model and checks Idle → Run → Jump → Idle, fixed visual-root position and disabled root motion, then replay reset. It intentionally fails if only the capsule fallback exists.
6. Run the complete verifier with the activated Editor path:

   `python tools/verify_unity.py --unity "C:/path/to/Editor/Unity.exe" --build both`

Retain logs, XML reports, generated import metadata and package lock after successful Unity execution. Manual playthrough, actual-device profiling and target builds remain required before Phase 1 acceptance.

## Checks executed here

- `tools/validate_source.py`: 112 structural checks passed.
- `tools/check_runner_integration.py --csharp`: four FBX hash/header checks, animation-module and Editor-reference checks, runner Python-tool syntax checks, and all 14 C# files parsed without syntax errors. Tree-sitter checks syntax only, not C# compilation or Unity APIs.
- `git diff --check`: passed.
- `tools/verify_unity.py --build both`: exit 2, BLOCKED because the Unity Editor is unavailable. No Unity import, tests, generated prefab, APK or Web build executed.

Earlier Blender evidence remains in `art/runner/animation-export-check.json`: all three animation FBXs reimported and sampled successfully, with fixed root translation and matching Idle/Run endpoints. Those results do not establish Unity playback.

## Remaining limitations

The character is prototype art with six materials and 26 skinned meshes; batching, bounds, draw calls and device performance need measurement. Foot sliding, armor intersections and transitions need visual polish. The airborne sampling excludes authored anticipation and recovery portions, because the current jump is immediate and gameplay-owned. Run cadence still needs calibration to 7 m/s movement. Humanoid retargeting, texture atlasing and IK are not implemented. No backend, blockchain, networking or future phase was added.

Unity import references: [ModelImporter](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/modelimporter), [clipAnimations](https://docs.unity.com/en-us/engine/6000.3/script-reference/unityeditor/modelimporter/clipanimations).
