from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import string

class tc_ID115185_removeconfigitemvalue(RHSMBase):
    modinsecure = 1
    modproxyport = 500

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # modify values of configuration item for the system
            # cmd="subscription-manager config --server.insecure=%s --server.proxy_port=%s --rhsm.insecure=%s --rhsm.proxy_port=%s --rhsmcertd.insecure=%s --rhsmcertd.proxy_port=%s"%(modinsecure, modproxyport, modinsecure, modproxyport, modinsecure, modproxyport)
            cmd = "subscription-manager config --server.insecure=%s --server.proxy_port=%s" % (self.modinsecure, self.modproxyport)
            (ret, output) = self.runcmd(cmd, "modify values of config items")
            if (self.is_configuration_modified()): 
                logger.info("Default values of configuration items(insecure and proxy_port) have been modified.")
                # remove values of configuration item for the system
                # cmd="subscription-manager config --remove server.insecure --remove server.proxy_port --remove rhsm.insecure --remove rhsm.proxy_port --remove rhsmcertd.insecure --remove rhsmcertd.proxy_port"
                cmd = "subscription-manager config --remove server.insecure --remove server.proxy_port"
                (ret, output) = self.runcmd(cmd, "remove values of config items")
                if ret == 0 and "You have removed the value for section" in output and "The default value for" in output:
                    if self.is_configuration_removed():
                        logger.info("It's successful to remove current values of configuration item for the system.")
                    else:
                        raise FailException("Test Failed - remove current values of configuration item are not correct.")
                else:
                    raise FailException("Failed to remove current values of configuration item.")
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
        else:
            raise FailException("Failed to List system configuration info.")

    def is_configuration_modified(self):
        flag = False
        modified_config = self.get_system_configuration()
        numsec = string.count(modified_config, 'insecure = %s' % self.modinsecure)
        numpp = string.count (modified_config, 'proxy_port = %s' % self.modproxyport)
        # if numsec == 3 and numpp == 3:
        if numsec == 1 and numpp == 1:
            flag = True
        return flag

    def is_configuration_removed(self):
        flag = False
        removed_config = self.get_system_configuration()
        numsec = string.count(removed_config, 'insecure = [0]')
        numpp = string.count (removed_config, 'proxy_port = []')
        if numsec == 1 and numpp == 1:
            flag = True
        return flag

    def remove_current_config(self):
        # remove modified value to default value
        # cmd="subscription-manager config --remove server.insecure --remove server.proxy_port --remove rhsm.insecure --remove rhsm.proxy_port --remove rhsmcertd.insecure --remove rhsmcertd.proxy_port"
        cmd = "subscription-manager config --remove server.insecure --remove server.proxy_port"
        self.runcmd(cmd, "remove values of config items")

if __name__ == "__main__":
    unittest.main()
