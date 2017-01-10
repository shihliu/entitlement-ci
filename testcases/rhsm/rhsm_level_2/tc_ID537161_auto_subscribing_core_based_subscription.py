from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537161_auto_subscribing_core_based_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_core")
                password = self.get_rhsm_cons("password_core")
                self.sub_register(username, password)
                # disable autoheal
                self.disable_autoheal()
                #remove subscription
                cmd = 'subscription-manager remove --all'
                (ret, output) = self.runcmd(cmd, "rmove subscription ")
                if ret == 0 and 'removed at the server' in output:
                    logger.info("It's successful to remove subscription")
                else:
                    raise FailException("Test Failed - Failed to remove subscription")
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.enable_autoheal()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
