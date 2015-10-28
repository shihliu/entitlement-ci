from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID141464_verify_consumer_deletion_from_server(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register to server
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            consumerid = self.cm_get_consumerid()
            # Delete the consumer from server
            self.server_remove_system(consumerid)

            # Check deleted consumer status
            cmd = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd, "check deleted consumer status")
            print "check output:\n", output

            if ret != 0:
                logger.info("It's successful to check deleted consumer status.")
            else:
                raise FailException("Test Failed - Failed to check deleted consumer status.")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error(str(e))
            raise FailException("Test Failed - error happened when verify consumer status after being deleted from server:" + str(e))
            self.assert_(False, case_name)

        finally:
            # clean local consumer and subscription data
            cmd = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd, "clean local data")
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % __name__)

if __name__ == "__main__":
    unittest.main()
