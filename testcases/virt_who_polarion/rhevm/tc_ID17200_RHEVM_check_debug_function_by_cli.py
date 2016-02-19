from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17200_RHEVM_check_debug_function_by_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "DEBUG" info is exist when run "virt-who --rhevm -d"
            cmd = self.virtwho_cli("rhevm") + " -d"
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG")
            # (2) Check "DEBUG" info is not exist when run "virt-who --rhevm",no "-d" option
            cmd = self.virtwho_cli("rhevm")
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG|ERROR", message_exists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
