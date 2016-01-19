from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17205_ESX_check_interval_function_by_config(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.vw_check_mapping_info_number_in_rhsm_log(1, 80)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 0)
            self.vw_check_mapping_info_number_in_rhsm_log(1, 80)
            for interval in [3, 5, 15, 30, 60]:
                self.config_option_setup_value("VIRTWHO_INTERVAL", interval)
                self.vw_check_mapping_info_number_in_rhsm_log(1, 80)
            self.check_virtwho_thread()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
