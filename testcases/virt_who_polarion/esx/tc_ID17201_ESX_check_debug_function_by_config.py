from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17201_ESX_check_debug_function_by_config(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.vw_check_message_in_rhsm_log("DEBUG")
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
