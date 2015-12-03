from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID417575_VDSM_validate_thread_with_diff_interval(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            # (1) Set virt-who interval to 1 then check virt-who thread
            self.update_rhel_vdsm_configure(1)
            self.vw_restart_virtwho()
            self.check_virtwho_thread()
            self.vw_restart_virtwho()
            self.check_virtwho_thread()
            # (2) Set virt-who interval to 10 then check virt-who thread
            self.update_rhel_vdsm_configure(10)
            self.vw_restart_virtwho()
            self.check_virtwho_thread()
            self.vw_restart_virtwho()
            self.check_virtwho_thread()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.update_rhel_vdsm_configure(5)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
