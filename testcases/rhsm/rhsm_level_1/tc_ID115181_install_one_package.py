from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID115181_install_one_package(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_satellite():
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                # get variables form ent_env
                repoid = self.get_rhsm_cons("productrepo")
                pid = self.get_rhsm_cons("pid")
                pkgtoinstall = self.get_rhsm_cons("pkgtoinstall")
                # check repo exist
                if self.is_enabled_repo(repoid):
                    # check package to be installed exist
                    self.check_givenpkg_avail(repoid, pkgtoinstall)
                    # install test-pkg
                    self.install_givenpkg(pkgtoinstall)
                else:
                    raise FailException("Test Failed - The product repoid is not exist.")
                # check the cert file exist.
                certfile = pid + ".pem"
                self.check_cert_file(certfile)
                # check productid cert
                self.sub_checkproductcert(pid)
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.uninstall_givenpkg(pkgtoinstall)
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def is_enabled_repo(self, repoid):
        cmd = "yum repolist"
        (ret, output) = self.runcmd(cmd, "list enabled repos")
        if ret == 0 and "repolist:(\s+)0" in output:
            raise FailException("Test Failed - There is not enabled repo to list.")
        else:
            logger.info("It's successful to list enabled repos.")
        if repoid in output:
            return True
        else:
            return False

    def check_givenpkg_avail(self, repoid, testpkg):
        cmd = "repoquery -a --repoid=%s | grep %s" % (repoid, testpkg)
        (ret, output) = self.runcmd(cmd, "check package available")
        if ret == 0 and testpkg in output:
            logger.info("The package %s exists." % (testpkg)) 
        else:
            raise FailException("Test Failed - The package %s does not exist." % (testpkg))

    def uninstall_givenpkg(self, testpkg):
        cmd = "rpm -qa | grep %s" % (testpkg)
        (ret, output) = self.runcmd(cmd, "check if package %s is installed" % testpkg) 
        if ret != 0:
            logger.info("Package %s is not installed at all no need to uninstall it." % testpkg)
        else:
            cmd = "yum remove -y %s" % (testpkg)
            (ret, output) = self.runcmd(cmd, "remove select package %s" % testpkg)
            if ret == 0 and "Complete!" in output and "Removed" in output:
                logger.info("The package %s is uninstalled successfully." % (testpkg))
            else:
                raise FailException("Test Failed - The package %s is failed to uninstall." % (testpkg))

    def install_givenpkg(self, testpkg):
        self.uninstall_givenpkg(testpkg)
        cmd = "yum install -y %s" % (testpkg)
        (ret, output) = self.runcmd(cmd, "install selected package %s" % testpkg)
        if ret == 0 and "Complete!" in output and "Error" not in output:
            logger.info("The package %s is installed successfully." % (testpkg))
        else:
            raise FailException("Test Failed - The package %s is failed to install." % (testpkg))

    def check_cert_file(self, certfile):
        cmd = "ls -l /etc/pki/product*/%s" % certfile
        (ret, output) = self.runcmd(cmd, "check the product cert file exists")
        if ret == 0 :
            logger.info("It's successful to check product cert file exists.")
        else:
            raise FailException("Test Failed - it's failed to check product cert file exists.")

if __name__ == "__main__":
    unittest.main()
