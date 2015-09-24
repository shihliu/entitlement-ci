from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID267326_access_unentitled_cdn_through_thumbslug(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.check_and_backup_yum_repos()
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            pkgtoinstall = RHSMConstants().get_constant("pkgtoinstall")
            # register to and auto-attach
            self.register_and_autosubscribe(username, password)
            # back up /etc/yum.repos.d/redhat.repo as /etc/yum.repos.d/redhat.repo.bak
            self.back_up_redhatrepo()
            # set all repos in /etc/yum.repos.d/redhat.repo to be disabled
            self.disable_all_repos()
            # install a pkg
            cmd = "yum install -y %s" % (pkgtoinstall)
            (ret, output) = self.runcmd(cmd, "install selected package %s" % pkgtoinstall)
            if ret == 1:
                logger.info("It's successful to verify that system cannot access unentitled CDN contents through thumbslug")
            else:
                raise FailException("Test Failed - failed to verify that system cannot access unentitled CDN contents through thumbslug")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.uninstall_givenpkg(pkgtoinstall)
            self.restore_redhat_repo()
            self.restore_repos()
            self.sub_unregister()
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def register_and_autosubscribe(self, username, password):
        cmd = "subscription-manager register --username=%s --password=%s --auto-attach --force" % (username, password)
        (ret, output) = self.runcmd(cmd, "register_and_autosubscribe")
        if (ret == 0) and ("The system has been registered with ID:" in output) and ('Not Subscribed' not in output) and ("Subscribed" in output):
            logger.info("It's successful to register and auto-attach")
        else:
            raise FailException("Test Failed - failed to register or auto-attach.")

    def back_up_redhatrepo(self):
        cmd = "yum repolist;cat /etc/yum.repos.d/redhat.repo > /etc/yum.repos.d/redhat.repo.bak"
        (ret, output) = self.runcmd(cmd, "back up redhat.repo")
        if ret == 0:
            logger.info("It's successful to back up redhat.repo file")
        else:
            raise FailException("Test Failed - failed to back up redhat.repo file")

    def disable_all_repos(self):
        cmd = "sed -i 's/enabled = 1/enabled = 0/g' /etc/yum.repos.d/redhat.repo"
        (ret, output) = self.runcmd(cmd, "disable_all_repos")
        if ret == 0:
            logger.info("It's successful to disable_all_repos")
        else:
            raise FailException("Test Failed - failed to disable_all_repos")

    def restore_redhat_repo(self):
        cmd = "rm -f /etc/yum.repos.d/redhat.repo;cat /etc/yum.repos.d/redhat.repo.bak > /etc/yum.repos.d/redhat.repo"
        (ret, output) = self.runcmd(cmd, "restore_redhat_repo")
        if ret == 0:
            logger.info("It's successful to restore_redhat_repo")
        else:
            raise FailException("Test Failed - failed to restore_redhat_repo")

    def uninstall_givenpkg(self, testpkg):
        cmd = "rpm -qa | grep %s" % (testpkg)
        (ret, output) = self.runcmd(cmd, "check package %s" % testpkg)
        if ret == 1:
            logger.info("There is no need to remove package")
        else:
            cmd = "yum remove -y %s" % (testpkg)
            (ret, output) = self.runcmd(cmd, "remove select package %s" % testpkg)
            if ret == 0 and "Complete!" in output and "Removed" in output:
                logger.info("The package %s is uninstalled successfully." % (testpkg))
            elif ret == 0 and "No package %s available" % testpkg in output:
                logger.info("The package %s is not installed at all" % (testpkg))
            else:
                raise FailException("Test Failed - The package %s is failed to uninstall." % (testpkg))

if __name__ == "__main__":
    unittest.main()
