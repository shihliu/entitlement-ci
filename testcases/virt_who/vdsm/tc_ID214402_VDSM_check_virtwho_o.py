from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID214402_VDSM_check_virtwho_o(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            self.vw_stop_virtwho_new()
            self.rhevm_start_vm(guest_name, rhevm_ip)
            cmd = "virt-who -o -d --vdsm"
            ret, output = self.runcmd(cmd, "run virt-who -o -d command")
            if ret == 0 :
                if ("Sending domain info" in output or "Sending list of uuids" in output) and guestuuid in output and "ERROR" not in output:
                    logger.info("Succeeded to check virt-who output when virt-who run at one-shot mode.")
                else:
                    raise FailException("Failed to check virt-who output when virt-who run at one-shot mode.")
            else:
                raise FailException("Failed to run virt-who -o -d.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # stop vm and restart virt-who
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
