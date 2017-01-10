from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537404_yum_shows_unicodedecodeerror_when_open_usr_share_locale_ja_ls_messages_rhsm_mo(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            #1 yum
            cmd = "LANG=ja_JP.UTF8 yum | grep 'UnicodeDecodeError'"
            (ret, output) = self.runcmd(cmd, "check unicodedecodeerror when running yum")
            if ret != 0 and 'UnicodeDecodeError' not in output:
                logger.info("It's successful to check unicodedecodeerror when running yum")
            else:
                raise FailException("Test Failed - Failed to check unicodedecodeerror when running yum")

            #2 yum -h
            cmd = "LANG=ja_JP.UTF8 yum -h | grep 'UnicodeDecodeError'"
            (ret, output) = self.runcmd(cmd, "check unicodedecodeerror when running yum -h")
            if ret != 0 and 'UnicodeDecodeError' not in output:
                logger.info("It's successful to check unicodedecodeerror when running yum -h")
            else:
                raise FailException("Test Failed - Failed to check unicodedecodeerror when running yum -h")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
