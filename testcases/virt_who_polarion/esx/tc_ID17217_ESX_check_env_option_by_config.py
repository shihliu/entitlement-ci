from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17217_ESX_check_env_option_by_config(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_without_env = self.get_vw_cons("esx_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("esx_error_msg_with_wrong_env")
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_ESX_ENV")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_env, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_env, cmd_retcode=3)
            self.config_option_enable("VIRTWHO_ESX_ENV")
            self.config_option_setup_value("VIRTWHO_ESX_ENV", self.get_vw_cons("wrong_env"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env)
            self.config_option_setup_value("VIRTWHO_ESX_ENV", esx_env)
            self.vw_check_mapping_info_number_in_rhsm_log()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_esx_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
