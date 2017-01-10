from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510132_rhsmcertd__update_when_rhsm_consumercertdir_configuration_is_changed(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Configure non-default consumerCertDir as the /tmp directory.
            cmd = 'subscription-manager config --rhsm.consumercertdir=/tmp/consumer --rhsmcertd.autoattachinterval=1'
            (ret, output) = self.runcmd(cmd, "configure non-default consumer-cert-dir")
            if ret ==0 and '' == output:
                logger.info("It's successful to configure non-default consumer-cert-dir")
            else:
                raise FailException("Test Failed - Failed to configure non-default consumer-cert-dir")

            # Register system
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Restart certd service
            checkcmd = 'service rhsmcertd restart'
            tmp_file = '/root/logfile'

            # Check rhsm.log
            self.generate_tmp_log(checkcmd, tmp_file)
            self.check_log(tmp_file, 'rhsm.log')
            self.clear_file_content(tmp_file)

            # Check rhsmcertd.log
            self.generate_tmp_log(checkcmd, tmp_file, log_file='rhsmcertd.log')
            self.check_log(tmp_file, 'rhsmcertd.log')

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.clear_file_content(tmp_file)
            self.restore_environment()
            self.restore_rhsm_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_log(self, tmp_file, logtype):
        cmd = 'egrep "trachback|Traceback" %s'%tmp_file
        (ret, output) = self.runcmd(cmd, "check log")
        if ret !=0 and '' == output.strip():
            logger.info("It's successful to check %s"%logtype)
        else:
            raise FailException("Test Failed - Failed to check %s"%logtype)

    def restore_rhsm_conf(self):
        cmd = 'subscription-manager config --remove rhsm.consumercertdir'
        (ret, output) = self.runcmd(cmd, "restore consumer cert dir")
        if ret == 0 and 'You have removed the value for section rhsm and name consumercertdir.' in output and 'The default value for consumercertdir will now be used.' in output:
            logger.info("It's successful to restore consumer cert dir")
        else:
            raise FailException("Test Failed - Failed to restore consumer cert dir")

        cmd = 'subscription-manager config --remove rhsmcertd.autoattachinterval'
        (ret, output) = self.runcmd(cmd, "restore auto attach interval")
        if ret == 0 and 'You have removed the value for section rhsmcertd and name autoattachinterval.' in output and 'The default value for autoattachinterval will now be used' in output:
            logger.info("It's successful to restore auto attach interval")
        else:
            raise FailException("Test Failed - Failed to restore auto attach interval")

if __name__ == "__main__":
    unittest.main()
