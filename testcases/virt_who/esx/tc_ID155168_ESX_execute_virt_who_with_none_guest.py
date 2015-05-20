from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155168_ESX_execute_virt_who_with_none_guest(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            host_uuid = self.esx_get_host_uuid(destination_ip)
            self.esx_remove_guest(guest_name, destination_ip)
            # restart virt-who service
            self.vw_restart_virtwho()
            # check log info in rhsm.log with none guest
            cmd = "sleep 30; tail -1 /var/log/rhsm/rhsm.log"
            expected_info = "Sending update in hosts-to-guests mapping: {%s: []}" % host_uuid
            (ret, output) = self.runcmd(cmd, "check log info in rhsm.log with none guest")
            if ret == 0 and expected_info in output:
                logger.info("Succeeded to execute_virt_who_with_none_guest.")
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to execute_virt_who_with_none_guest.")
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.esx_add_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
