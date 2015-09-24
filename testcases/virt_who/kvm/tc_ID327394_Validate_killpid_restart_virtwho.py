from utils import *
from testcases.virt_who.kvmbase import KVMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException
import commands, os, traceback, time, thread

class tc_ID327394_Validate_killpid_restart_virtwho(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            self.vw_stop_virtwho()

            thread.start_new_thread(self.stop_virt, (2, ))
            cmd = "virt-who -d "
            ret, output = self.runcmd(cmd, "run virt-who -d command")
            if "Sending domain info" in output:
                logger.info("Succeeded to check virt-who process.")
            else:
                logger.error("Failed to check virt-who process.")

            # restart virt-who service after kill all virt-who thread
            self.vw_restart_virtwho_new()
            self.vw_check_virtwho_status()
            self.vw_start_guests(guest_name)
            # Check guest's uuid and guest's attribute 
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid)
            # (2) pause guest    
            self.pause_vm(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 3, guestuuid)
            # (3) resume guest    
            self.resume_vm(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid)
            # (4) stop guest    
            self.vw_stop_guests(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 0, 'libvirt', 'QEMU', 5, guestuuid)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            #self.vw_stop_guests(guest_name)
            #cmd = "ps -ef|grep virt-who|cut -c 9-15|xargs kill -9"
            #ret, output = self.runcmd(cmd, "kill all virt-who thread")
            # stop virt-who command line mode
            self.vw_restart_virtwho()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def stop_virt(self, wait_sec):
        time.sleep(wait_sec)
        # kill all virt-who threads
        cmd = "ps -ef|grep virt-who|cut -c 9-15|xargs kill -9"
        ret, output = self.runcmd(cmd, "kill all virt-who thread")
        if "No such process" in output:
           logger.info("Succeeded to kill all virt-who thread.")
        else:
            logger.error("Failed to kill all virt-who thread %s.")
        thread.exit_thread() 

if __name__ == "__main__":
    unittest.main()


