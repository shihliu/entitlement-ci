from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID82507_HYPERV_check_mapping_info_when_register_activekey(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            key_name="define_key"
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            guestuuid = self.hyperv_get_guest_guid(guest_name)
            hostuuid = self.hyperv_get_host_uuid()

            # (1) Unregister host
            self.sub_unregister()
            # (2) Config hammer and create defined active key
            self.conf_hammel_credential(SERVER_USER, SERVER_PASS, SERVER_IP)
            self.create_active_key(key_name, hyperv_env, SERVER_IP)
            # (3) Register host to server with active key and check host/guest mapping info
            register_cmd = "subscription-manager register --org=%s --activationkey=%s" % (hyperv_env, key_name)
            self.hypervisor_check_uuid(hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)
            # (4) Unregister host then register with active key
            self.sub_unregister()
            self.register_with_active_key(key_name, hyperv_env)
            # (5) Restart virt-who and Check host/guest mappping info
            time.sleep(10)
            self.vw_check_mapping_info_in_rhsm_log(hostuuid, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_unregister()
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
