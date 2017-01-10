from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537298_store_version_of_installed_products_in_candlepin(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # list the installed product
            cmd = 'subscription-manager list --installed | grep Version'
            (ret, output) = self.runcmd(cmd, "list the installed product from client")
            product_version = output.strip().split(":")[1].strip()
            if ret == 0:
                logger.info("It's successful to list the installed product version from client")
            else:
                raise FailException("Test Failed - Failed to list the installed product version from client")

            serverhostname = self.get_hostname_from_config()
            prefix = self.get_rhsm_cons("prefix")
            system_uuid = self.cm_get_consumerid()
            if self.test_server == "SAM" :
                cmd = "curl -k -u %s:%s https://%s:443/%s/systems/%s | python -mjson.tool "%(username, password, serverhostname, prefix, system_uuid)
            else:
                cmd = "curl -k -u %s:%s https://%s:443/%s/consumers/%s | python -mjson.tool "%(username, password, serverhostname, prefix, system_uuid)
            (ret, output) = self.runcmd(cmd, "get the installed product version from server")
            pdt_ver_server= '\"version\": \"%s\"'%product_version
            if ret == 0 and pdt_ver_server in output:
                logger.info("It's successful to check the installed product version on server are same with that on client")
            else:
                raise FailException("Test Failed - Failed to check the installed product version on server are same with that on client")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
