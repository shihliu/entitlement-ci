from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17217_RHEVM_check_env_option_by_config(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
            error_msg = "Option --rhevm-env (or VIRTWHO_RHEVM_ENV environment variable) needs to be set"
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_RHEVM_ENV" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_RHEVM_ENV")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg , cmd_retcode=1)
            # (2) When "VIRTWHO_RHEVM_ENV" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_RHEVM_ENV")
            self.config_option_setup_value("VIRTWHO_RHEVM_ENV", "xxxxxxx")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg, cmd_retcode=1)
            # (3) When "VIRTWHO_RHEVM_ENV" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_RHEVM_ENV", rhevm_env)
            self.vw_check_mapping_info_number_in_rhsm_log()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_setup_value("VIRTWHO_RHEVM_ENV", rhevm_env)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
