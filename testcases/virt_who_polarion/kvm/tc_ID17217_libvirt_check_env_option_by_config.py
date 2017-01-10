from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17217_libvirt_check_env_option_by_config(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip = get_exported_param("REMOTE_IP")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            error_msg_without_env = self.get_vw_cons("libvirt_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("libvirt_error_msg_with_wrong_env")
            libvirt_owner, libvirt_env, libvirt_username, libvirt_password = self.get_libvirt_info()
            self.runcmd_service("stop_virtwho", remote_ip_2)
            self.set_remote_libvirt_conf(remote_ip, remote_ip_2)

            # (1) When "VIRTWHO_LIBVIRT_ENV" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_LIBVIRT_ENV", remote_ip_2)
            if self.get_os_serials(remote_ip_2) == 6:
                self.vw_check_message("service virt-who restart", error_msg_without_env, cmd_retcode=1, targetmachine_ip=remote_ip_2)
            else:
                self.runcmd_service("restart_virtwho", targetmachine_ip=remote_ip_2)
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_env, cmd_retcode=3, targetmachine_ip=remote_ip_2)
            # (2) When "VIRTWHO_LIBVIRT_ENV" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_LIBVIRT_ENV", remote_ip_2)
            self.config_option_setup_value("VIRTWHO_LIBVIRT_ENV", self.get_vw_cons("wrong_env"),remote_ip_2)
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env, remote_ip_2)
            # (3) When "VIRTWHO_LIBVIRT_ENV" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_LIBVIRT_ENV", libvirt_env, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.update_config_to_default(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
