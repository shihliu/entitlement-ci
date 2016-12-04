'''
@author            :soliu@redhat.com
@date              :2013-03-12
'''

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189250_facts_update_after_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            cmd_system_entitlement = "subscription-manager facts --list|grep system.entitlement"
            # step1:check its value of system.entitlements
            (ret, output) = self.runcmd(cmd_system_entitlement, "list system entilement")
            if ret == 0:
                if "system.entitlements_valid: invalid" in output:
                    logger.info("It is successful to check the value of system.entitlement after register!")
                else:
                    raise FailException("Failed to check the value of system.entitlement after register!")
            # step2:auto-subscribe
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # step3:re-check the value of system.entitlements_valid
            (ret, output) = self.runcmd(cmd_system_entitlement, "list system entilement")
            if ret == 0:
                if "system.entitlements_valid: valid" in output:
                    logger.info("It is successful to test facts update after subscription!")
                else:
                    raise FailException("Failed to test facts update after subscription!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
