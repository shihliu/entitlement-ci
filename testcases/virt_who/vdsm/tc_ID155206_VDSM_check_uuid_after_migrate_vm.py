from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID155206_VDSM_check_uuid_after_migrate_vm(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = self.get_vw_cons("RHEVM_HOST")
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            dest_host_uuid = self.vdsm_get_host_uuid(dest_host_name, rhevm_ip)

            # (1) start guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
 
            # (2) migrate guest from host1 to host2
            self.rhevm_migrate_vm(guest_name, dest_host_name , dest_host_uuid, rhevm_ip)
 
            # check if the uuid is correctly monitored by virt-who in host1 and host2.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=get_exported_param("REMOTE_IP_2"))

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
