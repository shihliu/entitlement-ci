from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID155173_ESX_check_uuid_when_guest_paused_or_shutdown(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # if the below step(1,2,3) failed, the guest will can't be stop.
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)

            # (1) start a guest    
            self.esx_start_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            if self.check_uuid_oneshot(guestuuid, "esx"):
                logger.info("Succeeded to find guestuuid from oneshot output when guest start")
            else:
                raise FailException("Failed to find guestuuid from oneshot output when guest start")

            # (2)pause a guest
            self.esx_pause_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            if self.check_uuid_oneshot(guestuuid, "esx"):
                logger.info("Succeeded to find guestuuid from oneshot output when guest pause")
            else:
                raise FailException("Failed to find guestuuid from oneshot output when guest pause")

            # (3)resume a guest
            self.esx_resume_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            if self.check_uuid_oneshot(guestuuid, "esx"):
                logger.info("Succeeded to find guestuuid from oneshot output when guest resume")
            else:
                raise FailException("Failed to find guestuuid from oneshot output when guest resume")

            # (4)shutdown a guest
            self.esx_stop_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            if self.check_uuid_oneshot(guestuuid, "esx"):
                logger.info("Succeeded to find guestuuid from oneshot output when guest shutdown")
            else:
                raise FailException("Failed to find guestuuid from oneshot output when guest shutdown")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
