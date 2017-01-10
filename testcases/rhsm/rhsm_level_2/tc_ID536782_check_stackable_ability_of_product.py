from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536782_check_stackable_ability_of_product(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_socket")
                password = self.get_rhsm_cons("password_socket")
                self.sub_register(username, password)
                facts_value = "echo \'{\"virt.is_guest\": \"True\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update"
                self.set_facts(facts_value)
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

                # check stacking id in ent cert
                cmd = "rct cat-cert /etc/pki/entitlement/%s | grep tacking"%entcert
                (ret, output) = self.runcmd(cmd, "check stacking id")
                if ret == 0 and 'Stacking ID:' in output:
                    logger.info("It's successful to check stacking id")
                else:
                    raise FailException("Test Failed - Failed to check stacking id")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_facts_value()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
