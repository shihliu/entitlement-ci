from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID155201_RHEVM_check_uuid_after_migrate_vm_restart_vdsm(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
    
            orig_hostname = self.get_hostname()
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            orig_host_uuid = self.get_host_uuid_on_rhevm(orig_hostname, rhevm_ip)
            dest_host_uuid = self.get_host_uuid_on_rhevm(dest_host_name, rhevm_ip)

            # (1) start guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(orig_host_uuid, guestuuid, uuidexists=True)
 
              # (2) Restart vdsmd service 
            self.vw_restart_vdsm_new()

            # (3) migrate guest from host1 to host2
            self.rhevm_migrate_vm(guest_name, dest_host_name , dest_host_uuid, rhevm_ip)
 
            # check if the uuid is correctly monitored by virt-who in host1 and host2.
            self.hypervisor_check_uuid(orig_host_uuid, guestuuid, uuidexists=False)
            self.hypervisor_check_uuid(dest_host_uuid, guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            #  migrate guest back from host2 to host1
            self.rhevm_migrate_vm(guest_name, orig_hostname , orig_host_uuid, rhevm_ip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
