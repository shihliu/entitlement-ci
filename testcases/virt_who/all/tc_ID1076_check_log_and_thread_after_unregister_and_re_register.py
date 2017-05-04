from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1076_check_log_and_thread_after_unregister_and_re_register(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            # (1).Unregister host,check virt-who log and threads
            cmd_unreg = "subscription-manager unregister"
            self.vw_check_message_in_rhsm_log("BadStatusLine|Interrupted system call", message_exists=False, checkcmd=cmd_unreg)
            self.check_virtwho_thread(1)
            # (2).Register host,check virt-who log and threads
            cmd_reg = "subscription-manager register --username=%s --password=%s" % (SERVER_USER, SERVER_PASS)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd=cmd_reg)
            self.check_virtwho_thread(1)
            self.assert_(True, case_name)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
