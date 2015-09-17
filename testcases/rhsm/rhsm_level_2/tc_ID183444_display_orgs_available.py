'''
@author           :soliu@redhat.com
@date             :2013-03-12
'''

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID183444_display_orgs_available(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        samhostip = get_exported_param("SERVER_IP")
        orgname2 = 'ACME_Corporation2'
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # check if the org ACME_Corporation2 exist on samserver
            is_multi_orgs = self.sam_remote_is_org_exist(samhostip, orgname2)
            # create another org if no multi-orgs env
            if not is_multi_orgs:
                self.sam_remote_create_org(samhostip, orgname2)
            # check the orgs in client
            cmd_display_orgs = "subscription-manager orgs --username=%s --password=%s" % (username, password)
            # step1:display the orgs available for a user
            (ret, output) = self.runcmd(cmd_display_orgs, "display orgs")
            if ret == 0:
                if "Name: ACME_Corporation" and "Name: ACME_Corporation2"in output:
                    logger.info("It is successful to display the multi-orgs avaiable for a user!")
                else:
                    raise FailException("Failed to display the multi-orgs available for a user!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sam_remote_delete_org(samhostip, orgname2)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
