from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID330263_Trim_trailing_whitespace_from_username_when_registering(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            # register with space on the back of username
            username1 = username + ' '
            cmd = "subscription-manager register --force --username='%s' --password=%s" % (username1, password)
            (ret, output) = self.runcmd(cmd, "register with space on the back of username")
            if ret == 0 and "The system has been registered with ID" in output:
                logger.info("It's successful to with space on the back of username.") 
            else:
                raise FailException("Test Failed - Failed to with space on the back of username.")
            # register with space on the front of username
            username2 = ' ' + username
            cmd = "subscription-manager register --force --username='%s' --password=%s" % (username2, password)
            (ret, output) = self.runcmd(cmd, "register with space on the front of username")
            if ret == 0 and "The system has been registered with ID" in output:
                logger.info("It's successful to with space on the back of username.") 
            else:
                raise FailException("Test Failed - Failed to with space on the front of username.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
