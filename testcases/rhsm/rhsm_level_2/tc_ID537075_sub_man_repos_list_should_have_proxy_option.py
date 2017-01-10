from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537075_sub_man_repos_list_should_have_proxy_option(RHSMBase):
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

                # Check the --proxy related parameters exit on "subscription-manager repos"
                cmd = "subscription-manager repos --help | grep proxy"
                (ret, output) = self.runcmd(cmd, "check proxy related parameters")
                if ret == 0 and '--proxy=PROXY_URL' in output and '--proxyuser=PROXY_USER' in output and '--proxypassword=PROXY_PASSWORD' in output:
                    return output.strip()
                    logger.info("It's successful to check proxy related parameters")
                else:
                    raise FailException("Test Failed - Failed to check proxy related parameters")

                # compare repos --list between proxy and no-proxy
                cmd = 'subscription-manager repos --list'
                (ret1, output1) = self.runcmd(cmd, "repos --list without proxy option")
                cmd = 'subscription-manager repos --list --proxy=file.bne.redhat.com:3128'
                (ret2, output2) = self.runcmd(cmd, "repos --list without proxy option")
                if ret1 == ret2 ==0 and output1 == output2:
                    logger.info("It's successful to verify that repos --list remains same with/without proxy option")
                else:
                    raise FailException("Test Failed - Failed to verify repos --list between proxy and no-proxy")

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
