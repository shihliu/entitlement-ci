#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509911_Core_and_RAM_limit_info_should_be_added_to_the_entitlement_certs(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            cmd = "ls /etc/pki/entitlement/ |grep -v 'key'"
            (ret, output) = self.runcmd(cmd, "list the entitlement cert")
            if ret == 0 and output :
                entcert = output
                entcert = entcert.strip().lstrip().rstrip('\n')
                logger.info("entitlement cert is listed")
            else:
                raise FailException("Test Failed - no entitlement cert found")

            cmd = "rct cat-cert /etc/pki/entitlement/%s | grep -A16 Order:" %entcert
            (ret, output) = self.runcmd(cmd, "use rct tool to check the entitlement cert")
            if ret == 0 and ( "Core Limit:"  in output) and ("RAM Limit:" in output):
                logger.info("Core and RAM limit info is added to the entitlement cert")
            else:
                raise FailException("Test Failed - Core and RAM limit info is added to the entitlement cert")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
