from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID477177_ESX_run_virtwho_with_exclude_host_uuids(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            VIRTWHO_ESX_OWNER = self.get_vw_cons("VIRTWHO_ESX_OWNER")
            VIRTWHO_ESX_ENV = self.get_vw_cons("VIRTWHO_ESX_ENV")
            VIRTWHO_ESX_SERVER = self.get_vw_cons("VIRTWHO_ESX_SERVER")
            VIRTWHO_ESX_USERNAME = self.get_vw_cons("VIRTWHO_ESX_USERNAME")
            VIRTWHO_ESX_PASSWORD = self.get_vw_cons("VIRTWHO_ESX_PASSWORD")

            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")
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

            #3). creat /etc/virt-who.d/virt.esx file for esxi with exclude_host_uuids=""
            conf_file = "/etc/virt-who.d/virt.esx"
            conf_data = '''[test-esx1]
type=esx
server=%s
username=%s
password=%s
owner=%s
env=%s
exclude_host_uuids="%s"''' % (VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV, host_uuid)

            self.set_virtwho_d_conf(conf_file, conf_data)


            #5). after stop virt-who, start to monitor the rhsm.log 
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")

            #6). virt-who restart
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running with exclude_host_uuids.")
            else:
                raise FailException("Failed to check, virt-who is not running or active with exclude_host_uuids.")

            #7). after restart virt-who, stop to monitor the rhsm.log
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parsing")
            if ret == 0 and output is not None and  "ERROR" not in output:
                rex7 = re.compile(r'Sending update in hosts-to-guests mapping: {.*?\n}\n', re.S)
                rex6 = re.compile(r'Sending update in hosts-to-guests mapping: {.*?]}\n', re.S)
                if len(rex7.findall(output)) > 0:
                    mapping_info = rex7.findall(output)[0]
                    logger.info(mapping_info)
                elif len(rex6.findall(output)) > 0:
                    mapping_info = rex6.findall(output)[0]
                else:
                    raise FailException("Failed to check, can not find hosts-to-guests mapping info.")
                logger.info("Check uuid from following data: \n%s" % mapping_info)
                if host_uuid not in mapping_info and guestuuid not in mapping_info:
                    logger.info("Succeeded to check, no host_uuid %s and guest_uuid %s found." %(host_uuid, guestuuid))
                else:
                    raise FailException("Failed to check, should be no host_uuid %s and guest_uuid %s found." %(host_uuid, guestuuid))
            else:
                raise FailException("Failed to check, there is an error message found or no output data.")

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

