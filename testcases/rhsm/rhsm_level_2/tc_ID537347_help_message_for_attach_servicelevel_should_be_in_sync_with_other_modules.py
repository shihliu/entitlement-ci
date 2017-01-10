from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537347_help_message_for_attach_servicelevel_should_be_in_sync_with_other_modules(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            #1 Check servicelevel description in attach help
            cmd = "subscription-manager attach --help | grep 'servicelevel' -A3"
            (ret, output) = self.runcmd(cmd, "check servicelevel description in attach help")
            if ret == 0 and '--servicelevel=SERVICE_LEVEL' in output and 'Automatically attach only subscriptions matching the' in output and 'specified service level; only used with --auto' in output:
                logger.info("It's successful to check servicelevel description in attach help")
            else:
                raise FailException("Test Failed - Failed to check servicelevel description in attach help")

            #2 Check servicelevel usage in when attaching
            cmd = "subscription-manager attach --pool 8ac6a3a241bae96a0141baea35901305 --servicelevel premium"
            (ret, output) = self.runcmd(cmd, "check servicelevel usage in when attaching")
            if ret != 0 and output.strip() == 'Error: The --servicelevel option cannot be used when specifying pools.':
                logger.info("It's successful to check servicelevel usage when attaching")
            else:
                raise FailException("Test Failed - Failed to check servicelevel usage when attaching")

            #3 Check servicelevel description in register help
            cmd = "subscription-manager register --help | grep servicelevel -A3"
            (ret, output) = self.runcmd(cmd, "check servicelevel description in attach help")
            if ret == 0 and '--servicelevel=SERVICE_LEVEL' in output and 'system preference used when subscribing automatically,' in output and 'requires --auto-attach' in output:
                logger.info("It's successful to check servicelevel description in register help")
            else:
                raise FailException("Test Failed - Failed to check servicelevel description in register help")

            #4 Check servicelevel description when using --org
            cmd = "subscription-manager attach --help | grep 'servicelevel' -A3"
            (ret, output) = self.runcmd(cmd, "check servicelevel description when using --org")
            if ret == 0 and '--servicelevel=SERVICE_LEVEL' in output and 'Automatically attach only subscriptions matching the' in output and 'specified service level; only used with --auto' in output:
                logger.info("It's successful to check servicelevel description when using --org")
            else:
                raise FailException("Test Failed - Failed to check servicelevel description when using --org")

            #5 Check --org in servicelevel man page
            cmd = "subscription-manager service-level --help | grep org -A3"
            (ret, output) = self.runcmd(cmd, "check --org in servicelevel man page")
            if ret == 0 and '--org=ORG_KEY         specify an organization when listing available service' in output and 'levels using the organization key, only used with' in output and '--list' in output:
                logger.info("It's successful to check servicelevel description in register help")
            else:
                raise FailException("Test Failed - Failed to check --org in servicelevel man page")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
