from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17306_check_thread_after_config_libvirt(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.vw_undefine_all_guests()
            if self.os_serial == "6":
                self.setup_libvirtd_config()
                self.vw_restart_libvirtd()
                for i in range(3):
                    self.runcmd_service("restart_virtwho")
                    self.vw_check_message_in_rhsm_log("Too many active clients", message_exists=False)
                    self.list_vm()
                    self.check_virtwho_thread(1)
                    time.sleep(5)
            else:
                logger.info("Libvirtd config not support it here, it Only supported in rhel6")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_libvirtd_config()
            self.vw_restart_libvirtd()
            self.vw_define_all_guests()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
