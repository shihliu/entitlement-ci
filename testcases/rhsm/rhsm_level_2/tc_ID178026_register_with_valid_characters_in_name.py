"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178026_register_with_valid_characters_in_name(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            systemname = 'test56_-.test'
            cmd = "subscription-manager register --username=%s --password='%s' --name=%s" % (username, password, systemname)
            (ret, output) = self.runcmd(cmd, "register with valid character in name")
            if ret == 0:
                if "The system has been registered with ID:" in output:
                    logger.info("It's successful to register with valid character in name.")
                else:
                    raise FailException("Test Failed - The information shown after registered with valid character in name is not correct.")
            else:
                raise FailException("Test Failed - Failed to register with valid system name.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
