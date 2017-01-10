from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537378_wrong_command_option_given_in_man_page_of_rhsm_debug_command(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            #1 check the head of rhsm-debug man page
            cmd = "man rhsm-debug | egrep 'RHSM Debug Tool'"
            (ret, output) = self.runcmd(cmd, "check the head of rhsm-debug man page")
            if ret == 0 and 'RHSM-DEBUG(8)                   RHSM Debug Tool                  RHSM-DEBUG(8)' in output:
                logger.info("It's successful to check the head of rhsm-debug man page")
            else:
                raise FailException("Test Failed - Failed to check the head of rhsm-debug man page")

            #2 check the supported modules in rhsm-debug man page
            cmd = "man rhsm-debug | egrep 'The currently supported modules are' -A5"
            (ret, output) = self.runcmd(cmd, "check the supported modules in rhsm-debug man page")
            if ret == 0 and '1. system\n' in output:
                logger.info("It's successful to check the supported modules in rhsm-debug man page")
            else:
                raise FailException("Test Failed - Failed to check the supported modules in rhsm-debug man page")

            #3 check the proxy password description in rhsm-debug man page
            cmd = "man rhsm-debug | col -b | egrep 'proxypass' -A5"
            (ret, output) = self.runcmd(cmd, "check the proxy password description in rhsm-debug man page")
            if ret == 0 and '--proxypassword=PROXYPASSWORD\n\t      Gives the password to use to authenticate to the HTTP proxy.' in output:
                logger.info("It's successful to check the proxy password description in rhsm-debug man page")
            else:
                raise FailException("Test Failed - Failed to check the proxy password description in rhsm-debug man page")

            #4 check the sos description in rhsm-debug man page
            cmd = "man rhsm-debug | egrep 'sos' -A5"
            (ret, output) = self.runcmd(cmd, "check the sos description in rhsm-debug man page")
            if ret == 0 and 'Excludes data files that are also  collected  by  the  sosreport' in output:
                logger.info("It's successful to check the sos description in rhsm-debug man page")
            else:
                raise FailException("Test Failed - Failed to check the sos description in rhsm-debug man page")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
