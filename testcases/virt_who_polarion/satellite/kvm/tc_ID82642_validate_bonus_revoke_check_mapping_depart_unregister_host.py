from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82642_validate_bonus_revoke_check_mapping_depart_unregister_host(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")
            hostuuid = self.get_hostname()

            self.runcmd_service("restart_virtwho")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # (1) Validate guest consumed bonus pool will revoke after unregister host
            # (1.1)subscribe the host to the physical pool which can generate bonus pool
            # host subscribe datacenter pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (1.2) Check guest uuid after unregister host and hypervisor
            tmp_file = "/tmp/tail.rhsm.log"
            cmd = "subscription-manager unregister"
            self.generate_tmp_log(cmd, tmp_file)
            cmd = "cat %s" % tmp_file
            ret, output = self.runcmd(cmd, "get temporary log generated")
            if ret == 0 and ("not registered" in output or "Successfully un-registered" in output):
                logger.info("Success to check virt-who log after unregister host")
            else:
                raise FailException("failed to check virt-who log after unregister host")
            self.server_remove_system(hostuuid, SERVER_IP)
#             time.sleep(60)
            self.sub_refresh(guestip)
            # (1.3)list consumed subscriptions on guest, bonus pool will revoke
            self.sub_listconsumed(sku_name, guestip, productexists=False)
            # (1.4) Check guest uuid after re-register
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.vw_check_uuid(guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
