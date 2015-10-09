"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID181220_import_invaild_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # create invaild pem file
            cmd = "touch /root/testinvalid.pem"
            (ret, output) = self.runcmd(cmd, "create invalid pem file")    
            if ret == 0:
                logger.info(" It's successful to create invalid pem file.")
            else:
                raise FailException("Test Failed - Failed to create invalied pem file.")
            # import the invaild pem file
            cmd = "subscription-manager import --certificate=/root/testinvalid.pem"
            (ret, output) = self.runcmd(cmd, "import invalid pem file")
            if ret != 0 and "not a valid certificate file" in output:
                logger.info("It's successful to check import invalid cert file.")
            else:
                raise FailException("Test Failed - Failed to check import invalid cert file.")
            # list consumed subscriptions
            cmd = "subscription-manager list --consumed"
            (ret, output) = self.runcmd(cmd, "list consumed subscriptions")  
            if (ret == 0) and ("No consumed subscription pools" in output):
                logger.info("It's successful to check consumed subscriptions.")
            else:
                raise FailException("Test Failed - Failed to check consumed subscriptions.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
