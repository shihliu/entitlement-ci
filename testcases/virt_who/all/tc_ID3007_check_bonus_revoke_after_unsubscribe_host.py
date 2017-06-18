from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID3007_check_bonus_revoke_after_unsubscribe_host(VIRTWHOBase):
    def run_kvm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            self.runcmd_service("restart_virtwho")

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (1) Validate guest consumed bonus pool will revoke after remove consumed sku on host
            # subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # unsubscribe all consumed sku on hosts
            self.sub_unsubscribe()
            # list consumed subscriptions on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.sub_unregister(guestip)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.vw_stop_guests(guest_name)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            guestuuid = self.vw_get_uuid(guest_name, remote_ip_1)
            host_uuid = self.get_host_uuid(remote_ip_1)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.vw_start_guests(guest_name, remote_ip_1)
            guestip = self.kvm_get_guest_ip(guest_name, remote_ip_1)
            self.runcmd_service("restart_virtwho")

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (1) Validate guest consumed bonus pool will revoke after remove consumed sku on host
            # Subscribe hypervisor
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # unsubscribe all consumed sku on hosts
            self.server_unsubscribe_all_system(host_uuid, SERVER_IP)
            # list consumed subscriptions on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.sub_unregister(guestip)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.vw_stop_guests(guest_name, remote_ip_1)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (1) Validate guest consumed bonus pool will revoke after remove consumed sku on host
            # subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # unsubscribe all consumed sku on hosts
            self.sub_unsubscribe()
            # list consumed subscriptions on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.sub_unregister(guestip)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.skipTest("test case skiped, not fit for rhevm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.skipTest("test case skiped, not fit for hyperv ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")
            sku_quantity = self.get_vw_cons("guestlimit_unlimited_guest")

            self.vw_restart_virtwho()

            # start guest
            if self.esx_guest_ispoweron(guest_name, esx_host_ip):
                self.esx_stop_guest(guest_name, esx_host_ip)
            self.esx_start_guest(guest_name, esx_host_ip)
            guestip = self.esx_get_guest_ip(guest_name, esx_host_ip)

            # register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)

            # subscribe esx host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), server_ip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            # list consumed subscriptions on the guest, should be listed
            self.sub_listconsumed(sku_name, guestip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.check_bonus_exist(sku_id, sku_quantity, guestip, bonus_exist=False)
            # list consumed subscriptions on the guest, should be not revoked
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.skipTest("test case skiped, not fit for xen ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            hypervisor_type = get_exported_param("HYPERVISOR_TYPE")
            if hasattr(self, "run_" + hypervisor_type):
                getattr(self, "run_" + hypervisor_type)()
            else:
                self.skipTest("test case skiped, not fit for %s" % hypervisor_type)
            self.assert_(True, case_name)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
