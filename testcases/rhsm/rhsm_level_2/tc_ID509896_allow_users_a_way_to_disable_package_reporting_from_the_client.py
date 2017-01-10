from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509896_allow_users_a_way_to_disable_package_reporting_from_the_client(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "grep report_package_profile /etc/rhsm/rhsm.conf"
            (ret, output) = self.runcmd(cmd, "check report pkg profile")
            if ret == 0 and output.strip() == 'report_package_profile = 1':
                logger.info("It's successful to check report pkg profile")
            else:
                raise FailException("Test Failed - Failed to check report pkg profile")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
