from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509884_man_page_change_rhsmcertd_option_cert_interval_to_cert_check_interval(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#            username = self.get_rhsm_cons("username")
#            password = self.get_rhsm_cons("password")
#            self.sub_register(username, password)
#            autosubprod = self.get_rhsm_cons("autosubprod")
#            self.sub_autosubscribe(autosubprod)
            cmd = "man -P cat rhsmcertd | grep 'cert-interval'"
            (ret, output) = self.runcmd(cmd, "grep the cert-interval")
            if ret == 1 and (not output):
                logger.info("cert-interval is not in the man page ")
            else:
                raise FailException("Test Failed - cert-interval is in the man page")

            cmd = "man -P cat rhsmcertd | grep 'cert-check-interval'"
            (ret, output) = self.runcmd(cmd, "grep the cert-check-interval")
            if ret == 0 and output:
                logger.info("cert-check-interval is in the man page ")
            else:
                raise FailException("Test Failed - cert-check-interval is not in the man page")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
