from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID190815_import_with_no_options(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # make the system unregistered.
            self.sub_unregister()

            # run subscription-manager import without option.
            cmd = "subscription-manager import"
            (ret, output) = self.runcmd(cmd, "running import command with no options")
            if ret != 0 and "Error: This command requires that you specify a certificate with --certificate." in output :
                logger.info("It's successful to check the error message when run import with no options with unregistered system.")
            else:
                raise FailException("Test Failed - Failed to check the error message when run import with no options with unregistered system.")

            # register to server
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            cmd = "subscription-manager import"
            (ret, output) = self.runcmd(cmd, "running import command with no options")
            if ret != 0 and "Error: You may not import certificates into a system that is registered to a subscription management service." in output :
                logger.info("It's successful to check the error message when run import with no options with registered system.")
            else:
                raise FailException("Test Failed - Failed to check the error message when run import with no options with registered system.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
