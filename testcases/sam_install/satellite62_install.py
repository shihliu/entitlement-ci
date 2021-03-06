from utils import *
from testcases.sam_install.install_base import Install_Base

class SATELLITE62_Install(Install_Base):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            logger.info("aaaaaaa")
            compose = "latest-Satellite-6.2-RHEL-6"
            sat_server = get_exported_param("REMOTE_IP")
            logger.info("satellite server is %s" %sat_server)
            logger.info("satellite_service is %s" %sat_server)
            self.install_satellite62(compose, sat_server)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
