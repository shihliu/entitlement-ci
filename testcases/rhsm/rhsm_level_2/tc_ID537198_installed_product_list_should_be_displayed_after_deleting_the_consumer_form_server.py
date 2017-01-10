from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537198_installed_product_list_should_be_displayed_after_deleting_the_consumer_form_server(RHSMBase):
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

            # Delete the consumer from server
            system_uuid = self.cm_get_consumerid()
            if self.test_server == "STAGE":
                system_uuid = self.get_hostname()
            server_ip = get_exported_param("SERVER_IP")
            self.server_remove_system(system_uuid, server_ip, self.get_rhsm_cons("username"), self.get_rhsm_cons("password"))

            # list the installed product
            cmd = 'subscription-manager list --installed'
            (ret, output) = self.runcmd(cmd, "list the installed product")
            if ret == 0 and ('Product Name:' in output and 'Product ID:' in output):
                logger.info("It's successful to list the installed product after delete consumer from server side")
            else:
                raise FailException("Test Failed - Failed to list the installed product after delete consumer from server side")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
