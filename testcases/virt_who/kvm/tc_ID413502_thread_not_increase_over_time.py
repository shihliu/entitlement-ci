from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID413502_thread_not_increase_over_time(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.vw_undefine_all_guests()
            if self.get_os_serials() == "6":
                self.setup_libvirtd_config()
                self.vw_restart_libvirtd()
                for i in range(3):
                    self.vw_restart_virtwho()
                    self.vw_check_message_in_rhsm_log("Too many active clients", message_exists=False)
                    self.list_vm()
                    self.check_virtwho_thread()
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

    def setup_libvirtd_config(self):
        cmd = "sed -i -e 's/^#listen_tls = 0/listen_tls = 0/g' -e 's/^#listen_tcp = 1/listen_tcp = 1/g' -e 's/^#auth_tcp = \"sasl\"/auth_tcp = \"sasl\"/g' -e 's/^#tcp_port = \"16509\"/tcp_port = \"16509\"/g' /etc/libvirt/libvirtd.conf"
        ret, output = self.runcmd(cmd, "setup_libvirtd_config")
        if ret == 0 :
            logger.info("Succeeded to setup_libvirtd_config.")
        else:
            raise FailException("Test Failed - Failed to setup_libvirtd_config.")

    def restore_libvirtd_config(self):
        cmd = "sed -i -e 's/^listen_tls = 0/#listen_tls = 0/g' -e 's/^listen_tcp = 1/#listen_tcp = 1/g' -e 's/^auth_tcp = \"sasl\"/#auth_tcp = \"sasl\"/g' -e 's/^tcp_port = \"16509\"/#tcp_port = \"16509\"/g' /etc/libvirt/libvirtd.conf"
        ret, output = self.runcmd(cmd, "restore_libvirtd_config")
        if ret == 0 :
            logger.info("Succeeded to restore_libvirtd_config.")
        else:
            raise FailException("Test Failed - Failed to restore_libvirtd_config.")

if __name__ == "__main__":
    unittest.main()
