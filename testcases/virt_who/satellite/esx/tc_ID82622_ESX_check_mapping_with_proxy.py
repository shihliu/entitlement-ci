from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID82622_ESX_check_mapping_with_proxy(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            http_proxy = self.get_vw_cons("http_proxy")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            mode = "esx"

            # (1) Configure http_proxy
            self.configure_http_proxy(mode, http_proxy, server_hostname)
            # (2) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Check http_proxy in rhsm log
            self.vw_check_message_in_rhsm_log(http_proxy)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_disable("https_proxy")
            self.config_option_disable("no_proxy")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
