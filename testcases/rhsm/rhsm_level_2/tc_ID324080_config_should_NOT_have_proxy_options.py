from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID324080_config_should_NOT_have_proxy_options(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "subscription-manager config --help | grep -A1 -- --proxy"
            (ret, output) = self.runcmd(cmd, "check proxy option")
            if ret != 0 and 'proxy' not in output:
                logger.info("It's successful to check config should NOT have proxy options")
            else:
                raise FailException("Test Failed - Failed to check config should NOT have proxy options.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
