from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID475862_VDSM_check_running_mode(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            rhsmlogfile = "/var/log/rhsm/rhsm.log"

            # check running mode 
            if self.get_os_serials() == "7":
                cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
                ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f")
                # ignore restart virt-who serivce since virt-who -b -d will stop
                self.vw_restart_virtwho_new()
                time.sleep(10)
                cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
                ret, output = self.runcmd(cmd, "get log number added to rhsm.log")
            else: 
                self.vw_restart_virtwho_new()
                cmd = "tail -3 %s " % rhsmlogfile
                ret, output = self.runcmd(cmd, "check output in rhsm.log")
            if ret == 0:
                if "Sending domain info" in output or "Sending list of uuids: " in output or " Sending update in hosts-to-guests mapping:" in output:
                    if 'Using configuration "env/cmdline" ("vdsm" mode)' in output:
                        logger.info("Succeeded to check running mode from rhsm.log.")
                    else:
                        raise FailException("Test Failed - Failed check running mode from rhsm.log.")
                else :
                    raise FailException("Test Failed - Failed to check host/guest mapping info")
            else:
                raise FailException("Failed to get rhsm.log")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
