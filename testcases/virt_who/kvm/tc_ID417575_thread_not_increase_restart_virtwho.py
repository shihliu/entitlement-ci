from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID417575_thread_not_increase_restart_virtwho(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.vw_restart_virtwho()
            self.check_virtwho_thread()
            self.vw_restart_virtwho()
            self.check_virtwho_thread()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_virtwho_thread(self):
        ''' check virt-who thread number '''
        cmd = "ps -ef | grep -v grep | grep virt-who | wc -l"
        ret, output = self.runcmd(cmd, "check virt-who thread")
        if ret == 0 and output.strip() == "1":
            logger.info("Succeeded to check virt-who thread number is 1.")
        else:
            raise FailException("Test Failed - Failed to check virt-who thread number is 1.")

if __name__ == "__main__":
    unittest.main()
