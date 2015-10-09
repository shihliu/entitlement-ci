from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID332939_display_stdout_to_user_with_actual_destination_by_rhsm_debug_system(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # execute rhsm-debug system
            cmd = "rhsm-debug system"
            (ret, output) = self.runcmd(cmd, "execute rhsm-debug system")
            if ret == 0 and "Wrote: /tmp/rhsm-debug-system" in output:
                self.check_rhsm_debug_system_output(output)
                logger.info("It's successful to display stdout to user with actual destination by rhsm debug system")
            else:
                raise FailException("Test Failed - display stdout to user with actual destination by rhsm debug system.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_rhsm_debug_system_output(self, output):
        debug_result = output.split(":")[1].strip()
        cmd = "ls %s" % debug_result
        (ret, output) = self.runcmd(cmd, "check rhsm-debug system result")
        if ret == 0 and debug_result in output:
            logger.info("It's successful to list rhsm debug system result: %s" % debug_result)
        else:
            raise FailException("Test Failed - Failed to list rhsm debug system result.")

if __name__ == "__main__":
    unittest.main()
