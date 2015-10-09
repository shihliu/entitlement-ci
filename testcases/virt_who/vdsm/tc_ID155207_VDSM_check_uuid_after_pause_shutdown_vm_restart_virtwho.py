import time
from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID155207_VDSM_check_uuid_after_pause_shutdown_vm_restart_virtwho(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = self.get_vw_cons("RHEVM_HOST")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            self.rhevm_start_vm(guest_name, rhevm_ip)

            # (1) Restart virt-who and libvirtd service.
            self.vw_restart_virtwho_new()

            # Check guest's uuid and guest's attribute 
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid)
            # (2) pause guest    
            self.rhevm_pause_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            # (3) resume guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid)
            # (4) stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
