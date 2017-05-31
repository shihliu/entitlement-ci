from utils import *
from from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID82506_XEN_check_mapping_info_after_register(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)

            # (1) Unregister host and configure xen
            self.sub_unregister()
            self.set_xen_conf()
            # (2) Register host to server and check host/guest mapping info
            self.xen_start_guest(guest_name, xen_host_ip)
            register_cmd = "subscription-manager register --username=%s --password=%s" %(SERVER_USER, SERVER_PASS)
            self.hypervisor_check_uuid(host_uuid, guest_uuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)

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
