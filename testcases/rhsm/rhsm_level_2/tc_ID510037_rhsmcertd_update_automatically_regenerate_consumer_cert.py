from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510037_rhsmcertd_update_automatically_regenerate_consumer_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_stage_check():
            try:
                # Check if insecure is 1
                if self.check_insecure_value() == '1':
                    logger.info("insecure is 1, no need set it")
                else:
                    self.set_insecure_value('1')

                serverip = get_exported_param("SERVER_IP")
                self.sync_times(serverip)

                # Register
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)

                # Get end date of consumer cert
                enddate = self.get_end_date()

                # fast-forward time into the future on both the candlepin server and the subscription-manager system to within 90 days before cert.pem 's EndDate
                # 1 server date
                date_cmd = "date -s '+15 year +9 month +2 day'"
                self.sam_remote_set_time(serverip, date_cmd)

                # 2 client date
                system_time = "\'+15 year +9 month +2 day\'"
                self.set_system_time(system_time)

                # restart certd and wait 2 minutes
                self.restart_rhsmcertd()
                time.sleep(130)

                # Get end date of consumer cert
                newenddate = self.get_end_date()

                if int(newenddate) == int(enddate)+16:
                    logger.info("It's successful to check regenerating consumer cert after restart certd")
                else:
                    raise FailException("Test Failed - Failed to check regenerating consumer cert after restart certd")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.sam_remote_set_time(serverip, 'hwclock --hctosys')
                self.restore_system_time()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def get_end_date(self):
        cmd = "rct cat-cert /etc/pki/consumer/cert.pem | grep 'End Date'"
        (ret, output) = self.runcmd(cmd, "get end date of consumer cert")
        if ret ==0 and 'End Date:' in output:
            enddate = output.strip().split(":")[1].strip().split('-')[0]
            return enddate
            logger.info("It's successful to get end date of consumer cert")
        else:
            raise FailException("Test Failed - Failed to get end date of consumer cert")

if __name__ == "__main__":
    unittest.main()
