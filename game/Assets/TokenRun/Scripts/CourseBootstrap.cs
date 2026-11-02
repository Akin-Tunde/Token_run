using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.InputSystem.OnScreen;
namespace TokenRun {
 // All geometry is original, code-generated PROTOTYPE geometry, not final art.
 public sealed class CourseBootstrap : MonoBehaviour {
  RaceDirector race; Font font;
  void Awake() {
   Application.targetFrameRate=60;
   font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
   race=gameObject.AddComponent<RaceDirector>();
   var light=new GameObject("Sun").AddComponent<Light>(); light.type=LightType.Directional; light.intensity=1.3f; light.transform.rotation=Quaternion.Euler(45,-25,0);
   RenderSettings.ambientLight=new Color(.5f,.55f,.65f);
   for(int i=0;i<4;i++) Box("Runway "+i,new Vector3(0,0,i*20+6),new Vector3(12,1,18),new Color(.18f,.3f,.45f));
   for(int i=0;i<3;i++) {
    var g=Box("Moving bumper "+i,new Vector3(0,1.1f,10+i*20),new Vector3(3,1.2f,1.2f),new Color(1,.35f,.15f));
    g.AddComponent<Rigidbody>(); var motion=g.AddComponent<ObstacleMotion>(); motion.Travel=new Vector3(4,0,0); motion.Period=3+i*.5f;
    var bar=Box("Rotating hazard "+i,new Vector3(0,1,17+i*20),new Vector3(8,.65f,.6f),new Color(1,.65f,.1f));
    bar.AddComponent<Rigidbody>(); bar.AddComponent<ObstacleMotion>().DegreesPerSecond=65;
    bar.GetComponent<Collider>().isTrigger=true; var hazard=bar.AddComponent<CourseTrigger>(); hazard.Race=race; hazard.IsHazard=true;
   }
   Gate("Checkpoint 1",25,1,false); Gate("Checkpoint 2",45,2,false); Gate("Finish",73,0,true);
   var player=new GameObject("Prototype capsule runner"); player.transform.position=new Vector3(0,2,0);
   var cc=player.AddComponent<CharacterController>(); cc.height=2; cc.radius=.45f; cc.center=Vector3.up; cc.stepOffset=.3f;
   var visual=GameObject.CreatePrimitive(PrimitiveType.Capsule); visual.name="Prototype body"; visual.transform.SetParent(player.transform,false); visual.transform.localPosition=Vector3.up;
   Destroy(visual.GetComponent<Collider>()); Paint(visual,new Color(.1f,1,.65f));
   player.AddComponent<RunnerInput>(); var motor=player.AddComponent<RunnerMotor>(); motor.Race=race; race.Runner=motor;
   var camera=new GameObject("Main Camera").AddComponent<Camera>(); camera.tag="MainCamera"; camera.backgroundColor=new Color(.04f,.06f,.12f); camera.clearFlags=CameraClearFlags.SolidColor;
   camera.transform.position=new Vector3(0,9,-10); camera.gameObject.AddComponent<AudioListener>(); camera.gameObject.AddComponent<FollowCamera>().Target=player.transform;
   BuildUI();
  }
  GameObject Box(string name,Vector3 pos,Vector3 scale,Color color) { var g=GameObject.CreatePrimitive(PrimitiveType.Cube); g.name=name; g.transform.position=pos; g.transform.localScale=scale; Paint(g,color); return g; }
  void Paint(GameObject g,Color color) { var shader=Shader.Find("Universal Render Pipeline/Lit"); if(!shader) shader=Shader.Find("Standard"); var template=Resources.Load<Material>("PrototypeMaterial"); var mat=template?new Material(template):new Material(shader); mat.color=color; g.GetComponent<Renderer>().sharedMaterial=mat; }
  void Gate(string name,float z,int id,bool finish) {
   var g=Box(name,new Vector3(0,2,z),new Vector3(12,4,.35f),finish?new Color(.2f,1,.5f,.25f):new Color(.2f,.7f,1));
   // Invisible trigger plus visible side markers; full-width gate never blocks movement.
   g.GetComponent<Renderer>().enabled=false; g.GetComponent<Collider>().isTrigger=true;
   var t=g.AddComponent<CourseTrigger>(); t.Race=race; t.Checkpoint=id; t.IsFinish=finish; t.Spawn=new Vector3(0,2,z+1);
   for(int side=-1;side<=1;side+=2) Box(name+" marker",new Vector3(side*5.5f,2,z),new Vector3(.35f,4,.35f),finish?Color.green:Color.cyan);
  }
  RectTransform Rect(string name,Transform parent,Vector2 anchor,Vector2 pos,Vector2 size) {
   var g=new GameObject(name,typeof(RectTransform)); var rt=g.GetComponent<RectTransform>(); rt.SetParent(parent,false); rt.anchorMin=rt.anchorMax=anchor; rt.anchoredPosition=pos; rt.sizeDelta=size; return rt;
  }
  Text Label(string name,Transform parent,string value,Vector2 anchor,Vector2 pos,Vector2 size,int fontSize) {
   var rt=Rect(name,parent,anchor,pos,size); var text=rt.gameObject.AddComponent<Text>(); text.font=font; text.text=value; text.fontSize=fontSize; text.color=Color.white; text.alignment=TextAnchor.MiddleCenter; text.raycastTarget=false; return text;
  }
  Button Button(string name,Transform parent,Vector2 pos,UnityEngine.Events.UnityAction action) {
   var rt=Rect(name,parent,new Vector2(.5f,.5f),pos,new Vector2(300,65)); rt.gameObject.AddComponent<Image>().color=new Color(.05f,.5f,.35f);
   var b=rt.gameObject.AddComponent<Button>(); b.onClick.AddListener(action); Label("Label",rt,name,new Vector2(.5f,.5f),Vector2.zero,new Vector2(300,65),26); return b;
  }
  GameObject Panel(string name,Transform parent,string title,out Text text) {
   var rt=Rect(name,parent,new Vector2(.5f,.5f),Vector2.zero,new Vector2(760,340)); rt.gameObject.AddComponent<Image>().color=new Color(.03f,.05f,.1f,.96f);
   text=Label("Title",rt,title,new Vector2(.5f,.5f),new Vector2(0,65),new Vector2(720,150),28); return rt.gameObject;
  }
  void BuildUI() {
   var canvas=new GameObject("Race UI").AddComponent<Canvas>(); canvas.renderMode=RenderMode.ScreenSpaceOverlay;
   var scale=canvas.gameObject.AddComponent<CanvasScaler>(); scale.uiScaleMode=CanvasScaler.ScaleMode.ScaleWithScreenSize; scale.referenceResolution=new Vector2(1280,720); scale.matchWidthOrHeight=.5f;
   canvas.gameObject.AddComponent<GraphicRaycaster>();
   var events=new GameObject("EventSystem"); events.AddComponent<EventSystem>(); events.AddComponent<InputSystemUIInputModule>();
   race.Status=Label("HUD",canvas.transform,"",new Vector2(.5f,1),new Vector2(0,-35),new Vector2(1200,60),22);
   Text title; race.StartPanel=Panel("Start",canvas.transform,"TOKEN RUN HYBRID\nMoon Launch • Phase 1 prototype\nWASD / arrows + Space, or touch stick + Jump\nCross both blue gates, then reach green. Avoid orange bars.",out title);
   Button("START RACE",race.StartPanel.transform,new Vector2(0,-100),race.Begin);
   race.ResultPanel=Panel("Result",canvas.transform,"",out race.Results); Button("RACE AGAIN",race.ResultPanel.transform,new Vector2(0,-100),race.Begin); race.ResultPanel.SetActive(false);
   var pad=Rect("Touch stick",canvas.transform,Vector2.zero,new Vector2(130,125),new Vector2(150,150)); pad.gameObject.AddComponent<Image>().color=new Color(.1f,.3f,.4f,.7f);
   var knob=Rect("Stick knob",pad,new Vector2(.5f,.5f),Vector2.zero,new Vector2(80,80)); knob.gameObject.AddComponent<Image>().color=Color.cyan;
   var stick=knob.gameObject.AddComponent<OnScreenStick>(); stick.controlPath="<Gamepad>/leftStick"; stick.movementRange=55;
   var jump=Rect("Touch jump",canvas.transform,new Vector2(1,0),new Vector2(-120,115),new Vector2(150,100)); jump.gameObject.AddComponent<Image>().color=new Color(.1f,.6f,.4f,.8f);
   var touch=jump.gameObject.AddComponent<OnScreenButton>(); touch.controlPath="<Gamepad>/buttonSouth";
   Label("Jump label",jump,"JUMP",new Vector2(.5f,.5f),Vector2.zero,new Vector2(150,100),28);
  }
 }
}
