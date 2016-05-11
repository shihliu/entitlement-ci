from utils import *
from testcases.sam_install.sam_install_base import SAM_Install_Base

class RHEVM40_Install(SAM_Install_Base):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            #compose = "latest-stable-Satellite-6.1-RHEL-7"
            compose = "7"
            self.install_rhevm40(compose)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
