from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17247_ESX_check_hypervisor_id_filter_host_uuids_in_virtwho_d(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            esx_host_name = self.esx_get_hostname(esx_host_ip)
            esx_host_ip_second = self.get_vw_cons("ESX_HOST_SECOND")
            esx_host_name_second = self.esx_get_hostname(esx_host_ip_second)
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            host_uuid_second = self.esx_get_host_uuid(esx_host_ip_second)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            self.set_hypervisor_id_filter_host_uuids("esx", "uuid", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_second, uuid_exist=False)
            self.set_hypervisor_id_filter_host_uuids("esx", "hostname", esx_host_name)
            self.vw_check_mapping_info_in_rhsm_log(esx_host_name, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(esx_host_name_second, uuid_exist=False)
            # self.set_hypervisor_id_filter_host_uuids("esx", "hwuuid", host_uuid)
            # do not know how to get hwuuid of esx, just check "host-" here
            # self.vw_check_mapping_info_in_rhsm_log("host-", guest_uuid)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
