from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17237_RHEVM_check_filter_host_uuids_in_virtwho_d(VDSMBase):
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
            host_uuid_sec = self.get_host_uuid_on_rhevm(get_exported_param("REMOTE_IP_2"),rhevm_ip)

            # (1) Filter_host_uuid=host_uuid, check virt-who send correct host/guest mapping to server
            self.set_filter_host_uuids("rhevm", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Filter_host_uuid="", check host/guest mapping 
            self.set_filter_host_uuids("rhevm", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (3) Filter_host_uuid='', check host/guest mapping 
            self.set_filter_host_uuids("rhevm", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (4) Filter_host_uuid=, check host/guest mapping 
            self.set_filter_host_uuids("rhevm", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (5) Filter_host_uuid="host_uuid","host_uuid_sec", virt-who will filter out host_uuid and host_uuid_sec
            self.set_filter_host_uuids("rhevm", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "")
            # (6) Filter_host_uuid='host_uuid','host_uuid_sec', virt-who will filter out host_uuid and host_uuid_sec
            self.set_filter_host_uuids("rhevm", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "")
            # (7) Filter_host_uuid='host_uuid', 'host_uuid_sec', virt-who will filter out host_uuid and host_uuid_sec
            self.set_filter_host_uuids("rhevm", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "")

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
