from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID330289_request_for_list_consumed_field_subscription_type(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # list available subscriptions and check the subscription type
            cmd = "subscription-manager list --available | grep 'Subscription Type'| sort | uniq"
            (ret, output) = self.runcmd(cmd, "check the subscription type for list available")
            if ret == 0 and "Subscription Type:" in output:
                logger.info("It's successful to check the subscription type for list available.") 
            else:
                raise FailException("Test Failed - Failed to check the subscription type for list available.")
            # auto-attach
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # list consumed subscriptions and check the subscription type
            cmd = " subscription-manager list --consumed | grep 'Subscription Type'| sort | uniq"
            (ret, output) = self.runcmd(cmd, "check the subscription type for list consumed")
            if ret == 0 and "Subscription Type:" in output:
                logger.info("It's successful to check the subscription type for list consumed.") 
            else:
                raise FailException("Test Failed - Failed to check the subscription type for list consumed.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
