from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID174959_ESX_validate_mapping_info_after_re_register_host(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            # 0).check the guest is power off or not on esxi host, if power on, stop it 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # 1). register esxi host on sam by restart virt-who service 
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running.")
            else:
                raise FailException("Failed to check, virt-who is not running or active.")

            # 2). check esxi host is registered or not on sam
            time.sleep(10)
            self.server_check_system(host_uuid, server_ip)

            # 3). unregister or remove esxi host from sam 
            self.service_command("stop_virtwho")
            self.server_remove_system(host_uuid, server_ip)

            # 4). after stop virt-who, start to monitor the rhsm.log 
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log(tmp_file)

            self.server_check_system(host_uuid, server_ip)

            self.esx_check_host_guest_uuid_exist_in_file(host_uuid, guest_uuid, tmp_file, destination_ip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
