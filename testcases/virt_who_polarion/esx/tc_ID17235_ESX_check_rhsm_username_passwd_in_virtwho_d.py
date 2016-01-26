from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17235_ESX_check_rhsm_username_passwd_in_virtwho_d(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            self.esx_set_rhsm_user_pass(server_user, server_pass, esx_owner, esx_env, esx_server, esx_username, esx_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            self.esx_set_rhsm_user_pass(server_user, "xxxxxxxx", esx_owner, esx_env, esx_server, esx_username, esx_password)
            self.vw_check_message_in_rhsm_log("BUG yet")
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
