using UnityEngine;
using UnityEngine.UI;
namespace TokenRun {
 public sealed class RaceDirector : MonoBehaviour {
  public const int RequiredCheckpoints=2;
  public readonly RaceState State=new RaceState();
  public RunnerMotor Runner; public Text Status; public GameObject StartPanel, ResultPanel; public Text Results;
  public void Begin() { Runner.ResetTo(new Vector3(0,2,0)); State.Start(); StartPanel.SetActive(false); ResultPanel.SetActive(false); }
  void Update() {
   State.Tick(Time.deltaTime);
   Status.text=$"TOKEN RUN • PROTOTYPE   |   {State.Seconds:0.0}s   |   Checkpoints {State.Checkpoint}/2   |   Respawns {State.Respawns}";
   if(State.Finished && !ResultPanel.activeSelf) { Results.text=$"COURSE COMPLETE\n{State.Seconds:0.00} seconds • {State.Respawns} respawns"; ResultPanel.SetActive(true); }
  }
 }
}
