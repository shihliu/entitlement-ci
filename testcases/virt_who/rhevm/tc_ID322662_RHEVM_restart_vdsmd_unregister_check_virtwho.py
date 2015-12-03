from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID322662_RHEVM_restart_vdsmd_unregister_check_virtwho(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            # restart virtwho service
            self.vw_restart_virtwho()
            # restart vdsmd service
            self.vw_restart_vdsm_new()
            # Unregister the host 
            self.sub_unregister()
            # check virt-who status
            self.vw_check_virtwho_status()
            # check libvirtd status
            self.vw_check_vdsm_status()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
