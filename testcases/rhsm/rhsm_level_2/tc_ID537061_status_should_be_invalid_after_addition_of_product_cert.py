from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537061_status_should_be_invalid_after_addition_of_product_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # check product status, it should be valid
            self.check_system_status_from_server(username, password, 'valid')

            # add new product cert
            self.add_new_product_cert()

            # check product status, it should be valid
            self.check_system_status_from_server(username, password, 'valid')

            # restart rhsmcerd
            self.restart_rhsmcertd()

            # wait 2 mins
            time.sleep(120)

            # check product status, it should be invalid
            self.check_system_status_from_server(username, password, 'invalid')

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rm_new_product_cert()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_system_status_from_server(self, username, password, check_value):
        system_uuid = self.cm_get_consumerid()
        if self.test_server == "STAGE":
            system_uuid = self.get_hostname()
            info_key = 'entitlementStatus'
        elif self.test_server == 'SAM':
            info_key = 'status'
        elif self.test_server == 'SATELLITE':
            info_key = 'subscription_status_label'
        if check_value == self.server_system_info(info_key, system_uuid, username, password):
            logger.info("It's successful to check system status from server side is %s"%check_value)
        else:
            raise FailException("Test Failed - Failed to check system status from server side is %s"%check_value)

if __name__ == "__main__":
    unittest.main()
