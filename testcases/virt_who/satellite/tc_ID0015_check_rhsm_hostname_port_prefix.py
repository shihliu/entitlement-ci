from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID0015_check_rhsm_hostname_port_prefix(VIRTWHOBase):
    def run_kvm(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
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
        finally:
            # Remove all conf in /etc/virt-who.d and reconfig virt-who, restart virt-who
            self.unset_all_virtwho_d_conf(remote_ip_2)
            # Register host
            self.config_hostname_port_prefix_enable(server_hostname, server_port, server_prefix, remote_ip_2)
            self.sub_register(server_user, server_pass, remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.runcmd_service("stop_virtwho")
            for i in range(1, 5):
                self.vw_check_mapping_info_number("virt-who --vdsm -o -d", 1)
            self.check_virtwho_thread(0)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            server_port = "443"
            server_prefix = "/rhsm"
            self.runcmd_service("stop_virtwho")
            # (1) Check config rhsm_hostname without "http://"
            # (1.1) Unregister host and disable rhevm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_RHEVM")
            self.sub_unregister()
            # (1.2) Virt-who send host/guest mapping info to server
            self.config_hostname_port_prefix_disable(server_hostname, server_port, server_prefix)
            self.set_rhsm_hostname_prefix_port("rhevm", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2) Check config rhsm_hostname with "http://"
            # (2.1) Virt-who send host/guest mapping info to server
            self.unset_all_virtwho_d_conf()
            self.set_rhsm_hostname_prefix_port("rhevm", server_user, server_pass, "http://" + server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            # Remove all conf in /etc/virt-who.d and reconfig virt-who, restart virt-who
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            # Register host
            self.config_hostname_port_prefix_enable(server_hostname, server_port, server_prefix)
            self.sub_register(server_user, server_pass)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            server_port = "443"
            server_prefix = "/rhsm"
            self.runcmd_service("stop_virtwho")
            # (1) Check config rhsm_hostname without "http://"
            # (1.1) Unregister host and disable hyperv mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_HYPERV")
            self.sub_unregister()
            # (1.2) Virt-who send host/guest mapping info to server
            self.config_hostname_port_prefix_disable(server_hostname, server_port, server_prefix)
            self.set_rhsm_hostname_prefix_port("hyperv", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2) Check config rhsm_hostname with "http://"
            # (2.1) Virt-who send host/guest mapping info to server
            self.unset_all_virtwho_d_conf()
            self.set_rhsm_hostname_prefix_port("hyperv", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            # Remove all conf in /etc/virt-who.d and reconfig virt-who, restart virt-who
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            # Register host
            self.config_hostname_port_prefix_enable(server_hostname, server_port, server_prefix)
            self.sub_register(server_user, server_pass)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            server_port = "443"
            server_prefix = "/rhsm"
            self.runcmd_service("stop_virtwho")
            # (1) Check config rhsm_hostname without "http://"
            # (1.1) Unregister host and disable esx mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_ESX")
            self.sub_unregister()
            # (1.2) Virt-who send host/guest mapping info to server
            self.config_hostname_port_prefix_disable(server_hostname, server_port, server_prefix)
            self.set_rhsm_hostname_prefix_port("esx", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2) Check config rhsm_hostname with "http://"
            # (2.1) Virt-who send host/guest mapping info to server
            self.unset_all_virtwho_d_conf()
#             self.set_rhsm_hostname_prefix_port("esx", server_user, server_pass, "https://"+server_hostname ,server_port, server_prefix)
            self.set_rhsm_hostname_prefix_port("esx", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            # Remove all conf in /etc/virt-who.d and reconfig virt-who, restart virt-who
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            self.runcmd_service("restart_virtwho")
            # Register host
            self.config_hostname_port_prefix_enable(server_hostname, server_port, server_prefix)
            self.sub_register(server_user, server_pass)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            server_port = "443"
            server_prefix = "/rhsm"
            self.runcmd_service("stop_virtwho")
            # (1) Check config rhsm_hostname without "http://"
            # (1.1) Unregister host and disable xen mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_XEN")
            self.sub_unregister()
            # (1.2) Virt-who send host/guest mapping info to server
            self.config_hostname_port_prefix_disable(server_hostname, server_port, server_prefix)
            self.set_rhsm_hostname_prefix_port("xen", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2) Check config rhsm_hostname with "http://"
            # (2.1) Virt-who send host/guest mapping info to server
            self.unset_all_virtwho_d_conf()
            self.set_rhsm_hostname_prefix_port("xen", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            # Remove all conf in /etc/virt-who.d and reconfig virt-who, restart virt-who
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
            self.runcmd_service("restart_virtwho")
            # Register host
            self.config_hostname_port_prefix_enable(server_hostname, server_port, server_prefix)
            self.sub_register(server_user, server_pass)
            logger.info("---------- succeed to restore environment ----------")

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            hypervisor_type = get_exported_param("HYPERVISOR_TYPE")
            if hasattr(self, "run_" + hypervisor_type):
                getattr(self, "run_" + hypervisor_type)()
            else:
                self.skipTest("test case skiped, not fit for %s" % hypervisor_type)
            self.assert_(True, case_name)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()