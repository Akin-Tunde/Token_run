using UnityEngine;
namespace TokenRun {
 [RequireComponent(typeof(RectTransform))]
 public sealed class SafeAreaLayout : MonoBehaviour {
  Rect last; int width, height; RectTransform rect;
  void Awake() { rect=GetComponent<RectTransform>(); Apply(); }
  void Update() { if(last!=Screen.safeArea || width!=Screen.width || height!=Screen.height) Apply(); }
  void Apply() {
   width=Screen.width; height=Screen.height; last=Screen.safeArea;
   if(width<=0 || height<=0) return;
   rect.anchorMin=new Vector2(last.xMin/width,last.yMin/height);
   rect.anchorMax=new Vector2(last.xMax/width,last.yMax/height);
   rect.offsetMin=rect.offsetMax=Vector2.zero;
  }
 }
}
