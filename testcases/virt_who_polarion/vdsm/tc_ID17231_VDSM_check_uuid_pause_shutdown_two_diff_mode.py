from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17231_VDSM_check_uuid_pause_shutdown_two_diff_mode(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip = get_exported_param("REMOTE_IP")
            remote_host_name = self.get_hostname()
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_host2_name = self.get_hostname(remote_ip_2)
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            mode="libvirt"

            # generate ssh key to host2
            self.update_vm_to_host(guest_name, remote_host2_name, rhevm_ip)
            self.generate_ssh_key()

            # (1) stop virt-who service on host1 and host2
            self.vw_stop_virtwho_new()
            self.vw_stop_virtwho_new(remote_ip_2)
            # (2) on host2, configure remote libvirt mode in config file /etc/virt-who.d/virtwho
            self.set_virtwho_sec_config(mode, remote_ip_2)
            # (3).check if the uuid and attributes are correctly monitored by virt-who.
            self.rhevm_start_vm(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=remote_ip_2)
            self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid, targetmachine_ip=remote_ip_2)
            # (4). pause guest   
            self.rhevm_pause_vm(guest_name, rhevm_ip)
            # (5).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=remote_ip_2)
            # (6). resume guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # (7)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=remote_ip_2)
            self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid, targetmachine_ip=remote_ip_2)
            # (9) stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # (10)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.update_vm_to_host(guest_name, remote_host_name, rhevm_ip)
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
