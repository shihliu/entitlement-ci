from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17202_VDSM_check_oneshot_function_by_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            for i in range(1, 5):
                self.vw_check_mapping_info_number("virt-who --vdsm -o -d", 1)
            self.check_virtwho_null_thread()

            self.assert_(True, case_name)
        except Exception, e:
            self.runcmd_service("restart_virtwho")
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
