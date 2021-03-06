from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase

class virtwho_rhel_rhevm_setup(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            if "RHEVH" in get_exported_param("RHEL_COMPOSE"):
                self.rhel_rhevm_sys_setup()
                self.generate_ssh_key()
            else:
                self.sys_setup()
                self.rhel_rhevm_static_sys_setup()
            self.rhel_rhevm_setup()
#             self.generate_ssh_key()
            # self.cm_install_desktop()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_virtwho_version()
            self.cm_set_rhsm_version()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
