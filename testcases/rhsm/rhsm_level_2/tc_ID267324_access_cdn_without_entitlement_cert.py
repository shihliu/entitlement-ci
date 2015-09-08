from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID267324_access_cdn_without_entitlement_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.check_and_backup_yum_repos()
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            autosubprod = RHSMConstants().get_constant("autosubprod")
            pkgtoinstall = RHSMConstants().get_constant("pkgtoinstall")
            # register to and auto-attach
            self.register_and_autosubscribe(username, password, autosubprod)
            # remove all cert files under /etc/pki/entitlement/
            self.remove_ent_cert()
            # install a pkg
            cmd = "yum install -y %s" % (pkgtoinstall)
            (ret, output) = self.runcmd(cmd, "install selected package %s" % pkgtoinstall)
            if ret == 1:
                logger.info("It's successful to verify that system without entitlement certificates cannot access CDN  contents through thumbslug")
            else:
                raise FailException("Test Failed - failed to verify that system without entitlement certificates cannot access CDN  contents through thumbslug")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.uninstall_givenpkg(pkgtoinstall)
            self.restore_repos()
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

    def register_and_autosubscribe(self, username, password, autosubprod):
        cmd = "subscription-manager register --username=%s --password=%s --auto-attach" % (username, password)
        (ret, output) = self.runcmd(cmd, "register_and_autosubscribe")
        if (ret == 0) and ("The system has been registered with ID:" in output) and (autosubprod in output) and ("Subscribed" in output):
            logger.info("It's successful to register and auto-attach")
        else:
            raise FailException("Test Failed - failed to register or auto-attach.")

    def remove_ent_cert(self):
        cmd = "rm -f /etc/pki/entitlement/*"
        (ret, output) = self.runcmd(cmd, "remove all entitlement certs")
        if ret == 0:
            logger.info("It's successful to remove all entitlement certs")
        else:
            raise FailException("Test Failed - failed to remove entitlement cert")

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
