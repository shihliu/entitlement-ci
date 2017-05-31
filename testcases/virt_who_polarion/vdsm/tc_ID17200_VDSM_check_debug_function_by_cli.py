from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17200_VDSM_check_debug_function_by_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # (1) Run virt-who, check debug info is not exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.vw_check_message_in_debug_cmd("virt-who", "DEBUG|ERROR|%s" % guestuuid, message_exists=False)
            # (2) Run virt-who -d, check guest uuid and DEBUG exist on virt-who log.
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.runcmd_service("stop_virtwho")
            self.vw_check_message_in_debug_cmd("virt-who --vdsm -d", "%s|\"vdsm\" mode|DEBUG" % guestuuid, message_exists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
