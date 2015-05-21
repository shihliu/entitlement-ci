from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID214402_ESX_execute_virtwho_o(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # (1)stop virt-who service
            self.vw_stop_virtwho()
            # (2)Execute virt-who in the one-shot mode.
            cmd = "virt-who -o -d"
            ret, output = self.runcmd(cmd, "executing virt-who with one-shot mode")
            if ret == 0 :
                # check the status of virt-who
                cmd = "ps -ef | grep virt-who"
                ret, output = self.runcmd(cmd, "check the process of virt-who with one-shot mode")
                if ret == 0 and "DEBUG" in output and "ERROR" not in output:
                    logger.info("Succeeded to execute virt-who with one-shot mode.")
                    self.assert_(True, case_name)
                else:
                    raise FailException("Failed to execute virt-who with one-shot mode.")
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
