from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID202507_ESX_verify_virtwho_interval(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            # 0).check the hostuuid and guestuuid
            host_uuid = self.esx_get_host_uuid(destination_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # 1). stop virt-who first
            self.service_command("stop_virtwho")

            # 2). fetch virt-who cmd with  -i 3 -d
            tmp_file = "/tmp/tail.rhsm.log"
            cmd = "nohup " + self.virtwho_cli("esx") + " -i 3 -d >%s 2>&1 &" % tmp_file
            self.runcmd(cmd, "start to run virt-who")

            # 3). kill virtwho pid after 15s
            time.sleep(15)
            self.kill_virt_who_pid()

            # 4). check host_uuid and guest_uuid from log file
            self.esx_check_host_guest_uuid_exist_in_file(host_uuid, guest_uuid, tmp_file, destination_ip)

            # 5). recover virt-who service 
            self.service_command("restart_virtwho")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
