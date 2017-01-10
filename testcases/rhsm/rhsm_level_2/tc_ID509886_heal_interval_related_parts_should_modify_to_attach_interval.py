from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509886_heal_interval_related_parts_should_modify_to_attach_interval(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#            username = self.get_rhsm_cons("username")
#            password = self.get_rhsm_cons("password")
#            self.sub_register(username, password)
#            autosubprod = self.get_rhsm_cons("autosubprod")
#            self.sub_autosubscribe(autosubprod)
            cmd = "rhsmcertd --help | grep cert"
            (ret, output) = self.runcmd(cmd, "run rhsmcertd --help | grep cert")
            if ret == 0 and ("--cert-interval=MINUTES                deprecated, see --cert-check-interval" in output) and \
            ("-c, --cert-check-interval=MINUTES      interval to run cert check (in minutes)" in output):
                logger.info("cert-interval is changed to cert-check-interval ")
            else:
                raise FailException("Test Failed - cert-interval is not changed to cert-check-interval")

            cmd = "grep -i interval /etc/rhsm/rhsm.conf"
            (ret, output) = self.runcmd(cmd, "run grep -i interval /etc/rhsm/rhsm.conf")
            if ret == 0 and ("certCheckInterval" in output) and ("autoAttachInterval" in output):
                logger.info("certCheckInterval and autoAttachInterval is in the config file ")
            else:
                raise FailException("Test Failed - certCheckInterval and autoAttachInterval is in the config file ")

            cmd = "subscription-manager config --help | grep -i interval"
            (ret, output) = self.runcmd(cmd, "run subscription-manager config --help | grep -i interval")
            if ret == 0 and ("--rhsmcertd.certcheckinterval" in output) and ("--rhsmcertd.autoattachinterval" in output):
                logger.info("rhsmcertd.certcheckinterval and rhsmcertd.autoattachinterval is in the config option's help doc ")
            else:
                raise FailException("Test Failed - rhsmcertd.certcheckinterval and rhsmcertd.autoattachinterval is not in the config option's help doc")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
