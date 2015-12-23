from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID322864_ESX_check_log_after_add_guest(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            # 1). config the virt-who config file, set VIRTWHO_INTERVAL = 5
            cmd = "sed -i 's/^#VIRTWHO_INTERVAL/VIRTWHO_INTERVAL/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "uncomment VIRTWHO_INTERVAL firstly in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to uncomment VIRTWHO_INTERVAL.")
            else:
                raise FailException("Failed to uncomment VIRTWHO_INTERVAL.")

            cmd = "sed -i 's/^VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=1/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "changing interval time in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=1.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=1.")

            # 2).check the guest is power off or not, if power_on, stop it
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # 3). stop virt-who firstly 
            self.service_command("stop_virtwho")

            # 4). after stop virt-who, start to monitor the rhsm.log 
            tmp_file = "/tmp/tail.rhsm.log"
            checkcmd = self.get_service_cmd("restart_virtwho")
            self.generate_tmp_log(checkcmd, tmp_file)

            self.esx_check_host_guest_uuid_exist_in_file(host_uuid, guest_uuid, tmp_file)

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
