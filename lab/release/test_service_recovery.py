"""No-cluster tests for startup enablement and reporting-timer lifecycle behavior."""
import contextlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import install_service_recovery as recovery

class RecoveryTests(unittest.TestCase):
 def invoke(self,args,run):
  with patch.object(sys,'argv',['installer',*args]),patch.object(recovery.subprocess,'run',run),contextlib.redirect_stdout(io.StringIO()) as output:recovery.main()
  return output.getvalue()
 def test_plan_is_non_mutating_and_includes_reporting(self):
  def denied(*args,**kw):raise AssertionError('Plan contacted systemctl')
  plan=json.loads(self.invoke([],denied));self.assertEqual(plan['boot_timers'],['iqs-analytics.timer']);self.assertFalse(plan['apply'])
 def test_apply_enables_reporting_once_but_watchdog_preserves_stop(self):
  calls=[]
  with tempfile.TemporaryDirectory() as d,patch.object(recovery,'Path',lambda _:Path(d)):
   self.invoke(['--apply'],lambda args,**kw:calls.append(args))
   self.assertIn(['systemctl','cat','iqs-analytics.timer'],calls)
   enable=next(c for c in calls if c[:3]==['systemctl','enable','--now']);self.assertIn('iqs-analytics.timer',enable)
   self.assertNotIn('iqs-analytics.timer',(Path(d)/'nigeria-portals-recovery.service').read_text())
   self.assertIn('OnUnitActiveSec=60s',(Path(d)/'nigeria-portals-recovery.timer').read_text())
 def test_optional_timer_can_be_omitted(self):
  plan=json.loads(self.invoke(['--timers'],lambda *a,**k:None));self.assertEqual(plan['boot_timers'],[])
 def test_missing_unit_fails_before_writing(self):
  with tempfile.TemporaryDirectory() as d,patch.object(recovery,'Path',lambda _:Path(d)):
   def missing(args,**kw):raise RuntimeError('Missing existing unit')
   with self.assertRaises(RuntimeError):self.invoke(['--apply'],missing)
   self.assertEqual(list(Path(d).iterdir()),[])
 def test_invalid_timer_fails_before_systemctl(self):
  with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):self.invoke(['--timers','bad.service'],lambda *a,**k:self.fail('Invalid unit reached systemctl'))

if __name__=='__main__':unittest.main()
