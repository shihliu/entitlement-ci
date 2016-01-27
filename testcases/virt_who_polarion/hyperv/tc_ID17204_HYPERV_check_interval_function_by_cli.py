from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17204_HYPERV_check_interval_function_by_cli(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            check_msg = "No change in report"
            #(1) Check virt-who refresh default interval is 60s
            cmd = self.virtwho_cli("hyperv") + " -d"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            #(2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = self.virtwho_cli("hyperv") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            #(3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = self.virtwho_cli("hyperv") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150)
            self.check_virtwho_null_thread()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
