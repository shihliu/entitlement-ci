from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17205_ESX_check_interval_function_by_config(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            loop_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            self.config_option_disable("VIRTWHO_INTERVAL")
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(loop_msg, 2, 150)
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(loop_msg, 1, 150)
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(1)
                time.sleep(5)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
