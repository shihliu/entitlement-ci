from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17252_check_uuid_fake_remote_libvird(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            mode="libvirt"
            VIRTWHO_SERVER = "qemu+ssh://" + remote_ip + "/system"
            remote_owner = self.get_vw_cons("VIRTWHO_LIBVIRT_OWNER")
            remote_env = self.get_vw_cons("VIRTWHO_LIBVIRT_ENV")
            remote_user = self.get_vw_cons("VIRTWHO_LIBVIRT_USERNAME")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake"

            # define a guest
            self.vw_define_guest(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) stop virt-who service on host1 and host2
            self.vw_stop_virtwho_new()
            self.vw_stop_virtwho_new(remote_ip_2)
            # (2) configure remote libvirt mode on host2, generate fake remote libvirt data
            self.set_virtwho_sec_config(mode, remote_ip_2)
            self.generate_fake_file("kvm", fake_file, remote_ip_2)
            # (3) delete virt-who's remote libvirt config on host2
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )
            # (4) configure fake mode on host2
            self.set_fake_mode_conf(fake_file, "True", remote_owner, remote_env, remote_ip_2)
            # (5) check if guest uuid is correctly monitored by virt-who.
            self.vw_check_message_in_rhsm_log("%s" % guestuuid, message_exists=True, targetmachine_ip=remote_ip_2)
            # (6) check if virt-who run at fake mode 
            self.vw_check_message_in_rhsm_log('Using configuration "fake"', targetmachine_ip=remote_ip_2)
            # (7) undefine a guest
            self.vw_undefine_guest(guest_name)
            # (8) check if the uuid still monitored by virt-who.
            self.vw_check_message_in_rhsm_log("%s" % guestuuid, message_exists=True, targetmachine_ip=remote_ip_2)
            # (9) configure error fake mode on host2
            self.unset_virtwho_d_conf(fake_config_file, targetmachine_ip=remote_ip_2)
            self.set_fake_mode_conf(fake_file, "False", remote_owner, remote_env, remote_ip_2)
            # (10) check if error info will show on log. 
            check_msg = "is not properly formed: uuid key shouldn't be present, try to check is_hypervisor value"
            self.vw_check_message_in_rhsm_log(check_msg, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.unset_virtwho_d_conf(fake_file, remote_ip_2)
            self.unset_virtwho_d_conf(fake_config_file, remote_ip_2)
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
