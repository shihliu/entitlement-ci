from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537053_bug_715096_rhel_for_sap_applications_only_available_for_x86_64(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_sap")
                password = self.get_rhsm_cons("password_sap")
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_register(username, password)
                self.sub_autosubscribe(autosubprod)

                # list installed product to check if sap product is installed
                if not self.check_sap_installed():
                    logger.info("It's successful to check no sap product installed")
                else:
                    raise FailException("Test Failed - Failed to check no sap product installed")

                # install SAP package
                self.install_pkg('compat-locales-sap')

                # list installed product to check if sap product is installed
                if self.check_sap_installed():
                    logger.info("It's successful to check sap product installed")
                else:
                    raise FailException("Test Failed - Failed to check sap product installed")
                
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_pkg('compat-locales-sap')
                self.remove_sap_product()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_sap_installed(self):
        cmd = "subscription-manager list --installed"
        sap_installed = False
        (ret, output) = self.runcmd(cmd, "check installed")
        if ret == 0:
            if 'Red Hat Enterprise Linux for SAP' in output:
                sap_installed = True
            logger.info("It's successful to check installed")
            return sap_installed
        else:
            raise FailException("Test Failed - Failed to check installed")

    def remove_sap_product(self):
        cmd = "rm -rf /etc/pki/product/*"
        (ret, output) = self.runcmd(cmd, "check installed")
        if ret == 0:
            logger.info("It's successful to remove sap product")
        else:
            raise FailException("Test Failed - Failed to remove sap product")

if __name__ == "__main__":
    unittest.main()
