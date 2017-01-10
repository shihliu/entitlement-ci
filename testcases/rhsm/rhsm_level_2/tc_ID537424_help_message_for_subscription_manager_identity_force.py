from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537424_help_message_for_subscription_manager_identity_force(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Specify incorrect "--serverurl" to register the system.
            cmd = "subscription-manager identity --help | grep force -A1"
            (ret, output) = self.runcmd(cmd, "check registration with specified wrong serverurl")
            if ret == 0 and output.strip() == '--force               force certificate regeneration (requires username and\n                        password); Only used with --regenerate':
                logger.info("It's successful to check registration with specified wrong serverurl")
            else:
                raise FailException("Test Failed - Failed to check registration with specified wrong serverurl")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
