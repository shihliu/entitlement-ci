from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID202507_ESX_verify_virtwho_interval(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # config the virt-who config file
            cmd = "sed -i 's/#VIRTWHO_INTERVAL=0/VIRTWHO_INTERVAL=5/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "changing interval time in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=5.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=5.")
            # restart virt-who service
            self.vw_restart_virtwho()
            cmd = "nohup tail -f -n 0 /var/log/rhsm/rhsm.log > /tmp/tail.rhsm.log 2>&1 &"
            self.runcmd(cmd, "got temp file /tmp/tail.rhsm.log")
            time.sleep(23)
            cmd = "killall -9 tail ; grep 'Sending update in hosts-to-guests mapping' /tmp/tail.rhsm.log | wc -l "
            (ret, output) = self.runcmd(cmd, "get log number added to rhsm.log")
            if ret == 0 and int(output) == 4:
                logger.info("Succeeded to check the log added.")
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to check the log added.")
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





