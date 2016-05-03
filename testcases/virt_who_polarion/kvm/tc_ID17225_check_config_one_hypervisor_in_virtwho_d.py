from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17225_check_config_one_hypervisor_in_virtwho_d(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            self.runcmd_service("stop_virtwho", remote_ip_2)
            self.update_vw_configure(targetmachine_ip=remote_ip_2)

            # (1) Config libvirt mode in /etc/virt-who.d
            self.set_virtwho_sec_config("libvirt", remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
