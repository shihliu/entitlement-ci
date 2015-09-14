"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178040_register_with_consumerID_and_other_account(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        samhostip = get_exported_param("SERVER_IP")
        usernamenew = "test456"
        passwordnew = "123456"
        emailnew = "test456@redhat.com"
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            if samhostip == None:
                logger.info("This case is just for SAM, no need to test against other servers!")
            else:
                self.sub_register(username, password)
                # record consumerid
                consumerid = self.sub_get_consumerid()
                # create a new account from SAM server
                self.create_sam_account(samhostip, usernamenew, passwordnew, emailnew)
                # clean client data
                cmd_clean = "subscription-manager clean"
                (ret, output) = self.runcmd(cmd_clean, "clean client data")
                if (ret == 0) and ("All local data removed" in output):
                    logger.info("It's successful to run subscription-manager clean")
                else:
                    raise FailException("Test Failed - error happened when run subscription-manager clean")
                # register with existing consumerid use new created account
                cmd_register = "subscription-manager register --username=test456 --password=123456 --consumerid=%s" % consumerid
                (ret, output) = self.runcmd(cmd_register, "register use different username and password")
                if (ret == 0) and ('The system has been registered with ID' in output):
                    logger.info("It's successful to verify that registration with existing consumerid using different account should succeed if the two accounts have same orgs")
                else:
                    raise FailException("Test Failed - error happened when register with existing consumerid using different account")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # delete the new account from SAM server
            self.delete_sam_account(samhostip, usernamenew)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def create_sam_account(self, samhostip, username, password, email):
        cmd_create = "headpin -u admin -p admin user create --username=%s --password=%s --email=%s;headpin -u admin -p admin user assign_role --username=%s --role=Administrator" % (username, password, email, username)
        (ret, output) = self.runcmd_remote(cmd_create, '', samhostip)
        if ret == 0 and "Successfully created user" in output:
            logger.info("It's successful to create a new account in SAM server:username=%s password=%s" % (username, password))
        else:
            raise FailException("TestFailed - Failed to create a new account!")

    def delete_sam_account(self, samhostip, username):
        cmd_delete = "headpin -u admin -p admin user delete --username=%s" % username
        (ret, output) = self.runcmd_remote(cmd_delete, '', samhostip)
        if ret == 0 and "Successfully deleted user [ test456 ]" in output:
            logger.info("It's successful to delete the username and password in SAM")
        else:
            raise FailException("Test Failed - error happened when delete the username and password in SAM")

if __name__ == "__main__":
    unittest.main()
