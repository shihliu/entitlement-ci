from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17233_VDSM_check_uuid_when_config_file_and_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            mode="libvirt"

            # start guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.generate_ssh_key()

            # (1) stop virt-who service on host1 and host2
            self.vw_stop_virtwho_new()
            self.vw_stop_virtwho_new(remote_ip_2)
            # (2) on host2, configure remote libvirt mode in config file /etc/virt-who.d/virtwho
            self.set_virtwho_sec_config(mode, remote_ip_2)
            # (3) on host2, run commond line mode to monitor remote libvirt
            cmd = "virt-who --vdsm -o -d"
            check_msg = "\"vdsm\" mode|Using configuration \"libvirt\"|Using configuration \"env/cmdline\"|\"libvirt\" mode" 
            self.vw_check_message(cmd, check_msg, targetmachine_ip=remote_ip_2 )

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
