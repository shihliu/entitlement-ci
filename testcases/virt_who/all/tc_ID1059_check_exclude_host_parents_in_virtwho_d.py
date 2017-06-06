from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1059_check_exclude_host_parents_in_virtwho_d(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.runcmd_service("stop_virtwho")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.vw_define_guest(guest_name)
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()

            # (1) Set Filter_hosts_parents, it will show error info,it will filter host/guest mapping info
            self.set_exclude_host_parents("libvirt", "host_parents", remote_ip_2)
            self.vw_check_message_in_rhsm_log("exclude_host_parents is not supported in libvirt mode, ignoring it", message_exists=True, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1) Set Filter_hosts_parents, it will show error info,it will filter host/guest mapping info
            self.set_exclude_host_parents("rhevm", "host_parents")
            self.vw_check_message_in_rhsm_log("exclude_host_parents is not supported in rhevm mode, ignoring it", message_exists=True)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")

            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()

            # (1) Set Filter_hosts_parents, it will show error info,it will filter host/guest mapping info
            self.set_exclude_host_parents("hyperv", "host_parents")
            self.vw_check_message_in_rhsm_log("exclude_host_parents is not supported in hyperv mode, ignoring it", message_exists=True)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
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
            esx_host_ip_second = self.get_vw_cons("ESX_HOST_SECOND")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            host_uuid_second = self.esx_get_host_uuid(esx_host_ip_second)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            host_parents_list = self.get_host_parents_list("esx")
            host_parents = host_parents_1 = host_parents_2 = host_parents_3 = ""
            for host_parent in host_parents_list:
                host_parents = host_parents + "\"%s\"," % host_parent
                host_parents_1 = host_parents_1 + "\"%s\"," % host_parent
                host_parents_2 = host_parents_2 + "\'%s\'," % host_parent
                host_parents_3 = host_parents_3 + "\"%s\", " % host_parent
            self.set_exclude_host_parents("esx", host_parents)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.set_exclude_host_parents("esx", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.set_exclude_host_parents("esx", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.set_exclude_host_parents("esx", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.set_exclude_host_parents("esx", host_parents_1)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.set_exclude_host_parents("esx", host_parents_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.set_exclude_host_parents("esx", host_parents_3)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)

            self.xen_start_guest(guest_name, xen_host_ip)

            # (1) Set Filter_hosts_parents, it will show error info,it will filter host/guest mapping info
            self.set_exclude_host_parents("xen", "host_parents")
            self.vw_check_message_in_rhsm_log("exclude_host_parents is not supported in xen mode, ignoring it", message_exists=True)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
            self.xen_stop_guest(guest_name, xen_host_ip)
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
