from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536762_subscribe_smart_management_via_cli(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_nocon")
                password = self.get_rhsm_cons("password_nocon")
                self.sub_register(username, password)
                facts_value = "echo \'{\"virt.is_guest\": \"True\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update"
                self.set_facts(facts_value)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # check product id
                cmd = 'for i in $(ls /etc/pki/entitlement/ | grep -v key.pem);do rct cat-cert /etc/pki/entitlement/$i; done | grep 69'
                (ret, output) = self.runcmd(cmd, "check product id")
                if ret == 0 and output.strip() == 'ID: 69':
                    logger.info("It's successful to check product id")
                else:
                    raise FailException("Test Failed - Failed to check product id")

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
