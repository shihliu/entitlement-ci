from utils import *
# from testcases.virt_who_polarion.vdsmbase import VDSMBase
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID82627_RHEVM_check_hypervisor_id_in_virtwho_d(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            rhevm_host_name = self.get_hostname(rhevm_ip)
            rhevm_host1_name = self.get_hostname(get_exported_param("RHEVM_HOST1_IP"))

            # (1) Set hypervisor_id=uuid, it will show uuid 
            self.set_hypervisor_id("rhevm", "uuid")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hypervisor_id=hostname, it will show hostname 
            self.set_hypervisor_id("rhevm", "hostname")
            self.vw_check_mapping_info_in_rhsm_log(rhevm_host1_name, guest_uuid)
            # (3) Set hypervisor_id=hwuuid, rhevm is not support hwuuid, it will report error
            self.set_hypervisor_id("rhevm", "hwuuid")
            self.vw_check_message_in_rhsm_log("Reporting of hypervisor hwuuid is not implemented in rhevm backend|Invalid option hwuuid for hypervisor_id", message_exists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
