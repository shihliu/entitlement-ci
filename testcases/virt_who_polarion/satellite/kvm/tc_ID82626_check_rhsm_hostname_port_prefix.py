from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82626_check_rhsm_hostname_port_prefix(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            server_port = "443"
            server_prefix = "/rhsm"
            self.runcmd_service("stop_virtwho")

            # (1) Check config rhsm_hostname without "http://"
            # (1.1) Unregister host and disable kvm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_LIBVIRT")
            self.sub_unregister(remote_ip_2)
            # (1.2) Virt-who send host/guest mapping info to server
            self.config_hostname_port_prefix_disable(server_hostname, server_port, server_prefix, remote_ip_2)
            self.set_rhsm_hostname_prefix_port("libvirt", server_user, server_pass, server_hostname ,server_port, server_prefix, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)

            # (2) Check config rhsm_hostname with "http://"
            # (2.1) Virt-who send host/guest mapping info to server
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.set_rhsm_hostname_prefix_port("libvirt", server_user, server_pass, "http://" + server_hostname ,server_port, server_prefix, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)
            
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # Remove all conf in /etc/virt-who.d and reconfig virt-who, restart virt-who
            self.unset_all_virtwho_d_conf(remote_ip_2)
            # Register host
            self.config_hostname_port_prefix_enable(server_hostname, server_port, server_prefix, remote_ip_2)
            self.sub_register(server_user, server_pass, remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
