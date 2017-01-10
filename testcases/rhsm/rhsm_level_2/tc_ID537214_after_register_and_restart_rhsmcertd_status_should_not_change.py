from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537214_after_register_and_restart_rhsmcertd_status_should_not_change(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register and attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # add new product cert
            self.add_new_product_cert()

            # list the installed product
            installed1 = self.list_installed_product_cert()

            # restart rhsmcertd
            self.restart_rhsmcertd()

            # list the installed product
            installed2 = self.list_installed_product_cert()

            if installed1 == installed2:
                logger.info("It's successful to check installed status not change after restart rhsmcertd")
            else:
                raise FailException("Test Failed - Failed to check installed status not change after restart rhsmcertd")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rm_new_product_cert()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_installed_product_cert(self):
        output = None
        cmd = 'subscription-manager list --installed'
        (ret, output) = self.runcmd(cmd, "list installed product cert")
        return output
        if ret == 0:
            logger.info("It's successful to list installed product cert")
        else:
            raise FailException("Test Failed - Failed to list installed product cert")

if __name__ == "__main__":
    unittest.main()
