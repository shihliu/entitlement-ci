from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1065_check_hypervisor_id_in_virtwho_d(VIRTWHOBase):
    def run_kvm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            self.runcmd_service("stop_virtwho")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.vw_define_guest(guest_name)
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()
            host_name = self.get_hostname(get_exported_param("REMOTE_IP"))

            # (1) Set hypervisor_id=uuid, it will show uuid 
            self.set_hypervisor_id("libvirt", "uuid", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (2) Set hypervisor_id=hostname, it will show hostname 
            self.set_hypervisor_id("libvirt", "hostname", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_name, guest_uuid, targetmachine_ip=remote_ip_2)
            # (3) Set hypervisor_id=hwuuid, hyperv is not support hwuuid, it will report error
            self.set_hypervisor_id("libvirt", "hwuuid", remote_ip_2)
            self.vw_check_message_in_rhsm_log("Reporting of hypervisor hwuuid is not implemented in libvirt backend|Invalid option hwuuid for hypervisor_id", message_exists=True, targetmachine_ip=remote_ip_2)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            self.sub_unregister()
            if not self.sub_isregistered():
                self.configure_server(SERVER_IP, SERVER_HOSTNAME)
                self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            self.runcmd_service("stop_virtwho")
            self.vw_define_guest(guest_name, remote_ip_1)
            guest_uuid = self.vw_get_uuid(guest_name, remote_ip_1)
            host_uuid = self.get_host_uuid(remote_ip_1)
            host_name = self.get_hostname(remote_ip_1)
            self.config_option_disable("VIRTWHO_LIBVIRT")

            # (1) Set hypervisor_id=uuid, it will show uuid 
            self.set_hypervisor_id("libvirt", "uuid")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hypervisor_id=hostname, it will show hostname 
            self.set_hypervisor_id("libvirt", "hostname")
            self.vw_check_mapping_info_in_rhsm_log(host_name, guest_uuid)
            # (3) Set hypervisor_id=hwuuid, hyperv is not support hwuuid, it will report error
            self.set_hypervisor_id("libvirt", "hwuuid")
            self.vw_check_message_in_rhsm_log("Reporting of hypervisor hwuuid is not implemented in libvirt backend|Invalid option hwuuid for hypervisor_id", message_exists=True)
        finally:
            self.unset_all_virtwho_d_conf()
            self.config_option_enable("VIRTWHO_LIBVIRT")
            self.runcmd_service("restart_virtwho")
            self.sub_unregister()
            if not self.sub_isregistered():
                self.configure_server(SERVER_IP, SERVER_HOSTNAME)
                self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            host_name = self.get_hostname(get_exported_param("RHEVM_HOST1_IP"))
            host_hwuuid = self.get_host_hwuuid_on_rhevm(get_exported_param("RHEVM_HOST1_IP"), rhevm_ip)

            # (1) Set hypervisor_id=uuid, it will show uuid 
            self.set_hypervisor_id("rhevm", "uuid")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hypervisor_id=hostname, it will show hostname 
            self.set_hypervisor_id("rhevm", "hostname")
            self.vw_check_mapping_info_in_rhsm_log(host_name, guest_uuid)
            # (3) Set hypervisor_id=hwuuid, it will show hwuuid
            self.set_hypervisor_id("rhevm", "hwuuid")
            self.vw_check_mapping_info_in_rhsm_log(host_hwuuid, guest_uuid)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.sub_unregister()
            if not self.sub_isregistered():
                self.configure_server(SERVER_IP, SERVER_HOSTNAME)
                self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")

            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()
            hyperv_host_name = self.hyperv_get_hostname(hyperv_host_ip)

            # (1) Set hypervisor_id=uuid, it will show uuid 
            self.set_hypervisor_id("hyperv", "uuid")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hypervisor_id=hostname, it will show hostname 
            self.set_hypervisor_id("hyperv", "hostname")
            self.vw_check_mapping_info_in_rhsm_log(hyperv_host_name, guest_uuid)
            # (3) Set hypervisor_id=hwuuid, hyperv is not support hwuuid, it will report error
            self.set_hypervisor_id("hyperv", "hwuuid")
            self.vw_check_message_in_rhsm_log("Reporting of hypervisor hwuuid is not implemented in hyperv backend|Invalid option hwuuid for hypervisor_id", message_exists=True)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            esx_host_name = self.esx_get_hostname(esx_host_ip)
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            self.set_hypervisor_id("esx", "uuid")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.set_hypervisor_id("esx", "hostname")
            self.vw_check_mapping_info_in_rhsm_log(esx_host_name, guest_uuid)
            self.set_hypervisor_id("esx", "hwuuid")
            # do not know how to get hwuuid of esx, just check "host-" here
            self.vw_check_mapping_info_in_rhsm_log("host-", guest_uuid)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.skipTest("test case skiped, not fit for xen ...")
        finally:
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
