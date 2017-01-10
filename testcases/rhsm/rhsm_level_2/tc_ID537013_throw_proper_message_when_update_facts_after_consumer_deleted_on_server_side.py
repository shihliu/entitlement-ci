from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537013_throw_proper_message_when_update_facts_after_consumer_deleted_on_server_side(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Delete the consumer from server
            system_uuid = self.cm_get_consumerid()
            if self.test_server == "STAGE":
                system_uuid = self.get_hostname()
            server_ip = get_exported_param("SERVER_IP")
            self.server_remove_system(system_uuid, server_ip, self.get_rhsm_cons("username"), self.get_rhsm_cons("password"))

            # Update facts and save rhsm.log
            checkcmd = 'subscription-manager facts --update'
            tmp_file = '/tmp/rhsm.log'
            self.generate_tmp_log(checkcmd, tmp_file)

            # Check rhsm.log
            cmd = 'grep "traceback" %s'%tmp_file
            (ret, output) = self.runcmd(cmd, "check rhsm.log")
            if ret != 0 and output.strip() == '':
                logger.info("It's successful to check rhsm.log")
            else:
                raise FailException("Test Failed - Failed to check rhsm.log")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
