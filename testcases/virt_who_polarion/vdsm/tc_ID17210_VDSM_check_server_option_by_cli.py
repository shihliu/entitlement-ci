from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17210_VDSM_check_server_option_by_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            server_type = get_exported_param("SERVER_TYPE")
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.runcmd_service("stop_virtwho")

            if server_type == "SAM":
                self.vw_check_mapping_info_number("virt-who -o -d --vdsm --sam", 1)
            elif server_type == "SATELLITE":
                self.vw_check_mapping_info_number("virt-who -o -d --vdsm --satellite6", 1)
            else:
                logger.info("it is %s mode, needn't to run this command" %server_type)
            self.check_virtwho_thread(0)

            self.assert_(True, case_name)
        except Exception, e:
            self.runcmd_service("restart_virtwho")
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
