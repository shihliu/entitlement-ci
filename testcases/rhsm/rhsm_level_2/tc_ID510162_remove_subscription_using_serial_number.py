from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510162_remove_subscription_using_serial_number(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.check_and_backup_yum_repos()
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # check consumed and get the serial number
            serial = self.check_consumed_serial()

            # reomve subscription by serial number
            cmd = 'subscription-manager remove --serial %s'%serial
            (ret, output) = self.runcmd(cmd, "reomve subscription by serial number")
            if ret ==0 and 'The entitlement server successfully removed these serial numbers:' in output:
                logger.info("It's successful to reomve subscription by serial number")
            else:
                raise FailException("Test Failed - Failed to reomve subscription by serial number")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_repos()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_consumed_serial(self):
        serial = ''
        cmd = 'subscription-manager list --consumed | egrep "Serial:|Pool"'
        (ret, output) = self.runcmd(cmd, "check consumed")
        if ret ==0 and 'Pool ID:' in output:
            serial = output.strip().split('\n')[0].split(":")[1].strip()
            logger.info("It's successful to check consumed subscription and get the serial number")
        else:
            raise FailException("Test Failed - Failed to check consumed subscription and get the serial number")
        return serial

if __name__ == "__main__":
    unittest.main()
