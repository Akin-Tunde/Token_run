using UnityEngine;
using UnityEngine.InputSystem;
namespace TokenRun {
 public sealed class RunnerInput : MonoBehaviour {
  InputAction move, jump;
  public Vector2 Move => move.ReadValue<Vector2>();
  public bool Jump => jump.WasPressedThisFrame();
  void Awake() {
   move=new InputAction("Move",InputActionType.Value);
   move.AddCompositeBinding("2DVector").With("Up","<Keyboard>/w").With("Down","<Keyboard>/s").With("Left","<Keyboard>/a").With("Right","<Keyboard>/d");
   move.AddCompositeBinding("2DVector").With("Up","<Keyboard>/upArrow").With("Down","<Keyboard>/downArrow").With("Left","<Keyboard>/leftArrow").With("Right","<Keyboard>/rightArrow");
   move.AddBinding("<Gamepad>/leftStick");
   jump=new InputAction("Jump",InputActionType.Button,"<Keyboard>/space"); jump.AddBinding("<Gamepad>/buttonSouth");
  }
  void OnEnable() { move.Enable(); jump.Enable(); }
  void OnDisable() { move.Disable(); jump.Disable(); }
  void OnDestroy() { move.Dispose(); jump.Dispose(); }
 }
}
