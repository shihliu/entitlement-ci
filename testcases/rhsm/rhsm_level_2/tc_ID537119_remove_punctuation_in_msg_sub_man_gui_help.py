#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537119_remove_punctuation_in_msg_sub_man_gui_help(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "export DISPLAY='127.0.0.1:1'; subscription-manager-gui --help"
            msg1 = 'Usage: subscription-manager-gui [OPTIONS]'
            msg2 = 'Options:'
            msg3 = '-h, --help  show this help message and exit'
            msg4 = '--register  launches the registration dialog on startup'
            (ret, output) = self.runcmd(cmd, "run subscription-manager-gui --help")
            if ret == 0 and msg1 in output and msg2 in output and msg3 in output and msg4 in output:
                logger.info("It's successful to verify the punctuation is removed")
            else:
                raise FailException("Test Failed - Failed to verify the punctuation is removed")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
