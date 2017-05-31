from utils import *
from from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID82505_check_cert_and_rhsm_config(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")

            # (1) Register host to Server 
            if not self.sub_isregistered():
                self.configure_server(SERVER_IP, SERVER_HOSTNAME)
                self.sub_register(SERVER_USER, SERVER_PASS)
            # (2) Check host's cert and rhsm config
            self.check_cert_privilege()
            self.check_rhsm_config(SERVER_HOSTNAME)
            # (3) Start guest and register guest to Server
            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
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
