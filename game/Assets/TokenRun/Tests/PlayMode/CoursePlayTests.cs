using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
namespace TokenRun.Tests {
 public sealed class CoursePlayTests {
  RaceDirector race; Keyboard keyboard;
  [UnitySetUp] public IEnumerator Setup() {
   yield return SceneManager.LoadSceneAsync("MoonLaunch",LoadSceneMode.Single);
   race=Object.FindFirstObjectByType<RaceDirector>(); Assert.IsNotNull(race);
   keyboard=InputSystem.AddDevice<Keyboard>();
   race.Begin(); yield return new WaitForSeconds(.6f);
  }
  [UnityTearDown] public IEnumerator Cleanup() {
   if(keyboard!=null && keyboard.added) InputSystem.RemoveDevice(keyboard);
   var old=SceneManager.GetActiveScene(); var clean=SceneManager.CreateScene("Test cleanup"); SceneManager.SetActiveScene(clean);
   yield return SceneManager.UnloadSceneAsync(old);
  }
  [UnityTest] public IEnumerator KeyboardMovesRunner() {
   float start=race.Runner.transform.position.z;
   InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.W));
   yield return new WaitForSeconds(.3f);
   InputSystem.QueueStateEvent(keyboard,new KeyboardState()); yield return null;
   Assert.Greater(race.Runner.transform.position.z,start+1f);
  }
  [UnityTest] public IEnumerator AnimatedRunnerTracksMovementJumpAndRestart() {
   var visual=race.Runner.GetComponentInChildren<RunnerAnimation>();
   Assert.IsNotNull(visual,"Run Token Run > Configure Phase 1 to generate the runner prefab.");
   var animator=visual.GetComponent<Animator>();
   Assert.IsNotNull(animator.runtimeAnimatorController);
   Assert.IsFalse(animator.applyRootMotion,"Animation must never move the gameplay controller.");
   Assert.AreEqual("Idle",visual.CurrentAnimation);
   Assert.AreEqual(26,visual.GetComponentsInChildren<SkinnedMeshRenderer>().Length);
   var visualRoot=visual.transform.localPosition;
   InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.W));
   yield return new WaitForSeconds(.25f);
   Assert.AreEqual("Run",visual.CurrentAnimation);
   InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.Space));
   yield return new WaitForSeconds(.15f);
   InputSystem.QueueStateEvent(keyboard,new KeyboardState());
   Assert.AreEqual("Jump",visual.CurrentAnimation);
   Assert.Greater(race.Runner.FlightProgress,0);
   Assert.Less(race.Runner.FlightProgress,1);
   yield return new WaitForSeconds(1f);
   Assert.IsTrue(race.Runner.Grounded);
   Assert.AreEqual("Idle",visual.CurrentAnimation);
   Assert.Less(Vector3.Distance(visualRoot,visual.transform.localPosition),.0001f);
   race.Begin(); yield return null;
   Assert.AreEqual("Idle",visual.CurrentAnimation,"Replay must reset animation state.");
  }
  [UnityTest] public IEnumerator GroundedJumpRisesAndLands() {
   float ground=race.Runner.transform.position.y;
   Assert.IsTrue(race.Runner.GetComponent<CharacterController>().isGrounded);
   InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.Space)); yield return null;
   InputSystem.QueueStateEvent(keyboard,new KeyboardState());
   yield return new WaitForSeconds(.2f);
   Assert.Greater(race.Runner.transform.position.y,ground+.5f);
   yield return new WaitForSeconds(1f);
   Assert.IsTrue(race.Runner.GetComponent<CharacterController>().isGrounded);
  }
  [UnityTest] public IEnumerator CheckpointTriggerChangesFallRespawn() {
   race.Runner.ResetTo(new Vector3(0,1,25)); Physics.SyncTransforms();
   yield return new WaitForSeconds(.1f);
   Assert.AreEqual(1,race.State.Checkpoint);
   // Move below the fall threshold without changing the stored spawn.
   var body=race.Runner.GetComponent<CharacterController>(); body.enabled=false;
   race.Runner.transform.position=new Vector3(0,-10,25); body.enabled=true;
   yield return null; yield return null;
   Assert.AreEqual(1,race.State.Respawns);
   Assert.Greater(race.Runner.transform.position.y,0);
   Assert.AreEqual(26,race.Runner.transform.position.z,.1f);
  }
  [UnityTest] public IEnumerator FinishRequiresCheckpointsAndShowsResults() {
   race.Runner.ResetTo(new Vector3(0,1,73)); Physics.SyncTransforms(); yield return new WaitForSeconds(.1f);
   Assert.IsFalse(race.State.Finished); Assert.IsFalse(race.ResultPanel.activeSelf);
   foreach(float z in new[]{25f,45f,73f}) {
    race.Runner.ResetTo(new Vector3(0,1,z)); Physics.SyncTransforms(); yield return new WaitForSeconds(.1f);
   }
   Assert.IsTrue(race.State.Finished); Assert.IsTrue(race.ResultPanel.activeSelf);
   float stopped=race.State.Seconds; yield return new WaitForSeconds(.1f); Assert.AreEqual(stopped,race.State.Seconds);
   race.Begin(); Assert.IsFalse(race.ResultPanel.activeSelf); Assert.AreEqual(0,race.State.Checkpoint); Assert.IsTrue(race.State.Running);
  }
 }
}
