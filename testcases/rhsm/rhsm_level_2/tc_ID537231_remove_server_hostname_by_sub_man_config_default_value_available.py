from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537231_remove_server_hostname_by_sub_man_config_default_value_available(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # get hostname before register
            hostname_original = self.get_hostname_from_config()

            # register with serverurl
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            if self.test_server == "STAGE":
                serverurl = hostname_original+':443/subscription'
            elif self.test_server == 'SAM':
                serverurl = hostname_original+':443/sam/api'
            elif self.test_server == 'SATELLITE':
                serverurl = hostname_original+':443/rhsm'

            cmd = 'subscription-manager register --username=%s --password=%s --serverurl=%s'%(username, password, serverurl)
            (ret, output) = self.runcmd(cmd, "register")
            if ret == 0 and (("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output)):
                logger.info("It's successful to register with serverurl.")
            else:
                raise FailException("Test Failed - Failed to register with serverurl.")

            # unregister and check the hostname after unregister
            self.sub_unregister()
            hostname_unregister = self.get_hostname_from_config()
            if hostname_original == hostname_unregister:
                logger.info("It's successfult to verify that server hostname won't change after unregister")
            else:
                raise FailException("Test Failed - Failed to verify that server hostname won't change after unregister")

            # remove server hostname
            self.rm_server_hostname()

            #check the hostname after removal
            df_hn = self.get_hostname_from_config()
            logger.info("000000000000000000%s0000000000000"%df_hn)
            if df_hn == "[subscription.rhsm.redhat.com]":
                logger.info("It's successful to check the server hostname to be the default one")
            else:
                raise FailException("Test Failed - Failed to check the server hostname to be the default one")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_server_hostname(hostname_original)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def rm_server_hostname(self):
        cmd = "subscription-manager config --remove server.hostname"
        (ret, output) = self.runcmd(cmd, "remove server hostname")
        if ret == 0 and 'You have removed the value for section server and name hostname' in output and 'The default value for hostname will now be used' in output:
            logger.info("It's successful to remove server hostname")
        else:
            raise FailException("Test Failed - Failed to remove server hostname")

if __name__ == "__main__":
    unittest.main()
