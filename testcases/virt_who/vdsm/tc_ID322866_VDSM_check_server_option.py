from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID322866_VDSM_check_server_option(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            # start a guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # stop virt-who service on host1
            self.vw_stop_virtwho_new()

            # check option of --satellite6 and --sam
            if self.test_server == "SATELLITE":
                cmd = "virt-who --vdsm --satellite6 -o -d"
                ret, output = self.runcmd(cmd, "run --satellite6 in CLI")
                if ret == 0 and guestuuid in output:
                    logger.info("Succeeded to check --satellite6 option")
                else:
                    raise FailException("Test Failed - Failed to check --satellite6 option")
            else:
                cmd = "virt-who --vdsm --sam -o -d"
                ret, output = self.runcmd(cmd, "run --sam in CLI")
                if ret == 0 and guestuuid in output:
                    logger.info("Succeeded to check --sam option")
                else:
                    raise FailException("Test Failed - Failed to check --sam option")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_restart_virtwho_new()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
