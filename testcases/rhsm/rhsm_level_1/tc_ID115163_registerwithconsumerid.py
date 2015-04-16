from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115163_registerwithconsumerid(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # get serialnumlist before remove local subscription data
            serialnumlist_pre = self.get_subscription_serialnumlist()
            # get uuid of consumer
            cmd = "subscription-manager identity | grep identity"
            (ret, output) = self.runcmd(cmd, "get the current identity")
            uuid = output.split(':')[1].strip()
            # remove all local consumer and subscription data
            cmd = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd, "clean local consumer and subscription data")
            if ret == 0 and "All local data removed" in output:
                logger.info("It's successful to remove local data")
            else:
                raise FailException("Test Failed - Failed to remove all local data.")
            # register with consumerid 
            cmd = "subscription-manager register --consumerid=%s --username=%s  --password=%s" % (uuid, username, password)
            (ret, output) = self.runcmd(cmd, "register with consumerid")
            successregister1 = "The system has been registered with id: %s" % uuid
            successregister2 = "The system has been registered with ID: %s" % uuid
            if ret == 0 and ((successregister2 in output) or (successregister1 in output)):
                logger.info("It's successful to register with consumerid")
            else:
                raise FailException("Test Failed - Failed to register with consumerid.")
            # get serialnumlist after register with consumerid
            serialnumlist_post = self.get_subscription_serialnumlist()
            if len(serialnumlist_post) == len(serialnumlist_pre) and (serialnumlist_post.sort() == serialnumlist_pre.sort()):
                logger.info("It's successful to download consumed subscription data")
            else:
                raise FailException("Test Failed - Failed to download consumed subscription.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
