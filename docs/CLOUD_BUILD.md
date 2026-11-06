# First Unity Build Automation target

The repository contains unverified Unity source. Cloud compilation and runtime checks have not yet executed. Connecting a repository alone does not upload local edits or configure a build.

Use these initial dashboard settings:

| Setting | Value |
|---|---|
| Target name | Token Run Web Test |
| Repository | Akin-Tunde/Token_run |
| Branch | cloud/phase1-runner |
| Project subfolder | game |
| Platform | Web / WebGL |
| Unity Editor | 6000.3.0f1 if available; validate and record any other 6.3 LTS patch before accepting results |
| Automatic builds | Off |
| Advanced > Script Hooks > Pre-Export Method | TokenRun.Editor.ProjectSetup.PrepareCloudBuild |
| Scenes, if the dashboard requires an explicit list | Assets/TokenRun/Scenes/MoonLaunch.unity |

The pre-export method runs inside Unity after compilation. It configures rendering, the Input System, the scene and the animated runner assets, then lets Build Automation run its own build. It also enables Web decompression fallback for simpler test hosting. Do not use `BuildWeb` as the hook: that would invoke a second build inside Build Automation.

The prepared changes are intended for the separate `cloud/phase1-runner` branch. Confirm that this branch exists on GitHub before starting a cloud build. Keep any authentication token in Unity's credential settings, outside this repository. Review current billing and build-consumption controls before starting chargeable jobs. No cloud build, hosting deployment or purchase is initiated by this source preparation.

Save the build configuration first. On the first run, inspect the complete logs for package resolution, compilation, model import, runner setup and build output. A successful build is not a passing gameplay test. Configure cloud EditMode/PlayMode testing separately, and check nonempty results. The current automated test suite expects setup-generated assets and the Input System backend; ordering must be validated on the actual runner. Play the Web artifact over HTTP and test controls, jumping, checkpoints, fall respawns, finish and replay. Android hardware tests remain separate.

Official references: [build configuration](https://docs.unity.com/en-us/build-automation/basic-build-configuration/overview), [pre-export hooks](https://docs.unity.com/en-us/build-automation/advanced-build-configuration/run-custom-scripts-during-the-build-process).
