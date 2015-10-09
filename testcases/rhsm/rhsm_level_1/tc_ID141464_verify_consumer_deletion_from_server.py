from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID141464_verify_consumer_deletion_from_server(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)

        # register to server
        username = self.get_rhsm_cons("username")
        password = self.get_rhsm_cons("password")
        self.sub_register(username, password)
        try:
            # get baseurl
            sever_hostname = get_exported_param("SERVER_HOSTNAME")
            samhostip = get_exported_param("SERVER_IP")
            server_type = get_exported_param("SERVER_TYPE")

            if server_type == "SAM":
                baseurl = "https://" + sever_hostname + "/sam/api"
            elif server_type == "SATELLITE":
                baseurl = "https://" + sever_hostname + "/rhsm"

            #if "8443" in baseurl:
             #   baseurl = baseurl + "/candlepin"
            #elif samhostip == None:
            #    baseurl = baseurl + "/subscription"
            #else:
            #    baseurl = baseurl + "/sam/api"

            # get consumerid
            cmd = "subscription-manager identity | grep identity"
            (ret, output) = self.runcmd(cmd, "get consumerid")
            consumerid = output.split(':')[1].strip()

            # Delete the consumer from candlepin server
            cmd = "curl -X DELETE -k -u %s:%s %s/consumers/%s" % (username, password, baseurl, consumerid)
            (ret, output) = self.runcmd(cmd, "delete consumer from candlepin server")
            if ret == 0:
                logger.info("It's successful to delete consumer from candlepin server.")
            else:
                raise FailException("Test Failed - Failed to delete consumer from candlepin server.")

            # Check deleted consumer status
            cmd = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd, "check deleted consumer status")
            print "check output:\n", output

            if ret != 0:
                logger.info("It's successful to check deleted consumer status.")
            else:
                raise FailException("Test Failed - Failed to check deleted consumer status.")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error(str(e))
            raise FailException("Test Failed - error happened when verify consumer status after being deleted from server:" + str(e))
            self.assert_(False, case_name)

        finally:
            # clean local consumer and subscription data
            cmd = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd, "clean local data")
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % __name__)

if __name__ == "__main__":
    unittest.main()
