from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17238_RHEVM_check_exclude_host_uuids_in_virtwho_d(VDSMBase):
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

            #(1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("rhevm", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            #(2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("rhevm", host_uuid_sec)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            #(3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("rhevm", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            #(4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("rhevm", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            #(5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("rhevm", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            #(6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("rhevm", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, guest_uuid, uuid_exist=False)
            #(7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("rhevm", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, guest_uuid, uuid_exist=False)
            #(8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("rhevm", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, guest_uuid, uuid_exist=False)

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
