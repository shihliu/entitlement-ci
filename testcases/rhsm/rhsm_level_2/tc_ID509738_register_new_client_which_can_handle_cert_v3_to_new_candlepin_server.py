from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509738_register_new_client_which_can_handle_cert_v3_to_new_candlepin_server(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            entitlementcerts=self.get_entitlementcerts_list()
            firstcert = entitlementcerts.split(' ')[0]
            cmd = "rct cat-cert --no-content --no-product /etc/pki/entitlement/%s"%firstcert
            (ret, output) = self.runcmd(cmd, "get certs version")
            if ret == 0 and 'Version: 3.' in output:
                logger.info("It's successful to check cert v3 in entitlement cert")
            else:
                raise FailException("Test Failed - Failed to check cert v3 in entitlement cert")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
