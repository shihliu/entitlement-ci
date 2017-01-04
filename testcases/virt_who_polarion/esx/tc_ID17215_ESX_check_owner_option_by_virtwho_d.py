from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17215_ESX_check_owner_option_by_virtwho_d(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_without_owner = self.get_vw_cons("esx_error_msg_without_owner_in_conf")
            error_msg_with_wrong_owner = self.get_vw_cons("esx_error_msg_with_wrong_owner")
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            self.set_virtwho_sec_config_with_keyvalue("esx", "owner", "")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_owner, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_owner, cmd_retcode=3)
            self.set_virtwho_sec_config_with_keyvalue("esx", "owner", self.get_vw_cons("wrong_owner"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner)
            self.set_virtwho_sec_config("esx")
            self.vw_check_mapping_info_number_in_rhsm_log()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
