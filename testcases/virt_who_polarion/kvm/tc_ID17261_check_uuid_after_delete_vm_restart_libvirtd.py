from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17261_check_uuid_after_delete_vm_restart_libvirtd(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 60)
            self.runcmd_service("restart_virtwho")
            cmd_start_guest = "virsh start %s" %guest_name

            # (1) Check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            # (2) Undefine guest
            self.vw_undefine_all_guests()
            # (3) Restart libvirtd service then check if the uuid is not monitored by virt-who
            self.vw_check_message_in_rhsm_log("Using libvirt url", checkcmd="service libvirtd restart")
            self.vw_define_all_guests()
            guestuuid = self.vw_get_uuid(guest_name)
#             self.vw_start_guests(guest_name)
            # (4) restart guest then check bonus pool is not revoke. 
            self.vw_check_uuid(guestuuid, uuidexists=True, checkcmd=cmd_start_guest)
            self.vw_check_attr(guest_name, 1, 'libvirt', 1, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.vw_stop_guests(guest_name)
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
