"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178036_register_when_registered(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            cmd = "subscription-manager register --username=%s --password='%s'" % (username, password)
            (ret, output) = self.runcmd(cmd, "register second time")
            if ret != 0 and "This system is already registered" in output:
                logger.info("It's successful to verify that re-register the second time.")
            else:
                raise FailException("Test Failed - The information shown after second registered is not correct.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
