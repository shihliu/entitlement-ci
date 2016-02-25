from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17233_check_uuid_when_config_file_and_cli(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            mode="libvirt"

            # define a guest
            self.vw_define_guest(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) stop virt-who service on host1 and host2
            self.vw_stop_virtwho_new()
            self.vw_stop_virtwho_new(remote_ip_2)
            # (2) on host2, configure remote libvirt mode in config file /etc/virt-who.d/virtwho
            self.set_virtwho_sec_config(mode, remote_ip_2)
            # (3) on host2, run commond line mode to monitor remote libvirt
            cmd = self.virtwho_cli("libvirt") + " -o -d"
            check_msg = "%s|Using configuration \"libvirt\"|Using configuration \"env/cmdline\"" %guestuuid
            self.vw_check_message(cmd, check_msg, targetmachine_ip=remote_ip_2 )

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
