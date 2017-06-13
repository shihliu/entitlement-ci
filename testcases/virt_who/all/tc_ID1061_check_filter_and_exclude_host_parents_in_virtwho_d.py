from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1061_check_filter_and_exclude_host_parents_in_virtwho_d(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.runcmd_service("stop_virtwho")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.vw_define_guest(guest_name)
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()

            # (1) Set Filter_host_parents and exclude_host_parentss, it will show error info,it will filter host/guest mapping info
            self.set_filter_exclude_host_parents("libvirt", "host_parents_filter", "host_parents_exclude", remote_ip_2)
            chkmsg = "filter_host_parents is not supported in libvirt mode, ignoring it|exclude_host_parents is not supported in libvirt mode, ignoring it"
            self.vw_check_message_in_rhsm_log(chkmsg, message_exists=True, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            guest_uuid = self.vw_get_uuid(guest_name, remote_ip_1)

            self.runcmd_service("stop_virtwho")
            self.vw_define_guest(guest_name, remote_ip_1)
            host_uuid = self.get_host_uuid(remote_ip_1)
            self.config_option_disable("VIRTWHO_LIBVIRT")

            # (1) Set Filter_host_parents and exclude_host_parentss, it will show error info,it will filter host/guest mapping info
            self.set_filter_exclude_host_parents("libvirt", "host_parents_filter", "host_parents_exclude")
            chkmsg = "filter_host_parents is not supported in libvirt mode, ignoring it|exclude_host_parents is not supported in libvirt mode, ignoring it"
            self.vw_check_message_in_rhsm_log(chkmsg, message_exists=True)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
            self.unset_all_virtwho_d_conf()
            self.config_option_enable("VIRTWHO_LIBVIRT")
            self.runcmd_service("restart_virtwho")
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

            # (1) Set Filter_host_parents and exclude_host_parents, it will show error info,it will filter host/guest mapping info
            self.set_filter_exclude_host_parents("rhevm", "host_parents_filter", "host_parents_exclude")
            chkmsg = "filter_host_parents is not supported in rhevm mode, ignoring it|exclude_host_parents is not supported in rhevm mode, ignoring it"
            self.vw_check_message_in_rhsm_log(chkmsg, message_exists=True)
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

            # (1) Set Filter_host_parents and exclude_host_parentss, it will show error info,it will filter host/guest mapping info
            self.set_filter_exclude_host_parents("hyperv", "host_parents_filter", "host_parents_exclude")
            chkmsg = "filter_host_parents is not supported in hyperv mode, ignoring it|exclude_host_parents is not supported in hyperv mode, ignoring it"
            self.vw_check_message_in_rhsm_log(chkmsg, message_exists=True)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.skipTest("test case skiped, not fit for esx ...")
        finally:
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

            # (1) Set Filter_host_parents and exclude_host_parentss, it will show error info,it will filter host/guest mapping info
            self.set_filter_exclude_host_parents("xen", "host_parents_filter", "host_parents_exclude")
            chkmsg = "filter_host_parents is not supported in xen mode, ignoring it|exclude_host_parents is not supported in xen mode, ignoring it"
            self.vw_check_message_in_rhsm_log(chkmsg, message_exists=True)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
#             self.xen_stop_guest(guest_name, xen_host_ip)
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
