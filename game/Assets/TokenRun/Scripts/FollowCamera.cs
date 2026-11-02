using UnityEngine;
namespace TokenRun {
 public sealed class FollowCamera : MonoBehaviour {
  public Transform Target; Vector3 velocity;
  void LateUpdate() { if(!Target) return; transform.position=Vector3.SmoothDamp(transform.position,Target.position+new Vector3(0,7,-10),ref velocity,.16f); transform.LookAt(Target.position+Vector3.up); }
 }
}
