from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID477180_ESX_run_virtwho_with_env_owner(ESXBase):
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
 
            # restart virt-who service for register esxi hypervisor
            self.service_command("restart_virtwho")

            # stop virt-who service
            self.service_command("stop_virtwho")

            # run virt-who with an wrong --esx-owner=xxxxxx
            cmd = "virt-who --esx --esx-owner=xxxxxx --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -o -d" % (esx_env, esx_server, esx_username, esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an wrong: --esx-owner=xxxxxx")
            if ret == 0 and "ERROR" in output:
                logger.info("Succeeded to check, with an wrong esx-owner, no host/guest mapping send.")
            elif host_uuid in output and guest_uuid in output:
                raise FailException("Failed to check, with an wrong esx-owner, virt-who should not send host/guest mapping.")
            else:
                raise FailException("Failed to run virt-who with an wrong esx-owner.")

            # run virt-who with an wrong ----esx-env=xxxxxx
            cmd = "virt-who --esx --esx-owner=%s --esx-env=xxxxxx --esx-server=%s --esx-username=%s --esx-password=%s -o -d" % (esx_owner, esx_server, esx_username, esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an wrong: --esx-env=xxxxxx")
            if ret == 0 and "ERROR" in output:
                logger.info("Succeeded to check, with an wrong esx-env, no host/guest mapping send.")
            elif host_uuid in output and guest_uuid in output:
                raise FailException("Failed to check, with an wrong esx-env, virt-who should not send host/guest mapping.")
            else:
                raise FailException("Failed to run virt-who with an wrong esx-env.")

            # run virt-who with an wrong ----esx-env=xxxxxx and --esx-owner=xxxxxx
            cmd = "virt-who --esx --esx-owner=xxxxxx --esx-env=xxxxxx --esx-server=%s --esx-username=%s --esx-password=%s -o -d" % (esx_server, esx_username, esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an wrong: --esx-env=xxxxxx and --esx-owner=xxxxxx")
            if ret == 0 and "ERROR" in output:
                logger.info("Succeeded to check, with an wrong esx-env and esx-owner, no host/guest mapping send.")
            elif host_uuid in output and guest_uuid in output:
                raise FailException("Failed to check, with an wrong esx-env and esx-owner, virt-who should not send host/guest mapping.")
            else:
                raise FailException("Failed to run virt-who with an wrong esx-env and esx-owner.")

            # run virt-who with right --esx-owner=%s --esx-env=%s
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -o -d" % (esx_owner, esx_env, esx_server, esx_username, esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an right: --esx-env and --esx-owner")
            if ret == 0 and host_uuid in output and guest_uuid in output:
                logger.info("Succeeded to check, with an right esx-env and esx-owner, host/guest mapping can be sent.")
            else:
                raise FailException("Failed to run virt-who with an right esx-env and esx-owner.")

            # update vrit-who config with an wrong esx_owner, esx_env 
            self.update_esx_vw_configure("xxxxxx", "xxxxxx", esx_server, esx_username, esx_password)

            # after stop virt-who, start to monitor the rhsm.log 
            self.service_command("stop_virtwho")
            tmp_file = "/tmp/tail.rhsm.log"
            checkcmd = self.get_service_cmd("restart_virtwho")
            self.generate_tmp_log(checkcmd, tmp_file)
            # after restart virt-who, stop to monitor the rhsm.log
            cmd = "cat %s" % tmp_file
            ret, output = self.runcmd(cmd, "feedback tail log for parse")
            if ret == 0 and output is not None and "ERROR" in output:
                logger.info("Succeeded to check, can find the ERROR info in rhsm.log with an wrong env and owner.")
            else:
                raise FailException("Failed to check, no ERROR info found in rhsm.log with an wrong env and owner")

            # update vrit-who config with an right esx_owner, esx_env 
            self.update_esx_vw_configure(esx_owner, esx_env, esx_server, esx_username, esx_password)

            # after stop virt-who, start to monitor the rhsm.log 
            self.service_command("stop_virtwho")
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
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
