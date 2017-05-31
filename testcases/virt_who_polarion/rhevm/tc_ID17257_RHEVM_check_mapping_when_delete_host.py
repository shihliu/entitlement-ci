from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17257_RHEVM_check_mapping_when_delete_host(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            host_name = get_exported_param("REMOTE_IP")
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            host_name_sec = get_exported_param("REMOTE_IP_2")
            host_uuid_sec = self.get_host_uuid_on_rhevm(get_exported_param("REMOTE_IP_2"), rhevm_ip)

            # (1) Delete host2, check host2/guest mapping info is not exist
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.rhevm_mantenance_host(host_name_sec, rhevm_ip)
            self.rhevm_delete_host(host_name_sec, rhevm_ip)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, uuid_exist=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # Readd host2, make sure host2 has been added to rhevm
            self.rhevm_add_host(host_name_sec, get_exported_param("REMOTE_IP_2"), rhevm_ip)
            self.update_vm_to_host(guest_name, host_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
