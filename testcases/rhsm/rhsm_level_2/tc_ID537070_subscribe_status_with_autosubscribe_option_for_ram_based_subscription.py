from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537070_subscribe_status_with_autosubscribe_option_for_ram_based_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # check status before register
                status1 = self.check_installed_status()
                if status1 == 'Unknown':
                    logger.info("It's successful to check installed status before register")
                else:
                    raise FailException("Test Failed - Failed to check installed status before register")

                # Register
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
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
                status1 = self.check_installed_status()
                if status1 == 'Not Subscribed':
                    logger.info("It's successful to check installed status before autoattach")
                else:
                    raise FailException("Test Failed - Failed to check installed status before autoattach")

                #auto-attach
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                status1 = self.check_installed_status()
                if status1 == 'Subscribed':
                    logger.info("It's successful to check installed status before autoattach")
                else:
                    raise FailException("Test Failed - Failed to check installed status before autoattach")

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
