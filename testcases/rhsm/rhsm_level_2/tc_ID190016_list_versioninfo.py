from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190016_list_versioninfo(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # list version of subscription-manager pythonrhsm and candlepin
            cmd = "subscription-manager version"
            (ret, output) = self.runcmd(cmd, "list version info")
            if (ret == 0) and ('subscription management server' in output) and ('subscription-manager' in output) and ('python-rhsm' in output):
                resultoutput = output.splitlines()
                for lineoutput in resultoutput:
                    tempoutput = lineoutput.strip().split(':')
                    if (tempoutput[0].strip() == "server type" and tempoutput[1].strip() == "Red Hat Subscription Management") or re.match('^[0-9]', tempoutput[1].strip()) is not None:
                        pass
                    else:
                        raise FailException("Test Failed - Failed to list the version of remote entitlment server.")
                logging.info("It's successful to list version info by running version command.")
            else:
                raise FailException("Test Failed - Failed to list the version info by running version command.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
