from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536990_yum_install_pkg_from_old_repo_should_not_change_product_cert_to_old_version(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_satellite_check():
            try:
                # Register
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                os_serial = self.os_serial
                old_release = os_serial + '.1'
                latest_release = os_serial + 'Server'
                pkg = self.get_rhsm_cons("pkgtoinstall")

                # List installed product and record the output as out1
                out3 = self.list_installed()

                # Back up product cert to compare
                cmd = "mkdir /root/product; cp /etc/pki/product-default/69.pem /root/product"
                (ret, out1) = self.runcmd(cmd, "back up product cert")
                if ret == 0:
                    logger.info("It's successful to back up product cert")
                else:
                    raise FailException("Test Failed - Failed to back up product cert")

                # Change release version to old one
                self.set_release(old_release)

                # Install one package from old repo
                self.install_pkg(pkg)

                # List installed product and record the output as out2
                out2 = self.list_installed()

                # Compare the product certs
                cmd = 'diff /etc/pki/product-default/69.pem /root/product/*'
                (ret, output) = self.runcmd(cmd, "check cert change")

                if out3 == out2 and ret == 0 and output.strip() == '':
                    logger.info("It's successful to verify certs are the same without any change")
                else:
                    raise FailException("Test Failed - Failed to verify certs are the same without any change")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_pkg(pkg)
                self.remove_bkcert()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def set_release(self, releases):
        cmd = "subscription-manager release --set=%s"%releases
        (ret, output) = self.runcmd(cmd, "set release")
        if ret == 0:
            logger.info("It's successful to set release %s"%releases)
        else:
            raise FailException("Test Failed - Failed to set release %s"%releases)

    def remove_bkcert(self):
        cmd = 'rm -rf /root/product'
        (ret, output) = self.runcmd(cmd, "remove backup cert")
        if ret == 0:
            logger.info("It's successful to remove backup cert")
        else:
            raise FailException("Test Failed - Failed to remove backup cert")

    def list_installed(self):
        outputreturn = None
        cmd = "subscription-manager list --installed"
        (ret, outputreturn) = self.runcmd(cmd, "list installed")
        return outputreturn
        if ret == 0:
            logger.info("It's successful to list installed product")
        else:
            raise FailException("Test Failed - Failed to list installed product")

if __name__ == "__main__":
    unittest.main()
