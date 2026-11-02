using NUnit.Framework;
namespace TokenRun.Tests {
 public sealed class RaceStateTests {
  [TestCase(-1f)] [TestCase(float.NaN)] [TestCase(float.PositiveInfinity)]
  public void RejectsInvalidTime(float dt) { Assert.Throws<System.ArgumentOutOfRangeException>(()=>new RaceState().Tick(dt)); }
  [Test] public void TimerOnlyRunsDuringRace() { var r=new RaceState(); r.Tick(2); Assert.AreEqual(0,r.Seconds); r.Start(); r.Tick(3); Assert.AreEqual(3,r.Seconds); r.Reach(1); r.Reach(2); Assert.IsTrue(r.Finish(2)); r.Tick(10); Assert.AreEqual(3,r.Seconds); }
  [Test] public void CannotSkipOrRepeatCheckpoints() { var r=new RaceState(); r.Start(); Assert.IsFalse(r.Reach(2)); Assert.IsFalse(r.Finish(2)); Assert.IsTrue(r.Reach(1)); Assert.IsFalse(r.Reach(1)); Assert.IsTrue(r.Reach(2)); Assert.IsTrue(r.Finish(2)); }
  [Test] public void RestartClearsPreviousRun() { var r=new RaceState(); r.Start(); r.Tick(7); r.Reach(1); r.Respawn(); r.Start(); Assert.AreEqual(0,r.Seconds); Assert.AreEqual(0,r.Checkpoint); Assert.AreEqual(0,r.Respawns); Assert.IsFalse(r.Finished); }
  [Test] public void RespawnPreservesProgressAndTime() { var r=new RaceState(); r.Start(); r.Reach(1); r.Tick(4); r.Respawn(); Assert.AreEqual(1,r.Checkpoint); Assert.AreEqual(4,r.Seconds); Assert.AreEqual(1,r.Respawns); }
 }
}
