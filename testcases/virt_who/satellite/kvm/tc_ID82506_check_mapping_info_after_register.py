from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82506_KVM_check_mapping_info_after_register(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) Unregister host and configure kvm
            self.sub_unregister()
            self.update_vw_configure()
            
            # (2) Register host to server and check host/guest mapping info
            register_cmd = "subscription-manager register --username=%s --password=%s" % (SERVER_USER, SERVER_PASS)
            ret, output = self.runcmd(register_cmd, "register system")
            # Check bug 1520762
            if "Host has already been taken" in output:
                register_cmd = "subscription-manager register --username=%s --password=%s" %(SERVER_USER, SERVER_PASS)
                ret, output = self.runcmd(register_cmd, "re-register system")
                logger.info("**********the output info is %s" %output)
            self.vw_check_uuid(guestuuid, checkcmd=register_cmd, uuidexists=True)

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
