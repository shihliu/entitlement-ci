from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510161_rhsmcertd_service_update_certs_and_log_in_rhsmcertd_log(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # remove all in case auto-healing
            self.disable_autoheal()
            self.remove_all_subscriptions()

            # check product status
            if self.check_installed_status() == 'Not Subscribed':
                logger.info("It's successful to check the installed product not subscribed")
            else:
                raise FailException("Test Failed - Failed to check the installed product not subscribed")

            # set autoAttachInterval is 1
            if self.check_auto_attach_interval() == '1':
                logger.info("auto attach interval is 1, no need to set it")
            else:
                self.set_auto_attach_interval('1')

            # enable auto heal
            self.enable_autoheal()

            # restart certd and check log
            tmp_file = '/root/logfile'
            checkcmd = 'service rhsmcertd restart'
            # check rhsm.log
            self.generate_tmp_log(checkcmd, tmp_file)
            cmd = 'cat %s | grep rhsmcertd-worker | egrep "repos updated"'%tmp_file
            (ret, output) = self.runcmd(cmd, "check rhsm.log")
            if ret == 0 and 'repos updated: Repo updates' in output:
                logger.info("It's successful to check rhsm.log")
            else:
                raise FailException("Test Failed - Failed to check rhsm.log")
            # check rhsmcertd.log
            self.generate_tmp_log(checkcmd, tmp_file, log_file='rhsmcertd.log')
            cmd = 'cat %s | grep "Certificates updated"'%tmp_file
            (ret, output) = self.runcmd(cmd, "check rhsmcertd.log")
            if ret == 0 and '(Auto-attach) Certificates updated.' in output:
                logger.info("It's successful to check rhsmcertd.log")
            else:
                raise FailException("Test Failed - Failed to check rhsmcertd.log")

            # wait 2 minutes
            time.sleep(120)

            # check product status
            if self.check_installed_status() == 'Subscribed':
                logger.info("It's successful to check the installed product subscribed")
            else:
                raise FailException("Test Failed - Failed to check the installed product subscribed")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_auto_attach_interval('1440')
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_installed_status(self):
        cmd = 'subscription-manager list --installed | grep Status:'
        (ret, output) = self.runcmd(cmd, "check installed status")
        if ret ==0:
            return output.split(':')[1].strip()
            logger.info("It's successful to check installed status")
        else:
            raise FailException("Test Failed - Failed to check installed status")

if __name__ == "__main__":
    unittest.main()
