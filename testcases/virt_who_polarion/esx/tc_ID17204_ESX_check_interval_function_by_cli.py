from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17204_ESX_check_interval_function_by_cli(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            loop_msg = "Waiting for ESX changes"
            cmd = self.virtwho_cli("esx") + " -d"
            self.vw_check_message_number_in_debug_cmd(cmd, loop_msg, 3, 150)
            cmd = self.virtwho_cli("esx") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, loop_msg, 3, 150)
            cmd = self.virtwho_cli("esx") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, loop_msg, 2, 150)
            self.check_virtwho_thread(0)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
