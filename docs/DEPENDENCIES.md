# Dependency baseline
| Dependency | Version | Purpose |
|---|---|---|
| Unity Editor | 6000.3.0f1 / 6.3 LTS | Initial import baseline; not yet executed |
| URP | 17.3.0 | Android/Web rendering |
| Input System | 1.17.0 | Actions and on-screen virtual gamepad |
| Unity Test Framework | 1.6.0 | EditMode NUnit tests |
| UGUI | 2.0.0 | Canvas screens and touch graphics |
| Built-in physics, UI, IMGUI, audio, textcorefontengine, textrendering | 1.0.0 | Engine modules |
| Python | 3 standard library | Source audit; not shipped in game |

Transitive packages are resolved by Unity Package Manager; no fabricated packages-lock.json is provided. Runtime compatibility and resolution remain UNVERIFIED. No third-party game assets or services are used. Blender is an optional future asset-authoring tool, not needed for primitive prototype geometry.

Official references checked 2026-11-02:
- https://unity.com/releases/unity-6/support
- https://unity.com/releases/editor/whats-new/6000.3.0f1
- https://docs.unity3d.com/kr/6000.0/Manual/com.unity.inputsystem.html
- https://unity.com/releases/editor/beta/6000.3.0b2 (Test Framework 1.6.0 update)
- https://docs.unity.cn/Packages/com.unity.render-pipelines.universal@17.3/api/UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset.html
