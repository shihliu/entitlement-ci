from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID155199_VDSM_check_uuid_after_pause_shutdown_vm_auto_assigned(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            orig_host_name = self.get_hostname(get_exported_param("REMOTE_IP"))
            dest_host_ip = get_exported_param("REMOTE_IP_2")
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            self.rhevm_start_vm(guest_name, rhevm_ip)

            # (1) Restart virt-who service.
            # Check guest's uuid and guest's attribute 
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid)
            # (2) stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            # (3) Auto assigned vm to host2
            self.rhevm_mantenance_host(orig_host_name, rhevm_ip)
            # (4) resume guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who on host1 and host2
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid, targetmachine_ip=dest_host_ip)
            # (5) pause guest    
            self.rhevm_pause_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=dest_host_ip)
            # (6) Active host1
            self.rhevm_active_host(orig_host_name, rhevm_ip)
            # (7) start guest, guest move back to host1    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who on host1 and host2
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=dest_host_ip)
            self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # Active host1
            self.rhevm_active_host(orig_host_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
