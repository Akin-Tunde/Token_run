using UnityEngine;
namespace TokenRun {
 [RequireComponent(typeof(CharacterController),typeof(RunnerInput))]
 public sealed class RunnerMotor : MonoBehaviour {
  public RaceDirector Race;
  CharacterController body; RunnerInput input; float vertical; Vector3 spawn;
  const float Speed=7f, Gravity=-24f, JumpHeight=1.65f;
  void Awake() { body=GetComponent<CharacterController>(); input=GetComponent<RunnerInput>(); spawn=transform.position; }
  void Update() {
   if(Race==null || !Race.State.Running) return;
   var axis=Vector2.ClampMagnitude(input.Move,1);
   var motion=new Vector3(axis.x,0,axis.y);
   if(body.isGrounded && vertical<0) vertical=-2;
   if(body.isGrounded && input.Jump) vertical=Mathf.Sqrt(-2*Gravity*JumpHeight);
   vertical+=Gravity*Time.deltaTime;
   body.Move((motion*Speed+Vector3.up*vertical)*Time.deltaTime);
   if(motion.sqrMagnitude>.01f) transform.rotation=Quaternion.Slerp(transform.rotation,Quaternion.LookRotation(motion),12*Time.deltaTime);
   if(transform.position.y < -8) Respawn();
  }
  public void SetSpawn(Vector3 point) { spawn=point; }
  public void ResetTo(Vector3 point) { spawn=point; Teleport(); }
  public void Respawn() { if(!Race.State.Running) return; Race.State.Respawn(); Teleport(); }
  void Teleport() { body.enabled=false; transform.position=spawn; transform.rotation=Quaternion.identity; vertical=0; body.enabled=true; }
 }
}
