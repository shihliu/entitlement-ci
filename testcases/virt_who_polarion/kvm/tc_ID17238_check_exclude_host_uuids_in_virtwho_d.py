from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17238_check_exclude_host_uuids_in_virtwho_d(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.vw_define_guest(guest_name)
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()
            host_uuid_sec = "test"

            # (1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("libvirt", host_uuid, remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("libvirt", host_uuid_sec, remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "\"\"", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "\'\'", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("libvirt", "", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("libvirt", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
