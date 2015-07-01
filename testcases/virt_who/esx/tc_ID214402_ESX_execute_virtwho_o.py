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
            if ret == 0 and "DEBUG" in output and "ERROR" not in output:
                logger.info("Succeeded to execute virt-who with one-shot mode.")
            else:
                raise FailException("Failed to execute virt-who with one-shot mode.")

            # (3)Check the status of virt-who
            # if 'virt-who -o -d' finished, 'ps -ef' shoud can't show any virt-who process because the one-shot mode! 
            cmd = "ps -ef | grep -E 'virtwho|virt-who'"
            ret, output = self.runcmd(cmd, "check the process of virt-who with one-shot mode")
            if ret == 0  and "virtwho.py -o -d" not in output:
                logger.info("All the virt-who processes exit successfully!")
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to stop virt-who process.")

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
