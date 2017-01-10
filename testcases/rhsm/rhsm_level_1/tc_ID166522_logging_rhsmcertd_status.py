from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID166522_logging_rhsmcertd_status(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # config rhsmcertd in /etc/rhsm/rhsm.conf
            self.sub_set_certcheckinterval(1)
            self.sub_set_autoattachinterval(1)

            # restart certd
            self.restart_rhsmcertd()

            cmd4 = 'tail -8 /var/log/rhsm/rhsmcertd.log'
            (ret4, output4) = self.runcmd(cmd4, "restart rhsmcertd service")

            if ret4 == 0 and "Auto-attach interval: 1.0 minute(s) [60 second(s)]" and "Cert check interval: 1.0 minute(s) [60 second(s)]" and "Starting rhsmcertd..." in output4:
                logger.info("It's successful to logging rhsmcertd statements.")
            else:
                FailException("Test Failed - Failed to logging rhsmcertd statements.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_set_certcheckinterval(240)
            self.sub_set_autoattachinterval(1440)
            self.restart_rhsmcertd()
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def sub_set_autoattachinterval(self, frtime):
        cmd = "subscription-manager config --rhsmcertd.autoattachinterval=%s" % frtime
        (ret, output) = self.runcmd(cmd, "set autoattachinterval")
        if ret == 0:
            logger.info("It successful to set autoattachinterval")
        else:
            raise FailException("Test Failed - Failed to set autoattachinterval")

    def sub_set_certcheckinterval(self, frtime):
        cmd = "subscription-manager config --rhsmcertd.certcheckinterval=%s" % frtime
        (ret, output) = self.runcmd(cmd, "set certcheckinterval")
        if ret == 0:
            logger.info("It successful to set certcheckinterval")
        else:
            raise FailException("Test Failed - Failed to set certcheckinterval")


if __name__ == "__main__":
    unittest.main()
