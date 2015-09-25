from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID165512_VDSM_validate_double_fork(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = VIRTWHOConstants().get_constant("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = VIRTWHOConstants().get_constant("RHEVM_HOST")
            slave_machine_ip = get_exported_param("REMOTE_IP_2")

            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)

            # (1) check guest uuid is exist.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            # (2) Check guest uuid is exist after restart virt-who on another host
            self.vw_restart_virtwho_new(slave_machine_ip)
            self.vw_check_uuid(guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
