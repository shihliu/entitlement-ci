from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510111_consumer_folder_is_moved_to_consumer_old_after_deleting_the_consumer(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Before registration, delete all consumer certs folders
            cmd = 'rm -rf /etc/pki/consumer*'
            (ret, output) = self.runcmd(cmd, "delete all consumer certs folders")
            if ret == 0 and '' == output:
                logger.info("It's successful to delete all consumer certs folders")
            else:
                raise FailException("Test Failed - Failed to delete all consumer certs folders")

            # Register to create consumer certs in /etc/pki/consumer
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Check /etc/pki/consumer folder.
            self.check_consumer_certs('/etc/pki/consumer')

            # Delete consumer from server side by API
            system_uuid = self.cm_get_consumerid()
            if self.test_server == "STAGE":
                system_uuid = self.get_hostname()
            server_ip = get_exported_param("SERVER_IP")
            self.server_remove_system(system_uuid, server_ip, self.get_rhsm_cons("username"), self.get_rhsm_cons("password"))

            # Restart certd service
            self.restart_rhsmcertd()
            time.sleep(130)

            # Check /etc/pki/consumer.old folder
            self.check_consumer_certs('/etc/pki/consumer.old')

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_consumer_certs(self, folder):
        folder_normal = '/etc/pki/consumer'
        folder_old = '/etc/pki/consumer.old'
        if folder == folder_normal:
            cmd = 'ls -l  /etc/pki/consumer'
            (ret, output) = self.runcmd(cmd, "check /etc/pki/consumer folder")
            if ret == 0 and 'cert.pem' in output and 'key.pem' in output:
                logger.info("It's successful to check /etc/pki/consumer folder")
            else:
                raise FailException("Test Failed - Failed to check /etc/pki/consumer folder")

            cmd = 'ls -l /etc/pki/consumer.old'
            (ret, output) = self.runcmd(cmd, "check /etc/pki/consumer.old folder")
            if ret != 0 and 'cannot access /etc/pki/consumer.old: No such file or directory' in output:
                logger.info("It's successful to check /etc/pki/consumer.old folder")
            else:
                raise FailException("Test Failed - Failed to check /etc/pki/consumer.old folder")
        elif folder == folder_old:
            cmd = 'ls -l /etc/pki/consumer.old'
            (ret, output) = self.runcmd(cmd, "check /etc/pki/consumer.old folder")
            if ret == 0 and 'cert.pem' in output and 'key.pem' in output:
                logger.info("It's successful to check /etc/pki/consumer.old folder")
            else:
                raise FailException("Test Failed - Failed to check /etc/pki/consumer.old folder")

            cmd = 'ls -l /etc/pki/consumer'
            (ret, output) = self.runcmd(cmd, "check /etc/pki/consumer folder")
            if ret == 0 and output.strip() == 'total 0':
                logger.info("It's successful to check /etc/pki/consumer folder")
            else:
                raise FailException("Test Failed - Failed to check /etc/pki/consumer folder")
            
if __name__ == "__main__":
    unittest.main()
