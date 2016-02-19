from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17248_RHEVM_check_hypervisor_id_exclude_host_uuids_in_virtwho_d(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            host_name = self.get_hostname(get_exported_param("REMOTE_IP"))
            host_hwuuid = self.get_host_hwuuid_on_rhevm(get_exported_param("REMOTE_IP"), rhevm_ip)
            host_name_sec = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            host_uuid_sec = self.get_host_uuid_on_rhevm(get_exported_param("REMOTE_IP_2"), rhevm_ip)
            host_hwuuid_sec = self.get_host_hwuuid_on_rhevm(get_exported_param("REMOTE_IP_2"), rhevm_ip)

            # (1) Set hypervisor_id=uuid and exclude_host_uuids=host_uuid, it will not show host1/guest uuid mapping info, it will show host2/guest uuid mapping info
            self.set_hypervisor_id_exclude_host_uuids("rhevm", "uuid", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "")
            self.vw_check_mapping_info_in_rhsm_log(host_name, uuid_exist=False)
            self.vw_check_message_in_rhsm_log("%s|%s|%s" % (host_hwuuid, host_name_sec, host_hwuuid_sec), message_exists=False)
            # (2) Set hypervisor_id=hostname and exclude_host_uuids=host_name, it will not show host1/guest name mapping info, it will show host2/guest name mapping info
            self.set_hypervisor_id_exclude_host_uuids("rhevm", "hostname", host_name)
            self.vw_check_mapping_info_in_rhsm_log(host_name, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_name_sec, "")
            self.vw_check_message_in_rhsm_log("%s|%s|%s|%s" % (host_uuid, host_hwuuid, host_uuid_sec, host_hwuuid_sec), message_exists=False)
            # (3) Set hypervisor_id=hwuuid, and exclude_host_uuids, it will not show host1/guest hwuuid mapping info, it will show host2/guest hwuuid mapping info
            self.set_hypervisor_id_exclude_host_uuids("rhevm", "hwuuid", host_hwuuid)
            self.vw_check_mapping_info_in_rhsm_log(host_hwuuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_hwuuid_sec, "")
            self.vw_check_mapping_info_in_rhsm_log(host_name, uuid_exist=False)
            self.vw_check_message_in_rhsm_log("%s|%s|%s" % (host_uuid, host_name_sec, host_uuid_sec), message_exists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
