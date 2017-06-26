from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1067_check_hypervisor_id_and_filter_hosts_in_virtwho_d(VIRTWHOBase):
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

            # (1) Set hypervisor_id=uuid, and fitler_host_uuids, it will show host/guest uuid mapping info
            self.set_hypervisor_id_filter_host_uuids("libvirt", "uuid", host_uuid, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (2) Set hypervisor_id=hostname, and fitler_host_uuids, it will show host/guest name mapping info
            self.set_hypervisor_id_filter_host_uuids("libvirt", "hostname", host_name, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_name, guest_uuid, targetmachine_ip=remote_ip_2)
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
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            guest_uuid = self.vw_get_uuid(guest_name, remote_ip_1)

            self.runcmd_service("stop_virtwho")
            self.vw_define_guest(guest_name, remote_ip_1)
            host_uuid = self.get_host_uuid(remote_ip_1)
            host_name = self.get_hostname(get_exported_param("REMOTE_IP_1"))
            self.config_option_disable("VIRTWHO_LIBVIRT")

            # (1) Set hypervisor_id=uuid, and fitler_host_uuids, it will show host/guest uuid mapping info
            self.set_hypervisor_id_filter_host_uuids("libvirt", "uuid", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hypervisor_id=hostname, and fitler_host_uuids, it will show host/guest name mapping info
            self.set_hypervisor_id_filter_host_uuids("libvirt", "hostname", host_name)
            self.vw_check_mapping_info_in_rhsm_log(host_name, guest_uuid)
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
            host_name_sec = self.get_hostname(get_exported_param("RHEVM_HOST2_IP"))
            host_uuid_sec = self.get_host_uuid_on_rhevm(get_exported_param("RHEVM_HOST2_IP"), rhevm_ip)
            host_hwuuid_sec = self.get_host_hwuuid_on_rhevm(get_exported_param("RHEVM_HOST2_IP"), rhevm_ip)

            # (1) Set hypervisor_id=uuid, and fitler_host_uuids, it will only show host/guest uuid mapping info
            self.set_hypervisor_id_filter_host_uuids("rhevm", "uuid", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_name, uuid_exist=False)
            self.vw_check_message_in_rhsm_log("%s|%s|%s|%s" % (host_hwuuid, host_name_sec, host_uuid_sec, host_hwuuid_sec), message_exists=False)
            # (2) Set hypervisor_id=hostname, and fitler_host_uuids, it will show host/guest name mapping info
            self.set_hypervisor_id_filter_host_uuids("rhevm", "hostname", host_name)
            self.vw_check_mapping_info_in_rhsm_log(host_name, guest_uuid)
            self.vw_check_message_in_rhsm_log("%s|%s|%s|%s|%s" % (host_uuid, host_hwuuid, host_name_sec, host_uuid_sec, host_hwuuid_sec), message_exists=False)
            # (3) Set hypervisor_id=hwuuid, and fitler_host_uuids, it will show host/guest hwuuid mapping info
            self.set_hypervisor_id_filter_host_uuids("rhevm", "hwuuid", host_hwuuid)
            self.vw_check_mapping_info_in_rhsm_log(host_hwuuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_name, uuid_exist=False)
            self.vw_check_message_in_rhsm_log("%s|%s|%s|%s" % (host_uuid, host_name_sec, host_uuid_sec, host_hwuuid_sec), message_exists=False)
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

            # (1) Set hypervisor_id=uuid, and fitler_host_uuids, it will show host/guest uuid mapping info
            self.set_hypervisor_id_filter_host_uuids("hyperv", "uuid", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
#             self.vw_check_message_in_rhsm_log(hyperv_host_name, message_exists=False)
            # (2) Set hypervisor_id=hostname, and fitler_host_uuids, it will show host/guest name mapping info
            self.set_hypervisor_id_filter_host_uuids("hyperv", "hostname", hyperv_host_name)
            self.vw_check_mapping_info_in_rhsm_log(hyperv_host_name, guest_uuid)
            self.vw_check_message_in_rhsm_log(host_uuid, message_exists=False)
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
            esx_host_ip_second = self.get_vw_cons("ESX_HOST_SECOND")
            esx_host_name_second = self.esx_get_hostname(esx_host_ip_second)
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            host_uuid_second = self.esx_get_host_uuid(esx_host_ip_second)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            self.set_hypervisor_id_filter_host_uuids("esx", "uuid", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_second, uuid_exist=False)
            self.set_hypervisor_id_filter_host_uuids("esx", "hostname", esx_host_name)
            self.vw_check_mapping_info_in_rhsm_log(esx_host_name, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(esx_host_name_second, uuid_exist=False)
            # self.set_hypervisor_id_filter_host_uuids("esx", "hwuuid", host_uuid)
            # do not know how to get hwuuid of esx, just check "host-" here
            # self.vw_check_mapping_info_in_rhsm_log("host-", guest_uuid)
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
