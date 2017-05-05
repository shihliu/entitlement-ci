from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17253_check_uuid_fake_local_libvirt_mode(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            VIRTWHO_OWNER = self.get_vw_cons("server_owner")
            VIRTWHO_ENV = self.get_vw_cons("server_env")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake.conf"

            # define a guest
            self.vw_define_guest(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_stop_virtwho()

            # (1) generate fake file
            self.generate_fake_file("kvm", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) check if guest uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.unset_virtwho_d_conf(fake_config_file)

            # (4) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "True", VIRTWHO_OWNER, VIRTWHO_ENV)
            # (5) check if error message will show on log file 
            self.vw_check_message_in_rhsm_log("is not properly formed: 'uuid'")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.unset_virtwho_d_conf(fake_file)
            self.unset_all_virtwho_d_conf()
            self.vw_restart_virtwho()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
