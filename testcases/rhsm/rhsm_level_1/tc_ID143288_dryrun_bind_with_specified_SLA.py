from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID143288_dryrun_bind_with_specified_SLA(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # get baseurl
            sever_hostname = get_exported_param("SERVER_HOSTNAME")
            samhostip = get_exported_param("SERVER_IP")

            if self.test_server == "SAM":
                baseurl = "https://" + sever_hostname + "/sam/api"
            elif self.test_server == "SATELLITE":
                baseurl = "https://" + sever_hostname + "/rhsm"
            elif self.test_server == "STAGE":
                baseurl = "https://" + self.get_rhsm_cons("hostname") + ":443/subscription"

            # get consumerid
            cmd = "subscription-manager identity | grep identity"
            (ret, output) = self.runcmd(cmd, "get consumerid")
            consumerid = output.split(':')[1].strip()
            service_level = self.get_rhsm_cons("servicelevel")
            # call dry run bind to products by api
            cmd = "curl -k --cert /etc/pki/consumer/cert.pem --key /etc/pki/consumer/key.pem %s/consumers/%s/entitlements/dry-run?service_level=%s && echo \"\r\"" % (baseurl, consumerid, service_level)
            (ret, output) = self.runcmd(cmd, "dry run bind by products api")
            if ret == 0 and ('"value":"%s"' % service_level in output or '"value":"%s"' % (((service_level).lower()).upper()) in output):
                logger.info("It's successful to dry run bind by products api with a specified SLA.")
            else:
                raise FailException("Test Failed - Failed to dry run bind by products api with a specified SLA.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()




