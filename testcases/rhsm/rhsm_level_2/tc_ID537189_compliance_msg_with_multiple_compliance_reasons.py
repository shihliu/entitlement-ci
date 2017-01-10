from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537189_compliance_msg_with_multiple_compliance_reasons(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
                self.sub_register(username, password)

                # auto-attach
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # change facts to make partial subscribed
                facts_value = "echo \'{\"uname.machine\":\"x390\",\"virt.is_guest\": \"False\",\"cpu.core(s)_per_socket\":\"8\", \"memory.memtotal\":\"40000000000\"}\' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update"
                self.set_facts(facts_value) 

                # check list installed status
                msg1 = 'Status:         Partially Subscribed'
                msg2 = 'Only supports 32GB of'
                msg3 = 'Supports architecture x86_64,ppc64le,ppc64,ia64,aarch64,ppc,s390,x86,s390x but the system is x390.'
                msga = 'Supports architecture x86_64,ppc64le,ppc64,ia64,ppc,x86,s390,s390x but the system is x390.'
                msg4 = 'Only supports 4 of 8 cores.'
                cmd = 'subscription-manager list --installed'
                (ret, output) = self.runcmd(cmd, "list installed status details")
                if ret == 0 and msg1 in output and msg2 in output and (msg3 or msga in output) and msg4 in output:
                    logger.info("It's successful to list installed status details")
                else:
                    raise FailException("Test Failed - Failed to list installed status details")

                # check list consumed status
                msg5 = 'Supports architecture x86_64,ppc64le,ppc64,ia64,aarch64,ppc,s390,x86,s390x but the system is x390.'
                msgb = 'Supports architecture x86_64,ppc64le,ppc64,ia64,ppc,x86,s390,s390x but the system is x390.'
                msg6 = 'Only supports 4 of 8 cores'
                msg7 = 'Only supports 32GB of'
                cmd = 'subscription-manager list --consumed'
                (ret, output) = self.runcmd(cmd, "list consumed status details")
                if ret == 0 and (msg5 or msgb in output) and msg6 in output and msg7 in output:
                    logger.info("It's successful to list consumed status details")
                else:
                    raise FailException("Test Failed - Failed to list consumed status details")

                # check overall status
                msg8 = 'Overall Status: Insufficient'
                msg9 = 'Only supports 32GB of'
                msg10 = 'Supports architecture x86_64,ppc64le,ppc64,ia64,aarch64,ppc,s390,x86,s390x but the system is x390'
                msgc = 'Supports architecture x86_64,ppc64le,ppc64,ia64,ppc,x86,s390,s390x but the system is x390.'
                msg11 = 'Only supports 4 of 8 cores'
                cmd = 'subscription-manager status'
                (ret, output) = self.runcmd(cmd, "list consumed status details")
                if ret == 0 and msg8 in output and msg9 in output and (msg10 or msgc in output) and msg11 in output:
                    logger.info("It's successful to list overall status details")
                else:
                    raise FailException("Test Failed - Failed to list overall status details")

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
