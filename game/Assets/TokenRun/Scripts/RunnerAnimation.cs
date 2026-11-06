using UnityEngine;

namespace TokenRun {
 // Cosmetic only: CharacterController continues to own translation and jumping.
 [RequireComponent(typeof(Animator))]
 public sealed class RunnerAnimation : MonoBehaviour {
  Animator animator;
  RunnerMotor motor;
  int resetVersion=-1;
  public string CurrentAnimation { get; private set; }
  static readonly int Idle=Animator.StringToHash("Base Layer.Idle");
  static readonly int Run=Animator.StringToHash("Base Layer.Run");
  static readonly int Jump=Animator.StringToHash("Base Layer.Jump");

  void Awake() {
   animator=GetComponent<Animator>();
   animator.applyRootMotion=false;
   motor=GetComponentInParent<RunnerMotor>();
  }

  void LateUpdate() {
   if(!motor || !animator.runtimeAnimatorController) return;
   if(resetVersion!=motor.AnimationResetVersion) {
    resetVersion=motor.AnimationResetVersion;
    animator.speed=1;
    animator.Play(Idle,0,0);
    CurrentAnimation="Idle";
    animator.Update(0);
    return;
   }
   bool running=motor.Race && motor.Race.State.Running;
   if(running && !motor.Grounded) {
    // Only sample the airborne segment; physics controls takeoff and landing.
    animator.speed=1;
    animator.Play(Jump,0,Mathf.Lerp(.30f,.70f,motor.FlightProgress));
    animator.Update(0);
    CurrentAnimation="Jump";
    return;
   }
   bool moving=running && motor.MovementFraction>.05f;
   string next=moving?"Run":"Idle";
   animator.speed=moving?Mathf.Clamp(motor.MovementFraction,.25f,1):1;
   if(CurrentAnimation!=next) {
    animator.CrossFadeInFixedTime(moving?Run:Idle,.10f,0,0);
    CurrentAnimation=next;
   }
  }
 }
}
