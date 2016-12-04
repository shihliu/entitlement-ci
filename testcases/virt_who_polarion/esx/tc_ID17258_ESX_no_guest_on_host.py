from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17258_ESX_no_guest_on_host(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)

            self.esx_remove_guest(guest_name, esx_host_ip)
            self.vw_check_mapping_info_in_rhsm_log("", guest_uuid, uuid_exist=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.esx_add_guest(guest_name, esx_host_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
