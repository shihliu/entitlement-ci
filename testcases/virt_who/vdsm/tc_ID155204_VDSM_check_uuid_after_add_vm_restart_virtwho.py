import time
from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155204_VDSM_check_uuid_after_add_vm_restart_virtwho(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = VIRTWHOConstants().get_constant("RHEVM_HOST")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # (1) stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            # (2) Restart libvirtd service
            self.update_rhevm_vdsm_configure(2)
            # (3) start guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
