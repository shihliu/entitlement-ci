from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17216_libvirt_check_env_option_by_cli(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip = get_exported_param("REMOTE_IP")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            error_msg_without_env = self.get_vw_cons("libvirt_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("libvirt_error_msg_with_wrong_env")
            libvirt_owner, libvirt_env, libvirt_username, libvirt_password = self.get_libvirt_info()
            self.runcmd_service("stop_virtwho", remote_ip_2)

            # (1) When "--libvirt-env" is not exist, virt-who should show error info
            cmd_without_env = "virt-who --libvirt --libvirt-owner=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, remote_ip, libvirt_username, libvirt_password) + " -o -d"
            self.vw_check_message(cmd_without_env, error_msg_without_env, cmd_retcode=1, targetmachine_ip=remote_ip_2)
            # (2) When "--libvirt-env" with wrong config, virt-who should show error info
            cmd_with_wrong_owner = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, self.get_vw_cons("wrong_env"), remote_ip, libvirt_username, libvirt_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, error_msg_with_wrong_env, targetmachine_ip=remote_ip_2)
            # (3) When "--libvirt-env" with correct config, virt-who should show error info
            cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, libvirt_env, remote_ip, libvirt_username, libvirt_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1, remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
