from utils import *
from testcases.virt_who.kvmbase import KVMBase

class upstream_virtwho_kvm_setup(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.kvm_sys_setup()
            self.kvm_sys_setup(get_exported_param("REMOTE_IP_2"))
            self.upstream_virtwho_install()
            self.kvm_setup()
            self.generate_ssh_key()
            self.install_desktop()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
