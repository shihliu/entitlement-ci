from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510025_show_a_warning_when_server_time_and_client_time_drift_is_big(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_stage_check():
            try:
                tmp_file = '/root/logfile'
                samhostip = get_exported_param("SERVER_IP")
                self.sync_times(samhostip)

                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)

                # Make response from the server, and check the rhsm.log for clock info
                self.response_from_server(tmp_file)

                if not self.check_clock_info(tmp_file):
                    logger.info("It's successful to check no time drift no warning.")
                else:
                    raise FailException("Test Failed - Failed to check no time drift no warning")

                self.clear_file_content(tmp_file)

                # Make the system's clock behind the candlepin server's clock by 7 hours.Make response from the server, and check the rhsm.log for clock info.
                self.make_time_drift('\"-7 hours\"')
                self.response_from_server(tmp_file)

                if self.check_clock_info(tmp_file):
                    logger.info("It's successful to check big time drift with warning.")
                else:
                    raise FailException("Test Failed - Failed to check big time drift with warning")

                self.clear_file_content(tmp_file)

                # Make the system's clock ahead of the candlepin server's clock by 7 hours.Make response from the server, and check the rhsm.log for clock info.
                self.make_time_drift('\"+14 hours\"')
                self.response_from_server(tmp_file)

                if self.check_clock_info(tmp_file):
                    logger.info("It's successful to check big time drift with warning.")
                else:
                    raise FailException("Test Failed - Failed to check big time drift with warning")

                self.clear_file_content(tmp_file)

                # Restore the client's clock.Make response from the server, and check the rhsm.log for clock info.
                self.make_time_drift('\"-7 hours\"')

                self.response_from_server(tmp_file)
                if not self.check_clock_info(tmp_file):
                    logger.info("It's successful to check no time drift no warning.")
                else:
                    raise FailException("Test Failed - Failed to check no time drift no warning")

                self.clear_file_content(tmp_file)

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.clear_file_content(tmp_file)
                self.restore_system_time()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def response_from_server(self, tmp_file):
        checkcmd = 'subscription-manager version'
        self.generate_tmp_log(checkcmd, tmp_file)

    def check_clock_info(self, tmp_file):
        cmd = 'grep -i "clock" %s -B2' % tmp_file
        time.sleep(10)
        (ret, output) = self.runcmd(cmd, "check clock info")
        if ret == 0 and 'Clock skew detected, please check your system time' in output:
            return True
            logger.info("It's successful to check clock info, there is a warning about system time drift")
        elif ret != 0 and output.strip() == '':
            return False
            logger.info("It's successful to check clock info, there is no warning about system time drift")
        else:
            raise FailException("Test Failed - Failed to check clock info")

    def make_time_drift(self, drift):
        cmd = 'date -s %s' % drift
        (ret, output) = self.runcmd(cmd, "make time drift")
        if ret == 0:
            logger.info("It's successful to make time drift %s" % drift)
        else:
            raise FailException("Test Failed - Failed to make time drift")

if __name__ == "__main__":
    unittest.main()
