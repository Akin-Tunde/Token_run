using UnityEngine;
namespace TokenRun {
 public sealed class CourseTrigger : MonoBehaviour {
  public RaceDirector Race; public int Checkpoint; public bool IsFinish, IsHazard; public Vector3 Spawn;
  void OnTriggerEnter(Collider other) {
   var runner=other.GetComponent<RunnerMotor>(); if(!runner || runner.Race!=Race || !Race.State.Running) return;
   if(IsHazard) runner.Respawn();
   else if(IsFinish) Race.State.Finish(RaceDirector.RequiredCheckpoints);
   else if(Race.State.Reach(Checkpoint)) runner.SetSpawn(Spawn);
  }
 }
}
