"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID178111_register_with_auto_when_no_compatible_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        samhostip = get_exported_param("SERVER_IP")
        try:
            if samhostip == None:
                logger.info("This case is just for SAM, no need to test against other servers!")
            else:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                # create a new org without available subscriptions in SAM
                orgname = "test"
                self.create_sam_org(samhostip, orgname)
                # register and auto-attach by this account
                cmd_to_test = "subscription-manager register --username=%s --password='%s' --org=%s --auto-attach" % (username, password, orgname)
                (ret, output) = self.runcmd(cmd_to_test, "register with auto subscribe option")
                if (ret != 0) and ("The system has been registered with ID" in output) and ("Not Subscribed" in output) and ("Unable to find available subscriptions for all your installed products" in output):
                    logger.info("It's successful to verify registeration with auto subscribe option if there is no compatible subscription")
                else:
                    raise FailException("Test Failed -Failed to verify registeration with auto subscribe option if there is no compatible subscription")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # delete the newly created account
            self.delete_sam_org(samhostip, orgname)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def create_sam_org(self, samhostip, neworgname):
        cmd_create = "headpin -u admin -p admin org create --name=%s" % neworgname
        (ret, output) = self.runcmd_sam(cmd_create, '', samhostip)
        if ret == 0 and "Successfully created org" in output:
            logger.info("It's successful to create a new org in SAM server:%s" % neworgname)
        else:
            raise FailException("TestFailed - Failed to create a new org!")

    def delete_sam_org(self, samhostip, orgname):
        cmd_delete = "headpin -u admin -p admin org delete --name=%s" % orgname
        (ret, output) = self.runcmd_sam(cmd_delete, '', samhostip)
        if ret == 0 and "Successfully deleted org" in output:
            logger.info("It's successful to delete the org in SAM")
        else:
            raise FailException("Test Failed - error happened when delete the org in SAM")

if __name__ == "__main__":
    unittest.main()
