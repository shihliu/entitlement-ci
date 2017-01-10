from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510163_rhsm_log_when_registration_with_server_side_error(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # get correct hostname
            cmd = "subscription-manager config | grep hostname | grep -v 'proxy'"
            (ret, output) = self.runcmd(cmd,'get server hostname in conf')
            correcthost = output.split('=')[1].strip()

            # set wrong hostname
            wronghost = '1' + correcthost
            self.set_server_hostname(wronghost)

            # register and see the rhsm.log
            tmp_file= '/root/logfile'
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            checkcmd = 'subscription-manager register --username=%s --password=%s'%(username, password)
            self.generate_tmp_log(checkcmd, tmp_file)
            cmd = 'grep -E "Name or service not known" %s'%tmp_file
            #cmd = 'grep -E "Name or service not known|Network error, unable to connect to server." %s'%tmp_file
            (ret, output) = self.runcmd(cmd, "check error in rhsm.log")
            if ret ==0 and 'Name or service not known' in output:
                logger.info("It's successful to check error in rhsm.log")
            else:
                raise FailException("Test Failed - Failed to check error in rhsm.log")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_server_hostname(correcthost)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def set_server_hostname(self, hostnamevalue):
        cmd="subscription-manager config --server.hostname=%s"%hostnamevalue
        (ret, output) = self.runcmd(cmd,'set server hostname in conf')
        if ret == 0:
            logger.info("It's successful to set server hostname in conf")
        else:
            raise FailException("Test Failed - Failed to set server hostname in conf")

if __name__ == "__main__":
    unittest.main()
