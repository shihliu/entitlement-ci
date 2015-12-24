from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID477299_ESX_run_virtwho_with_filter_host_parents_null(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            # check the guest is power off or not on esxi host, if power on, stop it firstly 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # stop virt-who firstly 
            self.service_command("stop_virtwho")

            # disable esx config
            self.unset_esx_conf()

            # creat /etc/virt-who.d/virt.esx file for esxi with filter_host_parents="" 
            conf_file = "/etc/virt-who.d/virt.esx"
            self.esx_set_filter_host_parents("", conf_file, esx_owner, esx_env, esx_server, esx_username, esx_password)

            # after stop virt-who, start to monitor the rhsm.log 
            tmp_file = "/tmp/tail.rhsm.log"
            checkcmd = self.get_service_cmd("restart_virtwho")
            self.generate_tmp_log(checkcmd, tmp_file)
            self.esx_check_host_guest_uuid_exist_in_file(host_uuid, guest_uuid, tmp_file, uuid_exist=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.set_esx_conf()
            self.service_command("restart_virtwho")
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

