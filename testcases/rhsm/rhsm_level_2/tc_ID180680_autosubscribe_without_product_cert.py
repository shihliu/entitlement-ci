"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID180680_autosubscribe_without_product_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Move the product cert to other dir
            cmd = "mv /etc/pki/product-default/*  /etc/pki/"
            (ret, output) = self.runcmd(cmd, "Move the product cert to other dir")    
            if ret == 0:
                logger.info(" It's successful to move the product cert.")
            else:
                raise FailException("Test Failed - Failed to move the product cert to other dir.")
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.check_autosub_result(autosubprod)
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
            self.move_back_cert()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_autosub_result(self, autosubprod):
        cmd = "subscription-manager subscribe --auto"
        (ret, output) = self.runcmd(cmd, "check auto-subscribe result")
        if ret != 0:
            if "No Installed products on system. No need to attach subscriptions." in output:
                logger.info("It's successful to check no need to update subscription for RHEL5 system.")
            elif ("Product Name:" not in output) and (autosubprod not in output):
                logger.info("It's successful to check no need to update subscription for RHEL6 system.")
        else:
            raise FailException("Test Failed - check no need to update subscription.")

    def move_back_cert(self):
        # Move the product cert back to /etc/pki/product
        cmd = "mv /etc/pki/*.pem  /etc/pki/product-default/"
        (ret, output) = self.runcmd(cmd, "Move the product cert back to the right dir")    
        if ret == 0:
            logger.info(" It's successful to move the product cert back.")
        else:
            raise FailException("Test Failed - Failed to move the product cert back.")

if __name__ == "__main__":
    unittest.main()
