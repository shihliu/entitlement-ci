"""******************************************

@author		: shihliu@redhat.com
@date		: 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID180671_subscribe_bogus_pool(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # Subscribe to a bogus pool ID
            cmd = "subscription-manager subscribe --pool=1234567890"
            (ret, output) = self.runcmd(cmd, "Subscribe to a bogus pool ID 1234567890")
            # if ret != 0 and "Subscription pool 1234567890 does not exist" in output :
            if ret != 0 and "Pool with id 1234567890 could not be found" in output :
                logger.info("It's successful to check subscribe to a bogus pool ID")
            else:
                raise FailException("Test Failed - Failed to check Subscribe to a bogus pool ID")
            # Check the entitlement cert
            cmd = "ls -l /etc/pki/entitlement"
            (ret, output) = self.runcmd(cmd, "Check the entitlement cert")
            if (ret == 0 and "total 0" in output):
                logger.info("It's successful to Check the entitlement cert--no file")
            else:
                raise FailException("Test Failed - Failed to Check the entitlement cert--has file")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
