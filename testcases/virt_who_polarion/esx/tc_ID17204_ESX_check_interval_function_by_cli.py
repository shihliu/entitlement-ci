from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17204_ESX_check_interval_function_by_cli(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            cmd = self.virtwho_cli("esx") + " -d"
            self.vw_check_mapping_info_number_in_debug_cmd(cmd, 1, 80)
            cmd = self.virtwho_cli("esx") + " -d -i 0"
            self.vw_check_mapping_info_number_in_debug_cmd(cmd, 1, 80)
            for interval in [3, 5, 15, 30, 60]:
                cmd = self.virtwho_cli("esx") + " -d -i %s" % interval
                self.vw_check_mapping_info_number_in_debug_cmd(cmd, 1, 80)
            self.check_virtwho_null_thread()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
