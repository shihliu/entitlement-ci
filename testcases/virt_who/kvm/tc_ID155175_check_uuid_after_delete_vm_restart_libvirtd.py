import time
from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155175_check_uuid_after_delete_vm_restart_libvirtd(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1)check if the uuid is exist before .
            self.vw_restart_virtwho()
            self.vw_check_uuid(guestuuid, uuidexists=True)
            # (2) Restart libvirtd service  
            self.vw_restart_libvirtd()
            time.sleep(10)
            # (3) undefine a guest    
            self.vw_undefine_guest(guest_name)
            # (4)check if the uuid is not exist after undefine guest.
            self.vw_check_uuid(guestuuid, uuidexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # self.shutdown_vm(guest_name)
            self.vw_define_all_guests()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
