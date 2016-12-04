from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID267328_access_cdn_with_revoked_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.check_and_backup_yum_repos()
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            autosubprod = self.get_rhsm_cons("autosubprod")
            pkgtoinstall = self.get_rhsm_cons("pkgtoinstall")
            # register to and auto-attach
            self.register_and_autosubscribe(username, password)
            # unregister
            self.sub_unregister()
            # install a pkg
            cmd = "yum install -y %s" % (pkgtoinstall)
            (ret, output) = self.runcmd(cmd, "install selected package %s" % pkgtoinstall)
            if ret == 1:
                logger.info("It's successful to verify that system cannot access CDN contents through thumbslug with revoked cert")
            else:
                raise FailException("Test Failed - failed to verify that system cannot access CDN contents through thumbslug with revoked cert")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.uninstall_givenpkg(pkgtoinstall)
            self.restore_repos()
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def register_and_autosubscribe(self, username, password):
        cmd = "subscription-manager register --username=%s --password=%s --auto-attach --force" % (username, password)
        (ret, output) = self.runcmd(cmd, "register_and_autosubscribe")
        if (ret == 0) and ("The system has been registered with ID:" in output) and ('Not Subscribe' not in output) and ("Subscribed" in output):
            logger.info("It's successful to register and auto-attach")
        else:
            raise FailException("Test Failed - failed to register or auto-attach.")

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
