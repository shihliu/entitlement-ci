from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510154_subscription_type_field_in_list_installed_and_consumed(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            #check subscription type in list available command
            cmd = "subscription-manager list --available | grep 'Subscription Type:'"
            (ret, output) = self.runcmd(cmd, "check subscription type in list available command")
            if ret ==0 and 'Subscription Type:   ' in output:
                logger.info("It's successful to check subscription type in list available command")
            else:
                raise FailException("Test Failed - Failed to check subscription type in list available command")

            #check subscription type in list consumed command
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            cmd = "subscription-manager list --consumed | grep 'Subscription Type:'"
            (ret, output) = self.runcmd(cmd, "check subscription type in list consumed command")
            if ret ==0 and 'Subscription Type:   ' in output:
                logger.info("It's successful to check subscription type in list consumed command")
            else:
                raise FailException("Test Failed - Failed to check subscription type in list consumed command")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
