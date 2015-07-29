from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID322864_ESX_check_log_after_add_guest(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            #1). config the virt-who config file, set VIRTWHO_INTERVAL = 5
            cmd = "sed -i 's/^#VIRTWHO_INTERVAL/VIRTWHO_INTERVAL/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "uncomment VIRTWHO_INTERVAL firstly in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to uncomment VIRTWHO_INTERVAL.")
            else:
                raise FailException("Failed to uncomment VIRTWHO_INTERVAL.")

            cmd = "sed -i 's/^VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=1/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "changing interval time in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=1.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=1.")

            #2).check the guest is power off or not, if power_on, stop it
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #3).restart virtwho service
            self.vw_restart_virtwho_new()

            #4).check virt-who log
            rhsmlogpath='/var/log/rhsm/rhsm.log'
            cmd = "tail -50 %s " % rhsmlogpath
            ret, output = self.runcmd(cmd, "check output in rhsm.log")
            if ret == 0 and ("AttributeError" not in output) and ("propSet" not in output) :
                logger.info("Success to check virt-who log normally after add a new guest.")
            else:
                raise FailException("Failed to check virt-who log normally after add a new guest.")
    
            #5).check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid_exist_in_rhsm_log(host_uuid)
            self.esx_check_uuid_exist_in_rhsm_log(guestuuid)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SAM_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
