from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17214_HYPERV_check_owner_option_by_config(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_without_owner = self.get_vw_cons("hyperv_error_msg_without_owner")
            error_msg_with_wrong_owner = self.get_vw_cons("hyperv_error_msg_with_wrong_owner")
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_HYPERV_OWNER" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_HYPERV_OWNER")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg_without_owner , cmd_retcode=1)
            # (2) When "VIRTWHO_HYPERV_OWNER" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_HYPERV_OWNER")
            self.config_option_setup_value("VIRTWHO_HYPERV_OWNER", self.get_vw_cons("wrong_owner"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner)
            # (3) When "VIRTWHO_HYPERV_OWNER" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_HYPERV_OWNER", hyperv_owner)
            self.vw_check_mapping_info_number_in_rhsm_log()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
