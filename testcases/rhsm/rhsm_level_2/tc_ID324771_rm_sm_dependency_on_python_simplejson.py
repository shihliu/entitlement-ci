from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID324771_rm_sm_dependency_on_python_simplejson(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "rpm --query --requires python-rhsm --verbose | grep 'python-simplejson'"
            (ret, output) = self.runcmd(cmd, "check dependency on python-simplejson")
            if ret != 0 and 'python-simplejson' not in output:
                logger.info("It's successful to check dependency on python-simplejson")
            else:
                raise FailException("Test Failed - Failed to check dependency on python-simplejson.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()