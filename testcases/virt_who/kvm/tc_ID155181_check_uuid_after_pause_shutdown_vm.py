import time
from utils import *
from testcases.virt_who.kvmbase import KVMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155181_check_uuid_after_pause_shutdown_vm(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_start_guests(guest_name)

            # (1) Restart virt-who and libvirtd service.
            self.vw_restart_virtwho()
            # Check guest's uuid and guest's attribute 
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid)
            # (2) pause guest    
            self.pause_vm(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 3, guestuuid)
            # (3) resume guest    
            self.resume_vm(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid)
            # (4) stop guest    
            self.vw_stop_guests(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 0, 'libvirt', 'QEMU', 5, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
