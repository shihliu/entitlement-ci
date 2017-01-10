from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537419_list_consumed_should_report_blank_not_none_when_no_contract_account_number(RHSMBase):
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

                # check contract account by rct from ent certs
                certs = self.get_entitlementcerts_list()
                accou_value = self.check_ent_cert(certs, 'Account')
                contr_value = self.check_ent_cert(certs, 'Contract')
                if accou_value == 'Account:' and contr_value == 'Contract:':
                    logger.info("It's successful to check number blank by rct")
                else:
                    raise FailException("Test Failed - Failed to check number blank by rct")

                # list consumed
                accou_value = self.check_consumed('Account')
                contr_value = self.check_consumed('Contract')
                if accou_value == 'Account:' and contr_value == 'Contract:':
                    logger.info("It's successful to check number blank in consumed")
                else:
                    raise FailException("Test Failed - Failed to check number blank in consumed")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_facts_value()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_ent_cert(self, certs, values):
        cmd = "rct cat-cert /etc/pki/entitlement/%s | grep %s"%(certs, values)
        logger.info(cmd)
        (ret, output) = self.runcmd(cmd, "check number")
        if ret == 0:
            return output.strip()
            logger.info("It's successful to check number blank by rct")
        else:
            raise FailException("Test Failed - Failed to check number blank by rct")

    def check_consumed(self, values):
        cmd = "subscription-manager list --consumed| grep %s"%values
        (ret, output) = self.runcmd(cmd, "check number")
        if ret == 0:
            return output.strip()
            logger.info("It's successful to check number blank in consumed")
        else:
            raise FailException("Test Failed - Failed to check number blank in consumed")	

if __name__ == "__main__":
    unittest.main()
