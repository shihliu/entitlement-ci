from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537186_verify_the_compliance_message_of_unregistered_system(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # check installed status
            cmd = 'subscription-manager list --installed | grep -E "Status:|Status Details:"'
            (ret, output) = self.runcmd(cmd, "check output info")
            installed_out = output.strip().split('\n')
            if ret == 0 and installed_out[0] == 'Status:         Unknown' and installed_out[1] == 'Status Details:':
                logger.info("It's successful to check compliance msg from installed info")
            else:
                raise FailException("Test Failed - Failed to check compliance msg from installed info")

            # check status
            cmd = 'subscription-manager status'
            (ret, output) = self.runcmd(cmd, "check output info")
            if ret == 0 and 'Overall Status: Unknown' in output:
                logger.info("It's successful to check compliance msg from status info")
            else:
                raise FailException("Test Failed - Failed to check compliance msg from status info")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
