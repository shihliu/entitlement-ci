from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID476491_ESX_check_virtwho_support_offline_mode(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            VIRTWHO_ESX_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
            VIRTWHO_ESX_ENV = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
            VIRTWHO_ESX_SERVER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
            VIRTWHO_ESX_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
            VIRTWHO_ESX_PASSWORD = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not on esxi host, if power on, stop it firstly 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). stop virt-who firstly 
            self.service_command("stop_virtwho")

            #2). disable esx config
            self.unset_esx_conf()

            #3). create offline data
            offline_data = "/tmp/offline.dat"
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -p -d > %s" %(VIRTWHO_ESX_OWNER,VIRTWHO_ESX_ENV,VIRTWHO_ESX_SERVER,VIRTWHO_ESX_USERNAME,VIRTWHO_ESX_PASSWORD,offline_data)
            ret, output = self.runcmd(cmd, "executing virt-who with -p -d for offline mode.")
            if ret == 0:
                logger.info("Succeeded to execute virt-who with -p -d for offline mode. ")
            else:
                raise FailException("Failed to execute virt-who with -o -d")

            #4). creat /etc/virt-who.d/virt.fake file for offline mode
            conf_file = "/etc/virt-who.d/virt.fake"
            conf_data = '''[fake-virt]
type=fake
file=%s
is_hypervisor=True
owner=%s
env=%s''' % (offline_data, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV)

            self.set_virtwho_d_conf(conf_file, conf_data)

            #5). virt-who restart
            self.service_command("restart_virtwho")

            #6). check whether the host/guest association info has been sent to server
            if self.esx_check_uuid_exist_in_rhsm_log(host_uuid) and self.esx_check_uuid_exist_in_rhsm_log(guestuuid):
                logger.info("Succeeded to get uuid list from rhsm.log.")
            else:
                raise FailException("Failed to get uuid list from rhsm.log")

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
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

