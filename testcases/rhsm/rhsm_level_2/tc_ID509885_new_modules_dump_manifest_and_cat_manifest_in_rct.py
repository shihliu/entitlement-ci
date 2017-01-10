from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509885_new_modules_dump_manifest_and_cat_manifest_in_rct(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#            username = self.get_rhsm_cons("username")
#            password = self.get_rhsm_cons("password")
#            self.sub_register(username, password)
#            autosubprod = self.get_rhsm_cons("autosubprod")
#            self.sub_autosubscribe(autosubprod)
            cmd = "rct --help"
            (ret, output) = self.runcmd(cmd, "run rct --help")
            if ret == 0 and ("cat-manifest" in output) and ("dump-manifest" in output):
                logger.info("cat-manifest and dump-manifest is added to the rct command ")
            else:
                raise FailException("Test Failed - cat-manifest and dump-manifest is not added to the rct command")

            cmd = "man rct | grep dump-manifest"
            (ret, output) = self.runcmd(cmd, "grep the dump-manifest")
            if ret == 0 and output:
                logger.info("dump-manifest is in the man page ")
            else:
                raise FailException("Test Failed - dump-manifest is not in the man page")

            cmd = "man rct | grep cat-manifest"
            (ret, output) = self.runcmd(cmd, "grep the cat-manifest")
            if ret == 0 and output:
                logger.info("cat-manifest is in the man page ")
            else:
                raise FailException("Test Failed - cat-manifest is not in the man page")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
