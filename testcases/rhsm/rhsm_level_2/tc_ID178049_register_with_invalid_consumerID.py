"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID178049_register_with_invalid_consumerID(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # clean client data
            cmd_clean = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd_clean, "clean client data")
            if (ret == 0) and ("All local data removed" in output):
                logger.info("It's successful to run subscription-manager clean")
            else:
                raise FailException("Test Failed - error happened when run subscription-manager clean")
            # register with invalid consumerid
            cmd_register = "subscription-manager register --username=%s --password='%s' --consumerid=1234567890" % (username, password)
            (ret, output) = self.runcmd(cmd_register, "register with invalid consumerid")
            if (ret != 0) and ("Consumer with id 1234567890 could not be found" in output):
                logger.info("It's successful to verify that registeration with invalid consumerid should not succeed")
            else:
                raise FailException("Test Failed - error happened when register with invalid consumerid")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
