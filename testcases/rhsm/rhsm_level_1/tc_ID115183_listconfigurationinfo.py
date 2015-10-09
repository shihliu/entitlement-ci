from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID115183_listconfigurationinfo(RHSMBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                # list configuration info for the system
                cmd = "subscription-manager config --list"
                (ret, output) = self.runcmd(cmd, "list configuration info")
                if (ret == 0) and ("server" in output) and ("rhsm" in output) and ("rhsmcertd" in output):
                    if self.is_configuration_item_correct(output):
                        logger.info("It's successful to list configuration info for the system.")
                    else: 
                        raise FailException("Test Failed - List configuration info are not correct.")
                else: 
                    raise FailException("Failed to List configuration info.")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def is_configuration_item_correct(self, output):
        flag = False
        cmd = "cat /etc/rhsm/rhsm.conf | grep '^hostname'"
        (ret_hn, output_hn) = self.runcmd(cmd, "check hostname configuration")
        cmd = "cat /etc/rhsm/rhsm.conf | grep '^baseurl'"
        (ret_bu, output_bu) = self.runcmd(cmd, "check baseurl configuration")
        if ret_hn == 0 and output_hn.split("=")[1].strip() in output and ret_bu == 0 and output_bu.split("=")[1].strip() in output:
            flag = True
        return flag

if __name__ == "__main__":
    unittest.main()
