from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID174959_ESX_validate_mapping_info_after_re_register_host(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not on esxi host, if power on, stop it 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). register esxi host on sam by restart virt-who service 
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running.")
            else:
                raise FailException("Failed to check, virt-who is not running or active.")

            #2). check esxi host is registered or not on sam
            time.sleep(10)
            self.esx_check_host_in_samserv(host_uuid, SERVER_IP)

            #3). unregister or remove esxi host from sam 
            self.service_command("stop_virtwho")
            self.esx_remove_host_in_samserv(host_uuid, SERVER_IP)

            #4). after stop virt-who, start to monitor the rhsm.log 
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")

            #5). re-register esxi host on sam by restart virt-who service 
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running.")
            else:
                raise FailException("Failed to check, virt-who is not running or active.")

            #6). check esxi host is registered or not on sam again, and check guest uuid from rhsm.log
            time.sleep(10)
            self.esx_check_host_in_samserv(host_uuid, SERVER_IP)

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
                if host_uuid in mapping_info and guestuuid in mapping_info:
                    logger.info("Succeeded to check, can find host_uuid %s and guest_uuid %s" %(host_uuid, guestuuid))
                else:
                    raise FailException("Failed to check, can not find host_uuid %s and guest_uuid %s" %(host_uuid, guestuuid))
            else:
                raise FailException("Failed to check, there is an error message found or no output data.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)

        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SERVER_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
