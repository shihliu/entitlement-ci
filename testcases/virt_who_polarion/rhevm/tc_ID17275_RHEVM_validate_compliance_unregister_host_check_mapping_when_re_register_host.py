from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17275_RHEVM_validate_compliance_unregister_host_check_mapping_when_re_register_host(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.vw_restart_virtwho()

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (1) Validate guest consumed bonus pool will revoke after unregister host
            # subscribe the host to the physical pool which can generate bonus pool
            # host subscribe physical pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (2) Check guest uuid after unregister host and hypervisor
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
            self.sub_refresh(guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip, productexists=False)
            # (3) Check guest uuid after re-register
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
