from utils import *
from testcases.install.install_base import Install_Base

class SATELLITE_OHSNAP_Install(Install_Base):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            #compose = "http://sat-r220-02.lab.eng.rdu2.redhat.com/pulp/repos/Sat6-CI/QA/Satellite_RHEL6/custom/Red_Hat_Satellite_6_2_Composes/RHEL6_Satellite_x86_64_os/"
            sat_server = get_exported_param("REMOTE_IP")
            self.install_satellite_ohsnap(sat_server)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
