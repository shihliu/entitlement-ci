from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537042_list_ram_info_in_entitlement_certificate(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Get entitlement certs
            cmd = 'ls /etc/pki/entitlement/ | grep -v key'
            (ret, output) = self.runcmd(cmd, "get ent cert")
            if ret == 0:
                entcert = output.strip().split('\n')[0]
                logger.info("It's successful to get entitlement cert")
            else:
                raise FailException("Test Failed - Failed to get entitlement cert")

            # check ram info in ent cert
            cmd = "rct cat-cert /etc/pki/entitlement/%s | grep RAM"%entcert
            (ret, output) = self.runcmd(cmd, "check ram info")
            if ret == 0 and 'RAM Limit:' in output:
                logger.info("It's successful to check ram info")
            else:
                raise FailException("Test Failed - Failed to check ram info")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
