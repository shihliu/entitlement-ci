from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID82526_HYPERV_check_mapping_in_sec_config(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")

            # (1) Disable hyperv mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_HYPERV")
            # (2) Config hyperv mode in /etc/virt-who.d
            self.set_virtwho_sec_config("hyperv")
            self.vw_check_mapping_info_number_in_rhsm_log()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_hyperv_conf()
            self.unset_all_virtwho_d_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
