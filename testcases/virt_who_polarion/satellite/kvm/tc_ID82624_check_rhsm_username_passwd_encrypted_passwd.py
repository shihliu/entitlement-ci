from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException
from utils.libvirtAPI.Python import utils

class tc_ID82624_check_rhsm_username_passwd_encrypted_passwd(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            self.runcmd_service("stop_virtwho")
            self.runcmd_service("stop_virtwho", remote_ip_2)
            self.update_vw_configure(targetmachine_ip=remote_ip_2)

            # (1) Check "rhsm_username+rhsm_passwd"
            self.config_option_disable("VIRTWHO_KVM", remote_ip_2)
            self.sub_unregister(remote_ip_2)
            # (1.1) Config kvm mode in /etc/virt-who.d with correct rhsm_username and rhsm_password
            self.set_rhsm_user_pass("libvirt", server_user, server_pass, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)
            # (1.2) Config kvm mode in /etc/virt-who.d with wrong rhsm_username and rhsm_password
            self.set_rhsm_user_pass("libvirt", server_user, "Welcome@*&$001", remote_ip_2)
            self.vw_check_message_in_rhsm_log("Communication with subscription manager failed with code 500|failed to sent", targetmachine_ip=remote_ip_2)

            # (2) Check "rhsm_username+rhsm_encrypted_passwd"
            self.unset_all_virtwho_d_conf(remote_ip_2)
            # (2.1) Config correct encryped password of kvm mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(server_pass)
#             self.scp_file(remote_ip_2, server_user, server_pass, "/var/lib/virt-who", "/var/lib/virt-who/key")
            ssh_cmd = "scp %s %s@%s:%s " % ("/var/lib/virt-who/key", "root", remote_ip_2, "/var/lib/virt-who")
            ret, output = self.runcmd_local_pexpect(ssh_cmd)
            if "key" in output:
                logger.info("Succeeded to copy key file to %s" % remote_ip_2)
            else:
                raise FailException("Failed to copy key file to %s" % remote_ip_2)
            self.set_rhsm_user_encrypted_passwd("libvirt", server_user, encrypted_password, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)
            # (2.2) Config wrong encryped password of kvm mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_rhsm_user_encrypted_passwd("libvirt", server_user, "xx", remote_ip_2)
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted", targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(server_user, server_pass, remote_ip_2)
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
