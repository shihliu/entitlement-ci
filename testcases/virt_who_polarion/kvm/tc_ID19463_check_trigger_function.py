from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID19463_check_trigger_function(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = "gathered, putting to queue for sending"
            check_start = "virsh start %s" %guest_name
            check_suspend = "virsh suspend %s" %guest_name
            #(1)When refresh default interval is 60s, virt-who trigger sucessfully.
            self.vw_check_message_number_in_rhsm_log(check_msg, checkcmd=check_start)
            self.shutdown_vm(guest_name)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid, checkcmd=check_start, waiting_time=60)
            #(2) When refresh interval is 80s, virt-who trigger sucessfully.
            self.config_option_setup_value("VIRTWHO_INTERVAL", 80)
            self.runcmd_service("restart_virtwho")
            self.shutdown_vm(guest_name)
            self.vw_check_message_number_in_rhsm_log(check_msg, checkcmd=check_start)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 3, guestuuid, checkcmd=check_suspend, waiting_time=80)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.shutdown_vm(guest_name)
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
