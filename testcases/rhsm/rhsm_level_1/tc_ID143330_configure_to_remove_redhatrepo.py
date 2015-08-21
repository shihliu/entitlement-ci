from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import time

class tc_ID143330_configure_to_remove_redhatrepo(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            if not self.skip_satellite():
                # [A] - prepare test env
                # register to server
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.sub_register(username, password)
                # auto subscribe to a pool
                autosubprod = RHSMConstants().get_constant("autosubprod")
                self.sub_autosubscribe(autosubprod)
                # [B] - run the test
                # list available repos
                cmd = "subscription-manager repos --list"
                (ret, output) = self.runcmd(cmd, "list available repos")
                productrepo = RHSMConstants().get_constant("productrepo")
                betarepo = RHSMConstants().get_constant("betarepo")
                if ret == 0 and productrepo in output and betarepo in output:
                    logger.info("It's successful to list available repos.")
                else:
                    raise FailException("Test Failed - Failed to list available repos.")
                # check redhat.repo existed in repo dir
                self.is_redhatrepo_exist(True)
                # configure to remove redhat.repo
                self.configure_to_handle_redhatrepo("off")
                # do a list to make disable work at once
                cmd = "subscription-manager repos --list"
                (ret, output) = self.runcmd(cmd, "list available repos")
                if ret == 0 and "Repositories disabled by configuration." in output:
                    logger.info("It's successful to verify no repo listed after configure to remove redhat.repo")
                else:
                    raise FailException("Test Failed - Failed to disable available repos")
                # check redhat.repo file be deleted
                self.is_redhatrepo_exist(False)
                self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.configure_to_handle_redhatrepo("on")
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def configure_to_handle_redhatrepo(self, switch):
        # configure to remove/add redhat.repo
        if switch == "off":
            cmd = "subscription-manager config --rhsm.manage_repos=0"
        else:
            cmd = "subscription-manager config --rhsm.manage_repos=1"
        (ret, output) = self.runcmd(cmd, "configure manage_repos")
        if ret == 0:
            logger.info("It's successful to configure option rhsm.manage_repos to %s." % switch)
        else:
            raise FailException("Test Failed - Failed to configure option rhsm.manage_repos to %s." % switch)
        # restart rhsmcertd service and wait for one minute
        cmd = "service rhsmcertd restart"
        (ret, output) = self.runcmd(cmd, "restart rhsmcertd service")
        if output.count("OK") == 2 or "Redirecting to /bin/systemctl restart  rhsmcertd.service" in output:
            logger.info("It's successful to restart rhsmcertd service.")
            logger.info("Waiting 240 seconds for rhsmcertd service to take effect...")
            time.sleep(240)
        else:
            raise FailException("Test Failed - Failed to restart rhsmcertd service.")

    def is_redhatrepo_exist(self, expectbool):
        # check redhat.repo file exist or not
        cmd = "ls /etc/yum.repos.d/"
        (ret, output) = self.runcmd(cmd, "check redhat.repo exist")
        if not expectbool :
            existed = output.count("bak") == output.count("redhat.repo")
        else:
            existed = not (output.count("bak") == output.count("redhat.repo"))
        if ret == 0 and existed:
            logger.info("It's successful to check redhat.repo file exist: %s." % expectbool)
        else:
            raise FailException("Test Failed - Failed to delete redhat.repo file.")

if __name__ == "__main__":
    unittest.main()







