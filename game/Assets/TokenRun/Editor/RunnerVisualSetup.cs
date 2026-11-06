using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace TokenRun.Editor {
 public static class RunnerVisualSetup {
  const string Art="Assets/TokenRun/Art/Runner/";
  const string ResourcesPath="Assets/TokenRun/Resources/";
  const string ControllerPath=ResourcesPath+"Runner.controller";

  [MenuItem("Token Run/Configure Animated Runner")]
  public static void Configure() {
   Folder("Assets/TokenRun","Resources");
   Folder("Assets/TokenRun/Materials","Runner");
   string basePath=Art+"Runner.fbx";
   ImportModel(basePath,false,null,null);
   var source=AssetDatabase.LoadAssetAtPath<GameObject>(basePath);
   if(!source) throw new InvalidOperationException("Runner FBX did not import: "+basePath);
   var avatar=AssetDatabase.LoadAllAssetsAtPath(basePath).OfType<Avatar>().FirstOrDefault();
   if(!avatar || !avatar.isValid) throw new InvalidOperationException("Runner Generic Avatar is invalid.");
   var clips=new AnimationClip[3];
   string[] names={"Idle","Run","Jump"};
   float[] lengths={2,.8f,1};
   for(int i=0;i<names.Length;i++) {
    string path=Art+names[i]+".fbx";
    ImportModel(path,true,avatar,names[i]);
    clips[i]=AssetDatabase.LoadAllAssetsAtPath(path).OfType<AnimationClip>().SingleOrDefault(c=>c.name==names[i]);
    if(!clips[i] || Mathf.Abs(clips[i].length-lengths[i])>.08f)
     throw new InvalidOperationException("Missing or incorrectly timed runner clip: "+path);
   }
   var controller=AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
   if(!controller) controller=AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
   var stateMachine=controller.layers[0].stateMachine;
   // Update the three generated states in place so repeated setup retains asset GUIDs.
   for(int i=0;i<names.Length;i++) {
    var state=stateMachine.states.Select(s=>s.state).FirstOrDefault(s=>s.name==names[i]);
    if(!state) state=stateMachine.AddState(names[i],new Vector3(250,50+i*70,0));
    state.motion=clips[i]; state.speed=i==2?0:1;
    state.writeDefaultValues=true;
    if(i==0) stateMachine.defaultState=state;
   }
   EditorUtility.SetDirty(controller);
   // Keep facing/ground correction outside the FBX animation binding hierarchy.
   var visual=new GameObject("Animated runner");
   try {
    var model=(GameObject)PrefabUtility.InstantiatePrefab(source);
    model.transform.SetParent(visual.transform,false);
    visual.transform.position=Vector3.zero;
    visual.transform.rotation=Quaternion.identity;
    visual.transform.localScale=Vector3.one;
    var animator=model.GetComponent<Animator>();
    if(!animator) animator=model.AddComponent<Animator>();
    animator.avatar=avatar;
    animator.runtimeAnimatorController=controller;
    animator.applyRootMotion=false;
    animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
    // Feet identify the actual imported forward axis; avoid an assumed FBX rotation.
    var transforms=visual.GetComponentsInChildren<Transform>();
    var foot=transforms.FirstOrDefault(t=>t.name=="Foot.L");
    var toes=transforms.FirstOrDefault(t=>t.name=="Toes.L");
    if(!foot || !toes) throw new InvalidOperationException("Imported runner is missing foot bones.");
    var forward=Vector3.ProjectOnPlane(toes.position-foot.position,Vector3.up);
    if(forward.sqrMagnitude<.0001f) throw new InvalidOperationException("Could not determine runner facing direction.");
    visual.transform.rotation=Quaternion.FromToRotation(forward.normalized,Vector3.forward);
    var renderers=visual.GetComponentsInChildren<SkinnedMeshRenderer>();
    if(renderers.Length!=26) throw new InvalidOperationException("Expected 26 skinned runner meshes.");
    var bounds=renderers[0].bounds;
    foreach(var r in renderers) {
     bounds.Encapsulate(r.bounds);
     var palette=r.sharedMaterials.Select(MaterialFor).ToArray();
     r.sharedMaterials=palette;
     // A padded skinned bound avoids disappearing limbs during the authored clips.
     var b=r.localBounds; b.Expand(1f); r.localBounds=b;
    }
    if(bounds.size.y<1.8f || bounds.size.y>2.2f)
     throw new InvalidOperationException("Runner FBX import scale is incorrect: "+bounds.size.y);
    // Keep model root at ground level; preserve its reference and animation hierarchy.
    visual.transform.position-=Vector3.up*bounds.min.y;
    if(!model.GetComponent<RunnerAnimation>()) model.AddComponent<RunnerAnimation>();
    if(!PrefabUtility.SaveAsPrefabAsset(visual,ResourcesPath+"RunnerVisual.prefab"))
     throw new InvalidOperationException("Could not save runner prefab.");
   } finally { UnityEngine.Object.DestroyImmediate(visual); }
   AssetDatabase.SaveAssets();
   Debug.Log("Animated runner configured: Generic rig, Idle/Run loops, physics-sampled airborne Jump, URP palette.");
  }

  static void ImportModel(string path,bool animate,Avatar avatar,string clipName) {
   AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);
   var importer=AssetImporter.GetAtPath(path) as ModelImporter;
   if(!importer) throw new InvalidOperationException("Missing runner source asset: "+path);
   importer.animationType=ModelImporterAnimationType.Generic;
   importer.avatarSetup=avatar?ModelImporterAvatarSetup.CopyFromOther:ModelImporterAvatarSetup.CreateFromThisModel;
   importer.sourceAvatar=avatar;
   importer.importAnimation=animate;
   importer.optimizeGameObjects=false;
   importer.addCollider=false;
   importer.animationCompression=ModelImporterAnimationCompression.Off;
   importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
   importer.SaveAndReimport();
   var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
   var root=model.GetComponentsInChildren<Transform>().FirstOrDefault(t=>t.name=="Root");
   if(!root) throw new InvalidOperationException("Runner motion root is missing in "+path);
   importer.motionNodeName=AnimationUtility.CalculateTransformPath(root,model.transform);
   importer.SaveAndReimport();
   if(!animate) return;
   var definitions=importer.defaultClipAnimations;
   if(definitions.Length!=1) throw new InvalidOperationException("Expected exactly one take in "+path);
   var definition=definitions[0];
   definition.name=clipName;
   definition.loopTime=clipName!="Jump";
   definition.loopPose=false;
   definition.keepOriginalOrientation=true;
   definition.keepOriginalPositionXZ=true;
   definition.keepOriginalPositionY=true;
   importer.clipAnimations=new[]{definition};
   importer.SaveAndReimport();
  }

  static Material MaterialFor(Material imported) {
   if(!imported) throw new InvalidOperationException("Runner has an empty material slot.");
   string name=imported.name.Replace('_',' ').ToLowerInvariant();
   string key; Color color; float smoothness=.4f;
   if(name.StartsWith("navy")) {key="Navy";color=new Color(.025f,.04f,.095f);}
   else if(name.StartsWith("teal")) {key="Teal";color=new Color(.008f,.43f,.44f);}
   else if(name.StartsWith("orange")) {key="Orange";color=new Color(1,.24f,.008f);}
   else if(name.StartsWith("visor")) {key="Visor";color=new Color(.012f,.018f,.035f);smoothness=.8f;}
   else if(name.StartsWith("light soles")) {key="Soles";color=new Color(.72f,.77f,.79f);}
   else if(name.StartsWith("face")) {key="Face";color=new Color(.72f,.37f,.18f);}
   else throw new InvalidOperationException("Unrecognized runner material: "+imported.name);
   string path="Assets/TokenRun/Materials/Runner/"+key+".mat";
   var material=AssetDatabase.LoadAssetAtPath<Material>(path);
   var shader=Shader.Find("Universal Render Pipeline/Lit");
   if(!shader) throw new InvalidOperationException("URP Lit shader is unavailable.");
   if(!material) {material=new Material(shader);AssetDatabase.CreateAsset(material,path);}
   material.shader=shader;
   material.SetColor("_BaseColor",color);
   material.SetFloat("_Smoothness",smoothness);
   EditorUtility.SetDirty(material);
   return material;
  }

  static void Folder(string parent,string name) {
   if(!AssetDatabase.IsValidFolder(parent+"/"+name)) AssetDatabase.CreateFolder(parent,name);
  }
 }
}
