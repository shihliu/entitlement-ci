from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID338068_VDSM_check_execute_virtwho_o_overtime(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = self.get_vw_cons("RHEVM_HOST")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.vw_stop_virtwho_new()

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # run cmd virt-who with -o and -d option in the host five times
            for i in range(1, 5):
                cmd = "virt-who -o -d --vdsm"
                ret, output = self.runcmd(cmd, "run virt-who -o -d --vdsmcommand")
                if ret == 0 and ("Sending domain info" in output or "Sending list of uuids" in output) and "ERROR" not in output:
                    logger.info("Succeeded to execute virt-who with one-shot mode.")
                    # check if the uuid is correctly monitored by virt-who.
                    if guestuuid in output:
                        logger.info("Successed to check guest uuid when virt-who at one-shot mode")
                    else:
                        raise FailException("Failed to check guest uuid when virt-who at one-shot mode")
                else:
                    raise FailException("Failed to run virt-who -o -d.")
                logger.info("Run virt-who at one-shot mode at the %s time" % i)
                i = i + 1

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # stop virt-who command line mode
            self.vw_restart_virtwho_new()
            # stop vm
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
