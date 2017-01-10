from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536920_set_a_wrong_servicelevel_in_cli(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_satellite_check():
            try:
                # Register
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)

                # Set wrong servicelevel
                cmd = "subscription-manager service-level --set=wrong"
                (ret, output) = self.runcmd(cmd, "set wrong servicelevel")
                if ret != 0 and "Service level 'wrong' is not available to" in output:
                    logger.info("It's successful to check enable set wrong servicelevel")
                else:
                    raise FailException("Test Failed - Failed to check set wrong servicelevel")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
