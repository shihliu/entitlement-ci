#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509880_subscription_manager_gui_help_description_should_be_localized(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "export DISPLAY='127.0.0.1:1'; LANG=zh_CN.UTF-8 subscription-manager-gui --help"
            (ret, output) = self.runcmd(cmd, "run LANG=zh_CN.UTF-8 subscription-manager-gui --help")
            if ret == 0 and ("使用：subscription-manager-gui [选项]" in output) and ("-h, --help  显示此帮助信息并退出" in output) \
            and ("--register  启动时载入注册对话框" in output) :
                logger.info("subscription-manager-gui's help is localized")
            else:
                raise FailException("Test Failed - subscription-manager-gui's help is not localized")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
