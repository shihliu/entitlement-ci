from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537363_request_for_new_sub_man_list_consumed_field_called_subscription_type(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # check sub-type field in list available
            cmd = "subscription-manager list --available | grep 'Subscription Type:'"
            (ret, output) = self.runcmd(cmd, "check sub-type field in list available")
            if ret == 0 and 'Subscription Type:' in output:
                logger.info("It's successful to check sub-type field in list available")
            else:
                raise FailException("Test Failed - Failed to check sub-type field in list available")

            # check sub-type field in list consumed
            cmd = "subscription-manager list --consumed | grep 'Subscription Type:'"
            (ret, output) = self.runcmd(cmd, "check sub-type field in list consumed")
            if ret == 0 and 'Subscription Type:' in output:
                logger.info("It's successful to check sub-type field in list consumed")
            else:
                raise FailException("Test Failed - Failed to check sub-type field in list consumed")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
