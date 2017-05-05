from utils import *
from testcases.virt_who_polarion.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class XENBase(VIRTWHOBase):

    def xen_get_hostname(self, targetmachine_ip=""):
        cmd = "hostname"
        ret, output = self.runcmd_xen(cmd, "geting xenserver hostname", targetmachine_ip)
        if ret == 0:
            hostname = output.strip(' \r\n').strip('\r\n') 
            logger.info("Succeeded to get xenserver hostname %s." % hostname) 
            return hostname
        else:
            raise FailException("Test Failed - Failed to get xenserver hostname %s." % self.get_hg_info(targetmachine_ip))

    def __get_vm_mac_addr(self, guest_name, targetmachine_ip=""):
        cmd = "xe vm-vif-list vm=%s" % guest_name
        ret, output = self.runcmd_xen(cmd, "get guest's mac", targetmachine_ip)
        if ret == 0:
            rex = re.compile(r'MAC(.*?)\n', re.S)
            mac = rex.findall(output)[0].split(": ")[1].strip()
            return mac
        else:
            raise FailException("Failed to get vm %s mac" % guest_name)

    def __generate_ipget_file(self, targetmachine_ip=""):
        generate_ipget_cmd = "wget -nc %s/ipget_xen.sh -P /root/ && chmod 777 /root/ipget_xen.sh" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd_xen(generate_ipget_cmd, "wget ipget_xen.sh file", targetmachine_ip)
        if ret == 0 or "already there" in output:
            logger.info("Succeeded to wget ipget.sh to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget ipget.sh to /root/.")

    def __mac_to_ip(self, mac, targetmachine_ip=""):
        if not mac:
            raise FailException("Failed to get guest mac ...")
        while True:
            cmd = "sh /root/ipget_xen.sh %s | grep -v nmap" % mac
            ret, output = self.runcmd_xen(cmd, "nmap to get guest ip via mac %s" % mac, targetmachine_ip, showlogger=False)
            if ret == 0:
                if "can not get ip by mac" not in output:
                    ip = output.strip("\n").strip("")
                    logger.info("Succeeded to get ip address %s." % ip)
                    time.sleep(10)
                    return ip
                else:
                    time.sleep(10)
            else:
                raise FailException("Test Failed - Failed to get ip address.")

    def xen_get_guest_ip(self, guest_name, targetmachine_ip=""):
        ''' get guest ip address in xenserver '''
        self.__generate_ipget_file(targetmachine_ip)
        guestip = self.__mac_to_ip(self.__get_vm_mac_addr(guest_name, targetmachine_ip), targetmachine_ip)
        if guestip == None or guestip == "":
            raise FailException("Faild to get guest %s ip." % guest_name)
        else:
            return guestip

#     def xen_get_guest_id(self, guest_name, targetmachine_ip=""):
#     # Get guest's id
#         output = self.runcmd_xen("Get-VM %s | select *" % guest_name)
#         if output is not "":
#             logger.info("Success to run command to get vm %s ID" % guest_name)
#             guest_id = self.get_key_rhevm(output, "Id", "VMName", guest_name)
#             logger.info("before decode guest uuid is %s" % guest_id)
#             guest_uuid_after_decode = self.decodeWinUUID(guest_id)
#             logger.info("after decode guest uuid is %s" % guest_uuid_after_decode)
#             return guest_id 
#         else:
#             raise FailException("Failed to run command to get vm %s ID" % guest_name)

    def xen_get_guest_uuid(self, guest_name, targetmachine_ip=""):
        cmd = "xe vm-list name-label=%s" % guest_name
        ret, output = self.runcmd_xen(cmd, "get guest's uuid", targetmachine_ip)
        if ret == 0:
            rex = re.compile(r'uuid(.*?)\n', re.S)
            guest_uuid = rex.findall(output)[0].split(":")[1].strip()
            return guest_uuid
        else:
            raise FailException("Failed to get vm %s uuid" % guest_name)

    def xen_get_host_uuid(self, targetmachine_ip=""):
        cmd = "xe host-list name-label=%s" % self.get_vw_cons("XEN_HOST_NAME_LABEL")
        ret, output = self.runcmd_xen(cmd, "get host's uuid", targetmachine_ip)
        if ret == 0:
            rex = re.compile(r'uuid(.*?)\n', re.S)
            guest_uuid = rex.findall(output)[0].split(":")[1].strip()
            return guest_uuid
        else:
            raise FailException("Failed to get host's uuid")

    def xen_get_hw_uuid(self, targetmachine_ip=""):
        cmd = "xe host-get-cpu-features"
        ret, output = self.runcmd_xen(cmd, "get xen hwuuid", targetmachine_ip)
        if ret == 0:
            return output.strip()
        else:
            raise FailException("Failed to get xen hwuuid")

    def xen_get_guest_status(self, guest_name, targetmachine_ip=""):
        cmd = "xe vm-list name-label=%s" % guest_name
        ret, output = self.runcmd_xen(cmd, "get guest's status", targetmachine_ip)
        if ret == 0:
            rex = re.compile(r'power-state(.*?)\n', re.S)
            guest_status = rex.findall(output)[0].split(":")[1].strip()
            return guest_status
        else:
            raise FailException("Failed to get guest %s status" % guest_name)

    def xen_start_guest(self, guest_name, targetmachine_ip=""):
        cmd = "xe vm-start vm=%s" % guest_name
        ret, output = self.runcmd_xen(cmd, "start vm %s" % guest_name, targetmachine_ip)
        if ret == 0:
            status = self.xen_get_guest_status(guest_name, targetmachine_ip)
            if "running" in status:
                logger.info("Success to start vm %s" % guest_name)
            else:
                raise FailException("Failed to start vm %s" % guest_name)
        elif "suspended" in output:
            # if guest in suspended status, resume it
            self.xen_resume_guest(guest_name, targetmachine_ip)
        elif "already running" in output:
            logger.info("Already in running status for vm %s, nothing to do ..." % guest_name)
        else:
            raise FailException("Failed to start vm %s" % guest_name)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def xen_stop_guest(self, guest_name, targetmachine_ip=""):
        cmd = "xe vm-shutdown vm=%s" % guest_name
        ret, output = self.runcmd_xen(cmd, "shutdown vm %s" % guest_name, targetmachine_ip)
        if ret == 0:
            status = self.xen_get_guest_status(guest_name, targetmachine_ip)
            if "halted" in status:
                logger.info("Success to stop vm %s" % guest_name)
            else:
                raise FailException("Failed to stop vm %s" % guest_name)
        elif "didn't acknowledge the need to shutdown" in output:
            logger.info("vm is started, it needn't to shutdown")
        else:
            raise FailException("Failed to shutdown vm %s" % guest_name)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def xen_suspend_guest(self, guest_name, targetmachine_ip=""):
        cmd = "xe vm-suspend vm=%s" % guest_name
        ret, output = self.runcmd_xen(cmd, "suspend vm %s" % guest_name, targetmachine_ip)
        if ret == 0:
            status = self.xen_get_guest_status(guest_name, targetmachine_ip)
            if "suspended" in status:
                logger.info("Success to suspend vm %s" % guest_name)
            else:
                raise FailException("Failed to suspend vm %s" % guest_name)
        else:
            raise FailException("Failed to suspend vm %s" % guest_name)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def xen_resume_guest(self, guest_name, targetmachine_ip=""):
        cmd = "xe vm-resume vm=%s" % guest_name
        ret, output = self.runcmd_xen(cmd, "resume vm %s" % guest_name, targetmachine_ip)
        if ret == 0:
            status = self.xen_get_guest_status(guest_name, targetmachine_ip)
            if "running" in status:
                logger.info("Success to resume vm %s" % guest_name)
            else:
                raise FailException("Failed to resume vm %s" % guest_name)
        else:
            raise FailException("Failed to resume vm %s" % guest_name)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def set_xen_conf(self, debug=1, targetmachine_ip=""):
        xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/.*VIRTWHO_XEN=.*/VIRTWHO_XEN=1/g' -e 's/.*VIRTWHO_XEN_OWNER=.*/VIRTWHO_XEN_OWNER=%s/g' -e 's/.*VIRTWHO_XEN_ENV=.*/VIRTWHO_XEN_ENV=%s/g' -e 's/.*VIRTWHO_XEN_SERVER=.*/VIRTWHO_XEN_SERVER=%s/g' -e 's/.*VIRTWHO_XEN_USERNAME=.*/VIRTWHO_XEN_USERNAME=%s/g' -e 's/.*VIRTWHO_XEN_PASSWORD=.*/VIRTWHO_XEN_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, xen_owner, xen_env, xen_server, xen_username, xen_password)
        ret, output = self.runcmd(cmd, "Setting xen mode in /etc/sysconfig/virt-who.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set xen mode in /etc/sysconfig/virt-who.")
        else:
            raise FailException("Test Failed - Failed  to set xen mode in /etc/sysconfig/virt-who.")

    # ========================================================
    #       XEN - test env set up function
    # ========================================================
    def xen_setup(self):
        server_ip, server_hostname, server_user, server_pass = self.get_server_info()
        self.set_xen_conf()
        self.runcmd_service("restart_virtwho")
        self.sub_unregister()
        self.configure_server(server_ip, server_hostname)
        self.sub_register(server_user, server_pass)
