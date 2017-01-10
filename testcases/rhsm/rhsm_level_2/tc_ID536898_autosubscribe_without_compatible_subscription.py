from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536898_autosubscribe_without_compatible_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_no_subscription")
                password = self.get_rhsm_cons("password_no_subscription")
                self.sub_register(username, password)

                # try to auto-attach
                cmd = "subscription-manager attach"
                (ret, output) = self.runcmd(cmd, "try to auto-attach")
                if ret != 0 and 'Not Subscribed' in output and 'Unable to find available subscriptions for all your installed products.' in output:
                    logger.info("It's successful to check no auto-attach")
                else:
                    raise FailException("Test Failed - Failed to check no auto-attach")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
