from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID417575_ESX_check_virtwho_thread_with_different_interval(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            #1). stop virt-who firstly 
            self.service_command("stop_virtwho")

            #2). kill all virt-who process
            #cmd = "pidof virtwho.py | xargs kill 9"
            cmd = "kill 9 `ps -ef | grep virtwho.py -i | grep -v grep | awk '{print $2}'`"
            ret, output = self.runcmd(cmd, "kill all the process of virt-who.")
            if ret == 0:
                logger.info("Succeeded to kill virt-who process.")
            else:
                raise FailException("Failed to kill virt-who process.")

            #3).config the virt-who config file, set VIRTWHO_INTERVAL=1, check pid
            self.config_virtwho_interval(1)
            self.service_command("restart_virtwho")
            time.sleep(5)
            self.check_virtwho_thread()

            #4).config the virt-who config file, set VIRTWHO_INTERVAL=3, check pid
            self.config_virtwho_interval(3)
            self.service_command("restart_virtwho")
            time.sleep(5)
            self.check_virtwho_thread()

            #5).config the virt-who config file, set VIRTWHO_INTERVAL=5, check pid
            self.config_virtwho_interval(5)
            self.service_command("restart_virtwho")
            time.sleep(5)
            self.check_virtwho_thread()

            #6).config the virt-who config file, set VIRTWHO_INTERVAL=10, check pid
            self.config_virtwho_interval(10)
            self.service_command("restart_virtwho")
            time.sleep(5)
            self.check_virtwho_thread()

            #7).config the virt-who config file, set VIRTWHO_INTERVAL=30, check pid
            self.config_virtwho_interval(30)
            self.service_command("restart_virtwho")
            time.sleep(5)
            self.check_virtwho_thread()

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_virtwho_interval(5)
            self.service_command("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

