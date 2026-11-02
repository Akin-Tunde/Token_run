using UnityEngine;
namespace TokenRun {
 [RequireComponent(typeof(Rigidbody))]
 public sealed class ObstacleMotion : MonoBehaviour {
  public Vector3 Travel; public float DegreesPerSecond; public float Period=3;
  Rigidbody body; Vector3 origin; Quaternion rotation; float elapsed;
  void Awake() { body=GetComponent<Rigidbody>(); body.isKinematic=true; body.interpolation=RigidbodyInterpolation.Interpolate; origin=transform.position; rotation=transform.rotation; }
  void FixedUpdate() { elapsed+=Time.fixedDeltaTime; body.MovePosition(origin+Travel*Mathf.Sin(elapsed*Mathf.PI*2/Period)); body.MoveRotation(rotation*Quaternion.Euler(0,elapsed*DegreesPerSecond,0)); }
 }
}
