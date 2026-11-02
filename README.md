# Token Run Hybrid — Phase 1 source prototype
Original single-player obstacle race for Unity, Android and Web. No wallet, token, purchases, backend or network connection is required or implemented.

**Status: implemented source, NOT a verified playable release.** Unity/Hub, C# compiler, Android SDK and Blender were not available in the authoring environment. No Unity compilation, package resolution, game execution or target build has been performed. See docs/VALIDATION.md.

## Open and play
1. Install Unity Hub and Unity **6.3 LTS (6000.3.0f1)** plus Android Build Support (SDK, NDK, OpenJDK) and Web Build Support. This reproducible baseline is not a claim that it is the latest security patch. Prefer a current patched 6.3 LTS editor for a release; validate and record any upgrade before shipping.
2. Add the `game/` directory as a Unity project. Let Package Manager resolve the pinned dependencies. Unity generates omitted default settings and package lock on first import; review and retain the resolved lock afterward.
3. Run **Token Run → Configure Phase 1**. It selects the Input System, creates a URP mobile pipeline and shader material, sets landscape orientation and registers the scene. Accept/restart Unity if prompted for the input backend. Do this before Play or build.
4. Open `Assets/TokenRun/Scenes/MoonLaunch.unity`, then press Play and START RACE. The saved scene contains a bootstrap component; original prototype geometry and UI are generated in Awake, so the course appears in Play mode.
5. WASD/arrows move along camera-aligned world axes; Space jumps. The on-screen stick and JUMP button also operate in Editor with a mouse, and with simultaneous touches on a phone. Cross both blue checkpoints in order, then the green finish gate. Jump the runway gaps and rotating orange bars. Falling or touching a rotating bar respawns at the latest checkpoint without resetting time. Moving solid bumpers block/push the route.
6. Finish shows elapsed time and respawns; RACE AGAIN resets the run.

## Android testing
Connect an Android device with USB debugging. Switch Build Profiles to Android, select the device, use development build and Build And Run. Configure selects IL2CPP + ARM64 and minimum Android API 26; install Android NDK support. Local debug signing only. Test stick+jump simultaneously, orientation, app pause/resume, respawns, restart and UI on different aspect ratios. Record device model, OS, resolution, CPU/GPU frame time, memory and thermal behavior. A targetFrameRate of 60 is a request, not a measured result.

## Web testing
Switch Build Profiles to Web and Build And Run with Unity's local server. Test a current desktop browser with keyboard and mouse; test mobile browsers separately. Serve via HTTP, not file://. No browser multiplayer transport is installed.

## Tests and command line
Run `python3 tools/validate_source.py` from the repository root (structural checks only).
Run Unity Test Runner → EditMode and PlayMode → Run All. There are seven race-state cases and four scene/gameplay tests. All require execution in Unity.

For an automated full verification run:
```sh
python3 tools/verify_unity.py --unity /absolute/path/to/Unity --build both
```
This refuses to pass if Unity is missing, reports contain zero tests, any test fails, or a build fails. Logs/XML are placed in `game/Builds/Validation/`. The optional manual GitHub workflow needs your own activated Unity runner labeled `token-run-unity`; no runner has been provisioned.
With an activated Unity editor, from the repository root (replace Unity with the editor executable):

```sh
Unity -batchmode -quit -projectPath "$PWD/game" -executeMethod TokenRun.Editor.ProjectSetup.Configure -logFile setup.log
Unity -batchmode -projectPath "$PWD/game" -runTests -testPlatform EditMode -testResults "$PWD/editmode-results.xml" -logFile tests.log
Unity -batchmode -quit -projectPath "$PWD/game" -executeMethod TokenRun.Editor.ProjectSetup.BuildAndroid -logFile android.log
Unity -batchmode -quit -projectPath "$PWD/game" -executeMethod TokenRun.Editor.ProjectSetup.BuildWeb -logFile web.log
```

Do not add `-quit` to the test command; the test runner exits on completion. Build functions throw on failure. Check logs and reports, not merely editor launch.

## Layout
`game/`: Unity client, runtime scripts, saved scene, Editor setup and NUnit tests.
`docs/`: technical plan, dependencies, Blender specification and validation.
`backend/`, `contracts/`: empty reserved folders; future phases require authorization.
`tools/`, `tests/`, `.github/workflows/`: source audit and CI.

All geometry is prototype art. No production character assets, audio, multiplayer, backend, blockchain, deployment or measured hardware performance is included. Do not describe Phase 1 as accepted until every runtime acceptance check is verified.
