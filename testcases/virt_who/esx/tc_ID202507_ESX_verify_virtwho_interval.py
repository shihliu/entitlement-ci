from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID202507_ESX_verify_virtwho_interval(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the hostuuid and guestuuid
            host_uuid = self.esx_get_host_uuid(destination_ip)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). stop virt-who first
            self.service_command("stop_virtwho")

            #2). fetch virt-who cmd with  -i 3 -d 
            cmd = "nohup " + self.virtwho_cli("esx") + " -i 3 -d >/tmp/tail.rhsm.log 2>&1 &"
            self.runcmd(cmd, "start to run virt-who")

            #3). kill virtwho pid after 15s
            time.sleep(15)
            cmd = "ps -ef | grep virtwho.py -i | grep -v grep | awk '{print $2}'"
            ret, output = self.runcmd(cmd, "start to check virt-who pid")
            if ret ==0 and output is not None:
                pids = output.strip().split('\n')
                for pid in pids:
                    kill_cmd = "kill -9 %s" %pid
                    self.runcmd(kill_cmd, "kill virt-who pid %s" %pid)

            #4). check host_uuid and guest_uuid from log file
            cmd = "cat /tmp/tail.rhsm.log"
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

            #5). recover virt-who service 
            self.service_command("restart_virtwho")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
