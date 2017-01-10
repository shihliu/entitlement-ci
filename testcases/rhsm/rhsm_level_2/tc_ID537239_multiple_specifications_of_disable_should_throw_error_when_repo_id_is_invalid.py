from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537239_multiple_specifications_of_disable_should_throw_error_when_repo_id_is_invalid(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Disable invalid repo
            info1 = "Error: \'huey\' does not match a valid repository ID. Use \"subscription-manager repos --list\" to see valid repositories."
            info2 = "Error: \'duey\' does not match a valid repository ID. Use \"subscription-manager repos --list\" to see valid repositories."
            info3 = "Error: \'luey\' does not match a valid repository ID. Use \"subscription-manager repos --list\" to see valid repositories."
            cmd = "subscription-manager repos --disable=huey --disable=duey --enable=luey"
            (ret, output) = self.runcmd(cmd, "Disable invalid repo")
            if ret != 0 and info1 in output and info2 in output and info3 in output:
                logger.info("It's successful to check error to tell invalid repo")
            else:
                raise FailException("Test Failed - Failed to check error to tell invalid repo")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
