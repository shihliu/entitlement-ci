from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID147222_check_healing_attribute_of_consumer(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # get baseurl
            if self.test_server == "SAM":
                server_hostname = get_exported_param("SERVER_HOSTNAME")
                baseurl = "https://" + server_hostname + "/sam/api"
            elif self.test_server == "SATELLITE":
                server_hostname = get_exported_param("SERVER_HOSTNAME")
                baseurl = "https://" + server_hostname + "/rhsm"
            elif self.test_server == "STAGE":
                baseurl = "https://" + self.get_rhsm_cons("hostname") + ":443/subscription"

            # get consumerid
            cmd = "subscription-manager identity | grep identity"
            (ret, output) = self.runcmd(cmd, "get consumerid")
            consumerid = output.split(':')[1].strip()
            # call check consumer info by api
            cmd = "curl --insecure --cert /etc/pki/consumer/cert.pem --key /etc/pki/consumer/key.pem %s/consumers/%s >/root/temp; sleep 10" % (baseurl, consumerid)
            (ret, output) = self.runcmd(cmd, "get curl return to /root/temp")
            cmd = "cat /root/temp"
            (ret, output) = self.runcmd(cmd, "check curl return in /root/temp")
            if ret == 0 and '"autoheal":true' in output:
                logger.info("It's successful to check the healing attribute of consumer is true.")
            else:
                raise FailException("Test Failed - Failed to check the healing attribute of consumer is true.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()



