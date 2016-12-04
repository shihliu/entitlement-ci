'''
author              :soliu@redhat.com
date                :2013-03-12
'''

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID183445_register_with_org(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            samhostip = get_exported_param("SERVER_IP")
            # unregister a system
            self.sub_unregister()
            # set up the multi-orgs env
            orgname2 = 'ACME_Corporation2'
            is_multi_orgs = self.sam_remote_is_org_exist(samhostip, orgname2)
            if not is_multi_orgs:
                self.sam_remote_create_org(samhostip, orgname2)
            # register with specified an org
            cmd_register_with_orgs = "subscription-manager register --org=ACME_Corporation --username=%s --password=%s" % (username, password)
            # step1:display the orgs available for a user
            (ret, output) = self.runcmd(cmd_register_with_orgs, "register with org option")
            if ret == 0:
                if "The system has been registered with ID" in output:
                    logger.info("It is successful to register with org option!")
                else:
                    raise FailException("Failed to register with org option!")
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



