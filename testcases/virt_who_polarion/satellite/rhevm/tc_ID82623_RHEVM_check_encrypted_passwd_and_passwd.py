from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID82623_RHEVM_check_encrypted_passwd_and_passwd(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_with_wrong_passwd = self.get_vw_cons("error_msg_with_wrong_passwd")
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            self.runcmd_service("stop_virtwho")
            rhevm_ip = get_exported_param("RHEVM_IP")
            rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
            if "rhevm-4"in rhevm_version:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443" + "\/ovirt-engine\/"
            else:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
            self.runcmd_service("stop_virtwho")

            # (1) Check encrypted_password option in /etc/virt-who.d/xxx
            # (1.1) Disable rhevm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_RHEVM")
            # (1.2) Check encrypted_password before run virt-who-password cmd
            self.set_encrypted_password("rhevm", "xxxxxxxxxxxxxxxxxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (1.3) Config correct encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(rhevm_password)
            self.set_encrypted_password("rhevm", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (1.4) Config wrong encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("rhevm", "xxxxxxxxxxxxxxxxxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")

            # (2) Check password option in /etc/virt-who.d/xxx
            # (2.1) Config correct password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            self.unset_all_virtwho_d_conf()
            self.set_virtwho_sec_config("rhevm")
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2.2) Config wrong password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_virtwho_sec_config_with_keyvalue("rhevm", "password", self.get_vw_cons("wrong_passwd"))
            self.vw_check_timeout_in_rhsm_log(error_msg_with_wrong_passwd)

            # (3) Check rhevm-password option in CLI
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("stop_virtwho")
            # (3.1) Config wrong password of rhevm mode in CLI mode
            cmd_with_wrong_passwd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, self.get_vw_cons("wrong_passwd")) + " -o -d"
            self.vw_check_message(cmd_with_wrong_passwd, error_msg_with_wrong_passwd)
            # (3.2) When "--rhevm-passwd" with correct config, virt-who send mapping info
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
