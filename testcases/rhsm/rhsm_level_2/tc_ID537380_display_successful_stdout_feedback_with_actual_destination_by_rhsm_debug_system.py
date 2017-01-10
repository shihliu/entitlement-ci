from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537380_display_successful_stdout_feedback_with_actual_destination_by_rhsm_debug_system(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # run rhsm-debug system
            cmd = "rhsm-debug system"
            (ret, output) = self.runcmd(cmd, "rhsm-debug system")
            if ret == 0 and 'Wrote: /tmp/rhsm-debug-system-' in output:
                logger.info("It's successful to run rhsm-debug system command")
            else:
                raise FailException("Test Failed - Failed to run rhsm-debug system command")

            # check destination
            desti = output.split(':')[1].strip()
            cmd = 'ls %s'%desti
            (ret, output) = self.runcmd(cmd, "check destination")
            if ret == 0 and output.strip() == desti:
                logger.info("It's successful to check rhsm-debug system output destination")
            else:
                raise FailException("Test Failed - Failed to check rhsm-debug system output destination")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
