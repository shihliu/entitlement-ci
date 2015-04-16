from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID166458_unregister_when_system_is_not_register(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            if self.sub_isregistered():
                self.sub_unregister()
            cmd = 'subscription-manager unregister'
            (ret, output) = self.runcmd(cmd, "unregister when system is not registered")
            if ret == 1 and 'This system is currently not registered' in output:
                logger.info("Test Successful - It's successful to verify unregister command when system is not registered.")
            else:
                raise FailException("Test Failed - Failed to verify unregister command when system is not registered.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()


 
