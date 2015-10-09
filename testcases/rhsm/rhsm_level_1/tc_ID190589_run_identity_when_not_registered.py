from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID190589_run_identity_when_not_registered(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # use identity command to show where system is registerd to
            cmd = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd, "running identity command")
            if ret != 0 and ("This system is not yet registered. Try 'subscription-manager register --help' for more information." in output):
                logger.info("It's successful to check the output of identity command when the machine is not registered.")
            else:
                raise FailException("Test Failed - Failed to check the output of identity command when the machine is not registered.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
