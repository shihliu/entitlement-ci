from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1039_check_mapping_after_restart_virtwho_and_rhsmcertd(VIRTWHOBase):
    def run_kvm(self):
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) Check host/guest mapping info is exist 
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (2) Check host/guest mapping has not update after restart rhsmcert
            self.vw_start_guests(guest_name)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="restart_rhsmcertd")
            # (3) Check host/guest mapping info is exist after restart virt-who 
            self.vw_check_uuid(guestuuid, uuidexists=True)
        finally:
            self.vw_stop_guests(guest_name)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # (1) Check host/guest mapping info is exist 
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (2) Check host/guest mapping has not update after restart rhsmcert
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="restart_rhsmcertd")
            # (3) Check host/guest mapping info is exist after restart virt-who 
            self.vw_check_uuid(guestuuid, uuidexists=True)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1) Check host/guest mapping info is exist 
            self.set_rhevm_conf()
            self.hypervisor_check_uuid(hostuuid, guestuuid)
#             self.vw_check_mapping_info_in_rhsm_log(hostuuid, guestuuid)
            # (2) Check host/guest mapping info is not exist after restart rhsmcert
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="restart_rhsmcertd")
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            guestuuid = self.hyperv_get_guest_guid(guest_name)
            hostuuid = self.hyperv_get_host_uuid()

            # (1) Check host/guest mapping info is exist 
            self.hypervisor_check_uuid(hostuuid, guestuuid)
            # (2) Check host/guest mapping has not update after restart rhsmcert
            self.hyperv_start_guest(guest_name)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="restart_rhsmcertd")
            # (3) Check host/guest mapping info is exist after restart virt-who 
            self.hypervisor_check_uuid(hostuuid, guestuuid)
        finally:
            self.hyperv_stop_guest(guest_name)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            self.set_esx_conf()
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="restart_rhsmcertd")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            guestuuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            hostuuid = self.xen_get_host_uuid(xen_host_ip)

            # (1) Check host/guest mapping info is exist 
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=False)
            # (2) Check host/guest mapping has not update after restart rhsmcert
            self.xen_start_guest(guest_name, xen_host_ip)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="restart_rhsmcertd")
            # (3) Check host/guest mapping info is exist after restart virt-who 
            self.hypervisor_check_uuid(hostuuid, guestuuid)
        finally:
            self.xen_stop_guest(guest_name, xen_host_ip)
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
