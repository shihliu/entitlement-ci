'''
@author           :soliu@redhat.com
@date             :2013-03-12
'''

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID189251_facts_update_after_unsubscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # step1:check the value of system.entitlements_valid
            cmd_system_entitlement = "subscription-manager facts --list|grep system.entitlement"
            (ret, output) = self.runcmd(cmd_system_entitlement, "list system entilement")
            if ret == 0:
                if "system.entitlements_valid: valid" in output:
                    logger.info("It is successful to check the value of system.entitlements after consume product!")
                else:
                    raise FailException("Failed to check the value of system.entitlements after consume product!")
            # step2:un-subscribe all products
            self.sub_unsubscribe()
            # step3:re-check the value of system.entitlements_valid
            (ret, output) = self.runcmd(cmd_system_entitlement, "list system entilement")
            if ret == 0:
                if "system.entitlements_valid: invalid" in output:
                    logger.info("It is successful to test the facts update after unsubscription!")
                else:
                    raise FailException("Failed to test the facts update after unsubscription!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()