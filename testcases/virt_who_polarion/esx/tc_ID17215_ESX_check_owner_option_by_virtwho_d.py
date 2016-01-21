from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17215_ESX_check_owner_option_by_virtwho_d(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg = "Option `owner` needs to be set in config `esx`"
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            self.set_virtwho_sec_config_with_keyvalue("esx", "owner", "")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg, cmd_retcode=1)
            self.set_virtwho_sec_config_with_keyvalue("esx", "owner", "xxxxxxx")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg, cmd_retcode=1)
            self.set_virtwho_sec_config("esx")
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
