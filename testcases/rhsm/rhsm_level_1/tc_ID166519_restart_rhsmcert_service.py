from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import time

class tc_ID166519_restart_rhsmcert_service(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # set healfrequency = 1
            self.sub_set_healfrequency(1)
            # 1. Unsubscribe the subscription
            self.sub_unsubscribe()
            # 2. refresh the local data
            cmd = 'subscription-manager refresh'
            (ret, output) = self.runcmd(cmd, "reflash")
            if ret == 0  and 'All local data refreshed' in output:    
                logger.info("It's successful to do refresh local data")
            else:
                raise FailException("Test Failed - Failed to do refresh.")
            # 3. Restart the rhsmcertd service
            cmd = 'service rhsmcertd restart'
            self.runcmd(cmd, "restart rhsmcertd")
            # 4. List the consumed
            cmd = 'subscription-manager refresh'
            (ret, output) = self.runcmd(cmd, "refresh rhsmcertd")
            logger.info("Waiting 90 seconds for rhsmcertd service to take effect...")
            time.sleep(90)
            if self.sub_isconsumed(autosubprod):
                logger.info("It's successful to list consumed.")
            else:
                raise FailException("Test Failed - Failed to list consumed.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_set_healfrequency(1440)
            cmd = 'service rhsmcertd restart'
            self.runcmd(cmd, "restart rhsmcertd")
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def sub_set_healfrequency(self, frtime):
        cmd = "subscription-manager config --rhsmcertd.autoattachinterval=%s" % frtime
        (ret, output) = self.runcmd(cmd, "set autoattachinterval")
        if ret == 0:
            logger.info("It successful to set autoattachinterval")
        else:
            logger.error("Test Failed - Failed to set healfrequency or autoattachinterval.")

if __name__ == "__main__":
    unittest.main()
