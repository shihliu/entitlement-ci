from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID477303_ESX_run_virtwho_with_exclude_host_parents_null(VIRTWHOBase):
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

            #6). creat /etc/virt-who.d/virt.esx file for esxi with exclude_host_parents=""
            conf_file = "/etc/virt-who.d/virt.esx"
            conf_data = '''[test-esx1]
type=esx
server=%s
username=%s
password=%s
owner=%s
env=%s
exclude_host_parents=%s''' % (VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV, domain_list)

            self.set_virtwho_d_conf(conf_file, conf_data)

            #5). after stop virt-who, start to monitor the rhsm.log 
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")

            #6). virt-who restart
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running whit exclude_host_parents.")
            else:
                raise FailException("Failed to check, virt-who is not running or active with exclude_host_parents.")

            #7). after restart virt-who, stop to monitor the rhsm.log
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parsing")
            if ret == 0 and output is not None and "ERROR" not in output:
                rex = re.compile(r'Sending update in hosts-to-guests mapping: {}', re.S)
                if len(rex.findall(output))>0:
                    mapping_info = rex.findall(output)[0]
                    if host_uuid not in mapping_info and guestuuid not in mapping_info:
                        logger.info("Succeeded to check, no host_uuid %s and guest_uuid %s found." %(host_uuid, guestuuid))
                    else:
                        raise FailException("Failed to check, should be no host_uuid %s and guest_uuid %s found." %(host_uuid, guestuuid))
                else:
                    raise FailException("Failed to check uuid list, no 'Sending update in hosts-to-guests mapping' keyword found.")
            else:
                raise FailException("Failed to check uuid list, there is an error message found or no data output.")

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

