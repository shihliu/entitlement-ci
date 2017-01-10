from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510157_subscription_management_server_is_displayed_regardless_of_registration(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # check if sm server is displayed before registration
            self.display_sm_server()

            # check if sm server is displayed after registration
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            self.display_sm_server()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def display_sm_server(self):
        cmd = "subscription-manager version"
        (ret, output) = self.runcmd(cmd, "list version info")
        out = output.splitlines()[1].split(':')[1]
        print 'out',out
        if re.match('^[0-9]', out.strip()) is not None:
            logger.info("It's successful to display subscription manager server version")
        else:
            raise FailException("Test Failed - Failed to display subscription manager server version")

if __name__ == "__main__":
    unittest.main()
