from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID476933_RHEVM_validate_offline_mode_bonus_pool_creation(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            VIRTWHO_RHEVM_OWNER = self.get_vw_cons("VIRTWHO_RHEVM_OWNER")
            VIRTWHO_RHEVM_ENV = self.get_vw_cons("VIRTWHO_RHEVM_ENV")
            VIRTWHO_RHEVM_SERVER = "https:\/\/" + rhevm_ip + ":443"
            VIRTWHO_RHEVM_SERVER_2 = "https://" + rhevm_ip + ":443"
            VIRTWHO_RHEVM_USERNAME = self.get_vw_cons("VIRTWHO_RHEVM_USERNAME")
            VIRTWHO_RHEVM_PASSWORD = self.get_vw_cons("VIRTWHO_RHEVM_PASSWORD")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            VIRTWHO_FAKE_FILE = "/home/fake"

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            #1). disable rhevm in /etc/sysconfig/virt-who
            cmd = "sed -i -e 's/.*VIRTWHO_RHEVM=.*/#VIRTWHO_RHEVM=1/g' /etc/sysconfig/virt-who"
            ret, output = self.runcmd(cmd, "Configure virt-who to disable VIRTWHO_RHEVM")
            if ret == 0:
                logger.info("Succeeded to disable VIRTWHO_RHEVM.")
            else:
                raise FailException("Test Failed - Failed to disable VIRTWHO_RHEVM.")

            #2). stop virt-who and remove hypervisor
            self.service_command("stop_virtwho")
            self.server_remove_system(hostuuid, SERVER_IP)
            # generate remote libvirt mapping info to /home/fake
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s -p -d > %s" % (VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, VIRTWHO_FAKE_FILE)
            ret, output = self.runcmd(cmd)
            if ret == 0 :
                logger.info("Succeeded to generate info which used to make virt-who run at fake mode")
            else:
                raise FailException("Test Failed - Failed to generate info which used to make virt-who run at fake mode")

            # creat /etc/virt-who.d/fake file which make virt-who run at fake mode
            conf_file = "/etc/virt-who.d/fake"
            conf_data = '''[fake]
type=fake
file=%s
is_hypervisor=True
owner=%s
env=%s''' % (VIRTWHO_FAKE_FILE, VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV)

            self.set_virtwho_d_conf(conf_file, conf_data)
            self.service_command("restart_virtwho")
            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the hypervsior to the physical pool which can generate bonus pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)

            # list available pools of guest, check related bonus pool generated.
            new_available_poollist = self.sub_listavailpools(test_sku, guestip)
            if new_available_poollist != None:
                for item in range(0, len(new_available_poollist)):
                    if "Temporary" in new_available_poollist[item]["SubscriptionType"]:
                        raise FailException("virt-who failed to get host/guest mapping.")
                    if "Available" in new_available_poollist[item]:
                        SKU_Number = "Available"
                    else:
                        SKU_Number = "Quantity"
                    if new_available_poollist[item]["SKU"] == test_sku and self.check_type_virtual(new_available_poollist[item]) and new_available_poollist[item][SKU_Number] == bonus_quantity:
                        logger.info("Succeeded to list bonus pool of product %s" % sku_name) 
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to get available pool list from guest.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe all subscriptions on  hypervisor
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.unset_virtwho_d_conf(conf_file)
            self.update_rhel_rhevm_configure("5", VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, debug=1)
            self.service_command("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
