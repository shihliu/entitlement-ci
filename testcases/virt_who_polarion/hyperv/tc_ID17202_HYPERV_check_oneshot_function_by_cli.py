from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17202_HYPERV_check_oneshot_function_by_cli(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            #(1) Check h/g mapping info show only once when run "virt-who --hyperv -o -d"
            #also check virt-who threads will not increase after run "-o -d" many times
            cmd = self.virtwho_cli("hyperv") + " -o -d"
            for i in range(1, 5):
                self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_null_thread()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
