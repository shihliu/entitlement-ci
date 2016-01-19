from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17232_check_uuid_two_config_same_mode(KVMBase):
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
            # (3) on host2, configure remote libvirt mode in config file /etc/sysconfig/virt-who
            self.set_remote_libvirt_conf(get_exported_param("REMOTE_IP"), remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(2, 80, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )
            self.clean_remote_libvirt_conf(remote_ip_2)
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
