from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510104_the_local_time_start_end_dates_rendered_during_daylight_savings(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Check start date on entitlement cert
            certname = self.get_subscription_serialnumlist()[0]
            cmd = 'rct cat-cert /etc/pki/entitlement/%s.pem | grep Start'%certname
            (ret, output) = self.runcmd(cmd, "check start date on entitlement cert")
            if ret ==0 and 'Start Date:' in output:
                expectdate = output.strip().split(': ')[1].split(' ')[0]
                logger.info("It's successful to check start date on entitlement cert")
            else:
                raise FailException("Test Failed - Failed to check start date on entitlement cert")

            # change date
            self.set_date_daylight(expectdate, '-7')

            # Check list consumed subscriptions
            self.check_expectdate_in_consumed(expectdate)

            # change date
            self.set_date_daylight(expectdate, '+7')

            # Check list consumed subscriptions
            self.check_expectdate_in_consumed(expectdate)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_system_time()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def set_date_daylight(self, expectdate, different):
        # set date 'different' days before expectdate
        cmd = 'date -d \"%s %s days\"'%(expectdate, different)
        (ret, output) = self.runcmd(cmd, "get changedate")
        if ret ==0:
            changedate = output.strip()
            logger.info("It's successful to get changedate")
        else:
            raise FailException("Test Failed - Failed to get date 7 days before expectdate")

        # change date
        cmd = 'date -s \"%s\"'%changedate
        (ret, output) = self.runcmd(cmd, "change date")
        if ret ==0 and changedate in output:
            logger.info("It's successful to change date")
        else:
            raise FailException("Test Failed - Failed to change date")

    def check_expectdate_in_consumed(self, expectdate):
        cmd = 'subscription-manager list --consumed | grep Starts:'
        date_fragment=expectdate.split('-')
        date_consumed=date_fragment[1]+'/'+date_fragment[2]+'/'+date_fragment[0]
        (ret, output) = self.runcmd(cmd, "check expect date")
        if ret ==0 and date_consumed in output:
            logger.info("It's successful to check expect date")
        else:
            raise FailException("Test Failed - Failed to check expect date")

if __name__ == "__main__":
    unittest.main()
