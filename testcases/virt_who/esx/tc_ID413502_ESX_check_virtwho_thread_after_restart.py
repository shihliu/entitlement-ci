from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID413502_ESX_check_virtwho_thread_after_restart(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            #). stop virt-who firstly 
            self.service_command("stop_virtwho")

            #). kill all virt-who process
            #cmd = "pidof virtwho.py | xargs kill 9"
            cmd = "kill 9 `ps -ef | grep virtwho.py -i | grep -v grep | awk '{print $2}'`"
            ret, output = self.runcmd(cmd, "kill all the process of virt-who.")
            if ret == 0:
                logger.info("Succeeded to kill virt-who process.")
            else:
                raise FailException("Failed to kill virt-who process.")

            #). restart virt-who and check the pid number
            for i in range(3):
                self.service_command("restart_virtwho")
                time.sleep(5)
                self.check_virtwho_thread()

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

