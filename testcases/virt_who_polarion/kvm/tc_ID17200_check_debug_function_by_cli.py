from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17200_check_debug_function_by_cli(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) Run virt-who, check debug info is not exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.vw_check_message_in_debug_cmd("virt-who", "DEBUG|ERROR", message_exists=False)
            # (2) Run virt-who -d, check guest uuid and DEBUG exist on virt-who log.
            self.vw_check_message_in_debug_cmd("virt-who -d", "%s|using libvirt as backend|DEBUG" % guestuuid, message_exists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
