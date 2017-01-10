"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID180401_unsubscribe_with_wrong_serial_number(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            #list consumed subscriptions
            installedproductname = self.get_rhsm_cons("installedproductname")
            self.list_consumed_subscriptions(installedproductname)
            #Unsubscribe the consumed subscription via the serial number
            cmd="subscription-manager unsubscribe --serial=1234567890"
            (ret, output) = self.runcmd(cmd, "Unsubscribe the consumed subscription via the wrong cert serial number")
            if (ret != 0) and "The entitlement server failed to remove these serial numbers:" in output:
                logging.info("It's successful to check Unsubscribe the consumed subscription via the wrong cert serial number")
            else:
                raise FailException("Test Failed - Failed to check Unsubscribe the consumed subscription via the wrong cert serial number")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_consumed_subscriptions(self, installedproductname):
        cmd="subscription-manager list --consumed"
        (ret,output)=self.runcmd(cmd,"list consumed subscriptions")
        output_join = " ".join(x.strip() for x in output.split())
        if ret == 0 and ((installedproductname in output) or (installedproductname in output_join)):
            logging.info("It's successful to list all consumed subscriptions.")
            return True
        else:
            raise FailException("Test Failed - Failed to list all consumed subscriptions.")

if __name__ == "__main__":
    unittest.main()
