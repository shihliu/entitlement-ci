from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17215_HYPERV_check_owner_option_by_virtwho_d(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            error_msg = "Option `owner` needs to be set in config `hyperv`"
            self.runcmd_service("stop_virtwho")
            self.unset_hyperv_conf()
            #(1) When "owner" is not exist, virt-who should show error info
            self.set_virtwho_sec_config_with_keyvalue("hyperv", "owner", "")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg, cmd_retcode=1)
            #(2) When "owner" with wrong config, virt-who should show error info
            self.set_virtwho_sec_config_with_keyvalue("hyperv", "owner", "xxxxxxx")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg, cmd_retcode=1)
            #(3) When "owner" with correct config, virt-who should show error info
            self.set_virtwho_sec_config("hyperv")
            self.vw_check_mapping_info_number_in_rhsm_log()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.update_vm_hyperv_configure(hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
