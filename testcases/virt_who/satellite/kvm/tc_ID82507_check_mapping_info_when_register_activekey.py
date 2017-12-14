from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82507_KVM_check_mapping_info_when_register_activekey(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            kvm_owner, kvm_env, kvm_username, kvm_password = self.get_libvirt_info()
            key_name = "define_key"
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) Unregister host
            self.sub_unregister()
            # (2) Config hammer and create defined active key
            self.conf_hammel_credential(SERVER_USER, SERVER_PASS, SERVER_IP)
            self.create_active_key(key_name, kvm_env, SERVER_IP)
            # (3) Register host to server with active key and check host/guest mapping info
            register_cmd = "subscription-manager register --org=%s --activationkey=%s" % (kvm_env, key_name)
            ret, output = self.runcmd(register_cmd, "register system")
            # Check bug 1520762
            if "Host has already been taken" in output:
                register_cmd = "subscription-manager register --org=%s --activationkey=%s --force" % (kvm_env, key_name)
                ret, output = self.runcmd(register_cmd, "re-register system")
                logger.info("**********the output info is %s" %output)
            self.sub_unregister()
            self.vw_check_uuid(guestuuid, checkcmd=register_cmd, uuidexists=True)
            # (4) Unregister host then register with active key
            self.sub_unregister()
            self.register_with_active_key(key_name, kvm_env)
            # (5) Restart virt-who and Check host/guest mappping info
            self.vw_check_uuid(guestuuid, uuidexists=True)

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
