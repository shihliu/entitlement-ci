from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17199_check_default_config(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_start_guests(guest_name)

            # (1) Set virt-who config to default.
            self.update_config_to_default()
            # (2) Check if debug info is not show on virt-who log.
            self.vw_check_message_in_rhsm_log("1 guests found", message_exists=True)
            # (3) Check debug info is not exist on virt-who log.
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            # (4) Check virt-who processes and virt-who service status.
            self.check_virtwho_thread()
            self.vw_check_virtwho_status()
            # (5) Stop virt-who service and check virt-who processes.
            self.vw_stop_virtwho_new()
            self.check_virtwho_null_thread()
            # (6) Run virt-who commond line, check debug info is not exist on virt-who log.
            self.vw_check_message_in_debug_cmd("virt-who", "DEBUG|ERROR", message_exists=False)
            # (7) Run virt-who commond line, check guest uuid exist on virt-who log.
            self.vw_check_message_in_debug_cmd("virt-who", "Sending update in guests lists for config|using libvirt as backend", message_exists=True)
            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_stop_guests(guest_name)
            self.update_vw_configure()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
