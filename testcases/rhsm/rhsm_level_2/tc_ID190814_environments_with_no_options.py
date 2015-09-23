from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190814_environments_with_no_options(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            samhostip = get_exported_param("SERVER_IP")
            cmd = "subscription-manager environments --username=%s --password=%s" % (username, password)
            (ret, output) = self.runcmd(cmd, "running environments command with no options")
            if samhostip != None and ret == 69 and "Error: Server does not support environments" in output:
                logger.info("It's successful to verify that SAM does not support environments")
            elif ret != 0 and "Error: This command requires that you specify an organization with --org" in output :
                logger.info("It's successful to check the error message when run environments with no options.")
            else:
                raise FailException("Test Failed - Failed to check the error message when run environments with no options.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
