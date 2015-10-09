from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID327125_help_message_for_attach_servicelevel_should_be_in_sync_with_other_modules(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # attach and service-level help msg
            cmd = "subscription-manager attach --help | grep 'servicelevel' -A3"
            (ret, output) = self.runcmd(cmd, "check help message for attach servicelevel")
            if ret == 0 and 'service level to apply to this system, requires --auto' in output:
                logger.info("It's successful to check help message for attach servicelevel")
            else:
                raise FailException("Test Failed - Failed to check help message for attach servicelevel")
            # attach with pool and service level
            cmd = "subscription-manager attach --pool 8ac6a3a241bae96a0141baea35901305 --servicelevel premium"
            (ret, output) = self.runcmd(cmd, "check help message for attach servicelevel")
            if ret != 0 and 'Error: Must use --auto with --servicelevel' in output:
                logger.info("It's successful to check attach with pool and service level")
            else:
                raise FailException("Test Failed - Failed to check attach with pool and service level")
            # register and service-level help msg
            cmd = "subscription-manager register --help | grep servicelevel -A3"
            (ret, output) = self.runcmd(cmd, "check register and service-level help msg")
            if ret == 0 and 'system preference used when subscribing automatically' in output and "requires --auto-attach" in output:
                logger.info("It's successful to check register and service-level help msg")
            else:
                raise FailException("Test Failed - Failed to check register and service-level help msg")
            # service-level with org
            cmd = "subscription-manager service-level --org=admin"
            (ret, output) = self.runcmd(cmd, "check service-level with org")
            if ret != 0 and 'Error: --org is only supported with the --list option' in output:
                logger.info("It's successful to check service-level with org")
            else:
                raise FailException("Test Failed - Failed to check service-level with org")
            # service-level and org help
            cmd = "subscription-manager service-level --help | grep org -A3"
            (ret, output) = self.runcmd(cmd, "check register and service-level help msg")
            if ret == 0 and 'specify an organization when listing available service' in output and "levels using the organization key, only used with" in output and "--list" in output:
                logger.info("It's successful to check service-level and org help")
            else:
                raise FailException("Test Failed - Failed to check service-level and org help")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
