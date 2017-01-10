from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509866_no_matter_how_many_trailing_slashes_are_configured_on_the_serverprefix(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            prefix = '/' + self.get_rhsm_cons("prefix")
            checkcmd = "subscription-manager list --available | grep Name:"
            tmp_file = "/root/logfile"

            # set no trailing slashes on the prefix, and check request urls.
            testprefix = prefix
            self.set_prefix(testprefix)
            self.check_prefix(prefix, checkcmd, tmp_file)

            # set 1 trailing slashes on the prefix, and check request urls.
            testprefix = prefix + '/'
            self.set_prefix(testprefix)
            self.check_prefix(prefix, checkcmd, tmp_file)

            # set many trailing slashes on the prefix, and check request urls.
            testprefix = prefix + '//////'
            self.set_prefix(testprefix)
            self.check_prefix(prefix, checkcmd, tmp_file)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_prefix(prefix)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def set_prefix(self, testprefix):
        cmd = "subscription-manager config --server.prefix=%s" % testprefix
        (ret, output) = self.runcmd(cmd, "test prefix")
        if ret == 0:
            logger.info("It's successful to set prefix as %s" % testprefix)
        else:
            raise FailException("Test Failed - Failed to set prefix as %s" % testprefix)

    def check_prefix(self, prefix, checkcmd, tmp_file):
        self.generate_tmp_log(checkcmd, tmp_file)
        cmd = "cat %s | grep handler=" % tmp_file
        (ret, output) = self.runcmd(cmd, "check test prefix in request urls")
        if ret == 0 and (" handler=%s " % prefix in output) and (" handler=%s/ " % prefix not in output):
            logger.info("It's successful to check test prefix in request urls")
        else:
            raise FailException("Test Failed - Failed to check test prefix in request urls.")

if __name__ == "__main__":
    unittest.main()
