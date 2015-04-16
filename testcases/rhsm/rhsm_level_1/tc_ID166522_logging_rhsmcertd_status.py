from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID166522_logging_rhsmcertd_status(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # config rhsmcertd in /etc/rhsm/rhsm.conf
            self.sub_set_certfrequency(1)
            self.sub_set_healfrequency(1)
            cmd3 = 'service rhsmcertd restart'
            (ret3, output3) = self.runcmd(cmd3, "restart rhsmcertd service")

            cmd4 = 'tail -4 /var/log/rhsm/rhsmcertd.log'
            (ret4, output4) = self.runcmd(cmd4, "restart rhsmcertd service")

            if ret4 == 0 and "healing check started: interval = 1" and "cert check started: interval = 1" and "certificates updated" in output4:
                logger.info("It's successful to logging rhsmcertd statements.")
            else:
                FailException("Test Failed - Failed to logging rhsmcertd statements.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_set_certfrequency(240)
            self.sub_set_healfrequency(1440)
            cmd = 'service rhsmcertd restart'
            self.runcmd(cmd, "restart rhsmcertd")
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def sub_set_healfrequency(self, frtime):
        cmd = "subscription-manager config --rhsmcertd.healfrequency=%s" % frtime
        cmd510 = "subscription-manager config --rhsmcertd.autoattachinterval=%s" % frtime
        (ret, output) = self.runcmd(cmd, "set healfrequency")
        if ret == 0:
            logger.info("It successful to set healfrequency")
        else:
            (ret, output) = self.runcmd(cmd510, "set autoattachinterval")
        if ret == 0:
            logger.info("It successful to set autoattachinterval")
        else:
            FailException("Test Failed - Failed to set healfrequency or autoattachinterval.")

    def sub_set_certfrequency(self, frtime):
        cmd = "subscription-manager config --rhsmcertd.certfrequency=%s" % frtime
        cmd510 = "subscription-manager config --rhsmcertd.certcheckinterval=%s" % frtime
        (ret, output) = self.runcmd(cmd, "set certfrequency")
        if ret == 0:
            logger.info("It successful to set healfrequency")
        else:
            (ret, output) = self.runcmd(cmd510, "set certcheckinterval")
        if ret == 0:
            logger.info("It successful to set certfrequency")
        else:
            FailException("Test Failed - Failed to set certfrequency or certcheckinterval.")

if __name__ == "__main__":
    unittest.main()
