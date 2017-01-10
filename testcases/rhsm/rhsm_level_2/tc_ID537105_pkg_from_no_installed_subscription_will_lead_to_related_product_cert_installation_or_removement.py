from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537105_pkg_from_no_installed_subscription_will_lead_to_related_product_cert_installation_or_removement(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_ha")
                password = self.get_rhsm_cons("password_ha")
                self.sub_register(username, password)

                # List available pools and attach it.
                pools = self.sub_list_availablepool_list()
                cmd = "subscription-manager attach --pool=%s"%pools[0]
                (ret, output) = self.runcmd(cmd, "attach pool")
                if ret == 0:
                    logger.info("It's successful to attach pool")
                else:
                    raise FailException("Test Failed - Failed to attach pool")

                # list installed product to check if sap product is installed
                if not self.check_ha_installed():
                    logger.info("It's successful to check no ha product installed")
                else:
                    raise FailException("Test Failed - Failed to check no ha product installed")

                # install SAP package
                self.install_pkg('ccs')

                # list installed product to check if sap product is installed
                if self.check_ha_installed():
                    logger.info("It's successful to check sap product installed")
                else:
                    raise FailException("Test Failed - Failed to check sap product installed")
                
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_pkg('ccs')
                self.remove_ha_product()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_ha_installed(self):
        cmd = "subscription-manager list --installed"
        sap_installed = False
        (ret, output) = self.runcmd(cmd, "check installed")
        if ret == 0:
            if 'Red Hat Enterprise Linux High Availability' in output:
                sap_installed = True
            logger.info("It's successful to check installed")
            return sap_installed
        else:
            raise FailException("Test Failed - Failed to check installed")

    def remove_ha_product(self):
        cmd = "rm -rf /etc/pki/product/*"
        (ret, output) = self.runcmd(cmd, "check installed")
        if ret == 0:
            logger.info("It's successful to remove sap product")
        else:
            raise FailException("Test Failed - Failed to remove sap product")

if __name__ == "__main__":
    unittest.main()
