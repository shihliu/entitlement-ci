"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID178051_register_with_invalid_username_and_password(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            invalidpassword = "test"
            if password == invalidpassword:
                logger.info("the invalid password happens to be a valid password, please choose another invalid password!")
            else:
                cmd = "subscription-manager register --username=%s --password='%s'" % (username, invalidpassword)
                (ret, output) = self.runcmd(cmd, "register with invalid username and password")
                if ret != 0:
                    if ("Invalid credentials" in output):
                        logger.info("It's successful to verify that invalid password can not be used to register.")
                    else:
                        raise FailException("Test Failed - The information shown after registeration with invalid username and password is not correct.")
                else:
                    raise FailException("Test Failed - Failed to verify registering with invalid username and password.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
