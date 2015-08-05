from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID477302_ESX_run_virtwho_with_filter_host_parents(VIRTWHOBase):
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

            #3). creat /etc/virt-who.d/virt.esx file for esxi with filter_host_parents="" to parser domain-xxx info
            conf_file = "/etc/virt-who.d/virt.esx"
            conf_data = '''[test-esx1]
type=esx
server=%s
username=%s
password=%s
filter_host_parents=""
owner=%s
env=%s''' % (VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV)

            self.set_virtwho_d_conf(conf_file, conf_data)

            #4). run virt-who one-shot with above config
            cmd = "virt-who -o -d"
            ret, output = self.runcmd(cmd, "executing virt-who with -o -d")
            if ret == 0 and output is not None:
                domain_list = re.findall(r"'domain-.*?'", output, re.I)
                if len(domain_list) > 0:
                    domain_list = ','.join(list(set(domain_list))).replace("'", "\"")
                else:
                    raise FailException("Failed, no domain host found.")
            else:
                raise FailException("Failed to execute virt-who with -o -d")

            #5). remove above /etc/virt-who.d/virt.esx
            self.unset_virtwho_d_conf(conf_file)

            #6). creat /etc/virt-who.d/virt.esx file for esxi with filter_host_parents=domain_list 
            conf_file = "/etc/virt-who.d/virt.esx"
            conf_data = '''[test-esx1]
type=esx
server=%s
username=%s
password=%s
owner=%s
env=%s
filter_host_parents=%s''' % (VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV, domain_list)

            self.set_virtwho_d_conf(conf_file, conf_data)

            #7). virt-who restart
            self.service_command("restart_virtwho")

            #8). check whether the host/guest association info has been sent to server
            if self.esx_check_uuid_exist_in_rhsm_log(host_uuid) and self.esx_check_uuid_exist_in_rhsm_log(guestuuid): 
                logger.info("Succeeded to check uuid list, host/guest association info can be found from rhsm.log.")
            else:
                raise FailException("Failed to check uuid list, host/guest association info should not be found from rhsm.log.")

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

