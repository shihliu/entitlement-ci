from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17228_VDSM_check_uuid_two_diff_mode(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip = get_exported_param("REMOTE_IP")
            remote_host_name = self.get_hostname()
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_host2_name = self.get_hostname(remote_ip_2)
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            mode="rhevm"

            # (1) stop virt-who service
            self.runcmd_service("stop_virtwho")
            # (2) on host2, configure remote rhevm mode in config file /etc/virt-who.d/virtwho
            self.set_virtwho_sec_config(mode)
            # (3).check if two modes are correctly monitored by virt-who.
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.hypervisor_check_uuid(hostuuid, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
