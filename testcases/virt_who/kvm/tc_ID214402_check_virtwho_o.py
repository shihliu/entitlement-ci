from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID214402_check_virtwho_o(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_stop_virtwho_new()

            cmd = "virt-who -o -d"
            ret, output = self.runcmd(cmd, "run virt-who -o -d command")
            if ret == 0 :
                if ("Sending domain info" in output or "Sending list of uuids" in output) and guestuuid in output and "ERROR" not in output:
                    logger.info("Succeeded to check virt-who output when virt-who run at one-shot mode.")
                else:
                    raise FailException("Failed to check virt-who output when virt-who run at one-shot mode.")
            else:
                raise FailException("Failed to run virt-who -o -d.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # stop virt-who command line mode
            self.vw_restart_virtwho()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
