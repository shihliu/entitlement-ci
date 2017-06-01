from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID82506_HYPERV_check_mapping_info_after_register(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            guestuuid = self.hyperv_get_guest_guid(guest_name)
            hostuuid = self.hyperv_get_host_uuid()

            # (1) Unregister host and configure hyperv
            self.sub_unregister()
            self.set_hyperv_conf()
            # (2) Register host to server and check host/guest mapping info
            register_cmd = "subscription-manager register --username=%s --password=%s" %(SERVER_USER, SERVER_PASS)
            self.hypervisor_check_uuid(hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)

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
