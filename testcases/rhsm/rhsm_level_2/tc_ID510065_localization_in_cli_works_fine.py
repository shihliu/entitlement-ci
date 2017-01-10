#coding=utf-8
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510065_localization_in_cli_works_fine(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'LANG=fr_FR.UTF-8 subscription-manager --help'
            (ret, output) = self.runcmd(cmd, "localization")
            if ret ==0 and 'Modules primaires' in output and 'Autres modules' in output and 'Utilisation : subscription-manager MODULE-NAME [MODULE-OPTIONS] [--help]' in output:
                logger.info("It's successful to check localization")
            else:
                raise FailException("Test Failed - Failed to check localization")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
