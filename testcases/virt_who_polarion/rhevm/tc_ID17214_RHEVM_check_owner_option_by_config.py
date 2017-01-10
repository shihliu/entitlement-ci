from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17214_RHEVM_check_owner_option_by_config(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_without_owner = self.get_vw_cons("rhevm_error_msg_without_owner")
            error_msg_with_wrong_owner = self.get_vw_cons("rhevm_error_msg_with_wrong_owner")
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_RHEVM_OWNER" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_RHEVM_OWNER")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_owner, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("service virt-who status", error_msg_without_owner, cmd_retcode=3)  
            # (2) When "VIRTWHO_RHEVM_OWNER" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_RHEVM_OWNER")
            self.config_option_setup_value("VIRTWHO_RHEVM_OWNER", self.get_vw_cons("wrong_owner"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner)
            # (3) When "VIRTWHO_RHEVM_OWNER" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_RHEVM_OWNER", rhevm_owner)
            self.vw_check_mapping_info_number_in_rhsm_log()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_setup_value("VIRTWHO_RHEVM_OWNER", rhevm_owner)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
