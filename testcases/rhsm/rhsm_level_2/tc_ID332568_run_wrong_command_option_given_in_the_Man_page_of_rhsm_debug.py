from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID332568_run_wrong_command_option_given_in_the_Man_page_of_rhsm_debug(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # check the man page header
            cmd = 'man rhsm-debug | egrep "RHSM Debug Tool"'
            (ret, output) = self.runcmd(cmd, "check the man page header")
            outputb = output.strip().split(" ")
            if ret == 0 and outputb[0] == outputb[len(outputb) - 1] == "RHSM-DEBUG(8)":
                logger.info("It's successful to check the man page header.") 
            else:
                raise FailException("Test Failed - Failed to check the man page header.")

            # check the correct command system
            cmd = 'man rhsm-debug | egrep "The currently supported modules are" -A5'
            (ret, output) = self.runcmd(cmd, "check the correct command system")
            if ret == 0 and "system" in output:
                logger.info("It's successful to check the correct command system.") 
            else:
                raise FailException("Test Failed - Failed to check the correct command system.")

            # check --proxypassword is correctly displayed.
            cmd = 'man rhsm-debug | egrep "Gives the password to use to authenticate to the HTTP proxy" -B1'
            (ret, output) = self.runcmd(cmd, "check the correct command system")
            if ret == 0 and "Gives the password to use to authenticate to the HTTP proxy" in output:
                logger.info("It's successful to check --proxypassword is correctly displayed") 
            else:
                raise FailException("Test Failed - Failed to check --proxypassword is correctly displayed")

            # check --sos is correctly displayed.
            cmd = 'man rhsm-debug | egrep "sos"'
            (ret, output) = self.runcmd(cmd, "check --sos")
            if ret == 0 and "Excludes  data  files  that  are also collected by the sosreport" in output:
                logger.info("It's successful to check --sos") 
            else:
                raise FailException("Test Failed - Failed to check --sos")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
