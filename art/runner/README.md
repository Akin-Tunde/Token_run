# Token Run runner model

Procedural Blender interpretation of the user-supplied teal sci-fi runner reference. Initial blockout generated with tools/create_runner.py; refinement generated with tools/refine_runner.py. No paid generation service used. The original blockout is preserved in blockout-v1/.

Files: TokenRun_Runner.blend (editable source with packed reference), TokenRun_Runner.fbx (mesh and six flat-color materials), runner-preview.png, runner-front.png and runner-back.png (renders), model-info.json (geometry and topology counts), export-check.json (independent Blender reopen / FBX reimport check).

Refinement replaces the intersecting suit pieces with a fused, smoothed, quad-remeshed body. The body is checked for one connected component and zero non-manifold edges. Chest armor follows the torso; arms, legs and boots have shaped cross sections; separate rigid shells retain the color scheme. The model uses Blender Z-up, faces -Y, and has a ground-level origin; FBX uses -Z forward / Y up conversion. Source and FBX triangle counts and height are checked by tools/check_runner_export.py.

The model remains unrigged and unanimated. Automatic quad remeshing is a starting point for skinning, not proof of correct elbow, shoulder, hip or knee deformation. Hands are stylized mittens. Armor parts may intersect the suit by design; the full character is not a single welded mesh. Six materials remain, with no UV texture atlas. Helmet markings are coarse face-color regions. No production skinning, Unity import validation, animation or device performance testing has been completed. The game has not been changed to use it. User must verify rights to the supplied reference before distribution.

## Rigged version

`TokenRun_Runner_Rigged.blend` and `TokenRun_Runner_Rigged.fbx` add a 22-bone FK skeleton (21 deforming bones), with Hips, Spine, Chest, Neck, Head, paired shoulders, arms, hands, legs, feet and toes. Root is non-deforming. The flexible suit uses Blender bone-heat weights, limited to four influences and normalized. Armor shells are weighted rigidly to their associated bones. The original unrigged files remain available.

Open the rigged Blender source, select `TokenRun_Humanoid`, enter Pose Mode, and rotate the bones. The saved source and FBX are in the neutral A-pose, not the diagnostic bent poses. Hands are mittens with no finger bones. There are no IK controllers or gameplay animation clips.

`tools/rig_runner.py` checks every mesh vertex for deform weights, normalization and the four-influence limit, then evaluates and renders two diagnostic poses. `rig-test-arms.png` covers raised shoulders and 75-degree elbow bends; `rig-test-stride.png` covers hip and knee bends. `rig-check.json` records the executed numeric checks. Bounded vertex motion alone does not establish good deformation; both rendered poses were also visually inspected. Extreme poses, twisting and animation sequences remain untested, and manual skin-weight or topology adjustments may still be needed.

`tools/check_runner_rig_export.py` independently reimports the FBX into Blender and verifies all required skeleton names, 26 skinned meshes, valid normalized weights with at most four influences, and a working 60-degree knee bend. Results are in `rig-export-check.json`. This is not a Unity Humanoid Avatar validation.

## Animated version

`TokenRun_Runner_Animated.blend` retains three original FK actions in the Action Editor, authored by `tools/animate_runner.py`. The saved project opens on Idle. `animations/Idle.fbx`, `Run.fbx`, and `Jump.fbx` each contain the character, skeleton and one baked animation. The unanimated rigged source remains intact.

| Action | Source frames | Duration at 30 FPS | Loop |
|---|---|---|---|
| Idle | 1–61 | 2 seconds | Yes |
| Run | 1–25 | 0.8 seconds | Yes |
| Jump | 1–31 | 1 second | No |

Root and armature translation stay fixed. Hip offsets handle stance / crouch, but horizontal movement and the actual airborne jump arc must come from the gameplay controller. The jump includes anticipation, tuck and recovery; do not assume its one-second duration already matches gameplay airtime. Run timing has not been calibrated to the controller's 7 m/s speed. Grounding checks constrain the lowest sole, not both feet or a planted foot trajectory; some foot sliding and shell intersection may need animation polish. These are prototype FK clips, not motion capture or final production animation.

`animation-check.json` records source loop and grounding checks. `tools/check_runner_animation_export.py` reimports each exported FBX independently, samples skinned mesh deformation across every frame, and checks fixed root translation and matching endpoints for Idle and Run. Blender's importer places these exported takes at frames 2–62, 2–26 and 2–32 respectively; durations are unchanged. Results are in `animation-export-check.json`. This is Blender playback validation, not Unity playback validation.

Rendered playback frames are in `animations/Idle/`, `Run/` and `Jump/`. `tools/preview_runner_animation.py` packages them into per-clip GIFs and six-frame contact sheets; Pillow is used only for these development previews, not shipped in the game.

Unity integration source is now prepared; see `docs/RUNNER_UNITY_INTEGRATION.md`. Four FBXs are copied into the game, and Configure Phase 1 will generate a Generic-rig prefab/controller with URP materials. The existing custom skeleton uses Generic mode, without humanoid retargeting. Root motion is off, Idle/Run loop, and the airborne portion of Jump is sampled against physics. The capsule remains the fallback until Unity setup produces the prefab. Actual Unity import, transitions, draw calls and gameplay remain unverified. Texture atlasing, run cadence calibration and animation polish are still needed.
