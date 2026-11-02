using System;
namespace TokenRun {
 public sealed class RaceState {
  public bool Running { get; private set; }
  public bool Finished { get; private set; }
  public float Seconds { get; private set; }
  public int Checkpoint { get; private set; }
  public int Respawns { get; private set; }
  public void Start() { Running=true; Finished=false; Seconds=0; Checkpoint=0; Respawns=0; }
  public void Tick(float dt) { if(dt<0) throw new ArgumentOutOfRangeException(nameof(dt)); if(Running) Seconds+=dt; }
  public bool Reach(int id) { if(!Running || id!=Checkpoint+1) return false; Checkpoint=id; return true; }
  public bool Finish(int required) { if(!Running || Checkpoint!=required) return false; Running=false; Finished=true; return true; }
  public void Respawn() { if(Running) Respawns++; }
 }
}
