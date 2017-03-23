from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID82624_RHEVM_check_rhsm_username_passwd_encrypted_passwd(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            self.runcmd_service("stop_virtwho")

            # (1) Check "rhsm_username+rhsm_passwd"
            self.config_option_disable("VIRTWHO_RHEVM")
            self.sub_unregister()
            # (1.1) Config rhevm mode in /etc/virt-who.d with correct rhsm_username and rhsm_password
            self.set_rhsm_user_pass("rhevm", server_user, server_pass)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (1.2) Config rhevm mode in /etc/virt-who.d with wrong rhsm_username and rhsm_password
            self.set_rhsm_user_pass("rhevm", server_user, "Welcome@*&$001")
            self.vw_check_message_in_rhsm_log("Communication with subscription manager failed with code 500|failed to sent")

            # (2) Check "rhsm_username+rhsm_encrypted_passwd"
            self.unset_all_virtwho_d_conf()
            # (2.1) Config correct encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(server_pass)
            self.set_rhsm_user_encrypted_passwd("rhevm", server_user, encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2.2) Config wrong encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_rhsm_user_encrypted_passwd("rhevm", server_user, "xx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(server_user, server_pass)
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
