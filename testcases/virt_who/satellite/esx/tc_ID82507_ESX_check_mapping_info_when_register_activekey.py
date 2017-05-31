from utils import *
from from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID82507_ESX_check_mapping_info_when_register_activekey(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            key_name="define_key"
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guestuuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            hostuuid = self.esx_get_host_uuid(esx_host_ip)

            # (1) Unregister host
            self.sub_unregister()
            # (2) Config hammer and create defined active key
            self.conf_hammel_credential(SERVER_USER, SERVER_PASS, SERVER_IP)
            self.create_active_key(key_name, esx_env, SERVER_IP)
            # (3) Register host to server with active key and check host/guest mapping info
            register_cmd = "subscription-manager register --org=%s --activationkey=%s" % (esx_env, key_name)
            self.hypervisor_check_uuid(hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)
            # (4) Unregister host then register with active key
            self.sub_unregister()
            self.register_with_active_key(key_name, esx_env)
            # (5) Restart virt-who and Check host/guest mappping info
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
