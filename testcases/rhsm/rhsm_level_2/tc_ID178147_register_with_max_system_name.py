"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178147_register_with_max_system_name(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            name249 = 'qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert1234'
            name250 = 'qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345'

            # register use system name with max characters(249)
            cmd_register = "subscription-manager register --username=%s --password='%s' --name=%s" % (username, password, name249)
            (ret, output) = self.runcmd(cmd_register, "register with max system name")
            if ret == 0 and 'The system has been registered with ID' in output:
                logger.info("It's successful to register with max system name")
            else:
                raise FailException("Test Failed - error happened when register with max system name")

            # unregister when system has registered using system name with max characters(249)
            cmd_unregister = "subscription-manager unregister"
            (ret, output) = self.runcmd(cmd_unregister, "unregister when system has registered using system name with max characters(249)")
            if ret == 0 and 'System has been unregistered' in output:
                logger.info("It's successful to unregister after system has registered using system name with max system name")
            else:
                raise FailException("Test Failed - error happened when unregister system") 

            # clean client data
            cmd_clean = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd_clean, "clean client data")
            if (ret == 0) and ("All local data removed" in output):
                logger.info("It's successful to run subscription-manager clean")
            else:
                raise FailException("Test Failed - error happened when run subscription-manager clean")

            # re-register with max characters(>=250)
            cmd_register = "subscription-manager register --username=%s --password='%s' --name=%s" % (username, password, name250)
            (ret, output) = self.runcmd(cmd_register, "register with max characters(>=250)")
            if (ret != 0) and ("Name of the unit must be shorter than 250 characters" in output):
                logger.info("It's successful to verify that registeration with max characters(>=250) should not succeed")
            else:
                raise FailException("Test Failed - error happened when re-register with max characters(>=250)")
  
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
