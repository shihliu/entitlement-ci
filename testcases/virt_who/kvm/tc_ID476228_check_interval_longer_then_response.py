from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID476228_check_interval_longer_then_response(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            rhsmlogfile = "/var/log/rhsm/rhsm.log"

            # stop virt-who service on host1
            self.vw_stop_virtwho_new()
            cmd = "sed -i 's/.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=30/g' /etc/sysconfig/virt-who"
            ret, output = self.runcmd(cmd, "changing interval time in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=30.")
            else:
                logger.error("Failed to set VIRTWHO_INTERVAL=30.")

            # check if the guest uuid is correctly monitored by virt-who. '''
            if self.get_os_serials() == "7":
                cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
                ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f")
                # ignore restart virt-who serivce since virt-who -b -d will stop
                self.vw_restart_virtwho_new()
                time.sleep(65)
                cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
                ret, output = self.runcmd(cmd, "get log number added to rhsm.log")
            else: 
                self.vw_restart_virtwho_new()
                cmd = "tail -3 %s " % rhsmlogfile
                ret, output = self.runcmd(cmd, "check output in rhsm.log")
            if ret == 0:
                if "Sending list of uuids: " in output:
                    cmd = "killall -9 tail ; grep 'Sending list of uuids' /tmp/tail.rhsm.log | wc -l "
                    ret, output = self.runcmd(cmd, "get log number added to rhsm.log")
                    tointer = int(output)
                    logger.info("Sending list of uuids in rhsm.log, update %s times." % tointer)
                elif "Sending update to updateConsumer: " in output:
                    cmd = "killall -9 tail ; grep 'Sending update to updateConsumer' /tmp/tail.rhsm.log | wc -l "
                    ret, output = self.runcmd(cmd, "get log number added to rhsm.log")
                    tointer = int(output)
                    logger.info("Sending list of uuids in rhsm.log, update %s times." % tointer)
                elif "Sending domain info" in output:
                    cmd = "grep 'Sending domain info' /tmp/tail.rhsm.log | wc -l "
                    ret, output = self.runcmd(cmd, "get log number added to rhsm.log")
                    tointer = int(output)
                    logger.info("Sending list of uuids in rhsm.log, update %s times." % tointer)
                elif "Sending update in hosts-to-guests mapping" in output:
                    cmd = "killall -9 tail ; grep 'Sending update in hosts-to-guests mapping' /tmp/tail.rhsm.log | wc -l "
                    ret, output = self.runcmd(cmd, "get log number added to rhsm.log")
                    tointer = int(output)
                    logger.info("Sending list of uuids in rhsm.log, update %s times." % tointer)
                else:
                    raise FailException("Test Failed -Failed to get send domain info from rhsm.log")
            else:
                raise FailException("Failed to get rhsm.log")
            if tointer == 3:
                logger.info("Succeeded to check the refresh interval.")
            else:
                raise FailException("Test Failed -Failed to check the refresh interval.")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.clean_remote_libvirt_conf()
            self.unset_virtwho_d_conf('/tmp/tail.rhsm.log')
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
