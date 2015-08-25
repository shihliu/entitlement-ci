from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID147222_check_healing_attribute_of_consumer(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # get baseurl
            sever_hostname = get_exported_param("SERVER_HOSTNAME")
            samhostip = get_exported_param("SERVER_IP")
            server_type = get_exported_param("SERVER_TYPE")

            if server_type == "SAM":
                baseurl = "https://" + sever_hostname + "/sam/api"
            elif server_type == "SATELLITE":
                baseurl = "https://" + sever_hostname + "/rhsm"

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



