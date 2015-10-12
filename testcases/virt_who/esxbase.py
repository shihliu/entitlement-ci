from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class ESXBase(VIRTWHOBase):

    def esx_setup(self):
        SERVER_IP = get_exported_param("SERVER_IP")
        SERVER_HOSTNAME = get_exported_param("SERVER_HOSTNAME")

        SERVER_USER = self.get_vw_cons("username")
        SERVER_PASS = self.get_vw_cons("password")

        ESX_HOST = self.get_vw_cons("ESX_HOST")

        VIRTWHO_ESX_OWNER = self.get_vw_cons("VIRTWHO_ESX_OWNER")
        VIRTWHO_ESX_ENV = self.get_vw_cons("VIRTWHO_ESX_ENV")
        VIRTWHO_ESX_SERVER = self.get_vw_cons("VIRTWHO_ESX_SERVER")
        VIRTWHO_ESX_USERNAME = self.get_vw_cons("VIRTWHO_ESX_USERNAME")
        VIRTWHO_ESX_PASSWORD = self.get_vw_cons("VIRTWHO_ESX_PASSWORD")
        # update virt-who configure file
        self.update_esx_vw_configure(VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD)
        # restart virt-who service
        self.vw_restart_virtwho()
        # if host was already registered for hyperV, need to unregistered firstly, and then config and register the host again
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        guest_name = self.get_vw_cons("ESX_GUEST_NAME")
#         if self.esx_check_host_exist(ESX_HOST, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD):
        self.wget_images(self.get_vw_cons("esx_guest_url"), guest_name, ESX_HOST)
        self.esx_add_guest(guest_name, ESX_HOST)
        self.esx_start_guest_first(guest_name, ESX_HOST)
        self.esx_service_restart(ESX_HOST)
        self.esx_stop_guest(guest_name, ESX_HOST)
        self.vw_restart_virtwho()
#         else:
#             raise FailException("ESX host:'%s' has not been added to vCenter yet, add it manually first!" % ESX_HOST)

    def unset_esx_conf(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/^VIRTWHO_ESX/#VIRTWHO_ESX/g' -e 's/^VIRTWHO_ESX_OWNER/#VIRTWHO_ESX_OWNER/g' -e 's/^VIRTWHO_ESX_ENV/#VIRTWHO_ESX_ENV/g' -e 's/^VIRTWHO_ESX_SERVER/#VIRTWHO_ESX_SERVER/g' -e 's/^VIRTWHO_ESX_USERNAME/#VIRTWHO_ESX_USERNAME/g' -e 's/^VIRTWHO_ESX_PASSWORD/#VIRTWHO_ESX_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "unset virt-who configure file for disable VIRTWHO_ESX", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to disable VIRTWHO_ESX.")
        else:
            raise FailException("Test Failed - Failed to disable VIRTWHO_ESX.")

    def set_esx_conf(self, targetmachine_ip=""):
        VIRTWHO_ESX_OWNER = self.get_vw_cons("VIRTWHO_ESX_OWNER")
        VIRTWHO_ESX_ENV = self.get_vw_cons("VIRTWHO_ESX_ENV")
        VIRTWHO_ESX_SERVER = self.get_vw_cons("VIRTWHO_ESX_SERVER")
        VIRTWHO_ESX_USERNAME = self.get_vw_cons("VIRTWHO_ESX_USERNAME")
        VIRTWHO_ESX_PASSWORD = self.get_vw_cons("VIRTWHO_ESX_PASSWORD")

        # clean # first
        cmd = "sed -i -e 's/^#VIRTWHO_ESX/VIRTWHO_ESX/g' -e 's/^#VIRTWHO_ESX_OWNER/VIRTWHO_ESX_OWNER/g' -e 's/^#VIRTWHO_ESX_ENV/VIRTWHO_ESX_ENV/g' -e 's/^#VIRTWHO_ESX_SERVER/VIRTWHO_ESX_SERVER/g' -e 's/^#VIRTWHO_ESX_USERNAME/VIRTWHO_ESX_USERNAME/g' -e 's/^#VIRTWHO_ESX_PASSWORD/VIRTWHO_ESX_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "set virt-who configure file for enable VIRTWHO_ESX", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_ESX.")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_ESX.")

        # set esx value
        cmd = "sed -i -e 's/^VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/^VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/^VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/^VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/^VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/^VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD)
        ret, output = self.runcmd(cmd, "setting value for esx conf.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set esx value.")
        else:
            raise FailException("Test Failed - Failed to set esx value.")

    #========================================================
    #     ESX Functions
    #========================================================
    def wget_images(self, wget_url, guest_name, destination_ip):
        ''' wget guest images '''
        # check whether guest has already been downloaded, if yes, unregister it from ESX and delete it from local
        cmd = "[ -d /vmfs/volumes/datastore*/%s ]" % guest_name
        ret, output = self.runcmd_esx(cmd, "check whether guest %s has been installed" % guest_name, destination_ip)
        if ret == 0:
            logger.info("guest '%s' has already been installed, continue..." % guest_name)
        else:
            logger.info("guest '%s' has not been installed yet, will install it next." % guest_name)
            cmd = "wget -P /vmfs/volumes/datastore* %s%s.tar.gz" % (wget_url, guest_name)
            ret, output = self.runcmd_esx(cmd, "wget guests", destination_ip)
            if ret == 0:
                logger.info("Succeeded to wget the guest '%s'." % guest_name)
            else:
                raise FailException("Failed to wget the guest '%s'." % guest_name)
            # uncompress guest and remove .gz file
            cmd = "tar -zxvf /vmfs/volumes/datastore*/%s.tar.gz -C /vmfs/volumes/datastore*/ && rm -f /vmfs/volumes/datastore*/%s.tar.gz" % (guest_name, guest_name)
            ret, output = self.runcmd_esx(cmd, "uncompress guest", destination_ip)
            if ret == 0:
                logger.info("Succeeded to uncompress guest '%s'." % guest_name)
            else:
                raise FailException("Failed to uncompress guest '%s'." % guest_name)

    def update_esx_vw_configure(self, esx_owner, esx_env, esx_server, esx_username, esx_password, background=1, debug=1):
        ''' update virt-who configure file /etc/sysconfig/virt-who for enable VIRTWHO_ESX'''
        cmd = "sed -i -e 's/^#VIRTWHO_DEBUG/VIRTWHO_DEBUG/g' -e 's/^#VIRTWHO_ESX/VIRTWHO_ESX/g' -e 's/^#VIRTWHO_ESX_OWNER/VIRTWHO_ESX_OWNERs/g' -e 's/^#VIRTWHO_ESX_ENV/VIRTWHO_ESX_ENV/g' -e 's/^#VIRTWHO_ESX_SERVER/VIRTWHO_ESX_SERVER/g' -e 's/^#VIRTWHO_ESX_USERNAME/VIRTWHO_ESX_USERNAME/g' -e 's/^#VIRTWHO_ESX_PASSWORD/VIRTWHO_ESX_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "updating virt-who configure file for enable VIRTWHO_ESX")
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_ESX.")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_ESX.")

        ''' update virt-who configure file /etc/sysconfig/virt-who for setting VIRTWHO_ESX'''
        cmd = "sed -i -e 's/^VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/^VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/^VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/^VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/^VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/^VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/^VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, esx_owner, esx_env, esx_server, esx_username, esx_password)
        ret, output = self.runcmd(cmd, "updating virt-who configure file setting VIRTWHO_ESX")
        if ret == 0:
            logger.info("Succeeded to setting VIRTWHO_ESX.")
        else:
            raise FailException("Test Failed - Failed to setting VIRTWHO_ESX.")

    def esx_guest_ispoweron(self, guest_name, destination_ip):
        ''' check guest is power on or off '''
        # get geust id by vmsvc/getallvms
        cmd = "vim-cmd vmsvc/getallvms | grep '%s' | awk '{print $1'}" % (guest_name)
        ret, output = self.runcmd_esx(cmd, "get guest '%s' ID" % (guest_name), destination_ip)
        if ret == 0:
            guest_id = output.strip()
        else:
            raise FailException("can't get guest '%s' ID" % guest_name)

        # check geust status by vmsvc/power.getstate 
        cmd = "vim-cmd vmsvc/power.getstate %s" % guest_id
        ret, output = self.runcmd_esx(cmd, "check guest '%s' status" % (guest_name), destination_ip)
        if ret == 0 and "Powered on" in output:
            return True
        elif ret == 0 and "Powered off" in output:
            return False
        else:
            raise FailException("Failed to check guest '%s' status" % guest_name)

    def esx_add_guest(self, guest_name, destination_ip):
        ''' add guest to esx host '''
        cmd = "vim-cmd solo/register /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "add guest '%s' to ESX '%s'" % (guest_name, destination_ip), destination_ip)
        if ret == 0:
            # need to wait 30 s for add sucess
            time.sleep(60)
            logger.info("Succeeded to add guest '%s' to ESX host" % guest_name)
        else:
            if "AlreadyExists" in output:
                logger.info("Guest '%s' already exist in ESX host" % guest_name)
            else:
                raise FailException("Failed to add guest '%s' to ESX host" % guest_name)

    def esx_create_dummy_guest(self, guest_name, destination_ip):
        ''' create dummy guest in esx '''
        cmd = "vim-cmd vmsvc/createdummyvm %s /vmfs/volumes/datastore*/" % guest_name
        ret, output = self.runcmd_esx(cmd, "add guest '%s' to ESX '%s'" % (guest_name, destination_ip), destination_ip)
        if ret == 0:
            # need to wait 30 s for add sucess
#             time.sleep(10)
            logger.info("Succeeded to add guest '%s' to ESX host" % guest_name)
        else:
            if "AlreadyExists" in output:
                logger.info("Guest '%s' already exist in ESX host" % guest_name)
            else:
                raise FailException("Failed to add guest '%s' to ESX host" % guest_name)

    def esx_service_restart(self, destination_ip):
        ''' restart esx service '''
        cmd = "/etc/init.d/hostd restart; /etc/init.d/vpxa restart"
        ret, output = self.runcmd_esx(cmd, "restart hostd and vpxa service", destination_ip)
        if ret == 0:
            logger.info("Succeeded to restart hostd and vpxa service")
        else:
            raise FailException("Failed to restart hostd and vpxa service")
        time.sleep(120)

    def esx_start_guest_first(self, guest_name, destination_ip):
        ''' start guest in esx host '''
        cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "start guest '%s' in ESX" % guest_name, destination_ip, timeout=120)
        if ret == 0:
            logger.info("Succeeded to first start guest '%s' in ESX host" % guest_name)
        else:
            logger.info("Failed to first start guest '%s' in ESX host" % guest_name)
        ''' Do not check whethre guest can be accessed by ip, since there's an error, need to restart esx service '''
        # self.esx_check_ip_accessable( guest_name, destination_ip, accessable=True)

    def esx_check_system_reboot(self, target_ip):
        time.sleep(120)
        cycle_count = 0
        while True:
            # wait max time 10 minutes
            max_cycle = 60
            cycle_count = cycle_count + 1
            cmd = "ping -c 5 %s" % target_ip
            ret, output = self.runcmd_esx(cmd, "ping system ip")
            if ret == 0 and "5 received" in output:
                logger.info("Succeeded to ping system ip")
                break
            if cycle_count == max_cycle:
                logger.info("Time out to ping system ip")
                break
            else:
                time.sleep(10)

# orphan guest left in vCenter, use vmware-cmd instead
#     def esx_remove_guest(self, guest_name, destination_ip):
#         ''' remove guest from esx '''
#         cmd = "vim-cmd vmsvc/unregister /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         ret, output = self.runcmd_esx(cmd, "remove guest '%s' from ESX" % guest_name, destination_ip)
#         if ret == 0:
#             logger.info("Succeeded to remove guest '%s' from ESX" % guest_name)
#         else:
#             raise FailException("Failed to remove guest '%s' from ESX" % guest_name)

    def esx_remove_guest(self, guest_name, esx_host, vCenter="", vCenter_user="", vCenter_pass=""):
        ''' remove guest from esx vCenter '''
        vmware_cmd_ip = self.get_vw_cons("VMWARE_CMD_IP")
        if vCenter == "" and vCenter_user == "" and vCenter_pass == "":
            vCenter = self.get_vw_cons("VIRTWHO_ESX_SERVER")
            vCenter_user = self.get_vw_cons("VIRTWHO_ESX_USERNAME")
            vCenter_pass = self.get_vw_cons("VIRTWHO_ESX_PASSWORD")
        cmd = "vmware-cmd -H %s -U %s -P %s --vihost %s -s unregister /vmfs/volumes/datastore1/%s/%s.vmx" % (vCenter, vCenter_user, vCenter_pass, esx_host, guest_name, guest_name)
        ret, output = self.runcmd(cmd, "remove guest '%s' from vCenter" % guest_name, targetmachine_ip=vmware_cmd_ip)
        if ret == 0:
            logger.info("Succeeded to remove guest '%s' from vCenter" % guest_name)
        else:
            raise FailException("Failed to remove guest '%s' from vCenter" % guest_name)

    def esx_destroy_guest(self, guest_name, esx_host):
        ''' destroy guest from esx'''
        cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
        ret, output = self.runcmd_esx(cmd, "destroy guest '%s' in ESX" % guest_name, esx_host)
        if ret == 0:
            logger.info("Succeeded to destroy guest '%s'" % guest_name)
        else:
            raise FailException("Failed to destroy guest '%s'" % guest_name)
# 
#     def esx_check_host_exist(self, esx_host, vCenter, vCenter_user, vCenter_pass):
#         ''' check whether esx host exist in vCenter '''
#         vmware_cmd_ip = ee.vmware_cmd_ip
#         cmd = "vmware-cmd -H %s -U %s -P %s --vihost %s -l" % (vCenter, vCenter_user, vCenter_pass, esx_host)
#         ret, output = self.runcmd(cmd, "check whether esx host:%s exist in vCenter" % esx_host, vmware_cmd_ip)
#         if "Host not found" in output:
#             raise FailException("esx host:%s not exist in vCenter" % esx_host)
#             return False
#         else:
#             logger.info("esx host:%s exist in vCenter" % esx_host)
#             return True
# 
#     def esx_remove_all_guests(self, guest_name, destination_ip):
#         return
# 
    def esx_start_guest(self, guest_name):
        ''' start guest in esx host '''
        esx_host_ip = self.get_vw_cons("ESX_HOST")
        cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "start guest '%s' in ESX" % guest_name, esx_host_ip)
        if ret == 0:
            logger.info("Succeeded to start guest '%s' in ESX host" % guest_name)
        else:
            raise FailException("Failed to start guest '%s' in ESX host" % guest_name)
        ''' check whethre guest can be accessed by ip '''
        self.esx_check_ip_accessable(guest_name, esx_host_ip, accessable=True)

    def esx_stop_guest(self, guest_name, destination_ip):
        ''' stop guest in esx host '''
        cmd = "vim-cmd vmsvc/power.off /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "stop guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
        if ret == 0:
            logger.info("Succeeded to stop guest '%s' in ESX host" % guest_name)
        else:
            raise FailException("Failed to stop guest '%s' in ESX host" % guest_name)
        ''' check whethre guest can not be accessed by ip '''
        self.esx_check_ip_accessable(guest_name, destination_ip, accessable=False)

    def esx_pause_guest(self, guest_name, destination_ip):
        ''' suspend guest in esx host '''
        cmd = "vim-cmd vmsvc/power.suspend /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "suspend guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
        if ret == 0:
            logger.info("Succeeded to suspend guest '%s' in ESX host" % guest_name)
        else:
            raise FailException("Failed to suspend guest '%s' in ESX host" % guest_name)

        ''' check whethre guest can not be accessed by ip '''
        self.esx_check_ip_accessable(guest_name, destination_ip, accessable=False)

    def esx_resume_guest(self, guest_name, destination_ip):
        ''' resume guest in esx host '''
        # cmd = "vim-cmd vmsvc/power.suspendResume /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "resume guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
        if ret == 0:
            logger.info("Succeeded to resume guest '%s' in ESX host" % guest_name)
        else:
            raise FailException("Failed to resume guest '%s' in ESX host" % guest_name)

        ''' check whethre guest can be accessed by ip '''
        self.esx_check_ip_accessable(guest_name, destination_ip, accessable=True)

    def esx_get_guest_mac(self, guest_name, destination_ip):
        ''' get guest mac address in esx host '''
        cmd = "vim-cmd vmsvc/device.getdevices /vmfs/volumes/datastore*/%s/%s.vmx | grep 'macAddress'" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "get guest mac address '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
        macAddress = output.split("=")[1].strip().strip(',').strip('"')
        if ret == 0:
            logger.info("Succeeded to get guest mac address '%s' in ESX host" % guest_name)
        else:
            raise FailException("Failed to get guest mac address '%s' in ESX host" % guest_name)

        return macAddress

    def esx_get_guest_ip(self, guest_name, destination_ip):
        ''' get guest ip address in esx host, need vmware-tools installed in guest '''
        cmd = "vim-cmd vmsvc/get.summary /vmfs/volumes/datastore*/%s/%s.vmx | grep 'ipAddress'" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "get guest ip address '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
        ipAddress = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
        if ret == 0:
            logger.info("Getting guest ip address '%s' in ESX host" % ipAddress)
            if ipAddress == None or ipAddress == "":
                raise FailException("Faild to get guest %s ip." % guest_name)
            else:
                return ipAddress
        else:
            raise FailException("Failed to get guest ip address '%s' in ESX host" % ipAddress)

    def esx_check_ip_accessable(self, guest_name, destination_ip, accessable):
        cycle_count = 0
        while True:
            # wait max time 10 minutes
            max_cycle = 60
            cycle_count = cycle_count + 1
            if accessable:
                if self.esx_get_guest_ip(guest_name, destination_ip) != "unset":
                    break
                if cycle_count == max_cycle:
                    logger.info("Time out to esx_check_ip_accessable")
                    break
                else:
                    time.sleep(20)
            else:
                time.sleep(30)
                if self.esx_get_guest_ip(guest_name, destination_ip) == "unset":
                    break
                if cycle_count == max_cycle:
                    logger.info("Time out to esx_check_ip_accessable")
                    break
                else:
                    time.sleep(20)

    def esx_get_guest_uuid(self, guest_name, destination_ip):
        ''' get guest uuid in esx host '''
        cmd = "vim-cmd vmsvc/get.summary /vmfs/volumes/datastore*/%s/%s.vmx | grep 'uuid'" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "get guest uuid '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
        uuid = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
        if ret == 0:
            logger.info("Succeeded to get guest uuid '%s' in ESX host" % guest_name)
        else:
            raise FailException("Failed to get guest uuid '%s' in ESX host" % guest_name)
        return uuid

    def esx_get_host_uuid(self, destination_ip):
        ''' get host uuid in esx host '''
        cmd = "vim-cmd hostsvc/hostsummary | grep 'uuid'"
        ret, output = self.runcmd_esx(cmd, "get host uuid in ESX '%s'" % destination_ip, destination_ip)
        uuid = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
        if ret == 0:
            logger.info("Succeeded to get host uuid '%s' in ESX host" % uuid)
        else:
            raise FailException("Failed to get host uuid '%s' in ESX host" % uuid)
        return uuid

    def esx_check_uuid(self, guestname, destination_ip, guestuuid="Default", uuidexists=True, rhsmlogpath='/var/log/rhsm'):
        ''' check if the guest uuid is correctly monitored by virt-who '''
        if guestname != "" and guestuuid == "Default":
            guestuuid = self.esx_get_guest_uuid(guestname, destination_ip)
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        self.vw_restart_virtwho()
        self.vw_restart_virtwho()
        # need to sleep tail -3, then can get the output normally
        cmd = "sleep 15; tail -3 %s " % rhsmlogfile
        ret, output = self.runcmd(cmd, "check output in rhsm.log")
        if ret == 0:
            ''' get guest uuid.list from rhsm.log '''
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update in hosts-to-guests mapping: " in output:
                log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
            # check guest uuid in log_uuid_list
            if uuidexists:
                if guestname == "":
                    return len(log_uuid_list) == 0
                else:
                    return guestuuid in log_uuid_list
            else:
                if guestname == "":
                    return not len(log_uuid_list) == 0
                else:
                    return not guestuuid in log_uuid_list
        else:
            raise FailException("Failed to get uuids in rhsm.log")

    def esx_check_uuid_exist_in_rhsm_log(self, uuid, destination_ip=""):
        ''' esx_check_uuid_exist_in_rhsm_log '''
        time.sleep(10)
        cmd = "tail -3 /var/log/rhsm/rhsm.log"
        ret, output = self.runcmd(cmd, "check output in rhsm.log")
        if ret == 0:
            ''' get uuid.list from rhsm.log '''

            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
                logger.info("Succeeded to get uuid.list from rhsm.log.")
            elif "Sending update in hosts-to-guests mapping: " in output:
                log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1]
                logger.info("Succeeded to get uuid.list from rhsm.log.")
            else:
                log_uuid_list = ""
                logger.info("No uuid.list found from rhsm.log.")
            # check guest uuid in log_uuid_list
            return uuid in log_uuid_list
        else:
            raise FailException("Failed to get uuids in rhsm.log")

    def esx_check_host_in_samserv(self, esx_uuid, destination_ip):
        ''' check esx host exist in sam server '''
        cmd = "headpin -u admin -p admin system list --org=ACME_Corporation --environment=Library"
        ret, output = self.runcmd_sam(cmd, "check esx host exist in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
        # if ret == 0 and output.find(esx_uuid) >= 0:
            logger.info("Succeeded to check esx host %s exist in sam server" % esx_uuid)
        else:
            raise FailException("Failed to check esx host %s exist in sam server" % esx_uuid)

    def esx_remove_host_in_samserv(self, esx_uuid, destination_ip):
        ''' remove esx host in sam server '''
        cmd = "headpin -u admin -p admin system unregister --name=%s --org=ACME_Corporation" % esx_uuid
        ret, output = self.runcmd_sam(cmd, "remove esx host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to remove esx host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to remove esx host %s in sam server" % esx_uuid)

    def esx_remove_deletion_record_in_samserv(self, esx_uuid, destination_ip):
        ''' remove deletion record in sam server '''
        cmd = "headpin -u admin -p admin system remove_deletion --uuid=%s" % esx_uuid
        ret, output = self.runcmd_sam(cmd, "remove deletion record in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to remove deletion record %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to remove deletion record %s in sam server" % esx_uuid)

    def esx_subscribe_host_in_samserv(self, esx_uuid, poolid, destination_ip):
        ''' subscribe host in sam server '''
        cmd = "headpin -u admin -p admin system subscribe --name=%s --org=ACME_Corporation --pool=%s " % (esx_uuid, poolid)
        ret, output = self.runcmd_sam(cmd, "subscribe host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to subscribe host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to subscribe host %s in sam server" % esx_uuid)

    def esx_unsubscribe_all_host_in_samserv(self, esx_uuid, destination_ip):
        ''' unsubscribe host in sam server '''
        cmd = "headpin -u admin -p admin system unsubscribe --name=%s --org=ACME_Corporation --all" % esx_uuid
        ret, output = self.runcmd_sam(cmd, "unsubscribe host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to unsubscribe host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to unsubscribe host %s in sam server" % esx_uuid)