from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException
import string

class tc_ID115184_modifyconfigitemvalue(RHSMBase):
    modinsecure = 1
    modproxyport = 500
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                cmd = "subscription-manager config --server.insecure=%s --server.proxy_port=%s" % (self.modinsecure, self.modproxyport)
                (ret, output) = self.runcmd(cmd, "modify configuration info")
                if ret == 0:
                    if self.is_configuration_modified(output):
                        logger.info("It's successful to modify configuration info for the system.")
                    else:
                        raise FailException("Test Failed - failed to modify the configuration")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.remove_current_config()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def get_system_configuration(self):
        cmd = "subscription-manager config --list"
        (ret, output) = self.runcmd(cmd, "get system configuration")
        if ret == 0:
            return output
            logger.info("It's successful to list config info")
        else :
            raise FailException("Failed to List system configuration info.")

    def is_configuration_modified(self, output):
        flag = False
        modified_config = self.get_system_configuration()
        numsec = string.count(modified_config, 'insecure = %s' % self.modinsecure)
        numpp = string.count (modified_config, 'proxy_port = %s' % self.modproxyport)
        if numsec == 1 and numpp == 1:
            flag = True
            logger.info("It's successful to verify modified configration")
        return flag

    def remove_current_config(self):
        cmd = "subscription-manager config --remove server.insecure --remove server.proxy_port"
        self.runcmd(cmd, "remove current configuration")
        logger.info("It's successful to remove current configuration")

if __name__ == "__main__":
    unittest.main()
