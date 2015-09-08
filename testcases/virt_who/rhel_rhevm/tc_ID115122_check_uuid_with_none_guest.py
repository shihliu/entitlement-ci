from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID115122_check_uuid_with_none_guest(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            rhevm_ip = "10.66.79.83"
            cmd = "rhevm-shell -c  -E 'list vms'"
            ret, output = self.runcmd(cmd, "list vms in rhevm",rhevm_ip)
            if ret == 0 :
                print 
                logger.info("Succeeded to list vms in rhevm.")
            else:
                raise FailException("Failed to list vms in rhevm.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
