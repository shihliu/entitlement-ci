from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID82623_ESX_check_encrypted_passwd_and_passwd(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_with_wrong_passwd = self.get_vw_cons("error_msg_with_wrong_passwd")
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")

            # (1) Check encrypted_password option in /etc/virt-who.d/xxx
            # (1.1) Disable esx mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_ESX")
            # (1.2) Check encrypted_password before run virt-who-password cmd
#             self.set_encrypted_password("esx", "xxxxxxWelcome@*&$001xxxx")
            self.set_encrypted_password("esx", "xxxxxxWelcome")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (1.3) Config correct encryped password of esx mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(esx_password)
            self.set_encrypted_password("esx", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (1.4) Config wrong encryped password of esx mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("esx", "xxxxxxWelcome")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")

            # (2) Check password option in /etc/virt-who.d/xxx
            # (2.1) Config correct password of esx mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            self.unset_all_virtwho_d_conf()
            self.set_virtwho_sec_config("esx")
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2.2) Config wrong password of esx mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_virtwho_sec_config_with_keyvalue("esx", "password", self.get_vw_cons("wrong_passwd"))
            self.vw_check_timeout_in_rhsm_log(error_msg_with_wrong_passwd)

            # (3) Check esx-password option in CLI
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("stop_virtwho")
            # (3.1) Config wrong password of esx mode in CLI mode
            cmd_with_wrong_passwd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, self.get_vw_cons("wrong_passwd")) + " -o -d"
            self.vw_check_message(cmd_with_wrong_passwd, error_msg_with_wrong_passwd)
            # (3.2) When "--esx-passwd" with correct config, virt-who send mapping info
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)

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
