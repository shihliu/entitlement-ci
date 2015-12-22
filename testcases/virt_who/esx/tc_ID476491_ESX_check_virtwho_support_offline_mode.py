from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID476491_ESX_check_virtwho_support_offline_mode(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
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
            self.generate_tmp_log(tmp_file)
            self.esx_check_host_guest_uuid_exist_in_file(host_uuid, guest_uuid, tmp_file, destination_ip)

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
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

