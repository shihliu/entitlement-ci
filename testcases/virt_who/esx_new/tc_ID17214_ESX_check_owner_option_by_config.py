from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17214_ESX_check_owner_option_by_config(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_ESX_OWNER")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), "Option --esx-owner (or VIRTWHO_ESX_OWNER environment variable) needs to be set", cmd_retcode=1)
            self.config_option_enable("VIRTWHO_ESX_OWNER")
            self.config_option_setup_value("VIRTWHO_ESX_OWNER", "xxxxxxx")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), "Option --esx-owner (or VIRTWHO_ESX_OWNER environment variable) needs to be set", cmd_retcode=1)
            self.config_option_setup_value("VIRTWHO_ESX_OWNER", esx_owner)
            self.vw_check_mapping_info_number_in_rhsm_log()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
