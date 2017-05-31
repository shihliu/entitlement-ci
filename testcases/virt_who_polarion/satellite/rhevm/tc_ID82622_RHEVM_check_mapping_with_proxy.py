from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID82622_RHEVM_check_mapping_with_proxy(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            http_proxy = self.get_vw_cons("http_proxy")
            guest_uuid = self.rhevm_get_guest_guid(guest_name)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            mode = "rhevm"

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
