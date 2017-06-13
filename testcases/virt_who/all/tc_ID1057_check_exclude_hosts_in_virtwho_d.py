from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1057_check_exclude_hosts_in_virtwho_d(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.runcmd_service("stop_virtwho")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.vw_define_guest(guest_name)
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()
            host_uuid_sec = "test"

            # (1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("libvirt", host_uuid, remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("libvirt", host_uuid_sec, remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "\"\"", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "\'\'", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
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
            host_uuid_sec = "test"
            self.config_option_disable("VIRTWHO_LIBVIRT")

            # (1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("libvirt", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("libvirt", host_uuid_sec)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
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
            host_uuid_sec = self.get_host_uuid_on_rhevm(get_exported_param("REMOTE_IP_2"), rhevm_ip)

            # (1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("rhevm", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("rhevm", host_uuid_sec)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("rhevm", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("rhevm", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("rhevm", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("rhevm", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, guest_uuid, uuid_exist=False)
            # (7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("rhevm", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, guest_uuid, uuid_exist=False)
            # (8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("rhevm", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, guest_uuid, uuid_exist=False)
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
            host_uuid_sec = "test"

            # (1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("hyperv", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("hyperv", host_uuid_sec)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("hyperv", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("hyperv", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("hyperv", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("hyperv", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("hyperv", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("hyperv", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
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
            self.set_exclude_host_uuids("esx", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.set_exclude_host_uuids("esx", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.set_exclude_host_uuids("esx", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.set_exclude_host_uuids("esx", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.set_exclude_host_uuids("esx", "\"%s\",\"%s\"" % (host_uuid, host_uuid_second))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_second, guest_uuid, uuid_exist=False)
            self.set_exclude_host_uuids("esx", "\'%s\',\'%s\'" % (host_uuid, host_uuid_second))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_second, guest_uuid, uuid_exist=False)
            self.set_exclude_host_uuids("esx", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_second))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_second, guest_uuid, uuid_exist=False)
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
            host_uuid_sec = "test"

            self.xen_start_guest(guest_name, xen_host_ip)

            # (1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("xen", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("xen", host_uuid_sec)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("xen", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("xen", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("xen", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("xen", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("xen", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("xen", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
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
