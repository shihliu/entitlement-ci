from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID202507_ESX_verify_virtwho_interval(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            #1). stop virt-who firstly 
            self.service_command("stop_virtwho")

            #2). config the virt-who config file
            cmd = "sed -i 's/^#VIRTWHO_INTERVAL/VIRTWHO_INTERVAL/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "uncomment VIRTWHO_INTERVAL firstly in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to uncomment VIRTWHO_INTERVAL.")
            else:
                raise FailException("Failed to uncomment VIRTWHO_INTERVAL.")

            cmd = "sed -i 's/^VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=5/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "changing interval time in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=5.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=5.")

            #3). after stop virt-who, start to monitor the rhsm.log 
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")

            #4). virt-who restart
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running with interval time 5.")
            else:
                raise FailException("Failed to check, virt-who is not running or active with interval time 5.")

            #5). after restart virt-who, stop to monitor the rhsm.log
            time.sleep(20)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parse")
            if ret == 0 and output is not None and  "ERROR" not in output:
                count = re.findall(r'Sending update in hosts-to-guests mapping:', output)
                if len(count) >= 3 and len(count) <=5:
                    logger.info("Succeeded to check the log added.")
                else:
                    raise FailException("Failed to check the log added.")
            else:
                raise FailException("Failed to check the log added.")

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
