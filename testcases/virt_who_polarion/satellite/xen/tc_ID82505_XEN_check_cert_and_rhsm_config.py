from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID82505_XEN_check_cert_and_rhsm_config(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            # (1) Register host to Server 
            if not self.sub_isregistered():
                self.configure_server(SERVER_IP, SERVER_HOSTNAME)
                self.sub_register(SERVER_USER, SERVER_PASS)
            # (2) Check host's cert and rhsm config
            self.check_cert_privilege()
            self.check_rhsm_config(SERVER_HOSTNAME)
            # (3) Start guest and register guest to Server
            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) Check guest's cert and rhsm config
            self.check_cert_privilege(guestip)
            self.check_rhsm_config(SERVER_HOSTNAME, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
