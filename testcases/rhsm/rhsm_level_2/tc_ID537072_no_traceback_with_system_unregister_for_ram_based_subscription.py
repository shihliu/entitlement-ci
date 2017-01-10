from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537072_no_traceback_with_system_unregister_for_ram_based_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # unregister and check rhsm.log
                checkcmd = 'subscription-manager unregister'
                tmp_file = '/tmp/rhsmlogfile'
                self.generate_tmp_log(checkcmd, tmp_file)

                cmd = 'grep -i traceback %s'%tmp_file
                (ret, output) = self.runcmd(cmd, "check traceback in rhsm.log")
                if ret != 0 and output.strip() == '':
                    logger.info("It's successful to check no traceback in rhsm.log when unregister")
                else:
                    raise FailException("Test Failed - Failed to check no traceback in rhsm.log when unregister")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                cmd = 'rm -f /etc/rhsm/facts/custom.facts;subscription-manager facts --update'
                (ret, output) = self.runcmd(cmd, "change ram facts")
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
