from utils import *
from from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID82622_check_mapping_with_proxy(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            http_proxy = self.get_vw_cons("http_proxy")
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()
            remote_ip_2 = get_exported_param("REMOTE_IP_2")      
            mode = "libvirt"

            # (1) Configure http_proxy
            self.set_remote_libvirt_conf(get_exported_param("REMOTE_IP"), remote_ip_2)
            self.configure_http_proxy(mode, http_proxy, server_hostname, remote_ip_2)
            # (2) Check host/guest mappping info
            self.vw_check_message_in_rhsm_log(guest_uuid, remote_ip_2)
            # (3) Check http_proxy in rhsm log
            self.vw_check_message_in_rhsm_log(http_proxy, remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.config_option_disable("http_proxy", remote_ip_2)
            self.config_option_disable("no_proxy", remote_ip_2)
            self.clean_remote_libvirt_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho")
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
