"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID183422_list_installed_product(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # list installed products
            installedproductname = self.get_rhsm_cons("installedproductname")
            cmd = "subscription-manager list --installed"
            (ret, output) = self.runcmd(cmd, "list installed products")
            if ret == 0 and installedproductname in output:
                logger.info("It's successful to list installed product %s." % (installedproductname))
                return True            
            else:
                raise FailException("Test Failed - The product %s is not installed." % (installedproductname))
                return False
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
