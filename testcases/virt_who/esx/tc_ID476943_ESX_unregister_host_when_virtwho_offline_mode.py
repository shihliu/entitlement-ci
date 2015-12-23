from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID476943_ESX_unregister_host_when_virtwho_offline_mode(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            product_name = self.get_vw_cons("datacenter_name")
            host_sku_id = self.get_vw_cons("datacenter_sku_id")
            bonus_sku_id = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")

            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            # 0).check the guest is power off or not on esxi host, if power on, stop it firstly 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # 1). stop virt-who firstly 
            self.service_command("stop_virtwho")

            # 2). disable esx config
            self.unset_esx_conf()

            # 3). create offline data
            offline_data = "/tmp/offline.dat"
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -p -d > %s" % (esx_owner, esx_env, esx_server, esx_username, esx_password, offline_data)
            ret, output = self.runcmd(cmd, "executing virt-who with -p -d for offline mode.")
            if ret == 0:
                logger.info("Succeeded to execute virt-who with -p -d for offline mode. ")
            else:
                raise FailException("Failed to execute virt-who with -o -d")

            # 4). creat /etc/virt-who.d/virt.fake file for offline mode
            conf_file = "/etc/virt-who.d/virt.fake"
            conf_data = '''[fake-virt]
type=fake
file=%s
is_hypervisor=True
owner=%s
env=%s''' % (offline_data, esx_owner, esx_env)

            self.set_virtwho_d_conf(conf_file, conf_data)

            # 5). after stop virt-who, start to monitor the rhsm.log 
            tmp_file = "/tmp/tail.rhsm.log"
            checkcmd = self.get_service_cmd("restart_virtwho")
            self.generate_tmp_log(checkcmd, tmp_file)
            self.esx_check_host_guest_uuid_exist_in_file(host_uuid, guest_uuid, tmp_file)

            # 8).check DataCenter is exist on host/hpyervisor
            host_pool_id = self.get_poolid_by_SKU(host_sku_id)
            if host_pool_id is not None or host_pool_id != "":
                logger.info("Succeeded to find the pool id of '%s': '%s'" % (host_sku_id, host_pool_id))
            else:
                raise FailException("Failed to find the pool id of %s" % host_sku_id)

            # 9).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)

            # 10).subscribe successfully to the DataCenter subscription pool on host
            self.server_subscribe_system(host_uuid, host_pool_id, server_ip)

            # 11).check the bonus pool is available
            if self.check_bonus_exist(bonus_sku_id, bonus_quantity, guestip) is True:
                logger.info("Succeeded to find the bonus pool of product '%s'" % product_name)
            else:
                raise FailException("Failed to find the bonus pool from guest.")

            # 12).subscribe to the bonus pool. 
            self.sub_subscribe_sku(bonus_sku_id, guestip)

            # 13).check the consumed product
            self.sub_listconsumed(product_name, guestip)

            # 14). unregister esxi host
            self.server_unsubscribe_all_system(host_uuid, server_ip)

            # 15). check the conusmed product again
            self.sub_refresh(guestip)
            cmd = "subscription-manager list --consumed"
            ret, output = self.runcmd(cmd, "list consumed subscriptions", guestip)
            if ret == 0 and "No consumed subscription pools to list" in output:
                logger.info("Succeeded to check, after unsubscribe pool from host, guest's consumed pool will be removed.")
            else:
                raise FailException("Failed to check the consumed subscriptions,should be no any consumed pool found.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            cmd = "rm -f %s" % offline_data
            self.runcmd(cmd, "run cmd: %s" % cmd)
            self.set_esx_conf()
            self.service_command("restart_virtwho")
            # Unregister the ESX host 
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

