from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17234_ESX_check_encrypted_passwd_in_virtwho_d(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            encrypted_password = self.run_virt_who_password(esx_password)
            self.esx_set_encrypted_password(encrypted_password, esx_owner, esx_env, esx_server, esx_username)
            self.vw_check_mapping_info_number_in_rhsm_log()
            self.esx_set_encrypted_password("xxxxxxxxxxxxxxxxxxx", esx_owner, esx_env, esx_server, esx_username)
            self.vw_check_message_in_rhsm_log("Password can't be decrypted, possibly corrupted")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
#             self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
