# coding:utf-8
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509850_register_with_invalid_credentials_should_not_throw_unicode_decode_error(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            checkcmd = 'LANG=de_DE.UTF-8 subscription-manager register --username=foo --password=bar'
            tmp_file = '/root/logfile'
            self.generate_tmp_log(checkcmd, tmp_file)
            
            # check rhsm.log
            cmd = 'grep -E "Unauthorized: Invalid credentials for request|Invalid credentials|Benutzername oder Passwort" %s' % (tmp_file)
            (ret, output) = self.runcmd(cmd, "check rhsm.log")
            if ret == 0 and ('Invalid credentials' in output or 'Benutzername oder Passwort' in output):
                logger.info("It's successful to check rhsm.log credentials exception")
            else:
                raise FailException("Test Failed - failed to check rhsm.log credentials exception")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.clear_file_content(tmp_file)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
