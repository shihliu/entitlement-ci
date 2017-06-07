from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase

class virtwho_kvm_setup(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.sys_setup()
            self.kvm_static_sys_setup(get_exported_param("REMOTE_IP_1"))
            self.kvm_static_sys_setup(get_exported_param("REMOTE_IP_2"))
            self.remote_libvirt_setup()
            self.generate_ssh_key_define()
#             self.cm_install_desktop()
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
