using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
namespace TokenRun.Editor {
 public static class ProjectSetup {
  [MenuItem("Token Run/Configure Phase 1")]
  public static void Configure() {
   var settings=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
   settings.FindProperty("activeInputHandler").intValue=1; settings.ApplyModifiedPropertiesWithoutUndo();
   PlayerSettings.companyName="Token Run"; PlayerSettings.productName="Token Run Hybrid";
   PlayerSettings.defaultInterfaceOrientation=UIOrientation.LandscapeLeft;
   PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel26;
   PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
   PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
   PlayerSettings.SetApplicationIdentifier(UnityEditor.Build.NamedBuildTarget.Android,"com.tokenrun.hybrid");
   const string path="Assets/TokenRun/Materials/MobilePipeline.asset";
   var pipeline=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(path);
   if(!pipeline) {
    var data=ScriptableObject.CreateInstance<UniversalRendererData>(); AssetDatabase.CreateAsset(data,"Assets/TokenRun/Materials/MobileRenderer.asset");
    pipeline=UniversalRenderPipelineAsset.Create(data); AssetDatabase.CreateAsset(pipeline,path);
    pipeline.renderScale=.85f; pipeline.msaaSampleCount=2; pipeline.shadowDistance=25;
   }
   GraphicsSettings.defaultRenderPipeline=pipeline; QualitySettings.renderPipeline=pipeline;
   EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene("Assets/TokenRun/Scenes/MoonLaunch.unity",true)};
   if(!AssetDatabase.IsValidFolder("Assets/TokenRun/Resources")) AssetDatabase.CreateFolder("Assets/TokenRun","Resources");
   if(!AssetDatabase.LoadAssetAtPath<Material>("Assets/TokenRun/Resources/PrototypeMaterial.mat")) AssetDatabase.CreateAsset(new Material(Shader.Find("Universal Render Pipeline/Lit")),"Assets/TokenRun/Resources/PrototypeMaterial.mat");
   RunnerVisualSetup.Configure();
   AssetDatabase.SaveAssets(); Debug.Log("Phase 1 configured. Restart Editor if input backend changed.");
  }
  public static void BuildWeb() { Configure(); Build("Builds/Web",BuildTarget.WebGL); }
  // Unity Build Automation pre-export hook; UBA owns the actual BuildPlayer call.
  public static void PrepareCloudBuild() {
   Configure();
   if(EditorUserBuildSettings.activeBuildTarget==BuildTarget.WebGL)
    PlayerSettings.WebGL.decompressionFallback=true;
   AssetDatabase.SaveAssets();
   Debug.Log("Cloud setup completed. This is configuration, not a successful build or test result.");
  }
  public static void BuildAndroid() { Configure(); Build("Builds/Android/TokenRun.apk",BuildTarget.Android); }
  static void Build(string path,BuildTarget target) {
   System.IO.Directory.CreateDirectory(target==BuildTarget.Android?System.IO.Path.GetDirectoryName(path):path);
   var report=BuildPipeline.BuildPlayer(EditorBuildSettings.scenes,path,target,BuildOptions.None);
   if(report.summary.result!=UnityEditor.Build.Reporting.BuildResult.Succeeded) throw new System.Exception("Build failed: "+report.summary.result);
  }
 }
}
