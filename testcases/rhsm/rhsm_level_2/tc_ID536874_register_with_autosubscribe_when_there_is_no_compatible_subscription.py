from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536874_register_with_autosubscribe_when_there_is_no_compatible_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_no_subscription")
                password = self.get_rhsm_cons("password_no_subscription")

                # try to register with auto-attach
                cmd = "subscription-manager register --username=%s --password=%s --auto-attach"%(username, password)
                (ret, output) = self.runcmd(cmd, "try to register with auto-attach")
                if ret != 0 and 'The system has been registered with' in output and 'Not Subscribed' in output and 'Unable to find available subscriptions for all your installed products' in output:
                    logger.info("It's successful to check no auto-attach with register")
                else:
                    raise FailException("Test Failed - Failed to check no auto-attach with register")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
