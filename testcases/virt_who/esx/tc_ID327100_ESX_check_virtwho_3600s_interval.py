from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID327100_ESX_check_virtwho_3600s_interval(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            #1).config the virt-who config file
            cmd = "sed -i 's/^#VIRTWHO_INTERVAL/VIRTWHO_INTERVAL/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "uncomment VIRTWHO_INTERVAL firstly in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to uncomment VIRTWHO_INTERVAL.")
            else:
                raise FailException("Failed to uncomment VIRTWHO_INTERVAL.")

            cmd = "sed -i 's/^VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=3600/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "changing interval time in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=3600.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=3600.")

            #2).restart virt-who service
            self.vw_restart_virtwho_new()

            #3).write log to /tmp/tail.rhsm.log
            time.sleep(10)
            cmd = "nohup tail -f -n 0 /var/log/rhsm/rhsm.log > /tmp/tail.rhsm.log 2>&1 &"
            self.runcmd(cmd, "got temp file /tmp/tail.rhsm.log")

            #3).after 900s, check /tmp/tail.rhsm.log, the log shouldn't be created 
            time.sleep(900)
            cmd = "grep 'Sending update in hosts-to-guests mapping' /tmp/tail.rhsm.log"
            (ret, output) = self.runcmd(cmd, "check log message is created or not.")
            if ret !=0:
                logger.info("Succeeded to check, still no log created.")
            else:
                raise FailException("Failed to check, the log shouldn't be created.")

            #4).after 3610s, check /tmp/tail.rhsm.log, the log should be created
            time.sleep(3610)
            cmd = "grep 'Sending update in hosts-to-guests mapping' /tmp/tail.rhsm.log"
            (ret, output) = self.runcmd(cmd, "check log message is created or not.")
            if ret ==0:
                logger.info("Succeeded to check, the log is created.")
            else:
                raise FailException("Failed to check, the log is still not created.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            cmd = "sed -i 's/VIRTWHO_INTERVAL=5/#VIRTWHO_INTERVAL=0/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "restoring the interval time as default setting in virt-who config file")

            cmd = "rm /tmp/tail.rhsm.log"
            (ret, output) = self.runcmd(cmd, "remove /tmp/tail.rhsm.log file generated")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
