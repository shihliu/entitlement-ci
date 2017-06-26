from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID0011_check_http_https_proxy(VIRTWHOBase):
    def run_kvm(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            http_proxy = self.get_vw_cons("http_proxy")
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()
            remote_ip_2 = get_exported_param("REMOTE_IP_2")      
            mode = "libvirt"
            # (1) Configure http_proxy
            self.set_remote_libvirt_conf(get_exported_param("REMOTE_IP"), remote_ip_2)
            self.configure_http_proxy(mode, http_proxy, server_hostname, remote_ip_2)
            # (2) Check host/guest mappping info
            self.vw_check_message_in_rhsm_log(guest_uuid, remote_ip_2)
            # (3) Check http_proxy in rhsm log
            self.vw_check_message_in_rhsm_log(http_proxy, remote_ip_2)
        finally:
            self.vw_define_all_guests()
            self.config_option_disable("http_proxy", remote_ip_2)
            self.config_option_disable("no_proxy", remote_ip_2)
            self.clean_remote_libvirt_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho")
            self.runcmd_service("restart_virtwho", remote_ip_2)
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
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            http_proxy = self.get_vw_cons("http_proxy")
            guest_uuid = self.rhevm_get_guest_guid(guest_name)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            mode = "rhevm"
            # (1) Configure http_proxy
            self.configure_http_proxy(mode, http_proxy, server_hostname)
            # (2) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Check http_proxy in rhsm log
            self.vw_check_message_in_rhsm_log(http_proxy)
        finally:
            self.config_option_disable("https_proxy")
            self.config_option_disable("no_proxy")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            http_proxy = self.get_vw_cons("http_proxy")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()
            mode = "hyperv"

            # (1) Configure http_proxy
            self.configure_http_proxy(mode, http_proxy, server_hostname)
            # (2) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Check http_proxy in rhsm log
            self.vw_check_message_in_rhsm_log(http_proxy)
        finally:
            self.config_option_disable("http_proxy")
            self.config_option_disable("no_proxy")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            http_proxy = self.get_vw_cons("http_proxy")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            mode = "esx"
            # (1) Configure http_proxy
            self.configure_http_proxy(mode, http_proxy, server_hostname)
            # (2) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Check http_proxy in rhsm log
            self.vw_check_message_in_rhsm_log(http_proxy)
        finally:
            self.config_option_disable("https_proxy")
            self.config_option_disable("no_proxy")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            http_proxy = self.get_vw_cons("http_proxy")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            mode = "xen"
            # (1) Configure http_proxy
            self.configure_http_proxy(mode, http_proxy, server_hostname)
            # (2) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Check http_proxy in rhsm log
            self.vw_check_message_in_rhsm_log(http_proxy)
        finally:
            self.config_option_disable("https_proxy")
            self.config_option_disable("no_proxy")
            self.runcmd_service("restart_virtwho")
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