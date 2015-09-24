from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import time

class tc_ID327120_consumer_folder_moved_to_consumer_old_after_deleting_the_consumer(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            baseurl = get_exported_param("SERVER_HOSTNAME")
            baseurl = baseurl + ':443/sam/api'
            # remove the consumer related files
            cmd = "rm -rf /etc/pki/consumer*"
            (ret, output) = self.runcmd(cmd, "remove the consumer related files before testing")
            if ret == 0:
                logger.info("It's successful to remove the consumer related files before testing")
            else:
                raise FailException("Test Failed - Failed to remove the consumer related files before testing.")
            # register the client
            self.sub_register(username, password)
            # check the consumer folder
            cmd = "ls /etc/pki | grep 'consumer'"
            (ret, output) = self.runcmd(cmd, "check the consumer folder after registration")
            if ret == 0 and 'consumer' in output and 'consumer.old' not in output:
                logger.info("It's successful to check the consumer folder after registration")
            else:
                raise FailException("Test Failed - Failed to check the consumer folder after registration.")
            # get consumerid of the client
            consumerid = self.sub_get_consumerid()
            # delete the consumer from server side.
            cmd = "curl -k -u %s:%s --request DELETE %s/consumers/%s" % (username, password, baseurl, consumerid)
            (ret, output) = self.runcmd(cmd, "check dependency on python-simplejson")
            # if ret == 0 and output == '':
            if ret == 0:
                logger.info("It's successful to delete the consumer from server side")
            else:
                raise FailException("Test Failed - Failed to delete the consumer from server side.")
            # restart rhsmcert service
            self.restart_rhsmcertd()
            # wait 2 mins
            time.sleep(125)
            # check if consumer.old exists
            cmd = "ls /etc/pki/consumer.old"
            (ret, output) = self.runcmd(cmd, "check if consumer.old exists")
            if ret == 0 and output != '':
                logger.info("It's successful to check that consumer.old exists")
            else:
                raise FailException("Test Failed - Failed to check that consumer.old exists.")
            # check if consumer folder exists
            cmd = "ls /etc/pki/consumer"
            (ret, output) = self.runcmd(cmd, "check if consumer exists")
            if ret == 0 and output == '':
                logger.info("It's successful to check that empty consumer folder exists")
            elif ret != 0 and "ls: cannot access consumer: No such file or directory" in output:
                logger.info("It's successful to check that consumer folder does not exist")
            else:
                raise FailException("Test Failed - Failed to check that consumer exists.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
