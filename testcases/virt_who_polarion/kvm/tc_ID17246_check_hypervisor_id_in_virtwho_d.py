from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17246_check_hypervisor_id_in_virtwho_d(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
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
            self.vw_check_message_in_rhsm_log("Reporting of hypervisor hwuuid is not implemented in libvirt backend", message_exists=True, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
