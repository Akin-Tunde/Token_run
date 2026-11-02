# Phase 1 technical plan
## Scope and architecture
One local obstacle race, Moon Launch prototype. RaceState owns ordered checkpoint progression, elapsed time, finish eligibility and restart. RaceDirector coordinates UI and runner. RunnerInput uses Unity Input System actions and virtual gamepad controls; RunnerMotor uses CharacterController with grounded jump and gravity. FollowCamera smooths separately in LateUpdate. CourseTrigger handles checkpoints, finish and respawns. ObstacleMotion moves kinematic Rigidbody hazards in FixedUpdate. CourseBootstrap creates original geometry, HUD, overlays and touch controls from a saved entry scene. Editor setup creates URP assets and build scene registration.

The camera has a fixed trailing orientation; input maps directly to the ground plane. There is no orbit camera. Movement is local and has no claim to anti-cheat protection. Never reuse client RaceState results as authoritative rewards in a future server.

## Course
Four 12m-wide runways, each 18m long, separated by 2m jump gaps. Three moving bumpers and three constant-speed rotating hazard bars telegraph danger through visible motion. Ordered checkpoints at z25 and z45; finish at z73. Groundless fall threshold y−8. Checkpoint spawns at gate+1m, inside safe runway areas. Prototype art only; scene generation is deterministic except time-based motion.

## Sequence and release gate
1. Import, resolve packages, run Configure, restart input backend.
2. Compile and run EditMode tests.
3. Play through full course with keyboard and with touch; record results against VALIDATION.md.
4. Test Android and Web builds, then profile actual devices.
5. Fix runtime failures within Phase 1. Stop before Phase 2; obtain authorization for additional scope.

## Performance assumptions and limitations
URP render scale .85, MSAA 2x, short shadow distance. Few static primitives and three kinematic moving bumpers plus three bars. No recurring entity spawn loop; pooling is unnecessary for this fixed course. Materials are currently per-object prototype instances, with no measured batching budget. No final textures or animation rigs exist. Device-adaptive tiers, compression and asset optimization await real assets and profiling. No 60 FPS claim. Current UI does not apply safe-area insets and needs notched-device testing. App suspension/focus timing follows Unity frame time; no persistence or offline elapsed-time guarantee. Movement on top of moving obstacles has no explicit platform carry behavior; course does not require riding them.

## Deferred architecture
Backend: TypeScript/PostgreSQL; Redis only if justified by queues, presence or caching. Authentication, ownership and inventory remain server responsibilities. Networking selection requires later comparison of Unity compatibility, Android/Web transports, authoritative dedicated servers, cost and maintenance, followed by real multi-client tests. No networking choice is made in Phase 1.
Robinhood Chain: deliberately unimplemented and unverified in this phase. Before Phase 5, consult official current chain/RPC/wallet/account-abstraction documentation. Testnet only; no production deploy or spending without approval. Gameplay remains off-chain and wallet-optional.
