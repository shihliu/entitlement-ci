from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID82627_ESX_check_hypervisor_id_in_virtwho_d(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_ESX")

            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guest_uuid = self.esx_get_guest_guid(guest_name)
            host_uuid = self.esx_get_host_uuid()
            esx_host_name = self.esx_get_hostname(esx_host_ip)

            # (1) Set hypervisor_id=uuid, it will show uuid 
            self.set_hypervisor_id("esx", "uuid")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hypervisor_id=hostname, it will show hostname 
            self.set_hypervisor_id("esx", "hostname")
            self.vw_check_mapping_info_in_rhsm_log(esx_host_name, guest_uuid)
            # (3) Set hypervisor_id=hwuuid, esx is not support hwuuid, it will report error
            self.set_hypervisor_id("esx", "hwuuid")
            self.vw_check_message_in_rhsm_log("Reporting of hypervisor hwuuid is not implemented in esx backend|Invalid option hwuuid for hypervisor_id", message_exists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
