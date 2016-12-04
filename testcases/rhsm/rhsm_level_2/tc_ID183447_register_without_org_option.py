'''
@author          :soliu@redhat.com
@date            :2013-03-12
'''

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID183447_register_without_org_option(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_unregister()
            cmd_register_without_org_option = "subscription-manager register --username=%s --password=%s" % (username, password)
            # step1:display the orgs available for a user
            (ret, output) = self.runcmd(cmd_register_without_org_option, "subscription-manager register without org option")
            if ret == 0:
                if "The system has been registered with ID" in output:
                    logger.info("It is successful to rigster without org option!")
                else:
                    raise FailException("Failed to register without org option!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
