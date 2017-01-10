from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537303_exceptions_valueerror_object_has_no_attribute_msg_with_clean_command(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Disable invalid repo
            cmd = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd, "clean local data")
            if ret == 0 and output.strip() == 'All local data removed':
                logger.info("It's successful to check no error when clean local data")
            else:
                raise FailException("Test Failed - Failed to check no error when clean local data")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
