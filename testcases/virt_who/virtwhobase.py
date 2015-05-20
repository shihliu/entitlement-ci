from utils import *
import time, random, commands
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants

class VIRTWHOBase(unittest.TestCase):
    # ========================================================
    #       Basic Functions
    # ========================================================

    def runcmd(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        if targetmachine_ip != None and targetmachine_ip != "":
            if targetmachine_user != None and targetmachine_user != "":
                commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
            else:
                commander = Command(targetmachine_ip, "root", "redhat")
        else:
            commander = Command(get_exported_param("REMOTE_IP"), username=get_exported_param("REMOTE_USER"), password=get_exported_param("REMOTE_PASSWD"))
        return commander.run(cmd, timeout, cmddesc)

    def runcmd_esx(self, cmd, cmddesc=None, targetmachine_ip=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "qwe123P", timeout, showlogger)

    def runcmd_guest(self, cmd, cmddesc=None, targetmachine_ip=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "redhat", timeout, showlogger)

#     def runcmd_byuser(self, cmd, cmddesc="", targetmachine_ip="", username="root", password="qwe123P", showlogger=True):
#         if targetmachine_ip == "":
#             (ret, output) = commands.getstatusoutput(cmd)
#         else:
#             (ret, output) = self.remote_esx_pexpect(targetmachine_ip, username, password, cmd)
#         if cmddesc != "":
#             cmddesc = " of " + cmddesc
#         if showlogger:
#             logger.info(" [command]%s: %s" % (cmddesc, cmd))
#             logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
#             logger.info(" [output ]%s: %s \n" % (cmddesc, output))
#         return ret, output
# 
#     def remote_esx_pexpect(self, hostname, username, password, cmd):
#         """ Remote exec function via pexpect """
#         user_hostname = "%s@%s" % (username, hostname)
#         child = pexpect.spawn("/usr/bin/ssh", [user_hostname, cmd], timeout=1800, maxread=2000, logfile=None)
#         while True:
#             index = child.expect(['(yes\/no)', 'Password:', pexpect.EOF, pexpect.TIMEOUT])
#             if index == 0:
#                 child.sendline("yes")
#             elif index == 1:
#                 child.sendline(password)
#             elif index == 2:
#                 child.close()
#                 return child.exitstatus, child.before
#             elif index == 3:
#                 child.close()
#                 return 1, ""
#         return 0

    def sys_setup(self):
        # system setup for virt-who testing
        cmd = "yum install -y virt-who"
#         cmd = "yum install -y @base @core @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization @desktop-debugging @dial-up @fonts @gnome-desktop @guest-desktop-agents @input-methods @internet-browser @multimedia @print-client @x11 nmap bridge-utils tunctl rpcbind qemu-kvm-tools expect pexpect git make gcc tigervnc-server"
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing.")
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing.")

    def esx_setup(self):
        SAM_IP = get_exported_param("SAM_IP")
        SAM_HOSTNAME = get_exported_param("SAM_HOSTNAME")

        SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
        SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

        ESX_HOST = VIRTWHOConstants().get_constant("ESX_HOST")

        VIRTWHO_ESX_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
        VIRTWHO_ESX_ENV = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
        VIRTWHO_ESX_SERVER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
        VIRTWHO_ESX_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
        VIRTWHO_ESX_PASSWORD = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")
        # update virt-who configure file
        self.update_esx_vw_configure(VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD)
        # restart virt-who service
        self.vw_restart_virtwho()
        if not self.sub_isregistered():
            self.configure_host(SAM_HOSTNAME, SAM_IP)
            self.sub_register(SAM_USER, SAM_PASS)
        guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
#         if self.esx_check_host_exist(ESX_HOST, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD):
        self.wget_images(VIRTWHOConstants().get_constant("esx_guest_url"), guest_name, ESX_HOST)
        self.esx_add_guest(guest_name, ESX_HOST)
        self.esx_start_guest_first(guest_name, ESX_HOST)
        self.esx_service_restart(ESX_HOST)
        self.esx_stop_guest(guest_name, ESX_HOST)
        self.vw_restart_virtwho()
#         else:
#             raise FailException("ESX host:'%s' has not been added to vCenter yet, add it manually first!" % ESX_HOST)

    def vw_restart_virtwho(self, targetmachine_ip=""):
        ''' restart virt-who service. '''
        cmd = "service virt-who restart; sleep 10"
        ret, output = self.runcmd(cmd, "restart virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart virt-who service.")
        else:
            raise FailException("Test Failed - Failed to restart virt-who service.")

    def sub_isregistered(self, targetmachine_ip=""):
        ''' check whether the machine is registered. '''
        cmd = "subscription-manager identity"
        ret, output = self.runcmd(cmd, "check whether the machine is registered", targetmachine_ip)
        if ret == 0:
            logger.info("System %s is registered." % self.get_hg_info(targetmachine_ip))
            return True
        else: 
            logger.info("System %s is not registered." % self.get_hg_info(targetmachine_ip))
            return False

    def sub_register(self, username, password, targetmachine_ip=""):
        ''' register the machine. '''
        cmd = "subscription-manager register --username=%s --password=%s" % (username, password)
        ret, output = self.runcmd(cmd, "register system", targetmachine_ip)
        if ret == 0 or "The system has been registered with id:" in output or "This system is already registered" in output:
            logger.info("Succeeded to register system %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to register system %s" % self.get_hg_info(targetmachine_ip))

    def sub_unregister(self, targetmachine_ip=""):
        ''' Unregister the machine. '''
        if self.sub_isregistered(targetmachine_ip):
            # need to sleep before destroy guest or else register error happens 
            cmd = "subscription-manager unregister"
            ret, output = self.runcmd(cmd, "unregister system", targetmachine_ip)
            if ret == 0 :
                logger.info("Succeeded to unregister %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to unregister %s." % self.get_hg_info(targetmachine_ip))
        else:
            logger.info("The machine is not registered to server now, no need to do unregister.")

    def get_hg_info(self, targetmachine_ip):
        if targetmachine_ip == "":
            host_guest_info = "in host machine"
        else:
            host_guest_info = "in guest machine %s" % targetmachine_ip
        return host_guest_info

    def configure_host(self, samhostname, samhostip, targetmachine_ip=""):
        ''' configure the host machine. '''
        if samhostname != None and samhostip != None:
            # add sam hostip and hostname in /etc/hosts
            cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
            ret, output = self.runcmd(cmd, "configure /etc/hosts", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_hg_info(targetmachine_ip)))
            else:
                raise FailException("Failed to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_hg_info(targetmachine_ip)))
            # config hostname, prefix, port, baseurl and repo_ca_crt by installing candlepin-cert
            cmd = "rpm -qa | grep candlepin-cert-consumer"
            ret, output = self.runcmd(cmd, "check whether candlepin-cert-consumer-%s-1.0-1.noarch exist" % samhostname, targetmachine_ip)
            if ret == 0:
                logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
                cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
                ret, output = self.runcmd(cmd, "remove candlepin-cert-consumer-%s-1.0-1.noarch to re-register system to SAM" % samhostname, targetmachine_ip)
                if ret == 0:
                     logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
                else:
                    raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
            cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
            ret, output = self.runcmd(cmd, "install candlepin-cert-consumer..rpm", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
            else:
                raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        elif samhostname == "subscription.rhn.stage.redhat.com":
            # configure /etc/rhsm/rhsm.conf to stage candlepin
            cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % samhostname
            ret, output = self.runcmd(cmd, "configure /etc/rhsm/rhsm.conf", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to configure rhsm.conf for stage in %s" % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to configure rhsm.conf for stage in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to configure the host")

    def sub_listavailpools(self, productid, targetmachine_ip="", showlog=True):
        ''' list available pools.'''
        cmd = "subscription-manager list --available"
        ret, output = self.runcmd(cmd, "run 'subscription-manager list --available'", targetmachine_ip, showlogger=showlog)
        if ret == 0:
            if "No Available subscription pools to list" not in output:
                if productid in output:
                    logger.info("Succeeded to run 'subscription-manager list --available' %s." % self.get_hg_info(targetmachine_ip))
                    pool_list = self.__parse_avail_pools(output)
                    return pool_list
                else:
                    raise FailException("Failed to run 'subscription-manager list --available' %s - Not the right available pools are listed!" % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to run 'subscription-manager list --available' %s - There is no Available subscription pools to list!" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to run 'subscription-manager list --available' %s." % self.get_hg_info(targetmachine_ip))

    def __parse_avail_pools(self, output):
        datalines = output.splitlines()
        pool_list = []
        data_segs = []
        segs = []
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName:" in line) or ("Subscription Name:" in line):
                segs.append(line)
            elif segs:
                # change this section for more than 1 lines without ":" exist
                if ":" in line:
                    segs.append(line)
                else:
                    segs[-1] = segs[-1] + " " + line.strip()
            if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line):
                data_segs.append(segs)
                segs = []
        # parse detail information for each pool
        for seg in data_segs:
            pool_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(" ", "")
                valueitem = item.split(":")[1].strip()
                pool_dict[keyitem] = valueitem
            pool_list.append(pool_dict)
        return pool_list

    def __parse_listavailable_output(self, output):
        datalines = output.splitlines()
        data_list = []
        # split output into segmentations for each pool
        data_segs = []
        segs = []
        tmpline = ""
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                tmpline = line
            elif line and ":" not in line:
                tmpline = tmpline + ' ' + line.strip()
            elif line and ":" in line:
                segs.append(tmpline)
                tmpline = line
            if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
                segs.append(tmpline)
                data_segs.append(segs)
                segs = []
        for seg in data_segs:
            data_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(' ', '')
                valueitem = item.split(":")[1].strip()
                data_dict[keyitem] = valueitem
            data_list.append(data_dict)
        return data_list

    def check_type_virtual(self, pool_dict):
        if "MachineType" in pool_dict.keys():
            TypeName = "MachineType"
        elif "SystemType" in pool_dict.keys():
            TypeName = "SystemType"
        return pool_dict[TypeName] == "Virtual" or pool_dict[TypeName] == "virtual"

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
#             cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
#             ret, output = self.runcmd_esx(cmd, "remove guests %s" % guest_name, destination_ip)
#             if ret == 0:
#                 logger.info("Succeeded to remove the guest '%s'." % guest_name)
#             else:
#                 raise FailException("Failed to remove the guest '%s'." % guest_name)
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
        ''' update virt-who configure file /etc/sysconfig/virt-who. '''
        cmd = "sed -i -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/#VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/#VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/#VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/#VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/#VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, esx_owner, esx_env, esx_server, esx_username, esx_password)
        ret, output = self.runcmd(cmd, "updating virt-who configure file for esx")
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file.")
        else:
            raise FailException("Test Failed - Failed to update virt-who configure file.")

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
            time.sleep(60)
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

#     def esx_remove_guest(self, guest_name, esx_host, vCenter, vCenter_user, vCenter_pass):
#         ''' remove guest from esx vCenter '''
#         vmware_cmd_ip = ee.vmware_cmd_ip
#         cmd = "vmware-cmd -H %s -U %s -P %s --vihost %s -s unregister /vmfs/volumes/datastore*/%s/%s.vmx" % (vCenter, vCenter_user, vCenter_pass, esx_host, guest_name, guest_name)
#         ret, output = self.runcmd(cmd, "remove guest '%s' from vCenter" % guest_name, vmware_cmd_ip)
#         if ret == 0:
#             logger.info("Succeeded to remove guest '%s' from vCenter" % guest_name)
#         else:
#             raise FailException("Failed to remove guest '%s' from vCenter" % guest_name)
# 
# 
#     def esx_destroy_guest(self, guest_name, esx_host):
#         ''' destroy guest from '''
#         # esx_host_ip = ee.esx_host_ip
#         # vmware_cmd_ip = ee.vmware_cmd_ip
#         # cmd = "vim-cmd vmsvc/destroy /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
#         ret, output = self.runcmd_esx(cmd, "destroy guest '%s' in ESX" % guest_name, esx_host)
#         if ret == 0:
#             logger.info("Succeeded to destroy guest '%s'" % guest_name)
#         else:
#             raise FailException("Failed to destroy guest '%s'" % guest_name)
# 
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
        esx_host_ip = VIRTWHOConstants().get_constant("ESX_HOST")
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
                    time.sleep(10)
            else:
                time.sleep(30)
                if self.esx_get_guest_ip(guest_name, destination_ip) == "unset":
                    break
                if cycle_count == max_cycle:
                    logger.info("Time out to esx_check_ip_accessable")
                    break
                else:
                    time.sleep(10)

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
        self.vw_restart_virtwho(logger)
        self.vw_restart_virtwho(logger)
        cmd = "tail -1 %s " % rhsmlogfile
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
        self.vw_restart_virtwho(logger)
        self.vw_restart_virtwho(logger)
        time.sleep(10)
        cmd = "tail -1 /var/log/rhsm/rhsm.log"
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
                raise FailException("Failed to get guest uuid.list from rhsm.log")
    
            # check guest uuid in log_uuid_list
            return uuid in log_uuid_list
        else:
            raise FailException("Failed to get uuids in rhsm.log")


    def get_uuid_list_in_rhsm_log(self, destination_ip=""):
        ''' esx_check_uuid_exist_in_rhsm_log '''
        self.vw_restart_virtwho(logger)
        time.sleep(20)
        cmd = "tail -1 /var/log/rhsm/rhsm.log"
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
                raise FailException("Failed to get guest uuid.list from rhsm.log")
    
            return log_uuid_list
        else:
            raise FailException("Failed to get uuid list in rhsm.log")


    def esx_check_host_in_samserv(self, esx_uuid, destination_ip):
        ''' check esx host exist in sam server '''
        cmd = "headpin -u admin -p admin system list --org=ACME_Corporation --environment=Library"
        ret, output = self.runcmd(cmd, "check esx host exist in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
        # if ret == 0 and output.find(esx_uuid) >= 0:
            logger.info("Succeeded to check esx host %s exist in sam server" % esx_uuid)
        else:
            raise FailException("Failed to check esx host %s exist in sam server" % esx_uuid)


    def esx_remove_host_in_samserv(self, esx_uuid, destination_ip):
        ''' remove esx host in sam server '''
        cmd = "headpin -u admin -p admin system unregister --name=%s --org=ACME_Corporation" % esx_uuid
        ret, output = self.runcmd(cmd, "remove esx host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to remove esx host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to remove esx host %s in sam server" % esx_uuid)


    def esx_remove_deletion_record_in_samserv(self, esx_uuid, destination_ip):
        ''' remove deletion record in sam server '''
        cmd = "headpin -u admin -p admin system remove_deletion --uuid=%s" % esx_uuid
        ret, output = self.runcmd(cmd, "remove deletion record in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to remove deletion record %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to remove deletion record %s in sam server" % esx_uuid)


    def esx_subscribe_host_in_samserv(self, esx_uuid, poolid, destination_ip):
        ''' subscribe host in sam server '''
        cmd = "headpin -u admin -p admin system subscribe --name=%s --org=ACME_Corporation --pool=%s " % (esx_uuid, poolid)
        ret, output = self.runcmd(cmd, "subscribe host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to subscribe host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to subscribe host %s in sam server" % esx_uuid)


    def esx_unsubscribe_all_host_in_samserv(self, esx_uuid, destination_ip):
        ''' unsubscribe host in sam server '''
        cmd = "headpin -u admin -p admin system unsubscribe --name=%s --org=ACME_Corporation --all" % esx_uuid
        ret, output = self.runcmd(cmd, "unsubscribe host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to unsubscribe host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to unsubscribe host %s in sam server" % esx_uuid)


    def get_poolid_by_SKU(self, sku, targetmachine_ip=""):
        ''' get_poolid_by_SKU '''
        availpoollist = self.sub_listavailpools(sku, targetmachine_ip)
        if availpoollist != None:
            for index in range(0, len(availpoollist)):
                if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku):
                    rindex = index
                    break
                elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == sku):
                    rindex = index
                    break
            if "PoolID" in availpoollist[index]:
                poolid = availpoollist[rindex]["PoolID"]
            else:
                poolid = availpoollist[rindex]["PoolId"]
            return poolid
        else:
            raise FailException("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % sku)

# 
#     # ========================================================
#     #       1. Keyword Functions
#     # ========================================================
#     def sub_autosubscribe(self, autosubprod):
#         # cmd = "subscription-manager subscribe --auto"
#         cmd = "subscription-manager attach --auto"
#         (ret, output) = self.runcmd(cmd, "auto-subscribe")
#         if ret == 0:
#             if ("Subscribed" in output) and ("Not Subscribed" not in output):
#                 logger.info("It's successful to auto-subscribe.")
#             else:
#                 raise FailException("Test Failed - Failed to auto-subscribe correct product.")
#         else:
#             raise FailException("Test Failed - Failed to auto-subscribe.")
# 
#     def sub_register(self, username, password, subtype=""):
#         if subtype == "":
#             cmd = "subscription-manager register --username=%s --password='%s'" % (username, password)
#         else:
#             cmd = "subscription-manager register --type=%s --username=%s --password='%s'" % (subtype, username, password)
# 
#         if self.sub_isregistered():
#             logger.info("The system is already registered, need to unregister first!")
#             cmd_unregister = "subscription-manager unregister"
#             (ret, output) = self.runcmd(cmd_unregister, "unregister")
#             if ret == 0:
#                 if ("System has been unregistered." in output) or ("System has been un-registered." in output):
#                     logger.info("It's successful to unregister.")
#                 else:
#                     logger.info("The system is failed to unregister, try to use '--force'!")
#                     cmd += " --force"
#         (ret, output) = self.runcmd(cmd, "register")
#         if ret == 0:
#             if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
#                 logger.info("It's successful to register.")
#             else:
#                 raise FailException("Test Failed - The information shown after registered is not correct.")
#         else:
#             raise FailException("Test Failed - Failed to register.")
# 


# 
#     def sub_clean_local_data(self):
#         cmd = "subscription-manager clean"
#         (ret, output) = self.runcmd(cmd, "clean local data")
#         if ret == 0 and "All local data removed" in output:
#             logger.info("Local data has been cleaned in the server now.")
#         else:
#             raise FailException("Test Failed - Failed to clean local data.")
# 
#     def sub_isregistered(self):
#         cmd = "subscription-manager identity"
#         (ret, output) = self.runcmd(cmd, "identity")
#         if ret == 0:
#             logger.info("The system is registered to server now.")
#             return True
#         else:
#             logger.info("The system is not registered to server now.")
#             if "has been deleted" in output:
#                 logger.info("the system is not registered to server but has local data!")
#             return False
# 
#     def sub_checkidcert(self):
#         cmd = "ls /etc/pki/consumer/"
#         (ret, output) = self.runcmd(cmd, "listing the files in /etc/pki/consumer/")
#         if ret == 0 and "cert.pem" in output and "key.pem" in output:
#             logger.info("There are identity certs in the consumer directory.")
#             return True
#         else:
#             logger.info("There is no identity certs in the consumer directory.")
#             return False
# 
#     def sub_set_servicelevel(self, service_level):
#         # set service-level
#         cmd = "subscription-manager service-level --set=%s" % service_level
#         (ret, output) = self.runcmd(cmd, "set service-level as %s" % service_level)
#         if ret == 0 and "Service level set to: %s" % service_level in output:
#             logger.info("It's successful to set service-level as %s" % service_level)
#         else:
#             raise FailException("Test Failed - Failed to set service-level as %s" % service_level)
# 
#     def sub_checkproductcert(self, productid):
#         rctcommand = self.check_rct()
#         if rctcommand == 0:
#             cmd = "for i in /etc/pki/product/*; do rct cat-cert $i; done"
#         else:
#             cmd = "for i in /etc/pki/product/*; do openssl x509 -text -noout -in $i; done"
#         (ret, output) = self.runcmd(cmd, "checking product cert")
#         if ret == 0:
#             if ("1.3.6.1.4.1.2312.9.1.%s" % productid in output) or ("ID: %s" % productid in output and "Path: /etc/pki/product/%s.pem" % productid in output):
#                 logger.info("The product cert is verified.")
#             else:
#                 raise FailException("Test Failed - The product cert is not correct.")
#         else:
#             raise FailException("Test Failed - Failed to check product cert.")
# 
#     def check_rct(self):
#         cmd = "rct cat-cert --help"
#         (ret, output) = Command().run(cmd)
#         if ret == 0:
#             logger.info("rct cat-cert command can be used in the system")
#             return True
#         else:
#             logger.info("rct cat-cert command can not be used in the system")
#             return False
# 
#     def sub_unsubscribe(self):
#         cmd = "subscription-manager unsubscribe --all"
#         (ret, output) = self.runcmd(cmd, "unsubscribe")
#         expectout = "This machine has been unsubscribed from"
#         expectoutnew = "subscription removed from this system."
#         expectout5101 = "subscription removed at the server."
#         expectout5102 = "local certificate has been deleted."
#         if ret == 0:
#             if output.strip() == "" or (((expectout5101 in output) and (expectout5102 in output)) or expectout in output or expectoutnew in output):
#                 logger.info("It's successful to unsubscribe.")
#             else:
#                 raise FailException("Test Failed - The information shown after unsubscribed is not correct.")
#         else:
#             raise FailException("Test Failed - Failed to unsubscribe.")
# 
#     def sub_getcurrentversion(self):
#         version = None
#         platform = None
#         currentversion = None
#         # get version
#         cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
#         (ret, output) = Command().run(cmd, comments=False)
#         if ret == 0:
#             version = output.strip("\n").strip(" ")
#             logger.info("It's successful to get system version.")
#         else:
#             logger.info("It's failed to get system version.")
#         # get paltform
#         cmd = "lsb_release -i"
#         (ret, output) = Command().run(cmd, comments=False)
#         if ret == 0:
#             platform = output.split("Enterprise")[1].strip(" ")
#             logger.info("It's successful to get system platform")
#         else:
#             logger.info("It's failed to get system platform.")
#         currentversion = version + platform
#         return currentversion
# 

# 
#     def get_subscription_serialnumlist(self):
#         cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
#         (ret, output) = self.runcmd(cmd, "list all certificates in /etc/pki/entitlement/")
#         ent_certs = output.splitlines()
#         serialnumlist = [line.replace('.pem', '') for line in ent_certs]
#         return serialnumlist
# 
#     def sub_checkentitlementcerts(self, productid):
#         rctcommand = self.check_rct()
#         if rctcommand == True:
#             cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do rct cat-cert /etc/pki/entitlement/$i; done | grep %s" % (productid)
#         else:
#             cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i; done | grep %s" % (productid)
#         (ret, output) = self.runcmd(cmd, "check entitlement certs")
#         if ret == 0:
#             if productid in output:
#                 logger.info("It's successful to check entitlement certificates.")
#             else:
#                 raise FailException("Test Failed - The information shown entitlement certificates is not correct.")
#         else:
#             raise FailException("Test Failed - Failed to check entitlement certificates.")
# 
#     def sub_isconsumed(self, productname):
#         cmd = "subscription-manager list --consumed"
#         (ret, output) = self.runcmd(cmd, "listing consumed subscriptions")
#         output_join = " ".join(x.strip() for x in output.split())
#         if (ret == 0) and (productname in output or productname in output_join):
#             logger.info("The subscription of the product is consumed.")
#             return True
#         else:
#             logger.info("The subscription of the product is not consumed.")
#             return False
# 
#     def sub_get_consumerid(self):
#         consumerid = ''
#         if self.sub_isregistered():
#             cmd = "subscription-manager identity"
#             (ret, output) = self.runcmd(cmd, "get consumerid")
#             if ret == 0 and ("system identity:" in output or "Current identity" in output):
#                 consumerid_gain = output.split('\n')
#                 consumerid_line_split = (consumerid_gain[0]).split(":")
#                 consumerid = (consumerid_line_split[1]).strip()
#                 logger.info("consumerid is gained successfully!")
#             else:
#                 raise FailException("Test Failed - Failed to get subscription-manager identity")
#         return consumerid
# 
#     def sub_listallavailpools(self, productid):
#         cmd = "subscription-manager list --available --all"
#         (ret, output) = self.runcmd(cmd, "listing available pools")
#         if ret == 0:
#             if "no available subscription pools to list" not in output.lower():
#                 if productid in output:
#                     logger.info("The right available pools are listed successfully.")
#                     pool_list = self.parse_listavailable_output(output)
#                     return pool_list
#                 else:
#                     raise FailException("Not the right available pools are listed!")
#             else:
#                 logger.info("There is no Available subscription pools to list!")
#                 return None
#         else:
#             raise FailException("Test Failed - Failed to list all available pools.")
# 
#     def parse_listavailable_output(self, output):
#         datalines = output.splitlines()
#         data_list = []
#         # split output into segmentations for each pool
#         data_segs = []
#         segs = []
#         tmpline = ""
#         for line in datalines:
#             if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
#                 tmpline = line
#             elif line and ":" not in line:
#                 tmpline = tmpline + ' ' + line.strip()
#             elif line and ":" in line:
#                 segs.append(tmpline)
#                 tmpline = line
#             if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
#                 segs.append(tmpline)
#                 data_segs.append(segs)
#                 segs = []
#         for seg in data_segs:
#             data_dict = {}
#             for item in seg:
#                 keyitem = item.split(":")[0].replace(' ', '')
#                 valueitem = item.split(":")[1].strip()
#                 data_dict[keyitem] = valueitem
#             data_list.append(data_dict)
#         return data_list
# 
#     def sam_remote_create_org(self, samserverIP, username, password, orgname):
#         # create organization with orgname
#         cmd = "headpin -u admin -p admin org create --name=%s" % (orgname)
#         (ret, output) = self.runcmd_remote(samserverIP, username, password, cmd)
#         if ret == 0 and "Successfully created org" in output:
#             logger.info("It's successful to create organization %s." % orgname)
#         else:
#             raise FailException("Test Failed - Failed to create organization %s." % orgname)
# 
#     def sam_remote_delete_org(self, samserverIP, username, password, orgname):
#         # delete an existing organization
#         if self.sam_remote_is_org_exist(samserverIP, username, password, orgname):
#             cmd = "headpin -u admin -p admin org delete --name=%s" % (orgname)
#             (ret, output) = self.runcmd_remote(samserverIP, username, password, cmd)
#             if ret == 0 and "Successfully deleted org" in output:
#                 logger.info("It's successful to delete organization %s." % orgname)
#             else:
#                 raise FailException("Test Failed - Failed to delete organization %s." % orgname)
#         else:
#             logger.info("Org %s to be deleted does not exist." % (orgname))
# 
#     def sam_remote_is_org_exist(self, samserverIP, username, password, orgname):
#         # check an organization existing or not
#         cmd = "headpin -u admin -p admin org list"
#         (ret, output) = self.runcmd_remote(samserverIP, username, password, cmd)
#         if ret == 0 and orgname in output:
#             logger.info("Organization %s exists." % orgname)
#             return True
#         else:
#             logger.info("Organization %s does not exist." % orgname)
#             return False
# 
#     def parse_listconsumed_output(self, output):
#         datalines = output.splitlines()
#         data_list = []
#         # split output into segmentations
#         data_segs = []
#         segs = []
#         tmpline = ""
#         '''
#         for line in datalines:
#         if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
#               segs.append(line)
#         elif segs:
#              segs.append(line)
#         if ("Expires:" in line) or ("Ends:" in line):
#                 data_segs.append(segs)
#                 segs = []
#         '''
#          # new way
#         for line in datalines:
#             if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
#                 tmpline = line
#             elif line and ":" not in line:
#                 tmpline = tmpline + ' ' + line.strip()
#             elif line and ":" in line:
#                 segs.append(tmpline)
#                 tmpline = line
#             if ("Expires:" in line) or ("Ends:" in line):
#                 segs.append(tmpline)
#                 data_segs.append(segs)
#                 segs = []
# 
#         '''# handle item with multi rows
#         for seg in data_segs:
#                 length = len(seg)
#                 for index in range(0, length):
#                         if ":" not in seg[index]:
#                                 seg[index-1] = seg[index-1] + " " + seg[index].strip()
#                 for item in seg:
#                         if ":" not in item:
#                                 seg.remove(item)
#         '''
#             # parse detail information
#         for seg in data_segs:
#             data_dict = {}
#         for item in seg:
#            keyitem = item.split(":")[0].replace(' ', '')
#            valueitem = item.split(":")[1].strip()
#            data_dict[keyitem] = valueitem
#         data_list.append(data_dict)
#         return data_list
# 
#     def restart_rhsmcertd(self):
#         cmd = "service rhsmcertd restart"
#         (ret, output) = self.runcmd(cmd, "restart rhsmcertd service")
#         if ret == 0 and "Redirecting to /bin/systemctl restart  rhsmcertd.service" in output:
#             logger.info("It's successful to restart rhsmcertd service")
#         else:
#             raise FailException("Test Failed - Failed to restart rhsmcertd service.")
# 
#     def check_and_backup_yum_repos(self):
#         # check if yum.repos.d is empty
#         cmd = "ls /etc/yum.repos.d | wc -l"
#         (ret, output) = self.runcmd(cmd, "check if yum.repos.d is empty")
#         if ret == 0:
#             if output.strip() != '0':
#                 logger.info("It's successful to verify yum.repos.d is NOT empty. Backup is needed before testing")
#                 backuprepo = True
#             else:
#                 logger.info("No need to back repos.")
#                 backuprepo = False
#         else:
#             raise FailException("Test Failed - Failed to check if yum.repos.d is empty.")
#         if backuprepo == True:
#             cmd = "rm -rf /root/backuprepo;mkdir /root/backuprepo; mv /etc/yum.repos.d/* /root/backuprepo/"
#             (ret, output) = self.runcmd(cmd, "backup repo")
#             if ret == 0:
#                 logger.info("It's successful to backup repo.")
#             else:
#                 raise FailException("Test Failed - Failed to backuprepo.")
#         else:
#             logger.info("No need to back up repos")
# 
#     def restore_repos(self):
#         cmd = "ls /root/backuprepo"
#         (ret, output) = self.runcmd(cmd, "check if repos' backup is empty")
#         if ret == 0:
#             logger.info("The repos backup exist, and need restore")
#             cmd = "mv /root/backuprepo/* /etc/yum.repos.d/"
#             (ret, output) = self.runcmd(cmd, "restore repos back up")
#             if ret == 0:
#                 logger.info("It's successful to restore repos")
#             else:
#                 raise FailException("Test Failed - Failed to restore repo.")
#         else:
#             logger.info("no need to restore the repos")
# 
# 
# #     def copyfiles(self, vm, sourcepath, targetpath, cmddesc=""):
# #             if vm != None:
# #                     vm.copy_files_to(sourcepath, targetpath)
# #             else:
# #                     cmd = "cp -rf %s %s" % (sourcepath, targetpath)
# #                     (ret, output) = self.runcmd(cmd, cmddesc)
# # 
# #     def write_proxy_to_yum_conf(self, params, env):
# #             logger.info("Add proxy to /etc/yum.conf")
# #             proxy_eng = "squid.corp.redhat.com:3128"
# # 
# #             # get proxy_eng value
# #             if proxy_eng == '':
# #                     pass
# #             else:
# #                     usrname = params.get("guest_name")
# #                     rel = usrname.split('.')[0]
# #                     proxy_head = 'proxy'
# # 
# #                     cmd = "cat /etc/yum.conf|grep 'proxy'"
# #                     (ret, output) = self.runcmd(cmd, "list proxy in /etc/yum.conf")
# #                     if (ret == 0):
# #                             pass
# #                     else:
# #                             input_proxy_eng = ('%s=https://%s' % (proxy_head, proxy_eng))
# #                             cmd = "echo %s >>/etc/yum.conf" % input_proxy_eng
# #                             (ret, output) = self.runcmd(cmd, "cat proxy to /etc/yum.conf")
# #                             if (ret == 0):
# #                                     logger.info("It is success to write %s to /etc/yum.conf" % input_proxy_eng)
# #                             else:
# #                                     raise FailException("It is failed to write %s to /etc/yum.conf" % input_proxy_eng)
# #                                     return False
# # 
# #     def write_proxy_to_rhsm_conf(self, params, env):
# #         logger.info("Add proxy to /etc/rhsm/rhsm.conf")
# #         proxy_hostname = "squid.corp.redhat.com"
# #         proxy_port = "3128"
# #     
# #         (ret, output) = self.runcmd("ifconfig", "get IP")
# #         if "10.66" in output and proxy_hostname != "":
# #             cmd = "cat /etc/rhsm/rhsm.conf | grep 'squid'"
# #             (ret, output) = self.runcmd(cmd, "check proxy setting in /etc/rhsm/rhsm.conf")
# #         if (ret == 0):
# #             pass
# #         else:
# #             cmd = "sed -i 's/proxy_hostname =/proxy_hostname = squid.corp.redhat.com/' /etc/rhsm/rhsm.conf"
# #             (ret, output) = self.runcmd(cmd, "set proxy_hostname")
# #         if (ret == 0):
# #                 logger.info("It is success to set proxy_hostname to /etc/rhsm/rhsm.conf")
# #         else:
# #                 raise FailException("It is failed to set proxy_hostname to /etc/rhsm/rhsm.conf")
# #                 return False
# # 
# #         cmd = "sed -i 's/proxy_port =/proxy_port = 3128/' /etc/rhsm/rhsm.conf"
# #         (ret, output) = self.runcmd(cmd, "set proxy_port")
# #         if (ret == 0):
# #                 logger.info("It is success to set proxy_port to /etc/rhsm/rhsm.conf")
# #         else:
# #                 raise FailException("It is failed to set proxy_port to /etc/rhsm/rhsm.conf")
# #                 return False
# #     
# #     def is_file(self, file_path):
# #         # confirm the file is existing or not
# #         cmd = "(if [ -s '%s' ];then echo \"SUCCESS to find file %s\";else  echo \"FAIL to find file %s\"; fi)" % (file_path, file_path, file_path)
# #         (ret, output) = self.runcmd(cmd, "find the file")
# #         
# #         if ret == 0 and 'SUCCESS' in output:
# #             return True
# #         else:
# #             return False
# # 
# #     # ========================================================
# #     #       1. 'Acceptance' Test Common Functions
# #     # ========================================================
# # 
# #     def sub_configplatform(self, hostname):
# #             cmd = "subscription-manager config --server.hostname=%s" % (hostname)
# #             (ret, output) = self.runcmd(cmd, "configuring the system")
# # 
# #             if ret == 0:
# #                     logger.info("It's successful to configure the system as %s." % hostname)
# #             else:
# #                     raise FailException("Test Failed - Failed to configure the system as %s." % hostname)
# # 
# 
# # 
# 
# # 
# #     def sub_get_poolid(self):
# #             poolid = ''
# #             if self.sub_isregistered():
# #                     cmd = "subscription-manager list --consumed"
# #                     (ret, output) = self.runcmd(cmd, "get poolid")
# #                     if ret == 0 and "Pool ID:" in output:
# #                             poolid_gain = output.split('\n')
# #                             poolid_line_split = (poolid_gain[0]).split(":")
# #                             poolid = (poolid_line_split[1]).strip()
# #                             logger.info("poolid is gained successfully!")
# #                     else:
# #                             raise FailException("Test Failed - Failed to get subscription-manager poolid")
# #             return poolid
# # 
# #     def sub_listavailpools(self, productid):
# #             cmd = "subscription-manager list --available"
# #             (ret, output) = self.runcmd(cmd, "listing available pools")
# # 
# #             if ret == 0:
# #                     if "no available subscription pools to list" not in output.lower():
# #                             if productid in output:
# #                                     logger.info("The right available pools are listed successfully.")
# #                                     pool_list = self.parse_listavailable_output(output)
# #                                     return pool_list
# #                             else:
# #                                     raise FailException("Not the right available pools are listed!")
# # 
# #                     else:
# #                             logger.info("There is no Available subscription pools to list!")
# #                             return None
# #             else:
# #                     raise FailException("Test Failed - Failed to list available pools.")
# # 
# #     def sub_listinstalledpools(self):
# #             cmd = "subscription-manager list --installed"
# #             (ret, output) = self.runcmd(cmd, "listing installed pools")
# #             if ret == 0:
# #                     logger.info("The right installed pools are listed successfully.")
# #                     pool_list = self.parse_listavailable_output(output)
# #                     return pool_list
# #             else:
# #                     raise FailException("Test Failed - Failed to list installed pools.")
# # 
# #     def sub_listconsumedpools(self):
# #             cmd = "subscription-manager list --consumed"
# #             (ret, output) = self.runcmd(cmd, "listing consumed pools")
# #             if ret == 0:
# #                     logger.info("The right consumed pools are listed successfully.")
# #                     pool_list = self.parse_listavailable_output(output)
# #                     return pool_list
# #             else:
# #                     raise FailException("Test Failed - Failed to list consumed pools.")
# # 
# 
# # 
# 
# # 
# 
# 
# #     def sub_subscribetopool(self, poolid):
# #             cmd = "subscription-manager subscribe --pool=%s" % (poolid)
# #             (ret, output) = self.runcmd(cmd, "subscribe")
# # 
# #             if ret == 0:
# #                     # Note: the exact output should be as below:
# #                     # For 6.2: "Successfully subscribed the system to Pool"
# #                     # For 5.8: "Successfully consumed a subscription from the pool with id"
# #                     if "Successfully " in output:
# #                             logger.info("It's successful to subscribe.")
# #                     else:
# #                             raise FailException("Test Failed - The information shown after subscribing is not correct.")
# #             else:
# #                     raise FailException("Test Failed - Failed to subscribe.")
# # 
# 
# 
# 
# # 
# 
# # 
# 
# #     def cnt_subscribe_product_with_specified_sku(self, prodsku):
# #             # subscribe with the specified prodsku
# #             dictlist = self.sub_listavailpools_of_sku(prodsku)
# #             odict = dictlist[0]
# #             prodpool = ''
# #             if odict.has_key('SKU'):
# #                     if odict.get('SKU') == prodsku:
# #                             if odict.has_key('Pool ID'):
# #                                     prodpool = odict.get('Pool ID')
# #                             elif odict.has_key('PoolId'):
# #                                     prodpool = odict.get('PoolId')
# #                             elif odict.has_key('PoolID'):
# #                                     prodpool = odict.get('PoolID')
# # 
# #                             self.sub_subscribetopool(prodpool)
# #                             return True
# #             else:
# #                     return False
# # 
# 
# 
# # 
# #     def sub_checkidcert(self):
# #             cmd = "ls /etc/pki/consumer/"
# #             (ret, output) = self.runcmd(cmd, "listing the files in /etc/pki/consumer/")
# # 
# #             if ret == 0 and "cert.pem" in output and "key.pem" in output:
# #                     logger.info("There are identity certs in the consumer directory.")
# #                     return True
# #             else:
# #                     logger.info("There is no identity certs in the consumer directory.")
# #                     return False
# # 
# 
# # 
# 
# # 
# #     def sub_getcurrentversion2(self, guestname):
# #             os_version = guestname.split('-')[-1].strip()
# #             return os_version
# # 
# 
# 
# 
# #             # stop rhsmcertd because healing(autosubscribe) will run 2 mins after the machine is started, then every 24 hours after that, which will influence our content test.
# #             cmd = 'service rhsmcertd status'
# #             (ret, output) = self.runcmd(cmd, "check rhsmcertd service status")
# #             if 'stopped' in output or 'Stopped' in output:
# #                     return
# # 
# #             cmd = 'service rhsmcertd stop'
# #             (ret, output) = self.runcmd(cmd, "stop rhsmcertd service")
# #             if (ret == 0):
# #                     cmd = 'service rhsmcertd status'
# #                     (ret, output) = self.runcmd(cmd, "check rhsmcertd service status")
# #                     if 'stopped' in output or 'Stopped' in output:
# #                             logger.info("It's successful to stop rhsmcertd service.")
# #                     else:
# #                         raise FailException("Failed to stop rhsmcertd service.")
# #             else:
# #                 raise FailException("Failed to stop rhsmcertd service.")
# # 
# #     # ========================================================
# #     #       3. 'SAM Server' Test Common Functions
# #     # ========================================================
# # 
# #     def sam_create_user(self, username, password, email):
# #             # create user with username, password and email address
# #             cmd = "headpin -u admin -p admin user create --username=%s --password=%s --email=%s" % (username, password, email)
# #             (ret, output) = self.runcmd(cmd, "creating user")
# # 
# #             if (ret == 0) and ("Successfully created user" in output):
# #                     logger.info("It's successful to create user %s with password %s and email %s." % (username, password, email))
# #             else:
# #                     raise FailException("Test Failed - Failed to create user %s with password %s and email %s." % (username, password, email))
# # 
# #     def sam_is_user_exist(self, username):
# #             # check a user exist or not
# #             cmd = "headpin -u admin -p admin user list"
# #             (ret, output) = self.runcmd(cmd, "listing user")
# # 
# #             if (ret == 0) and (username in output):
# #                     logger.info("User %s exists." % (username))
# #                     return True
# #             else:
# #                     logger.info("User %s does not exist." % (username))
# #                     return False
# # 
# #     def sam_delete_user(self, username):
# #             # delete user with username
# #             if self.sam_is_user_exist(username):
# #                     cmd = "headpin -u admin -p admin user delete --username=%s" % (username)
# #                     (ret, output) = self.runcmd(cmd, "deleting user")
# # 
# #                     if (ret == 0) and ("Successfully deleted user" in output):
# #                             logger.info("It's successful to delete user %s." % (username))
# #                     else:
# #                             raise FailException("Test Failed - Failed to delete user %s." % (username))
# #             else:
# #                     logger.info("User %s to be deleted does not exist." % (username))
# # 
# #     def sam_create_org(self, orgname):
# #             # create organization with orgname
# #             cmd = "headpin -u admin -p admin org create --name=%s" % (orgname)
# #             (ret, output) = self.runcmd(cmd, "creating organization")
# # 
# #             if ret == 0 and "Successfully created org" in output:
# #                     logger.info("It's successful to create organization %s." % orgname)
# #             else:
# #                     raise FailException("Test Failed - Failed to create organization %s." % orgname)
# # 
# # 
# #     def sam_is_org_exist(self, orgname):
# #             # check an organization existing or not
# #             cmd = "headpin -u admin -p admin org list"
# #             (ret, output) = self.runcmd(cmd, "list organization")
# # 
# #             if ret == 0 and orgname in output:
# #                     logger.info("Organization %s exists." % orgname)
# #                     return True
# #             else:
# #                     logger.info("Organization %s does not exist." % orgname)
# #                     return False
# # 
# #     def sam_delete_org(self, orgname):
# #             # delete an existing organization
# #             if self.sam_is_org_exist(orgname):
# #                     cmd = "headpin -u admin -p admin org delete --name=%s" % (orgname)
# #                     (ret, output) = self.runcmd(cmd, "delete organization")
# # 
# #                     if ret == 0 and "Successfully deleted org" in output:
# #                             logger.info("It's successful to delete organization %s." % orgname)
# #                     else:
# #                             raise FailException("Test Failed - Failed to delete organization %s." % orgname)
# #             else:
# #                     logger.info("Org %s to be deleted does not exist." % (orgname))
# # 
# 
# 
# 
# # 
# #     def sam_create_env(self, envname, orgname, priorenv):
# #             ''' create environment belong to organizaiton with prior environment. '''
# # 
# #             cmd = "headpin -u admin -p admin environment create --name=%s --org=%s --prior=%s" % (envname, orgname, priorenv)
# #             (ret, output) = self.runcmd(cmd, "create environment")
# # 
# #             if ret == 0:
# #                     logger.info("It's successful to create environment '%s' - belong to organizaiton '%s' with prior environment '%s'." % (envname, orgname, priorenv))
# #             else:
# #                     raise FailException("Test Failed - Failed to create environment '%s' - belong to organizaiton '%s' with prior environment '%s'." % (envname, orgname, priorenv))
# # 
# #     def sam_check_env(self, envname, orgname, priorenv, desc='None'):
# #             ''' check environment info. '''
# # 
# #             cmd = "headpin -u admin -p admin environment info --name=%s --org=%s" % (envname, orgname)
# #             (ret, output) = self.runcmd(cmd, "check environment detail info")
# # 
# #             if (ret == 0) and (envname in output) and (orgname in output) and (priorenv in output) and (desc in output):
# #                     logger.info("It's successful to check environment detail info.")
# #             else:
# #                     raise FailException("Test Failed - Failed to check environment detail info.")
# # 
# #     def sam_is_env_exist(self, envname, orgname):
# #             ''' check if an environment of one org existing or not. '''
# # 
# #             cmd = "headpin -u admin -p admin environment list --org=%s" % orgname
# #             (ret, output) = self.runcmd(cmd, "list environment")
# # 
# #             if ret == 0 and envname in output:
# #                     logger.info("Environment %s exists." % envname)
# #                     return True
# #             else:
# #                     logger.info("Environment %s does not exist." % envname)
# #                     return False
# # 
# #     def sam_delete_env(self, envname, orgname):
# #             ''' delete an existing environment. '''
# # 
# #             if self.sam_is_env_exist(envname, orgname):
# #                     cmd = "headpin -u admin -p admin environment delete --name=%s --org=%s" % (envname, orgname)
# #                     (ret, output) = self.runcmd(cmd, "delete environment")
# # 
# #                     if ret == 0 and "Successfully deleted environment" in output:
# #                             logger.info("It's successful to delete environment %s." % envname)
# #                     else:
# #                             raise FailException("Test Failed - Failed to delete environment %s." % envname)
# #             else:
# #                     logger.info("Environment %s to be deleted does not exist." % (envname))
# # 
# #     def sam_create_activationkey(self, keyname, envname, orgname):
# #             # create an activationkey
# #             cmd = "headpin -u admin -p admin activation_key create --name=%s --org=%s --env=%s" % (keyname, orgname, envname)
# #             (ret, output) = self.runcmd(cmd, "create activationkey")
# # 
# #             if ret == 0 and "Successfully created activation key" in output:
# #                     logger.info("It's successful to create activationkey %s belong to organizaiton %s environment %s." % (keyname, orgname, envname))
# #             else:
# #                     raise FailException("Test Failed - Failed to create activationkey %s belong to organizaiton %s environment %s." % (keyname, orgname, envname))
# # 
# #     def sam_is_activationkey_exist(self, keyname, orgname):
# #             # check an activationkey of one org existing or not
# #             cmd = "headpin -u admin -p admin activation_key list --org=%s" % orgname
# #             (ret, output) = self.runcmd(cmd, "list activationkey")
# # 
# #             if ret == 0 and keyname in output:
# #                     logger.info("Activationkey %s exists." % keyname)
# #                     return True
# #             else:
# #                     logger.info("Activationkey %s doesn't exist." % keyname)
# #                     return False
# # 
# #     def sam_delete_activationkey(self, keyname, orgname):
# #             # delete an existing activation key
# #             if self.sam_is_activationkey_exist(keyname, orgname):
# #                     cmd = "headpin -u admin -p admin activation_key delete --name=%s --org=%s" % (keyname, orgname)
# #                     (ret, output) = self.runcmd(cmd, "delete activationkey")
# # 
# #                     if ret == 0 and "Successfully deleted activation key" in output:
# #                             logger.info("It's successful to delete activation key %s." % keyname)
# #                     else:
# #                             raise FailException("Test Failed - Failed to delete activation key %s." % keyname)
# #             else:
# #                     logger.info("Activationkey %s to be deleted doesn't exist." % (keyname))
# # 
# #     def sam_save_option(self, optionname, optionvalue):
# #             ''' save an option. '''
# # 
# #             cmd = "headpin -u admin -p admin client remember --option=%s --value=%s" % (optionname, optionvalue)
# #             (ret, output) = self.runcmd(cmd, "save option")
# # 
# #             if ret == 0 and "Successfully remembered option [ %s ]" % (optionname) in output:
# #                     logger.info("It's successful to save the option '%s'." % optionname)
# #             else:
# #                     raise FailException("Test Failed - Failed to save the option '%s'." % optionname)
# # 
# #     def sam_remove_option(self, optionname):
# #             ''' remove an option. '''
# # 
# #             cmd = "headpin -u admin -p admin client forget --option=%s" % optionname
# #             (ret, output) = self.runcmd(cmd, "remove option")
# # 
# #             if ret == 0 and "Successfully forgot option [ %s ]" % (optionname) in output:
# #                     logger.info("It's successful to remove the option '%s'." % optionname)
# #             else:
# #                     raise FailException("Test Failed - Failed to remove the option '%s'." % optionname)
# # 
# #     def sam_add_pool_to_activationkey(self, orgname, keyname):
# #             # find a pool belonging to the key's org
# #             cmd = "curl -u admin:admin -k https://localhost/sam/api/owners/%s/pools |python -mjson.tool|grep 'pools'|awk -F'\"' '{print $4}'" % (orgname)
# #             (ret, output) = self.runcmd(cmd, "finding an available pool")
# # 
# #             if ret == 0 and "pools" in output:
# #                     poollist = self.__parse_sam_avail_pools(output)
# # 
# #                     # get an available entitlement pool to subscribe with random.sample
# #                     poolid = random.sample(poollist, 1)[0]
# #                     logger.info("It's successful to find an available pool '%s'." % (poolid))
# # 
# #                     # add a pool to an activationkey
# #                     cmd = "headpin -u admin -p admin activation_key update --org=%s --name=%s --add_subscription=%s" % (orgname, keyname, poolid)
# #                     (ret, output) = self.runcmd(cmd, "add a pool to an activationkey")
# # 
# #                     if ret == 0 and "Successfully updated activation key [ %s ]" % (keyname) in output:
# #                             # check whether the pool is in the key
# #                             cmd = "headpin -u admin -p admin activation_key info --name=%s --org=%s" % (keyname, orgname)
# #                             (ret, output) = self.runcmd(cmd, "check activationkey info")
# # 
# #                             if ret == 0 and poolid in output:
# #                                     logger.info("It's successful to add pool '%s' to activationkey '%s'." % (poolid, keyname))
# #                                     return poolid
# #                             else:
# #                                     raise FailException("It's failed to add a pool to activationkey '%s'." % keyname)
# #                     else:
# #                             raise FailException("Test Failed - Failed to add a pool to activationkey '%s'." % keyname)
# #             else:
# #                     raise FailException("Test Failed - Failed to find an available pool")
# # 
# #     def __parse_sam_avail_pools(self, output):
# #             datalines = output.splitlines()
# #             poollist = []
# #             # pick up pool lines from output
# #             data_segs = []
# #             for line in datalines:
# #                     if "/pools/" in line:
# #                             data_segs.append(line)
# # 
# #             # put poolids into poolist
# #             for seg in data_segs:
# #                     pool = seg.split("/")[2]
# #                     poollist.append(pool)
# #             return poollist
# # 
# #     def sam_import_manifest_to_org(self, filepath, orgname, provider):
# #             # import a manifest to an organization
# #             cmd = "headpin -u admin -p admin provider import_manifest --org=%s --name='%s' --file=%s" % (orgname, provider, filepath)
# #             (ret, output) = self.runcmd(cmd, "import manifest")
# # 
# #             if ret == 0 and "Manifest imported" in output:
# #                     logger.info("It's successful to import manifest to org '%s'." % orgname)
# #             else:
# #                     raise FailException("Test Failed - Failed to import manifest to org '%s'." % orgname)
# # 
# #     def sam_is_product_exist(self, productname, provider, orgname):
# #             # check whether a product is in the product list of an org
# #             cmd = "headpin -u admin -p admin product list --org=%s --provider='%s'" % (orgname, provider)
# #             (ret, output) = self.runcmd(cmd, "list products of an organization")
# # 
# #             if ret == 0 and productname in output:
# #                     logger.info("The product '%s' is in the product list of org '%s'." % (productname, orgname))
# #                     return True
# #             else:
# #                     logger.info("The product '%s' isn't in the product list of org '%s'." % (productname, orgname))
# #                     return False
# # 
# #     def sam_create_system(self, systemname, orgname, envname):
# #             # get environment id of envname
# #             cmd = "curl -u admin:admin -k https://localhost/sam/api/organizations/%s/environments/|python -mjson.tool|grep -C 2 '\"name\": \"%s\"'" % (orgname, envname)
# #             (ret, output) = self.runcmd(cmd, "get environment id")
# # 
# #             if ret == 0 and envname in output:
# #                     # get the env id from output
# #                     envid = self.__parse_env_output(output)
# # 
# #                     if envid != "":
# #                             # create a new system using candlepin api
# #                             cmd = "curl -u admin:admin -k --request POST --data '{\"name\":\"%s\",\"cp_type\":\"system\",\"facts\":{\"distribution.name\":\"Red Hat Enterprise Linux Server\",\"cpu.cpu_socket(s)\":\"1\",\"virt.is_guest\":\"False\",\"uname.machine\":\"x86_64\"}}' --header 'accept: application/json' --header 'content-type: application/json' https://localhost/sam/api/environments/%s/systems|grep %s" % (systemname, envid, systemname)
# # 
# #                             (ret, output) = self.runcmd(cmd, "create a system")
# # 
# #                             if ret == 0 and systemname in output:
# #                                     logger.info("It's successful to create system '%s' in org '%s'." % (systemname, orgname))
# #                             else:
# #                                     raise FailException("Test Failed - Failed to create system '%s' in org '%s'." % (systemname, orgname))
# #                     else:
# #                             raise FailException("Test Failed - Failed to get envid of env '%s' from org '%s'." % (envname, orgname))
# #             else:
# #                     raise FailException("Test Failed - Failed to get env info from org '%s'." % orgname)
# # 
# #     def __parse_env_output(self, output):
# #             datalines = output.splitlines()
# #             envid = ""
# #             for line in datalines:
# #                     if "\"id\"" in line:
# #                             envid = line.split(":")[1].split(",")[0].strip()
# #                             break
# #             return envid
# # 
# #     def sam_list_system(self, orgname, systemname):
# #             ''' list system and then check system list. '''
# # 
# #             cmd = "headpin -u admin -p admin system list --org=%s" % (orgname)
# #             (ret, output) = self.runcmd(cmd, "list system")
# # 
# #             if (ret == 0) and (systemname in output):
# #                     logger.info("It's successful to list system '%s'." % systemname)
# #             else:
# #                     raise FailException("Test Failed - Failed to list system '%s'." % systemname)
# # 
# #     def sam_is_system_exist(self, orgname, systemname):
# #             ''' check if the system exists. '''
# # 
# #             cmd = "headpin -u admin -p admin system list --org=%s" % (orgname)
# #             (ret, output) = self.runcmd(cmd, "list system")
# # 
# #             if (ret == 0) and (systemname in output):
# #                     logger.info("The system '%s' exists." % systemname)
# #                     return True
# #             else:
# #                     logger.info("The system %s does not exist." % systemname)
# #                     return False
# # 
# #     def sam_list_system_detail_info(self, systemname, orgname, envname, checkinfolist):
# #             ''' list system info. '''
# # 
# #             cmd = "headpin -u admin -p admin system info --name=%s --org=%s --environment=%s" % (systemname, orgname, envname)
# #             (ret, output) = self.runcmd(cmd, "list system detail info")
# # 
# #             if (ret == 0):
# #                     for i in checkinfolist:
# #                             if i in output:
# #                                     logger.info("The info '%s' is in command output." % i)
# #                             else:
# #                                     raise FailException("Test Failed - Failed to list system detail info - the info '%s' is not in command output." % i)
# # 
# #                     logger.info("It's successful to list system detail info.")
# #             else:
# #                     raise FailException("Test Failed - Failed to list system detail info.")
# # 
# #     def sam_unregister_system(self, systemname, orgname):
# #             ''' unregister a system. '''
# # 
# #             if self.sam_is_system_exist(orgname, systemname):
# #                     cmd = "headpin -u admin -p admin system unregister --name=%s --org=%s" % (systemname, orgname)
# #                     (ret, output) = self.runcmd(cmd, "register system")
# # 
# #                     if ret == 0 and "Successfully unregistered System [ %s ]" % systemname in output:
# #                             logger.info("It's successful to unregister the system '%s' - belong to organizaiton '%s'." % (systemname, orgname))
# #                     else:
# #                             raise FailException("Test Failed - Failed to unregister the system '%s' - belong to organizaiton '%s'." % (systemname, orgname))
# #             else:
# #                     logger.info("System '%s' to be unregistered does not exist." % (systemname))
# # 
# #     def sam_listavailpools(self, systemname, orgname):
# #             ''' list available subscriptions. '''
# #             cmd = "headpin -u admin -p admin system subscriptions --org=%s --name=%s --available" % (orgname, systemname)
# #             (ret, output) = self.runcmd(cmd, "list available pools")
# # 
# #             if ret == 0 and ("Pool" in output or "PoolId" in output):
# #                     logger.info("The available pools are listed successfully.")
# #                     pool_list = self.__parse_sam_avail_pools_cli(output)
# #                     return pool_list
# #             else:
# #                     raise FailException("Test Failed - Failed to list available pools.")
# #                     return None
# # 
# #     def __parse_sam_avail_pools_cli(self, output):
# #             datalines = output.splitlines()
# #             pool_list = []
# #             # split output into segmentations for each pool
# #             data_segs = []
# #             segs = []
# #             for line in datalines:
# #                     if "Pool:" in line or "PoolId" in line:
# #                             segs.append(line)
# #                     elif segs:
# #                             segs.append(line)
# import sys, os, subprocess, commands, string, re, random, time, pexpect
# from utils.Python.utils import Utils as utils
# from repos.domain import define
# from repos.domain import undefine
# from repos.domain import suspend
# from repos.domain import resume
# from repos.domain import shutdown
# from repos.domain import start
# from repos.domain import destroy
# from repos.domain import migrate
# from repos.entitlement.ent_env import ent_env as ee
# 
# class ent_utils:
# 
#     # ========================================================
#     #        0. 'Basic' Common Functions
#     # ========================================================
# 
#     def runcmd(self, cmd, cmddesc="", targetmachine_ip="", showlogger=True):
#         if targetmachine_ip == "":
#             (ret, output) = commands.getstatusoutput(cmd)
#         else:
#             if "redhat.com" in targetmachine_ip:
#                 # run in beaker
#                 (ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "xxoo2014", cmd)
#             else:
#                 (ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "redhat", cmd)
#         if cmddesc != "":
#             cmddesc = " of " + cmddesc
#         if showlogger:
#             logger.info(" [command]%s: %s" % (cmddesc, cmd))
#             logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
#             logger.info(" [output ]%s: %s \n" % (cmddesc, output))
#         return ret, output
# 
#     def runcmd_esx(self, cmd, cmddesc="", targetmachine_ip="", username="root", password="qwe123P", showlogger=True):
#         if targetmachine_ip == "":
#             (ret, output) = commands.getstatusoutput(cmd)
#         else:
#             (ret, output) = self.remote_esx_pexpect(targetmachine_ip, username, password, cmd)
#         if cmddesc != "":
#             cmddesc = " of " + cmddesc
#         if showlogger:
#             logger.info(" [command]%s: %s" % (cmddesc, cmd))
#             logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
#             logger.info(" [output ]%s: %s \n" % (cmddesc, output))
#         return ret, output
# 
#     def runcmd_rhevm(self, cmd, cmddesc="run rhevm-shell command", rhevm_ip="", showlogger=True):
#         # 1. add rhevm_script file
#         utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "echo '%s' > /tmp/rhevm_script" % cmd)
#         # 2. change rhevm_control file
#         utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "echo 1 > /tmp/rhevm_control")
#         if self.check_rhevm_shell_finished(rhevm_ip):
#             # 3. get rhevm_result file
#             (ret, output) = utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "cat /tmp/rhevm_result")
#         if cmddesc != "":
#             cmddesc = " of " + cmddesc
#         if showlogger:
#             logger.info(" [command]%s: %s" % (cmddesc, cmd))
#             logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
#             logger.info(" [output ]%s: %s \n" % (cmddesc, output))
#         return ret, output
# 
#     def runcmd_indns(self, cmd, cmddesc="", targetmachine_ip="", username="root", password="forsamdns", showlogger=True):
#         if targetmachine_ip == "":
#             (ret, output) = commands.getstatusoutput(cmd)
#         else:
#             (ret, output) = utils().remote_exec_pexpect(targetmachine_ip, username, password, cmd)
#         if cmddesc != "":
#             cmddesc = " of " + cmddesc
#         if showlogger:
#             logger.info(" [command]%s: %s" % (cmddesc, cmd))
#             logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
#             logger.info(" [output ]%s: %s \n" % (cmddesc, output))
#         return ret, output
# 

# 
#     def runcmd_subprocess(self, cmd, cmddesc=""):
#         logger.info("[ command of subprocess]%s: %s" % (cmddesc, cmd))
#         ret = subprocess.call(cmd, shell=True)
#         # result.stdout.readlines())
#         # handle = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
#         # ##logger.info("[ result of subprocess] : %s" % handle.communicate()[0]
#         return ret, ""
# 
#     def runcmd_rhevmprocess(self, cmd, cmddesc=""):
#         logger.info("[ command of rhevm-shell]%s: %s" % (cmddesc, cmd))
#         output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#         for line in output.stdout.readlines():
#             return line
# 
#     def get_hg_info(self, targetmachine_ip):
#         if targetmachine_ip == "":
#             host_guest_info = "in host machine"
#         else:
#             host_guest_info = "in guest machine %s" % targetmachine_ip
#         return host_guest_info
# 
#     def get_guest_IP(self, guest_name):
#         mac = utils().get_dom_mac_addr(guest_name)
#         guestip = utils().mac_to_ip(mac)
#         if guestip == None:
#             raise FailException("Failed to get guest IP.")
# 
#         else:
#             logger.info("Succeeded to get guest IP: %s" % guestip)
#             return guestip
# 
#     # For return test result
#     RESULT = 1
#     def RESET_RESULT(self):
#         global RESULT
#         RESULT = 1
#         # print "RESULT has been reseted %s" % RESULT
#     def TEST_RESULT(self):
#         global RESULT
#         if RESULT > 1:
#             RESULT = 1
#         # print "RESULT has been returned %s" % RESULT
#         return RESULT
#     def SET_RESULT(self, step_result):
#         global RESULT
#         if step_result == 0:
#             # print "RESULT has been minused"
#             RESULT = RESULT - 1
#             # print "RESULT = %s" % RESULT
#         else:
#             # print "RESULT has been added"
#             RESULT = RESULT + step_result
#             # print "RESULT = %s" % RESULT
# 
#     # ========================================================
#     #     1. 'RHSM' Test Common Functions
#     # ========================================================
# 

# 
# 
#     def sub_isregistered(self, targetmachine_ip=""):
#         ''' Check whether the machine is registered. '''
#         cmd = "subscription-manager identity"
#         ret, output = self.runcmd(cmd, "check whether the machine is registered", targetmachine_ip)
#         if ret == 0:
#             logger.info("System %s is registered." % self.get_hg_info(targetmachine_ip))
#             return True
#         else: 
#             logger.info("System %s is not registered." % self.get_hg_info(targetmachine_ip))
#             return False
# 

# 

# 
# 
#     def sub_datacenter_listavailpools(self, subscription_name, targetmachine_ip="", showlog=True):
#         ''' List available pools.'''
#         cmd = "subscription-manager list --available"
#         ret, output = self.runcmd(cmd, "list available subscriptions", targetmachine_ip, showlogger=showlog)
#         if ret == 0:
#             if "No Available subscription pools to list" not in output:
#                 if subscription_name in output:
#                     logger.info("Succeeded to list the right available pools %s." % self.get_hg_info(targetmachine_ip))
#                     pool_list = self.__parse_avail_pools(output)
#                     return pool_list
#                 else:
#                     raise FailException("Failed to list available pools %s - Not the right available pools are listed!" % self.get_hg_info(targetmachine_ip))
#         
#             else:
#                 raise FailException("Failed to list available pools %s - There is no Available subscription pools to list!" % self.get_hg_info(targetmachine_ip))
#     
#         else:
#             raise FailException("Failed to list available pools %s." % self.get_hg_info(targetmachine_ip))
# 
# 

# 
#     def sub_subscribetopool(self, poolid, targetmachine_ip=""):
#         ''' Subscribe to a pool. '''
#         cmd = "subscription-manager subscribe --pool=%s" % (poolid)
#         ret, output = self.runcmd(cmd, "subscribe by --pool", targetmachine_ip)
#         if ret == 0:
#             if "Successfully " in output:
#                 logger.info("Succeeded to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))
#             else:
#                 raise FailException("Failed to show correct information after subscribing %s." % self.get_hg_info(targetmachine_ip))
#     
#         else:
#             raise FailException("Failed to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#     def sub_subscribe_instance_pool(self, poolid, targetmachine_ip=""):
#         ''' Subscribe to an instance pool. '''
#         cmd = "subscription-manager subscribe --pool=%s --quantity=2" % (poolid)
#         ret, output = self.runcmd(cmd, "subscribe an instance pool", targetmachine_ip)
#         if ret == 0:
#             if "Successfully " in output:
#                 logger.info("Succeeded to subscribe an instance pool %s." % self.get_hg_info(targetmachine_ip))
#             else:
#                 raise FailException("Failed to subscribe an instance pool %s." % self.get_hg_info(targetmachine_ip))
#     
#         else:
#             raise FailException("Failed to subscribe an instance pool %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#     def sub_subscribetopool_of_product(self, productid, targetmachine_ip=""):
#         ''' Subscribe to the pool of the product: productid. '''
#         availpoollist = self.sub_listavailpools(productid, targetmachine_ip)
#         if availpoollist != None:
#             rindex = -1
#             for index in range(0, len(availpoollist)):
#                 if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == productid):
#                     rindex = index
#                     break
#                 elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == productid):
#                     rindex = index
#                     break
#             if rindex == -1:
#                 raise FailException("Failed to show find the bonus pool")
#     
#             if "PoolID" in availpoollist[index]:
#                 poolid = availpoollist[rindex]["PoolID"]
#             else:
#                 poolid = availpoollist[rindex]["PoolId"]
#             self.sub_subscribetopool(poolid, targetmachine_ip)
#         else:
#             raise FailException("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % productid)
# 
# 
#     def sub_subscribe_to_bonus_pool(self, productid, guest_ip=""):
#         ''' Subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
#         availpoollistguest = self.sub_listavailpools(productid, guest_ip)
#         if availpoollistguest != None:
#             rindex = -1
#             for index in range(0, len(availpoollistguest)):
#                 # if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and availpoollistguest[index][self.get_type_name(availpoollistguest[index])] == "virtual"):
#                 if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and self.check_type_virtual(availpoollistguest[index])):
#                     rindex = index
#                     break
#                 # elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and availpoollistguest[index][self.get_type_name(availpoollistguest[index])] == "virtual"):
#                 elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and self.check_type_virtual(availpoollistguest[index])):
#                     rindex = index
#                     break
#             if rindex == -1:
#                 raise FailException("Failed to show find the bonus pool")
#     
#             if "PoolID" in availpoollistguest[index]:
#                 gpoolid = availpoollistguest[rindex]["PoolID"]
#             else:
#                 gpoolid = availpoollistguest[rindex]["PoolId"]
#             self.sub_subscribetopool(gpoolid, guest_ip)
#         else:
#             raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % productid)
# 
# 
#     def subscribe_datacenter_bonus_pool(self, subscription_name, guest_ip=""):
#         ''' Subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
#         availpoollistguest = self.sub_datacenter_listavailpools(subscription_name, guest_ip)
#         if availpoollistguest != None:
#             for index in range(0, len(availpoollistguest)):
#                 if("SubscriptionName" in availpoollistguest[index] and availpoollistguest[index]["SubscriptionName"] == subscription_name and self.check_type_virtual(availpoollistguest[index])):
#                     rindex = index
#                     break
#             if "PoolID" in availpoollistguest[rindex]:
#                 gpoolid = availpoollistguest[rindex]["PoolID"]
#             else:
#                 gpoolid = availpoollistguest[rindex]["PoolId"]
#             self.sub_subscribetopool(gpoolid, guest_ip)
#         else:
#             raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % subscription_name)
# 
# 
#     def subscribe_instance_pool(self, SKU_id, guest_ip=""):
#         ''' subscribe_instance_pool '''
#         availpoollistguest = self.sub_listavailpools(SKU_id, guest_ip)
#         if availpoollistguest != None:
#             for index in range(0, len(availpoollistguest)):
#                 if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
#                     rindex = index
#                     break
#             if "PoolID" in availpoollistguest[index]:
#                 gpoolid = availpoollistguest[rindex]["PoolID"]
#             else:
#                 gpoolid = availpoollistguest[rindex]["PoolId"]
#             self.sub_subscribe_instance_pool(gpoolid, guest_ip)
#         else:
#             raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)
# 
# 
#     def get_pool_by_SKU(self, SKU_id, guest_ip=""):
#         ''' get_pool_by_SKU '''
#         availpoollistguest = self.sub_listavailpools(SKU_id, guest_ip)
#         if availpoollistguest != None:
#             for index in range(0, len(availpoollistguest)):
#                 if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
#                     rindex = index
#                     break
#             if "PoolID" in availpoollistguest[index]:
#                 gpoolid = availpoollistguest[rindex]["PoolID"]
#             else:
#                 gpoolid = availpoollistguest[rindex]["PoolId"]
#             return gpoolid
#         else:
#             raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)
# 
# 
#     def get_SKU_attribute(self, SKU_id, attribute_key, guest_ip=""):
#         availpoollistguest = self.sub_listavailpools(SKU_id, guest_ip)
#         if availpoollistguest != None:
#             for index in range(0, len(availpoollistguest)):
#                 if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
#                     rindex = index
#                     break
#             if attribute_key in availpoollistguest[index]:
#                 attribute_value = availpoollistguest[rindex][attribute_key]
#             return attribute_value
#         else:
#             raise FailException("Failed to list available subscriptions" % SKU_id)
# 
# 
#     def sub_autosubscribe(self, autosubprod, targetmachine_ip=""):
#         cmd = "subscription-manager subscribe --auto"
#         (ret, output) = self.runcmd(cmd, "auto-subscribe", targetmachine_ip="")
#         if ret == 0:
#             if (autosubprod in output) and ("Subscribed" in output) and ("Not Subscribed" not in output):
#                 logger.info("It's successful to auto-subscribe.")
#             else:
#                 raise FailException("Test Failed - Failed to auto-subscribe correct product.")
#         else:
#             raise FailException("Test Failed - Failed to auto-subscribe.")
# 
#     def auto_subscribe(self, targetmachine_ip=""):
#         cmd = "subscription-manager subscribe --auto"
#         (ret, output) = self.runcmd(cmd, "auto-subscribe", targetmachine_ip="")
#         if ret == 0:
#             if ("Subscribed" in output) and ("Not Subscribed" not in output):
#                 logger.info("It's successful to auto-subscribe.")
#             else:
#                 raise FailException("Test Failed - Failed to auto-subscribe correct product.")
#         else:
#             raise FailException("Test Failed - Failed to auto-subscribe.")
# 
#     def get_type_name(self, pool_dict):
#         if "MachineType" in pool_dict.keys():
#             TypeName = "MachineType"
#         elif "SystemType" in pool_dict.keys():
#             TypeName = "SystemType"
#         # print "TypeName = %s" % TypeName
#         return TypeName
#     

# 
#     def sub_unsubscribe(self, targetmachine_ip=""):
#         ''' Unsubscribe from all entitlements. '''
#         cmd = "subscription-manager unsubscribe --all"
#         ret, output = self.runcmd(cmd, "unsubscribe all", targetmachine_ip)
# 
#         if ret == 0:
#             cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
#             ret1, output1 = self.runcmd(cmd, "check whether key.pem exist", targetmachine_ip)
# 
#             if ret1 == 0 :
#                 raise FailException("Failed to unsubscribe all entitlements %s." % self.get_hg_info(targetmachine_ip))
#     
#             else:
#                 logger.info("Succeeded to unsubscribe all entitlements %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to unsubscribe %s." % self.get_hg_info(targetmachine_ip))
# 
#     def sub_listconsumed(self, productname, targetmachine_ip="", productexists=True):
#         ''' List consumed entitlements. '''
#         cmd = "subscription-manager list --consumed"
#         ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
#         if ret == 0:
#             if productexists:
#                 if "No Consumed subscription pools to list" not in output:
#                     if productname in output:
#                         logger.info("Succeeded to list the right consumed subscription %s." % self.get_hg_info(targetmachine_ip))
#                     else:
#                         raise FailException("Failed to list consumed subscription %s - Not the right consumed subscription is listed!" % self.get_hg_info(targetmachine_ip))
#             
#                 else:
#                     raise FailException("Failed to list consumed subscription %s - There is no consumed subscription to list!")
#         
#             else:
#                 if productname not in output:
#                     logger.info("Succeeded to check entitlements %s - the product '%s' is not subscribed now." % (self.get_hg_info(targetmachine_ip), productname))
#                 else:
#                     raise FailException("Failed to check entitlements %s - the product '%s' is still subscribed now." % (self.get_hg_info(targetmachine_ip), productname))
#         
#         else:
#             raise FailException("Failed to list consumed subscriptions.")
# 
# 
#     def sub_refresh(self, targetmachine_ip=""):
#         ''' Refresh all local data. '''
#         cmd = "subscription-manager refresh; sleep 10"
#         ret, output = self.runcmd(cmd, "subscription fresh", targetmachine_ip)
#         if ret == 0 and "All local data refreshed" in output:
#             logger.info("Succeeded to refresh all local data %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to refresh all local data %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#     # ========================================================
#     #     2. 'Virt-Who' Test Common Functions
#     # ========================================================
# 
#     def get_env(self, logger):
#         env = {}
#         cmd = "grep '^hostname = subscription.rhn.stage.redhat.com' /etc/rhsm/rhsm.conf"
#         ret, output = self.runcmd(cmd, "check stage config")
#         if "hostname = subscription.rhn.stage.redhat.com" == output:
#             # logger.info("**** Auto Suite Running Against Stage Candlepin ****")
#             Stage = True
#         else:
#             # logger.info("**** Auto Suite Running Against SAM ****")
#             Stage = False
#         cmd = "echo $(python -c \"import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)\" | grep 'releasever' | awk -F\":\" '{print $2}' | sed  -e \"s/^ '//\" -e \"s/'}$//\" -e \"s/',$//\")"
#         ret, output = self.runcmd(cmd, "get_env")
#         if Stage :
#             env["username"] = ee.username_stage
#             env["password"] = ee.password_stage
#         else:
#             if "5Client" in output:
#                 env["username"] = ee.username1s
#                 env["password"] = ee.password1s
#                 env["autosubprod"] = ee.autosubprod1s
#                 env["installedproductname"] = ee.installedproductname1s
#                 env["productid"] = ee.productid1s
#                 env["pid"] = ee.pid1s
#                 env["pkgtoinstall"] = ee.pkgtoinstall1s
#                 env["productrepo"] = ee.productrepo1s
#                 env["betarepo"] = ee.betarepo1s
#             elif "5Server" in output:
#                 env["username"] = ee.username2s
#                 env["password"] = ee.password2s
#                 env["autosubprod"] = ee.autosubprod2s
#                 env["installedproductname"] = ee.installedproductname2s
#                 env["productid"] = ee.productid2s
#                 env["pid"] = ee.pid2s
#                 env["pkgtoinstall"] = ee.pkgtoinstall2s
#                 env["productrepo"] = ee.productrepo2s
#                 env["betarepo"] = ee.betarepo2s
#             elif "5Workstation" in output:
#                 env["username"] = ee.username3s
#                 env["password"] = ee.password3s
#             elif ("6Server" in output) or ("6Client" in output):
#                 env["username"] = ee.username4s
#                 env["password"] = ee.password4s
#                 env["autosubprod"] = ee.autosubprod4s
#             elif "6Workstation" in output:
#                 env["username"] = ee.username5s
#                 env["password"] = ee.password5s
#             elif ("7Server" in output) or ("7Client" in output):
#                 env["username"] = ee.username4s
#                 env["password"] = ee.password4s
#                 env["autosubprod"] = ee.autosubprod4s
#             elif "7Workstation" in output:
#                 env["username"] = ee.username5s
#                 env["password"] = ee.password5s
#             elif "6ComputeNode" in output:
#                 env["username"] = ee.username5s
#                 env["password"] = ee.password5s    
#         return env
# 
#     def above_7_serials(self, logger):
#         cmd = "echo $(python -c \"import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)\" | grep 'releasever' | awk -F\":\" '{print $2}' | sed  -e \"s/^ '//\" -e \"s/'}$//\" -e \"s/',$//\")"
#         ret, output = self.runcmd(cmd, "get rhel version")
#         if output[0:1] >= 7:
#             logger.info("System version is above or equal 7 serials")
#             return True
#         else:
#             logger.info("System version is bellow 7 serials")
#             return False
# 
#     def configure_host(self, samhostname, samhostip, targetmachine_ip=""):
#         ''' configure the host machine. '''
#         if samhostname != None and samhostip != None:
#             # add sam hostip and hostname in /etc/hosts
#             cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
#             ret, output = self.runcmd(cmd, "configure /etc/hosts", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_hg_info(targetmachine_ip)))
#             else:
#                 raise FailException("Failed to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_hg_info(targetmachine_ip)))
#     
#             # config hostname, prefix, port, baseurl and repo_ca_crt by installing candlepin-cert
#             cmd = "rpm -qa | grep candlepin-cert-consumer"
#             ret, output = self.runcmd(cmd, "check whether candlepin-cert-consumer-%s-1.0-1.noarch exist" % samhostname, targetmachine_ip)
#             if ret == 0:
#                 logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
#                 cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
#                 ret, output = self.runcmd(cmd, "remove candlepin-cert-consumer-%s-1.0-1.noarch to re-register system to SAM" % samhostname, targetmachine_ip)
#                 if ret == 0:
#                      logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
#                 else:
#                     raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
#         
#             cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
#             ret, output = self.runcmd(cmd, "install candlepin-cert-consumer..rpm", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
#             else:
#                 raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
#     
#         elif samhostname == "subscription.rhn.stage.redhat.com":
#             # configure /etc/rhsm/rhsm.conf to stage candlepin
#             cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % samhostname
#             ret, output = self.runcmd(cmd, "configure /etc/rhsm/rhsm.conf", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to configure rhsm.conf for stage in %s" % self.get_hg_info(targetmachine_ip))
#             else:
#                 raise FailException("Failed to configure rhsm.conf for stage in %s" % self.get_hg_info(targetmachine_ip))
#     
#         else:
#             raise FailException("Failed to configure the host")
# 
# 
#     def configure_stage_host(self, serverhostname, targetmachine_ip=""):
#         ''' configure the host machine. '''
#         if serverhostname == "subscription.rhn.stage.redhat.com":
#             # configure /etc/rhsm/rhsm.conf to stage candlepin
#             cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % serverhostname
#             ret, output = self.runcmd(cmd, "configure /etc/rhsm/rhsm.conf", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to configure rhsm.conf for stage in %s" % self.get_hg_info(targetmachine_ip))
#             else:
#                 raise FailException("Failed to configure rhsm.conf for stage in %s" % self.get_hg_info(targetmachine_ip))
#     
#         else:
#             raise FailException("Failed to configure stage host")
# 
# 
# # Can't pass in RHEL5.11, will research later
# #    def vw_restart_virtwho(self, targetmachine_ip=""):
# #        ''' Restart the virt-who service. '''
# #        if self.above_7_serials(logger):
# #            cmd = "systemctl restart virt-who.service; sleep 10"
# #            ret, output = self.runcmd(cmd, "systemctl restart virt-who.service", targetmachine_ip)
# #            if ret == 0:
# #                logger.info("Succeeded to restart virt-who service by systemctl.")
# #            else:
# #                raise FailException("Failed to restart virt-who service by systemctl.")
# #    
# #        else:
# #            if targetmachine_ip == "":
# #                subprocess.call("service virt-who restart; sleep 10", shell=True)
# #            else:
# #                cmd = "service virt-who restart; sleep 10"
# #                ret, output = self.runcmd(cmd, "restart virt-who", targetmachine_ip)
# #                if ret == 0:
# #                    logger.info("Succeeded to restart virt-who service.")
# #                else:
# #                    raise FailException("Failed to restart virt-who service.")
# #        
# 
#     def vw_restart_virtwho(self, targetmachine_ip=""):
#         ''' Restart the virt-who service. '''
#         if targetmachine_ip == "":
#             subprocess.call("service virt-who restart; sleep 10", shell=True)
#         else:
#             cmd = "service virt-who restart; sleep 10"
#             ret, output = self.runcmd(cmd, "stop virt-who", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to restart virt-who service.")
#             else:
#                 raise FailException("Failed to restart virt-who service.")
#     
# 
#     def vw_stop_virtwho(self, targetmachine_ip=""):
#         ''' Stop virt-who service. '''
#         cmd = "service virt-who stop; sleep 10"
#         ret, output = self.runcmd(cmd, "stop virt-who", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to stop virt-who service.")
#         else:
#             raise FailException("Failed to stop virt-who service.")
# 
#                 
#     def vw_check_virtwho_status(self, targetmachine_ip=""):
#         ''' Check the virt-who status. '''
#         cmd = "service virt-who status; sleep 10"
#         ret, output = self.runcmd(cmd, "virt-who status", targetmachine_ip)
#         if self.above_7_serials(logger):
#             if ret == 0 and "running" in output:
#                 logger.info("Succeeded to check virt-who is running.")
#             else:
#                 raise FailException("Failed to check virt-who is running.")
#     
#         else:
#             if ret == 0 and "running" in output:
#                 logger.info("Succeeded to check virt-who is running.")
#     
#             else:
#                 raise FailException("Failed to check virt-who is running.")
#     
# 
#     def vw_check_libvirtd_status(self, targetmachine_ip=""):
#         ''' Check the libvirtd status. '''
#         cmd = "service libvirtd status; sleep 10"
#         ret, output = self.runcmd(cmd, "libvirtd status", targetmachine_ip)
#         if self.above_7_serials(logger):
#             if ret == 0 and "running" in output:
#                 logger.info("Succeeded to check libvirtd is running.")
#             else:
#                 raise FailException("Failed to check libvirtd is running.")
#     
#         else:
#             if ret == 0 and "running" in output:
#                 logger.info("Succeeded to check libvirtd is running.")
#     
#             else:
#                 raise FailException("Failed to check libvirtd is running.")
#     
# 
#     def vw_restart_libvirtd(self, targetmachine_ip=""):
#         ''' Restart the libvirtd service on host: service libvirtd restart. '''
#         cmd = "service libvirtd restart; sleep 30"
#         ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
#         if self.above_7_serials(logger):
#             if ret == 0:
#                 logger.info("Succeeded to restart libvirtd service.")
#             else:
#                 raise FailException("Failed to restart libvirtd service.")
#     
#         else:
#             if ret == 0 and "OK" in output:
#                 logger.info("Succeeded to restart libvirtd service.")
#             else:
#                 raise FailException("Failed to restart libvirtd service.")
#     
#                 
#     def vw_restart_vdsm(self, targetmachine_ip=""):
#         ''' Restart the libvirtd service on host: service libvirtd restart. '''
#         cmd = "service vdsmd restart; sleep 30"
#         ret, output = self.runcmd(cmd, "restart vdsmd", targetmachine_ip)
#         if ret == 0 and "OK" in output:
#             logger.info("Succeeded to restart vdsm service.")
#         else:
#             raise FailException("Failed to restart vdsm service.")
# 
# 
#     def vw_get_uuid(self, guestname):
#         ''' get the guest uuid. '''
#         cmd = "virsh domuuid %s" % guestname
#         ret, output = self.runcmd(cmd, "get virsh domuuid")
#         guestuuid = output[:-1]
#         return guestuuid
# 
#     def vw_check_uuid(self, params, guestname, guestuuid="Default", uuidexists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
#         ''' check if the guest uuid is correctly monitored by virt-who. '''
#         if guestname != "" and guestuuid == "Default":
#             guestuuid = self.vw_get_uuid(guestname)
#         rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
#         self.vw_restart_virtwho(targetmachine_ip)
#         cmd = "tail -1 %s " % rhsmlogfile
#         ret, output = self.runcmd(cmd, "check output in rhsm.log")
#         if ret == 0:
#             ''' get guest uuid.list from rhsm.log '''
#             if "Sending list of uuids: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update to updateConsumer: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             else:
#                 raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
#     
# #             # for kvm send uuid list changes
# #             temp_list = []
# #             for item in log_uuid_list:
# #                 if item.has_key("guestId"):
# #                     temp_list.append(item["guestId"])
#             # check guest uuid in log_uuid_list
#             if uuidexists:
#                 if guestname == "":
#                     return len(log_uuid_list) == 0
#                 else:
#                     logger.info("guestuuid %s in log_uuid_list" % guestuuid)
#                     return (guestuuid in log_uuid_list)
#             else:
#                 if guestname == "":
#                     return not len(log_uuid_list) == 0
#                 else:
#                     return not (guestuuid in log_uuid_list)
#         else:
#             raise FailException("Failed to get uuids in rhsm.log")
# 
# 
#     def vw_check_attr(self, params, guestname, guest_status, guest_type, guest_hypertype, guest_state, guestuuid, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
#         ''' check if the guest attributions is correctly monitored by virt-who. '''
#         rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
#         self.vw_restart_virtwho(targetmachine_ip)
#         cmd = "tail -1 %s " % rhsmlogfile
#         ret, output = self.runcmd(cmd, "check output in rhsm.log")
#         if ret == 0:
#             ''' get guest uuid.list from rhsm.log '''
#             if "Sending list of uuids: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update to updateConsumer: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             else:
#                 raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
#     
#             loglist = eval(log_uuid_list)
#             for item in loglist:
#                 if item['guestId'] == guestuuid:
#                     attr_status = item['attributes']['active']
#                     logger.info("guest's active status is %s." % attr_status)
#                     attr_type = item['attributes']['virtWhoType']
#                     logger.info("guest virtwhotype is %s." % attr_type)
#                     attr_hypertype = item['attributes']['hypervisorType']
#                     logger.info("guest hypervisortype is %s." % attr_hypertype)
#                     attr_state = item['state']
#                     logger.info("guest state is %s." % attr_state)
#             if guestname != "" and (guest_status == attr_status) and (guest_type in attr_type) and (guest_hypertype in attr_hypertype) and (guest_state == attr_state):
#                 logger.info("successed to check guest %s attribute" % guestname)
#                 return True
#             else:
#                 raise FailException("Failed to check guest %s attribute" % guestname)
#                 return False
#         else:
#             raise FailException("Failed to get uuids in rhsm.log")
# 
# 
#     def check_virtpid(self, checkpid, checknum, targetmachine_ip=""):
#         cmd = "ls /proc/%s/task/ | wc -l" %checkpid
#         (ret, output) = self.runcmd(cmd, "get virt-who thread num", targetmachine_ip)
#         if ret == 0 and int(output) == checknum:
#             logger.info("Succeeded to check the virt-who thread.")
#         else:
#             raise FailException("Failed to check the virt-who thread.")
# 
#                 
#     def sub_check_bonus(self, productid, targetmachine_ip=""):
#         # List available pools of guest
#         new_available_poollist = self.sub_listavailpools(ee.productid_guest, targetmachine_ip)
#         if new_available_poollist != None:
#             bonus_pool_check = 1
#             for item in range(0, len(new_available_poollist)):
#                 if new_available_poollist[item]["SKU"] == ee.productid_guest and self.check_type_virtual(new_available_poollist[item]) and new_available_poollist[item]["Quantity"] == ee.guestlimit:
#                     logger.info("Succeeded to list bonus pool of product %s" % ee.productname_guest) 
#                     bonus_pool_check = 0
#             if bonus_pool_check == 1:
#     
#         else:
#             raise FailException("Failed to get available pool list from guest.")
# 
# 
#     def check_bonus_existance(self, SKU_id, targetmachine_ip="", existance=True):
#         new_available_poollist = self.sub_listavailpools(SKU_id, targetmachine_ip)
#         if new_available_poollist != None:
#             if existance:
#                 bonus_pool_check = 1
#                 for item in range(0, len(new_available_poollist)):
#                     if new_available_poollist[item]["SKU"] == SKU_id and self.check_type_virtual(new_available_poollist[item]):
#                         logger.info("Succeeded to list bonus pool of product %s" % SKU_id) 
#                         bonus_pool_check = 0
#             else:
#                 bonus_pool_check = 0
#                 for item in range(0, len(new_available_poollist)):
#                     if new_available_poollist[item]["SKU"] == SKU_id and self.check_type_virtual(new_available_poollist[item]):
#                         logger.info("Unexpected to list bonus pool of product %s" % SKU_id) 
#                         bonus_pool_check = 1
#             if bonus_pool_check == 1:
#     
#         else:
#             raise FailException("Failed to get available pool list from guest.")
# 
# 
#     def check_datacenter_bonus_existance(self, subscription_name, targetmachine_ip="", existance=True):
#         new_available_poollist = self.sub_datacenter_listavailpools(subscription_name, targetmachine_ip)
#         if new_available_poollist != None:
#             if existance:
#                 bonus_pool_check = 1
#                 for item in range(0, len(new_available_poollist)):
#                     if new_available_poollist[item]["SubscriptionName"] == subscription_name and self.check_type_virtual(new_available_poollist[item]):
#                         logger.info("Succeeded to list bonus pool of product %s" % subscription_name) 
#                         bonus_pool_check = 0
#             else:
#                 bonus_pool_check = 0
#                 for item in range(0, len(new_available_poollist)):
#                     if new_available_poollist[item]["SubscriptionName"] == subscription_name and self.check_type_virtual(new_available_poollist[item]):
#                         raise FailException("Unexpected to list bonus pool of product %s" % subscription_name) 
#                         bonus_pool_check = 1
#             if bonus_pool_check == 1:
#     
#         else:
#             raise FailException("Failed to get available pool list from guest.")
# 
# 
#     def check_bonus_attribute(self, subscription_name, attribute_key, attribute_value, targetmachine_ip=""):
#         new_available_poollist = self.sub_datacenter_listavailpools(subscription_name, targetmachine_ip)
#         if new_available_poollist != None:
#             check_result = 1
#             for item in range(0, len(new_available_poollist)):
#                 if attribute_key == "Available":
#                     if "Quantity" in new_available_poollist[item]:
#                         attribute_key = "Quantity"
#                 if new_available_poollist[item]["SubscriptionName"] == subscription_name and self.check_type_virtual(new_available_poollist[item]):
#                     if new_available_poollist[item][attribute_key] == attribute_value:
#                         logger.info("Succeeded to check_bonus_attribute %s is: %s" % (attribute_key, attribute_value))
#                         check_result = 0
#             if check_result == 1:
#     
#         else:
#             raise FailException("Failed to get available pool list from guest.")
# 
# 
#     def setup_custom_facts(self, facts_key, facts_value, targetmachine_ip=""):
#         ''' setup_custom_facts '''
#         cmd = "echo '{\"" + facts_key + "\":\"" + facts_value + "\"}' > /etc/rhsm/facts/custom.facts"
#         ret, output = self.runcmd(cmd, "create custom.facts", targetmachine_ip)
#         if ret == 0 :
#             logger.info("Succeeded to create custom.facts %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to create custom.facts %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#         cmd = "subscription-manager facts --update"
#         ret, output = self.runcmd(cmd, "update subscription facts", targetmachine_ip)
#         if ret == 0 and "Successfully updated the system facts" in output:
#             logger.info("Succeeded to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#     def restore_facts(self, targetmachine_ip=""):
#         ''' setup_custom_facts '''
#         cmd = "rm -f /etc/rhsm/facts/custom.facts"
#         ret, output = self.runcmd(cmd, "remove custom.facts", targetmachine_ip)
#         if ret == 0 :
#             logger.info("Succeeded to remove custom.facts %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to remove custom.facts %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#         cmd = "subscription-manager facts --update"
#         ret, output = self.runcmd(cmd, "update subscription facts", targetmachine_ip)
#         if ret == 0 and "Successfully updated the system facts" in output:
#             logger.info("Succeeded to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#     def vw_define_all_guests(self, testtype, params, targetmachine_ip=""):
#         if testtype == "kvm":
#             for guestname in ee().get_all_guests_list(ee.imagepath_kvm):
#                 params["guesttype"] = "kvm"
#                 params["fullimagepath"] = os.path.join(ee.imagepath_kvm, guestname)
#                 self.vw_define_guest(params, guestname)
#         elif testtype == "xen":
#             for guestname in ee().get_all_guests_list(ee.imagepath_xen_pv):
#                 params["guesttype"] = "xenpv"
#                 params["fullimagepath"] = os.path.join(ee.imagepath_xen_pv, guestname)
#                 self.vw_define_guest(params, guestname)
#             for guestname in ee().get_all_guests_list(ee.imagepath_xen_fv):
#                 params["guesttype"] = "xenfv"
#                 params["fullimagepath"] = os.path.join(ee.imagepath_xen_fv, guestname)
#                 self.vw_define_guest(params, guestname)
# 
#     def vw_define_guest(self, params, guestname, targetmachine_ip=""):
#         ''' Define a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if not guestname + " " in output:
#             params["guestname"] = guestname
#             self.set_guestpath_guesttype(guestname, params)
#             params["ifacetype"] = "bridge"
#             params["source"] = "switch"
#             if define.define(params) == 0:
#                 logger.info("Succeeded to define the guest '%s' in host machine.\n" % guestname)
#             else:
#                 raise FailException("Failed to define the guest '%s' in host machine.\n" % guestname)
#             ret, output = self.runcmd(cmd, "list all guest", targetmachine_ip)
# 
#     def vw_force_define_guest(self, params, guestname, targetmachine_ip=""):
#         ''' Define a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", True)
#         if output is not "":
#             params["guestname"] = guestname
#             self.set_guestpath_guesttype(guestname, params)
#             params["ifacetype"] = "bridge"
#             params["source"] = "switch"
#             if define.define(params) == 0:
#                 logger.info("Succeeded to define the guest '%s' in host machine.\n" % guestname)
#             else:
#                 raise FailException("Failed to define the guest '%s' in host machine.\n" % guestname)
#             ret, output = self.runcmd(cmd, "list all guest", targetmachine_ip)
# 
#     def set_guestpath_guesttype(self, guestname, params):
#         ''' set fullimagepath and guesttype for define guest '''
#         if "PV" in guestname:
#             params["guesttype"] = "xenpv"
#             params["fullimagepath"] = os.path.join(ee.imagepath_xen_pv, guestname)
#         elif "FV" in guestname:
#             params["guesttype"] = "xenfv"
#             params["fullimagepath"] = os.path.join(ee.imagepath_xen_fv, guestname)
#         else:
#             params["guesttype"] = "kvm"
#             params["fullimagepath"] = os.path.join(ee.imagepath_kvm, guestname)
# 
#     def vw_start_guest(self, params, guestname):
#         ''' Start a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if guestname + " " in output:
#             params["guestname"] = guestname
#             if start.start(params) == 0:
#                 logger.info("Succeeded to start the guest '%s' in host machine." % guestname)
#                 time.sleep(20)
#             else:
#                 raise FailException("Failed to start the guest '%s' in host machine." % guestname)
#                 self.vw_destroy_guest(params, guestname)
#     
#         else:
#             raise FailException("The guest '%s' is not in host machine, can not do start." % guestname)
# 
# 
#     def vw_pause_guest(self, params, guestname):
#         ''' Pause a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if guestname + " " in output:
#             params["guestname"] = guestname
#             if suspend.suspend(params) == 0:
#                 logger.info("Succeeded to pause the guest '%s' in host machine." % guestname)
#             else:
#                 raise FailException("Failed to pause the guest '%s' in host machine." % guestname)
#                 self.vw_destroy_guest(params, guestname)
#     
#         else:
#             raise FailException("The guest '%s' is not in host machine, can not do pause." % guestname)
# 
# 
#     def vw_resume_guest(self, params, guestname):
#         ''' Resume a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if guestname + " " in output:
#             params["guestname"] = guestname
#             if resume.resume(params) == 0:
#                 logger.info("Succeeded to resume the guest '%s' in host machine." % guestname)
#             else:
#                 raise FailException("Failed to resume the guest '%s' in host machine." % guestname)
#                 self.vw_destroy_guest(params, guestname)
#     
#         else:
#             raise FailException("The guest '%s' is not in host machine, can not do resume." % guestname)
# 
# 
#     def vw_shutdown_guest(self, params, guestname):
#         ''' Shutdown a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if guestname + " " in output:
#             params["guestname"] = guestname
#             if shutdown.shutdown(params) == 0:
#                 logger.info("Succeeded to shutdown the guest '%s' in host machine." % guestname)
#             else:
#                 logger.info("shutdown guest is failed, try to do destroy to the guest '%s'" % guestname)
#                 self.vw_destroy_guest(params, guestname)
#     
#         else:
#             raise FailException("The guest '%s' is not in host machine, can not do shutdown." % guestname)
# 
# 
#     def vw_destroy_guest(self, params, guestname):
#         ''' Destory a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if guestname + " " in output:
#             params["guestname"] = guestname
#             if destroy.destroy(params) == 0:
#                 logger.info("Succeeded to destroy the guest '%s' in host machine." % guestname)
#                 ret, output = self.runcmd(cmd, "list all guest after destory guest %s." % guestname)
#             else:
#                 raise FailException("Failed to destroy the guest '%s' in host machine." % guestname)
#     
#         else:
#             raise FailException("The guest '%s' is not in host machine, can not do destroy." % guestname)
# 
# 
#     def vw_undefine_guest(self, params, guestname):
#         ''' Undefine a guest in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if guestname + " " in output:
#             params["guestname"] = guestname
#             if undefine.undefine(params) == 0:
#                 logger.info("Succeeded to undefine the guest '%s' in host machine." % guestname)
#                 ret, output = self.runcmd(cmd, "list all guest after undefine guest.")
#             else:
#                 raise FailException("Failed to undefine the guest '%s' in host machine." % guestname)
#     
#         else:
#             raise FailException("Failed to undefine the guest '%s' which is not defined in host machine." % guestname)
# 
# 
#     def vw_undefine_all_guests(self, params):
#         ''' Undefine all guests in host machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         # get guest list by parse output
#         datalines = output.splitlines()
#         guest_list = []
#         for line in datalines:
#             if " -     " in line:
#                 guest_list.append(line.split(" ")[6])
#         for item in guest_list:
#             self.vw_undefine_guest(params, item)
#         ret, output = self.runcmd(cmd, "list all guest after undefine all guests.")
# #         srcuri = utils().get_uri("127.0.0.1")
# #         conn = connectAPI.ConnectAPI()
# #         src = conn.open(srcuri)
# #         srcdom = DomainAPI(src)
# #         guest_names = srcdom.get_list()
# #         guest_names += srcdom.get_defined_list()
# #         logger.info("All defined guests [total: %d]: " % len(guest_names) + ", ".join(guest_names))
# #         if len(guest_names) != 0:
# #             for guestname in guest_names:
# #                 if (guestname in ee.guestnamekcol) or (guestname in ee.guestnamepcol) or (guestname in ee.guestnamefcol):
# #                     gueststate = srcdom.get_state(guestname)
# #                     if  gueststate == 'running' or gueststate == 'blocked' or gueststate == 'paused':
# #                         if self.vw_destroy_guest(params, guestname):
# #                             src.close()
# #                             logger.info("close local hypervisor connection")
# #                             raise FailException("Failed to destroy the guest '%s' when try to undefine all the guests." % guestname)
# #             
# #                     if self.vw_undefine_guest(params, guestname):
# #                         src.close()
# #                         logger.info("close local hypervisor connection")
# #             
# #                 else:
# #                     logger.info("The guest '%s' is not in test scope so not handled when try to undefine all the guests." % guestname)
# #
# #             logger.info("Succeeded to undefine all the %d guests in host machine: %s" % (len(guest_names), ", ".join(guest_names)))
# #         else:
# #             logger.info("There is no any guest to undefine in host machine, so no action happens to undefine all guests.")
# #         
# #         src.close()
# #         logger.info("close local hypervisor connection")    
# #         return 0
# 
#     def vw_migrate_guest(self, params, guestname, targetmachine_ip):
#         ''' Migrate a guest from source machine to target machine. '''
#         cmd = "virsh list --all"
#         ret, output = self.runcmd(cmd, "list all guest", "", False)
#         if guestname + " " in output:
#             params['transport'] = "ssh"
#             params['target_machine'] = targetmachine_ip
#             params['username'] = "root"
#             if "redhat.com" in targetmachine_ip:
#                 # run in beaker
#                 params['password'] = "xxoo2014"
#             else:
#                 params['password'] = "redhat"
#             params["guestname"] = guestname
#             params['flags'] = "live"
#             '''
#             params['poststate']="running"
#             params['presrcconfig']="false"
#             params['postsrcconfig']="false"
#             params['predstconfig']="false"
#             params['postdstconfig']="true"
#             '''
#             if migrate.migrate(params) == 0:
#                 logger.info("Succeeded to migrate the guest '%s'." % guestname)
#                 ret, output = self.runcmd(cmd, "list all guest after migrate guest %s" % guestname)
#             else:
#                 raise FailException("Failed to migrate the guest '%s'." % guestname)
#     
#         else:
#             raise FailException("The guest '%s' is not in host machine, can not do migrate." % guestname)
# 
#         self.vw_undefine_guest(params, guestname)
# 
#     def vw_migrate_guest_by_cmd(self, guestname, migratetargetmachine_ip, targetmachine_ip=""):
#         ''' migrate a guest from source machine to target machine. '''
#         uri = utils().get_uri(migratetargetmachine_ip)
#         cmd = "virsh migrate --live %s %s --undefinesource" % (guestname, uri)
#         ret, output = self.runcmd(cmd, "migrate the guest in host 2", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to migrate the guest '%s'." % guestname)
#         else:
#             raise FailException("Failed to migrate the guest '%s'." % guestname)
# 
# 
#     def vw_undefine_guest_by_cmd(self, guestname, targetmachine_ip=""):
#         ''' Undefine a guest in host machine. '''
#         cmd = "virsh undefine %s" % guestname
#         ret, output = self.runcmd(cmd, "undefine guest in %s" % targetmachine_ip, targetmachine_ip)
#         if "Domain %s has been undefined" % guestname in output:
#             logger.info("Succeeded to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))
#         else:
#             raise FailException("Failed to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))
# 
#     #========================================================
#     #     3. Common Setup Functions
#     #========================================================
# 
#     def set_cpu_socket(self, cpu_socket=1, targetmachine_ip=""):
#         ''' To set cpu socket in configure file /etc/rhsm/facts/custom.facts. '''
#         cmd = """echo \"{\\"cpu.cpu_socket(s)\\":%s}\">/etc/rhsm/facts/custom.facts""" % (cpu_socket)
#         ret, output = self.runcmd(cmd, "set cpu socket", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to setting cpu socket.")
#         else:
#             raise FailException("Failed to setting cpu socket.")
# 
# 
#     def copy_images(self, testtype, mount_point, image_machine_imagepath, imagepath):
#         ''' copy the images from the image source machine. '''
#         if not os.path.exists(imagepath):
#             os.makedirs(imagepath)
#             logger.info("Created the dir '%s'." % imagepath)
# 
#         tmpimagepath = "/tmp/entimages" + time.strftime('%Y%m%d%H%M%S')
#         os.makedirs(tmpimagepath)
#         logger.info("Dir '%s' has been created for copy guest image to host." % tmpimagepath)
# 
#         cmd = "mount -r %s %s" % (mount_point, tmpimagepath)
#         ret, output = self.runcmd(cmd, "mount images in host")
#         if ret == 0:
#             logger.info("Succeeded to mount images machine %s." % mount_point)
#         else:
#             raise FailException("Failed to mount images machine %s." % mount_point)
# 
#         logger.info("Begin to copy guest images...")
# 
#         imagesrcpath = os.path.join(tmpimagepath, os.path.join(image_machine_imagepath, testtype))
#         imagetgtpath = imagepath
#         cmd = "cp -rf %s %s" % (imagesrcpath, imagetgtpath)
#         ret, output = self.runcmd(cmd, "copy images")
#         if ret == 0:
#             logger.info("Succeeded to copy guest images to host machine.")
#         else:
#             raise FailException("Failed to copy guest images to host machine.")
# 
# 
#         if os.path.ismount(tmpimagepath):
#             cmd = "umount -f %s" % (tmpimagepath)
#             ret, output = self.runcmd(cmd, "unmount images in host")
#             if ret == 0:
#                 logger.info("Succeeded to unmount images machine %s." % mount_point)
#             else:
#                 raise FailException("Failed to unmount images machine %s." % mount_point)
# 
#         os.removedirs(tmpimagepath)
#         logger.info("Removed the dir '%s'." % tmpimagepath)
# 

# 
#     def export_dir_as_nfs(self, nfs_dir, targetmachine_ip=""):
#         ''' export a dir as nfs '''
#         cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (nfs_dir.replace('/', '\/'), nfs_dir)
#         ret, output = self.runcmd(cmd, "set exporting destination dir", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % nfs_dir)
#         else:
#             raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % nfs_dir)
# 
#         cmd = "service nfs restart; sleep 10"
#         ret, output = self.runcmd(cmd, "restarting nfs service", targetmachine_ip)
#         if ret == 0 :
#             logger.info("Succeeded to restart service nfs.")
#         else:
#             raise FailException("Failed to restart service nfs.")
# 
#         cmd = "rpc.mountd"
#         ret, output = self.runcmd(cmd, "rpc.mountd", targetmachine_ip)
#         cmd = "showmount -e 127.0.0.1"
#         ret, output = self.runcmd(cmd, "showmount", targetmachine_ip)
#         if ret == 0 and (nfs_dir in output):
#             logger.info("Succeeded to export dir '%s' as nfs." % nfs_dir)
#         else:
#             raise FailException("Failed to export dir '%s' as nfs." % nfs_dir)
# 
# 
#     def mount_images_in_sourcemachine(self, imagenfspath, imagepath):
#         ''' mount the images of the image source machine in the source machine. '''
#         # create image path in source machine
#         cmd = "test -d %s" % (imagepath)
#         ret, output = self.runcmd(cmd, "check images path in source machine")
#         if ret != 0:
#             cmd = "mkdir -p %s" % (imagepath)
#             ret, output = self.runcmd(cmd, "create image path in the source machine")
#             if ret == 0 or "/home/ENT_TEST_MEDIUM/images is busy or already mounted" in output:
#                 logger.info("Succeeded to create imagepath in the source machine.")
#             else:
#                 raise FailException("Failed to create imagepath in the source machine.")
#     
# 
#         # mount image path of source machine into just created image path in target machine
#         sourcemachine_ip = utils().get_ip_address("switch")
#         cmd = "mount %s:%s %s" % (sourcemachine_ip, imagenfspath, imagepath)
#         ret, output = self.runcmd(cmd, "mount nfs images in host machine")
#         if ret == 0 or "is busy or already mounted" in output:
#             logger.info("Succeeded to mount nfs images in host machine.")
#         else:
#             raise FailException("Failed to mount nfs images in host machine.")
# 
# 
#     def update_vw_configure(self, background=1, debug=1, targetmachine_ip=""):
#         ''' update virt-who configure file /etc/sysconfig/virt-who. '''
#         # cmd = "sed -i -e 's/VIRTWHO_BACKGROUND=.*/VIRTWHO_BACKGROUND=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' /etc/sysconfig/virt-who" % (background, debug)
#         # VIRTWHO_BACKGROUND removed from configure file
#         cmd = "sed -i -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' /etc/sysconfig/virt-who" % (debug)
#         ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to update virt-who configure file.")
#         else:
#             raise FailException("Failed to update virt-who configure file.")
# 
# 
#     def update_esx_vw_configure(self, esx_owner, esx_env, esx_server, esx_username, esx_password, background=1, debug=1):
#         ''' update virt-who configure file /etc/sysconfig/virt-who. '''
#         # cmd = "sed -i -e 's/VIRTWHO_BACKGROUND=.*/VIRTWHO_BACKGROUND=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/#VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/#VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/#VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/#VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/#VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (background, debug, esx_owner, esx_env, esx_server, esx_username, esx_password)
#         cmd = "sed -i -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/#VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/#VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/#VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/#VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/#VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, esx_owner, esx_env, esx_server, esx_username, esx_password)
#         ret, output = self.runcmd(cmd, "updating virt-who configure file")
#         if ret == 0:
#             logger.info("Succeeded to update virt-who configure file.")
#         else:
#             raise FailException("Failed to update virt-who configure file.")
# 
# 
#     def __parse_avail_hosts(self, output):
#         datalines = output.splitlines()
#         pool_list = []
#         data_segs = []
#         segs = []
#         for line in datalines:
#             if "id:" in line:
#                 segs.append(line)
#             elif segs:
#                 segs.append(line)
#             if "name:" in line:
#                 data_segs.append(segs)
#                 segs = []
# 
#         # handle item with multi rows
#         for seg in data_segs:
#             length = len(seg)
#             for index in range(0, length):
#                 if ":" not in seg[index]:
#                     seg[index - 1] = seg[index - 1] + " " + seg[index].strip()
#             for item in seg:
#                 if ":" not in item:
#                     seg.remove(item)
# 
#         # parse detail information for each pool
#         for seg in data_segs:
#             pool_dict = {}
#             for item in seg:
#                 keyitem = item.split(":")[0].replace(" ", "")
#                 valueitem = item.split(":")[1].strip()
#                 pool_dict[keyitem] = valueitem
#             pool_list.append(pool_dict)
#         return pool_list
# 
#     def sub_listavailhosts(self, hostname, targetmachine_ip=""):
#         ''' List available pools.'''
#         self.enter_rhevm_shell(targetmachine_ip)
#         cmd = "list hosts"
#         ret, output = self.runcmd(cmd, "list all hosts in rhevm")
#         if ret == 0:
#             if "name" in output:
#                 if id in output:
#                     logger.info("Succeeded to list the hosts %s." % self.get_hg_info(targetmachine_ip))
#                     pool_list = self.__parse_avail_hosts(output)
#                     return pool_list
#                 else:
#                     raise FailException("Failed to list the hosts %s." % self.get_hg_info(targetmachine_ip))
#         
#             else:
#                 raise FailException("Failed to list the hosts %s. - There is no hosts to list!" % self.get_hg_info(targetmachine_ip))
#     
#         else:
#             raise FailException("Failed to list hosts %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#     def kvm_wget_xml_file(self, targetmachine_ip=""):
#         ''' wget xml for define guest: virsh define kvm_auto_guest.xml.'''
#         cmd = "wget -P /tmp/ http://10.66.100.116/projects/sam-virtwho/kvm_auto_guest.xml"
#         ret, output = self.runcmd(cmd, "wget kvm xml file", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to wget xml img file")
#         else:
#             raise FailException("Failed to wget xml img file")
# 
# 
#     def kvm_create_dummy_guest(self, guest_name, destination_ip=""):
#         ''' create dummy guest in kvm '''
#         cmd = "sed -i -e 's/kvm_auto_guest_[0-9]*/%s/g' /tmp/kvm_auto_guest.xml" % guest_name
#         ret, output = self.runcmd(cmd, "Set kvm auto guest name to %s" % guest_name, destination_ip)
#         # if ret == 0:
#         #     logger.info("Succeeded to set kvm auto guest name %s" % guest_name)
#         # else:
#         #     raise FailException("Failed to set kvm auto guest name %s" % guest_name)
#         #     self.SET_RESULT(1)
#         cmd = "virsh define /tmp/kvm_auto_guest.xml"
#         ret, output = self.runcmd(cmd, "define kvm auto guest: %s" % guest_name, destination_ip)
#         if ret == 0:
#             logger.info("Succeeded to define kvm auto guest: %s" % guest_name)
#         else:
#             raise FailException("Failed to define kvm auto guest: %s" % guest_name)
# 
# 
#     def kvm_get_guest_uuid(self, guest_name, destination_ip=""):
#         ''' kvm_get_guest_uuid '''
#         cmd = "virsh domuuid %s" % guest_name
#         ret, output = self.runcmd(cmd, "get kvm auto guest uuid: %s" % guest_name, destination_ip)
#         if ret == 0:
#             logger.info("Succeeded to get kvm auto guest uuid: %s" % guest_name)
#             return output.strip()
#         else:
#             raise FailException("Failed to get kvm auto guest uuid: %s" % guest_name)
# 
# 
#     def kvm_remove_guest(self, guest_name, destination_ip=""):
#         ''' kvm_remove_guest '''
#         cmd = "virsh undefine %s" % guest_name
#         ret, output = self.runcmd(cmd, "remove kvm auto guest: %s" % guest_name, destination_ip)
#         time.sleep(1)
#         if ret == 0:
#             logger.info("Succeeded to remove kvm auto guest: %s" % guest_name)
#             return output.strip()
#         else:
#             raise FailException("Failed to remove kvm auto guest: %s" % guest_name)
# 
# 
#     #========================================================
#     #     4. Migration Functions
#     #========================================================
# 
#     def mount_images_in_targetmachine(self, targetmachine_ip, imagenfspath, imagepath):
#         ''' mount the images of the image source machine in the target machine. '''
#         cmd = "test -d %s" % (imagepath)
#         ret, output = self.runcmd(cmd, "check images dir exist", targetmachine_ip)
#         if ret == 1:
#             cmd = "mkdir -p %s" % (imagepath)
#             ret, output = self.runcmd(cmd, "create image path in the target machine", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to create imagepath in the target machine.")
#             else:
#                 raise FailException("Failed to create imagepath in the target machine.")
#     
#         # mount image path of source machine into just created image path in target machine
#         sourcemachine_ip = utils().get_ip_address("switch")
#         cmd = "mount %s:%s %s" % (sourcemachine_ip, imagenfspath, imagepath)
#         ret, output = self.runcmd(cmd, "mount images in the target machine", targetmachine_ip)
#         if ret == 0 or "is busy or already mounted" in output:
#             logger.info("Succeeded to mount images in the target machine.")
#         else:
#             raise FailException("Failed to mount images in the target machine.")
# 
# 
#     def mount_rhsmlog_of_targetmachine(self, targetmachine_ip, rhsmlog_for_targetmachine):
#         ''' mount the rhsm log of the target machine into source machine. '''
#         # create the dir rhsmlog_for_targetmachine
#         # if not os.path.exists(rhsmlog_for_targetmachine):
#         #     os.makedirs(rhsmlog_for_targetmachine)
#         #     logger.info("Created the dir '%s'." % rhsmlog_for_targetmachine)
#         cmd = "test -d %s" % (rhsmlog_for_targetmachine)
#         ret, output = self.runcmd(cmd, "check rhsmlog nfs dir exist")
#         if ret != 0:
#             cmd = "mkdir -p %s" % (rhsmlog_for_targetmachine)
#             ret, output = self.runcmd(cmd, "create rhsmlog nfs dir in source machine")
#             if ret == 0:
#                 logger.info("Succeeded to create rhsmlog nfs dir.")
#             else:
#                 raise FailException("Failed to create rhsmlog nfs dir.")
#     
#         self.export_dir_as_nfs("/var/log/rhsm", targetmachine_ip)
#         if os.path.ismount(rhsmlog_for_targetmachine):
#             logger.info("The rhsm log of target machine has already been mounted in '%s'." % rhsmlog_for_targetmachine)
#         else:
#             # mount the rhsm log of target machine into the dir rhsmlog_for_targetmachine
#             cmd = "mount -r %s:%s %s" % (targetmachine_ip, "/var/log/rhsm/", rhsmlog_for_targetmachine)
#             ret, output = self.runcmd(cmd, "mount the rhsm log dir of target machine")
#             if ret == 0:
#                 logger.info("Succeeded to mount the rhsm log dir of target machine.")
#             else:
#                 raise FailException("Failed to mount the rhsm log dir of target machine.")
#     
# 
#     def update_hosts_file(self, targetmachine_ip, targetmachine_hostname):
#         ''' update /etc/hosts file with the host name/ip and migration destination host name/ip. '''
#         # (1)add target machine hostip and hostname in /etc/hosts of source machine
#         cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (targetmachine_ip, targetmachine_ip, targetmachine_hostname)
#         logger.info(cmd)
#         ret, output = self.runcmd(cmd, "adding hostip hostname to /etc/hosts of source machine")
#         if ret == 0:
#             logger.info("Succeeded to add %s %s to /etc/hosts of source machine." % (targetmachine_ip, targetmachine_hostname))
#         else:
#             raise FailException("Failed to add %s %s to /etc/hosts of source machine." % (targetmachine_ip, targetmachine_hostname))
# 
#         # (2)add source machine hostip and hostname in /etc/hosts of target machine
#         sourcemachine_ip = utils().get_ip_address("switch")
#         sourcemachine_hostname = utils().get_local_hostname()
#         cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (sourcemachine_ip, sourcemachine_ip, sourcemachine_hostname)
#         ret, output = self.runcmd(cmd, "adding hostip hostname to /etc/hosts of target machine", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add hostip %s and hostname %s in /etc/hosts of target machine." % (sourcemachine_ip, sourcemachine_hostname))
#         else:
#             raise FailException("Failed to add hostip %s and hostname %s in /etc/hosts of target machine." % (sourcemachine_ip, sourcemachine_hostname))
# 
# 
#     def stop_firewall(self, targetmachine_ip=""):
#         ''' Stop iptables service and setenforce as 0. '''
#         # stop iptables service
#         cmd = "service iptables stop; sleep 20"
#         ret, output = self.runcmd(cmd, "Stop iptables service", targetmachine_ip)
#         cmd = "service iptables status; sleep 10"
#         ret, output = self.runcmd(cmd, "Chech iptables service status", targetmachine_ip)
#         if ("Firewall is stopped" in output) or ("Firewall is not running" in output) or ("Active: inactive" in output):
#             logger.info("Succeeded to stop iptables service.")
#         else:
#             raise FailException("Failed to stop iptables service.")
# 
#         # setenforce as 0
#         cmd = "setenforce 0"
#         ret, output = self.runcmd(cmd, "Set setenforce 0", targetmachine_ip)
#         cmd = "getenforce"
#         ret, output = self.runcmd(cmd, "Get setenforce 0", targetmachine_ip)
#         if ret == 0 and "Permissive" in output:
#             logger.info("Succeeded to setenforce as 0.")
#         else:
#             raise FailException("Failed to setenforce as 0.")
# 
# 
#     def update_xen_configure(self, targetmachine_ip=""):
#         ''' update xen configuration file /etc/xen/xend-config.sxp for migration to 
#             make sure contain necessary config options, and then restart service xend.
#         '''
#         # (1)update xen configuration file /etc/xen/xend-config.sxp
#         expr1 = "'s/#(xend-relocation-server no)/(xend-relocation-server yes)/'"
#         expr2 = "'s/#(xend-relocation-port 8002)/(xend-relocation-port 8002)/'"
#         expr3 = "\"s/#(xend-relocation-address '')/(xend-relocation-address '')/\""
#         expr4 = "\"s/#(xend-relocation-hosts-allow '')/(xend-relocation-hosts-allow '')/\""
#         cmd = "sed  -i -e %s -e %s -e %s -e %s /etc/xen/xend-config.sxp" % (expr1, expr2, expr3, expr4)
#         if targetmachine_ip == "":
#             (ret, output) = commands.getstatusoutput(cmd)
#         else:
#             (ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "redhat", cmd)
#         logger.info(" [command] of updating xen configuration file /etc/xen/xend-config.sxp: \n%s" % cmd)
#         logger.info(" [result ] of updating xen configuration file /etc/xen/xend-config.sxp: %s" % str(ret))
#         logger.info(" [output ] of updating xen configuration file /etc/xen/xend-config.sxp: \n%s" % str(output))
#         if ret:
#             raise FailException("Failed to updating xen configuration file /etc/xen/xend-config.sxp.")
# 
#         else:
#             logger.info("Succeeded to updating xen configuration file /etc/xen/xend-config.sxp.")
#             
#         # (2)restart service xend.
#         cmd = "service xend restart; sleep 10"
#         if targetmachine_ip == "":
#             (ret, output) = commands.getstatusoutput(cmd)
#         else:
#             (ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "redhat", cmd)
#         time.sleep(3)  # wait some time for service xend restart
#         logger.info(" [command] of restart xend service: %s" % cmd)
#         logger.info(" [result ] of restart xend service: %s" % str(ret))
#         logger.info(" [output ] of restart xend service: \n%s" % str(output))
#         if ret:
#             raise FailException("Failed to restart xend service.")
# 
#         else:
#             logger.info("Succeeded to restart xend service.")
#             return 0
# 
#     def unmount_imagepath_in_sourcemachine(self, imagepath):
#         ''' unmount the image path in the source machine. '''
#         cmd = "mount"
#         ret, output = self.runcmd(cmd, "showing mount point in source machine")
#         if "on %s type nfs" % (imagepath) in output:
#             cmd = "umount -f %s" % (imagepath)
#             ret, output = self.runcmd(cmd, "unmount the image path in source machine")
#             if ret == 0:
#                 logger.info("Succeeded to unmount the image path in source machine.")
#             else:
#                 raise FailException("Failed to unmount the image path in source machine.")
#     
#         else:
#             logger.info("The image path dir is not mounted in source machine.")
# 
#     def unmount_imagepath_in_targetmachine(self, imagepath, targetmachine_ip):
#         ''' unmount the image path in the target machine. '''
#         cmd = "mount"
#         ret, output = self.runcmd(cmd, "showing mount point in target machine", targetmachine_ip)
#         if "on %s type nfs" % (imagepath) in output:
#             cmd = "umount -f %s" % (imagepath)
#             ret, output = self.runcmd(cmd, "unmount the image path in target machine", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to unmount the image path in target machine.")
#             else:
#                 raise FailException("Failed to unmount the image path in target machine.")
#     
#         else:
#             logger.info("The image path dir is not mounted in target machine.")
# 
#     def unmount_rhsmlog_of_targetmachine(self, rhsmlog_for_targetmachine):
#         ''' unmount the rhsm log of the target machine. '''
#         # unmount and remove the dir rhsmlog_for_targetmachine
#         if os.path.ismount(rhsmlog_for_targetmachine):
#             cmd = "umount -f %s" % (rhsmlog_for_targetmachine)
#             ret, output = self.runcmd(cmd, "unmount the rhsm log dir of target machine")
#             if ret == 0:
#                 logger.info("Succeeded to unmount the rhsm log dir of target machine.")
#                 # remove the dir rhsmlog_for_targetmachine
#                 os.removedirs(rhsmlog_for_targetmachine)
#                 logger.info("Removed the dir '%s'." % rhsmlog_for_targetmachine)
#             else:
#                 raise FailException("Failed to unmount the rhsm log dir of target machine.")
#     
# 
#     #========================================================
#     #     4. ESX Functions
#     #========================================================
#     def esx_add_guest(self, guest_name, destination_ip):
#         ''' add guest to esx host '''
#         cmd = "vim-cmd solo/register /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         ret, output = self.runcmd_esx(cmd, "add guest '%s' to ESX '%s'" % (guest_name, destination_ip), destination_ip)
#         if ret == 0:
#             # need to wait 30 s for add sucess
#             time.sleep(60)
#             logger.info("Succeeded to add guest '%s' to ESX host" % guest_name)
#         else:
#             if "AlreadyExists" in output:
#                 logger.info("Guest '%s' already exist in ESX host" % guest_name)
#             else:
#                 raise FailException("Failed to add guest '%s' to ESX host" % guest_name)
#     
# 
#     def esx_create_dummy_guest(self, guest_name, destination_ip):
#         ''' create dummy guest in esx '''
#         cmd = "vim-cmd vmsvc/createdummyvm %s /vmfs/volumes/datastore*/" % guest_name
#         ret, output = self.runcmd_esx(cmd, "add guest '%s' to ESX '%s'" % (guest_name, destination_ip), destination_ip)
#         if ret == 0:
#             # need to wait 30 s for add sucess
#             time.sleep(60)
#             logger.info("Succeeded to add guest '%s' to ESX host" % guest_name)
#         else:
#             if "AlreadyExists" in output:
#                 logger.info("Guest '%s' already exist in ESX host" % guest_name)
#             else:
#                 raise FailException("Failed to add guest '%s' to ESX host" % guest_name)
#     
# 
#     def esx_service_restart(self, destination_ip):
#         ''' restart esx service '''
#         cmd = "/etc/init.d/hostd restart; /etc/init.d/vpxa restart"
#         ret, output = self.runcmd_esx(cmd, "restart hostd and vpxa service", destination_ip)
#         if ret == 0:
#             logger.info("Succeeded to restart hostd and vpxa service")
#         else:
#             raise FailException("Failed to restart hostd and vpxa service")
# 
#         time.sleep(120)
# 

#     def esx_check_system_reboot(self, target_ip):
#         time.sleep(120)
#         cycle_count = 0
#         while True:
#             # wait max time 10 minutes
#             max_cycle = 60
#             cycle_count = cycle_count + 1
#             cmd = "ping -c 5 %s" % target_ip
#             ret, output = self.runcmd_esx(cmd, "ping system ip")
#             if ret == 0 and "5 received" in output:
#                 logger.info("Succeeded to ping system ip")
#                 break
#             if cycle_count == max_cycle:
#                 logger.info("Time out to ping system ip")
#                 break
#             else:
#                 time.sleep(10)
# 
#     def esx_remove_guest(self, guest_name, esx_host, vCenter, vCenter_user, vCenter_pass):
#         ''' remove guest from esx vCenter '''
#         vmware_cmd_ip = ee.vmware_cmd_ip
#         cmd = "vmware-cmd -H %s -U %s -P %s --vihost %s -s unregister /vmfs/volumes/datastore*/%s/%s.vmx" % (vCenter, vCenter_user, vCenter_pass, esx_host, guest_name, guest_name)
#         ret, output = self.runcmd(cmd, "remove guest '%s' from vCenter" % guest_name, vmware_cmd_ip)
#         if ret == 0:
#             logger.info("Succeeded to remove guest '%s' from vCenter" % guest_name)
#         else:
#             raise FailException("Failed to remove guest '%s' from vCenter" % guest_name)
# 
# 
#     def esx_destroy_guest(self, guest_name, esx_host):
#         ''' destroy guest from '''
#         # esx_host_ip = ee.esx_host_ip
#         # vmware_cmd_ip = ee.vmware_cmd_ip
#         # cmd = "vim-cmd vmsvc/destroy /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
#         ret, output = self.runcmd_esx(cmd, "destroy guest '%s' in ESX" % guest_name, esx_host)
#         if ret == 0:
#             logger.info("Succeeded to destroy guest '%s'" % guest_name)
#         else:
#             raise FailException("Failed to destroy guest '%s'" % guest_name)
# 
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

# 
#     def esx_stop_guest(self, guest_name, destination_ip):
#         ''' stop guest in esx host '''
#         cmd = "vim-cmd vmsvc/power.off /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         ret, output = self.runcmd_esx(cmd, "stop guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
#         if ret == 0:
#             logger.info("Succeeded to stop guest '%s' in ESX host" % guest_name)
#         else:
#             raise FailException("Failed to stop guest '%s' in ESX host" % guest_name)
# 
#         ''' check whethre guest can not be accessed by ip '''
#         self.esx_check_ip_accessable(guest_name, destination_ip, accessable=False)
# 
#     def esx_pause_guest(self, guest_name, destination_ip):
#         ''' suspend guest in esx host '''
#         cmd = "vim-cmd vmsvc/power.suspend /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         ret, output = self.runcmd_esx(cmd, "suspend guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
#         if ret == 0:
#             logger.info("Succeeded to suspend guest '%s' in ESX host" % guest_name)
#         else:
#             raise FailException("Failed to suspend guest '%s' in ESX host" % guest_name)
# 
#         ''' check whethre guest can not be accessed by ip '''
#         self.esx_check_ip_accessable(guest_name, destination_ip, accessable=False)
# 
#     def esx_resume_guest(self, guest_name, destination_ip):
#         ''' resume guest in esx host '''
#         # cmd = "vim-cmd vmsvc/power.suspendResume /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
#         ret, output = self.runcmd_esx(cmd, "resume guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
#         if ret == 0:
#             logger.info("Succeeded to resume guest '%s' in ESX host" % guest_name)
#         else:
#             raise FailException("Failed to resume guest '%s' in ESX host" % guest_name)
# 
#         ''' check whethre guest can be accessed by ip '''
#         self.esx_check_ip_accessable(guest_name, destination_ip, accessable=True)
# 
#     def esx_get_guest_mac(self, guest_name, destination_ip):
#         ''' get guest mac address in esx host '''
#         cmd = "vim-cmd vmsvc/device.getdevices /vmfs/volumes/datastore*/%s/%s.vmx | grep 'macAddress'" % (guest_name, guest_name)
#         ret, output = self.runcmd_esx(cmd, "get guest mac address '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
#         macAddress = output.split("=")[1].strip().strip(',').strip('"')
#         if ret == 0:
#             logger.info("Succeeded to get guest mac address '%s' in ESX host" % guest_name)
#         else:
#             raise FailException("Failed to get guest mac address '%s' in ESX host" % guest_name)
# 
#         return macAddress
#     
# 
#     def esx_check_ip_accessable(self, guest_name, destination_ip, accessable):
#         cycle_count = 0
#         while True:
#             # wait max time 10 minutes
#             max_cycle = 60
#             cycle_count = cycle_count + 1
#             if accessable:
#                 if self.esx_get_guest_ip(guest_name, destination_ip) != "unset":
#                     break
#                 if cycle_count == max_cycle:
#                     logger.info("Time out to esx_check_ip_accessable")
#                     break
#                 else:
#                     time.sleep(10)
#             else:
#                 time.sleep(30)
#                 if self.esx_get_guest_ip(guest_name, destination_ip) == "unset":
#                     break
#                 if cycle_count == max_cycle:
#                     logger.info("Time out to esx_check_ip_accessable")
#                     break
#                 else:
#                     time.sleep(10)
# 
#     def esx_get_guest_uuid(self, guest_name, destination_ip):
#         ''' get guest uuid in esx host '''
#         cmd = "vim-cmd vmsvc/get.summary /vmfs/volumes/datastore*/%s/%s.vmx | grep 'uuid'" % (guest_name, guest_name)
#         ret, output = self.runcmd_esx(cmd, "get guest uuid '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
#         uuid = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
#         if ret == 0:
#             logger.info("Succeeded to get guest uuid '%s' in ESX host" % guest_name)
#         else:
#             raise FailException("Failed to get guest uuid '%s' in ESX host" % guest_name)
# 
#         return uuid
# 
#     def esx_get_host_uuid(self, destination_ip):
#         ''' get host uuid in esx host '''
#         cmd = "vim-cmd hostsvc/hostsummary | grep 'uuid'"
#         ret, output = self.runcmd_esx(cmd, "get host uuid in ESX '%s'" % destination_ip, destination_ip)
#         uuid = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
#         if ret == 0:
#             logger.info("Succeeded to get host uuid '%s' in ESX host" % uuid)
#         else:
#             raise FailException("Failed to get host uuid '%s' in ESX host" % uuid)
# 
#         return uuid
# 
#     def esx_check_uuid(self, guestname, destination_ip, guestuuid="Default", uuidexists=True, rhsmlogpath='/var/log/rhsm'):
#         ''' check if the guest uuid is correctly monitored by virt-who '''
#         if guestname != "" and guestuuid == "Default":
#             guestuuid = self.esx_get_guest_uuid(guestname, destination_ip)
#         rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
#         self.vw_restart_virtwho(logger)
#         self.vw_restart_virtwho(logger)
#         cmd = "tail -1 %s " % rhsmlogfile
#         ret, output = self.runcmd(cmd, "check output in rhsm.log")
#         if ret == 0:
#             ''' get guest uuid.list from rhsm.log '''
#             if "Sending list of uuids: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update to updateConsumer: " in output:
#                 log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update in hosts-to-guests mapping: " in output:
#                 log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             else:
#                 raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
#     
#             # check guest uuid in log_uuid_list
#             if uuidexists:
#                 if guestname == "":
#                     return len(log_uuid_list) == 0
#                 else:
#                     return guestuuid in log_uuid_list
#             else:
#                 if guestname == "":
#                     return not len(log_uuid_list) == 0
#                 else:
#                     return not guestuuid in log_uuid_list
#         else:
#             raise FailException("Failed to get uuids in rhsm.log")
# 
# 
#     def esx_check_uuid_exist_in_rhsm_log(self, uuid, destination_ip=""):
#         ''' esx_check_uuid_exist_in_rhsm_log '''
#         self.vw_restart_virtwho(logger)
#         self.vw_restart_virtwho(logger)
#         time.sleep(10)
#         cmd = "tail -1 /var/log/rhsm/rhsm.log"
#         ret, output = self.runcmd(cmd, "check output in rhsm.log")
#         if ret == 0:
#             ''' get guest uuid.list from rhsm.log '''
#             if "Sending list of uuids: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update to updateConsumer: " in output:
#                 log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update in hosts-to-guests mapping: " in output:
#                 log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             else:
#                 raise FailException("Failed to get guest uuid.list from rhsm.log")
#     
#             # check guest uuid in log_uuid_list
#             return uuid in log_uuid_list
#         else:
#             raise FailException("Failed to get uuids in rhsm.log")
# 
# 
#     def get_uuid_list_in_rhsm_log(self, destination_ip=""):
#         ''' esx_check_uuid_exist_in_rhsm_log '''
#         self.vw_restart_virtwho(logger)
#         time.sleep(20)
#         cmd = "tail -1 /var/log/rhsm/rhsm.log"
#         ret, output = self.runcmd(cmd, "check output in rhsm.log")
#         if ret == 0:
#             ''' get guest uuid.list from rhsm.log '''
#             if "Sending list of uuids: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update to updateConsumer: " in output:
#                 log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update in hosts-to-guests mapping: " in output:
#                 log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             else:
#                 raise FailException("Failed to get guest uuid.list from rhsm.log")
#     
#             return log_uuid_list
#         else:
#             raise FailException("Failed to get uuid list in rhsm.log")
# 
# 
#     def esx_check_host_in_samserv(self, esx_uuid, destination_ip):
#         ''' check esx host exist in sam server '''
#         cmd = "headpin -u admin -p admin system list --org=ACME_Corporation --environment=Library"
#         ret, output = self.runcmd(cmd, "check esx host exist in sam server", destination_ip)
#         if ret == 0 and esx_uuid in output:
#         # if ret == 0 and output.find(esx_uuid) >= 0:
#             logger.info("Succeeded to check esx host %s exist in sam server" % esx_uuid)
#         else:
#             raise FailException("Failed to check esx host %s exist in sam server" % esx_uuid)
# 
# 
#     def esx_remove_host_in_samserv(self, esx_uuid, destination_ip):
#         ''' remove esx host in sam server '''
#         cmd = "headpin -u admin -p admin system unregister --name=%s --org=ACME_Corporation" % esx_uuid
#         ret, output = self.runcmd(cmd, "remove esx host in sam server", destination_ip)
#         if ret == 0 and esx_uuid in output:
#             logger.info("Succeeded to remove esx host %s in sam server" % esx_uuid)
#         else:
#             raise FailException("Failed to remove esx host %s in sam server" % esx_uuid)
# 
# 
#     def esx_remove_deletion_record_in_samserv(self, esx_uuid, destination_ip):
#         ''' remove deletion record in sam server '''
#         cmd = "headpin -u admin -p admin system remove_deletion --uuid=%s" % esx_uuid
#         ret, output = self.runcmd(cmd, "remove deletion record in sam server", destination_ip)
#         if ret == 0 and esx_uuid in output:
#             logger.info("Succeeded to remove deletion record %s in sam server" % esx_uuid)
#         else:
#             raise FailException("Failed to remove deletion record %s in sam server" % esx_uuid)
# 
# 
#     def esx_subscribe_host_in_samserv(self, esx_uuid, poolid, destination_ip):
#         ''' subscribe host in sam server '''
#         cmd = "headpin -u admin -p admin system subscribe --name=%s --org=ACME_Corporation --pool=%s " % (esx_uuid, poolid)
#         ret, output = self.runcmd(cmd, "subscribe host in sam server", destination_ip)
#         if ret == 0 and esx_uuid in output:
#             logger.info("Succeeded to subscribe host %s in sam server" % esx_uuid)
#         else:
#             raise FailException("Failed to subscribe host %s in sam server" % esx_uuid)
# 
# 
#     def esx_unsubscribe_all_host_in_samserv(self, esx_uuid, destination_ip):
#         ''' unsubscribe host in sam server '''
#         cmd = "headpin -u admin -p admin system unsubscribe --name=%s --org=ACME_Corporation --all" % esx_uuid
#         ret, output = self.runcmd(cmd, "unsubscribe host in sam server", destination_ip)
#         if ret == 0 and esx_uuid in output:
#             logger.info("Succeeded to unsubscribe host %s in sam server" % esx_uuid)
#         else:
#             raise FailException("Failed to unsubscribe host %s in sam server" % esx_uuid)
# 
# 
#     def get_poolid_by_SKU(self, sku, targetmachine_ip=""):
#         ''' get_poolid_by_SKU '''
#         availpoollist = self.sub_listavailpools(sku, targetmachine_ip)
#         if availpoollist != None:
#             for index in range(0, len(availpoollist)):
#                 if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku):
#                     rindex = index
#                     break
#                 elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == sku):
#                     rindex = index
#                     break
#             if "PoolID" in availpoollist[index]:
#                 poolid = availpoollist[rindex]["PoolID"]
#             else:
#                 poolid = availpoollist[rindex]["PoolId"]
#             return poolid
#         else:
#             raise FailException("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % sku)
# 
# 
#     #========================================================
#     #     5. Rhevm Functions
#     #========================================================
#     def add_rhevm_server_to_host(self, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
#         ''' Add rhevm hostname and hostip to /etc/hosts '''
#         cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (rhevmmachine_ip, rhevmmachine_ip, rhevmmachine_name)
#         ret, output = self.runcmd(cmd, "add rhevm name and ip to /etc/hosts", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add rhevm hostip %s and rhevm hostname %s %s." % (rhevmmachine_ip, rhevmmachine_name, self.get_hg_info(targetmachine_ip)))
#         else:
#             raise FailException("Failed to add rhevm hostip %s and rhevm hostname %s %s" % (rhevmmachine_ip, rhevmmachine_name, self.get_hg_info(targetmachine_ip)))
# 
# 
#     def configure_host_bridge(self, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
#         eth0_addr = '/etc/sysconfig/network-scripts/ifcfg-eth0'
#         br0_addr = '/etc/sysconfig/network-scripts/ifcfg-br0'
#         cmd = "ifconfig rhevm"
#         ret, output = self.runcmd(cmd, "Check bridge rhevm exist", targetmachine_ip)
#         ''' configure the host bridge. '''
#         if ret != 0 and rhevmmachine_name != None and rhevmmachine_ip != None :
#             # set the eth0's bridge to rhevm
#             cmd = "sed -i '/^BRIDGE/d' %s ; echo 'BRIDGE=rhevm' >> %s" % (eth0_addr, eth0_addr)
#             ret, output = self.runcmd(cmd, "configure eth0 bridge name to rhevm", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to configure eth0 bridge name to rhevm")
#             else:
#                 raise FailException("Failed to configure eth0 bridge name to rhevm")
#     
#             cmd = "sed -i '/^DEVICE/d' %s ; echo 'DEVICE=rhevm' >> %s" % (br0_addr, br0_addr)
#             ret, output = self.runcmd(cmd, "configure br0 drive name to rhevm", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to configure br0 drive name to rhevm")
#             else:
#                 raise FailException("Failed to configure br0 drive name to rhevm")
#     
#             cmd = "init 6"
#             ret, output = self.runcmd(cmd, "reboot system", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Start to reboot system %s, please wait for a moment!" % targetmachine_ip)
#             else:
#                 raise FailException("Failed to reboot system %s, please wait for a moment!" % targetmachine_ip)
#     
#             self.ping_host(targetmachine_ip)
#             cmd = "ifconfig rhevm"
#             ret, output = self.runcmd(cmd, "Check bridge rhevm exist", targetmachine_ip)
#             if ret == 0 :
#                 logger.info("Succesfully to configured bridge rhevm on %s" % targetmachine_ip)
#             else:
#                 raise FailException("Failed to configured bridge rhevm on %s" % targetmachine_ip)
#     
# 
#     def ping_host(self, ip, timeout=600):
#         """Ping some host,return True on success or False on Failure,timeout should be greater or equal to 10"""
#         time.sleep(10)
#         cmd = "ping -c 3 " + str(ip)
#         while True:
#             if(timeout > 0):
#                 time.sleep(10)
#                 timeout -= 10
#                 (ret, out) = commands.getstatusoutput(cmd)
#                 if ret == 0:
#                     logger.info("ping successfully")
#                     time.sleep(30)
#                     break
#                 logger.info("left %s s to reboot %s" % (timeout, ip))
#             else:
#                 raise FailException("ping time out")
#     
# 
#     def get_rhevm_repo_file(self, targetmachine_ip=""):
#         ''' wget rhevm repo file and add to rhel host '''
#         cmd = "wget -P /etc/yum.repos.d/ http://10.66.100.116/projects/sam-virtwho/rhevm-6.5.repo"
#         ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to wget rhevm repo file and add to rhel host")
#         else:
#             raise FailException("Failed to wget rhevm repo file and add to rhel host")
# 
# 
#     def install_host_vdsm(self, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
#         '''install VDSM'''
#         if rhevmmachine_name != None and rhevmmachine_ip != None:
#             cmd = "rpm -q vdsm"
#             ret, output = self.runcmd(cmd, "check whether vdsm exist", targetmachine_ip)      
#             if ret == 0:
#                 logger.info("vdsm has already exist, needn't to install it.")
#             else:
#                 cmd = "yum install vdsm -y"
#                 ret, output = self.runcmd(cmd, "install vdsm", targetmachine_ip)
#                 if ret == 0 and "Complete!" in output:
#                     logger.info("Succeeded to install vdsm.")
#                 elif ret == 0 and "already installed" in output:
#                     logger.info("vdsm has been installed.")
#                 else:
#                     raise FailException("Failed to install vdsm")
#         
# 
#     def install_virtV2V(self, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
#         '''install virt-V2V'''
#         if rhevmmachine_name != None and rhevmmachine_ip != None:
#             cmd = "rpm -q virt-v2v"
#             ret, output = self.runcmd(cmd, "check whether virt-V2V exist", targetmachine_ip)
#             if ret == 0:
#                 logger.info("virt-V2V has already exist, needn't to install it.")
#             else:
#                 logger.info("virt-V2V hasn't been installed.")
#                 cmd = "yum install virt-v2v -y"
#                 ret, output = self.runcmd(cmd, "install vdsm", targetmachine_ip)
#                 if ret == 0 and "Complete!" in output:
#                     logger.info("Succeeded to install virt-V2V.")
#                 else:
#                     raise FailException("Failed to install virt-V2V")
#         
# 
#     def rhevm_update_vw_configure(self, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password, background=1, debug=1, targetmachine_ip=""):
#         ''' update virt-who configure file /etc/sysconfig/virt-who. '''
#         cmd = "sed -i -e 's/#VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=5/g' -e 's/VIRTWHO_BACKGROUND=.*/VIRTWHO_BACKGROUND=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_RHEVM=.*/VIRTWHO_RHEVM=1/g' -e 's/#VIRTWHO_RHEVM_OWNER=.*/VIRTWHO_RHEVM_OWNER=%s/g' -e 's/#VIRTWHO_RHEVM_ENV=.*/VIRTWHO_RHEVM_ENV=%s/g' -e 's/#VIRTWHO_RHEVM_SERVER=.*/VIRTWHO_RHEVM_SERVER=%s/g' -e 's/#VIRTWHO_RHEVM_USERNAME=.*/VIRTWHO_RHEVM_USERNAME=%s/g' -e 's/#VIRTWHO_RHEVM_PASSWORD=.*/VIRTWHO_RHEVM_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (background, debug, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
#         ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to update virt-who configure file.")
#         else:
#             raise FailException("Failed to update virt-who configure file.")
# 
# 
#     # Get the machine's hostname
#     def get_hostname(self, targetmachine_ip=""):
#         cmd = "hostname"
#         ret, output = self.runcmd(cmd, "geting the machine's hostname", targetmachine_ip)
#         if ret == 0:
#             hostname = output.strip(' \r\n').strip('\r\n') 
#             logger.info("Succeeded to get the machine's hostname %s." % hostname) 
#             return hostname
#         else:
#             raise FailException("Failed to get the machine's hostname.")
# 
# 
#     def rhevm_add_dns_to_host(self, DNSserver_ip, targetmachine_ip=""):
#         ''' add dns server to /etc/resolv.conf. '''
#         cmd = "sed -i '/%s/d' /etc/resolv.conf; sed -i '/search/a nameserver %s' /etc/resolv.conf" % (DNSserver_ip, DNSserver_ip)
#         ret, output = self.runcmd(cmd, "add_dns_to_host in /etc/resolv.conf.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add_dns_to_host in /etc/resolve.conf.")
#         else:
#             raise FailException("Failed to add_dns_to_host in /etc/resolve.conf.")
# 
# 
#     def add_dns_to_host(self, DNSserver_ip, targetmachine_ip=""):
#         ''' add dns server to /etc/resolv.conf. '''
#         cmd = "sed -i '/%s/d' /etc/resolv.conf; sed -i '/search/a nameserver %s\nnameserver 10.16.101.41\nnameserver 10.11.5.19' /etc/resolv.conf" % (DNSserver_ip, DNSserver_ip)
#         ret, output = self.runcmd(cmd, "add_dns_to_host in /etc/resolv.conf.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add_dns_to_host in /etc/resolve.conf.")
#         else:
#             raise FailException("Failed to add_dns_to_host in /etc/resolve.conf.")
# 
#         # make /etc/resolv.conf can not be changed 
#         cmd = "chattr +i /etc/resolv.conf"
#         ret, output = self.runcmd(cmd, "Fix /etc/resolv.conf.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to fix /etc/resolve.conf.")
#         else:
#             raise FailException("Failed to fix /etc/resolve.conf.")
# 
# 
#     # Convert the ip address's last two bits
#     def get_conv_ip(self, sourceip, targetmachine_ip=""):
#         convtip = sourceip.split(".")
#         logger.info("Succeeded to get converted ip address %s" % convtip)
#         return convtip[3] + "." + convtip[2]
# 
#     # Remove hostname's '.redhat.com'
#     def get_conv_name(self, sourcename, targetmachine_ip=""):
#         convtname = sourcename[0:sourcename.rfind('.redhat.com')] 
#         logger.info("Succeeded to get convname %s" % convtname)
#         return convtname
# 
#     # configure dns server
#     def config_dnsserver(self, host_ip, host_name, targetmachine_ip):
#         ''' configure dns server '''
#         dirct_addr = '/var/named/named.66.10'
#         revert_addr = '/var/named/named.redhat.com'
#         conv_host_ip = self.get_conv_ip(host_ip)
#         conv_host_name = self.get_conv_name(host_name)
#         cmd = "sed -i '/%s/d' %s; sed -i '$ a\%s\tIN\tPTR\t%s.' %s" % (host_name, dirct_addr, conv_host_ip, host_name, dirct_addr)
#         ret, output = self.runcmd_indns(cmd, "Add host %s ip address to named.66.10" % host_ip, targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add host's ip %s to DNS server." % host_ip)
#         else:
#             raise FailException("Failed to add host's ip %s to DNS server." % host_ip)
#  
#         cmd = "sed -i '/%s/d' %s; sed -i '$ a\%s\tIN\tA\t%s' %s" % (conv_host_name, revert_addr, conv_host_name, host_ip, revert_addr) 
#         ret, output = self.runcmd_indns(cmd, "Add host name %s to named.redhat.com" % host_name, targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add host's name %s to DNS server." % host_name)
#         else:
#             raise FailException("Failed to add host's name %s to DNS server." % host_name)
# 
#         # restart dns service
#         cmd = "service named restart"
#         ret, output = self.runcmd_indns(cmd, "service named restart", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to restart dns service.")
#         else:
#             raise FailException("Failed to restart dns service.")
# 
# 
#     # configure dns server
#     def config_yum(self, proxy_ip, targetmachine_ip):
#         ''' configure yum '''
#         cmd = "sed -i '/%s/d' /etc/yum.conf; sed -i '/search/a %s' /etc/yum.conf" % (proxy_ip, proxy_ip)
#         ret, output = self.runcmd(cmd, "add proxy to /etc/yum.conf.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add proxy to /etc/yum.conf.")
#         else:
#             raise FailException("Failed to add proxy to /etc/yum.conf.")
# 
# 
#     # configure rhsm.conf to candlepin server
#     def conf_rhsm_candlepin(self, targetmachine_ip):
#         ''' configure candlepin '''
#         cmd = "sed -i -e 's/^hostname =.*/hostname = subscription.rhn.redhat.com/g' -e 's/baseurl=.*/baseurl=https:\/\/cdn.redhat.com/g' /etc/rhsm/rhsm.conf"
#         ret, output = self.runcmd(cmd, "Configure candlepin server.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to configure candlepin server.")
#         else:
#             raise FailException("Failed to Configure candlepin server.")
# 
# 
#     # configure rhsm.conf to sam server
#     def conf_rhsm_sam(self, targetmachine_ip):
#         ''' configure candlepin '''
#         cmd = "sed -i -e 's/hostname =.*/hostname = samserv.redhat.com/g' -e 's/baseurl=.*/baseurl=https:\/\/samserv.redhat.com:8088/g' /etc/rhsm/rhsm.conf"
#         ret, output = self.runcmd(cmd, "Configure SAM server.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to configure SAM server.")
#         else:
#             raise FailException("Failed to Configure SAM server.")
# 
# 
#     # Configure NFS server
#     def config_nfsserver(self, exportdir, targetmachine_ip=""):
#         cmd = "ll %s" % (exportdir)
#         ret, output = self.runcmd(cmd, "check images path in the NFS Server", targetmachine_ip)
#         if ret == 0 and output is not "":
#             cmd = "rm -rf %s/*" % (exportdir)
#             ret, output = self.runcmd(cmd, "It has content in the exportdir, need to delete", targetmachine_ip)
#             if ret == 0:
#                 logger.info("Succeeded to delete content in the exportdir.")
#             else:
#                 raise FailException("Failed to delete content in the exportdir.")
#                 
#         cmd = "mkdir -p %s" % (exportdir)
#         ret, output = self.runcmd(cmd, "create image path in the NFS Server", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to create imagepath in the source machine.")
#         else:
#             raise FailException("Failed to create imagepath in the source machine.")
# 
#         ''' export a dir as nfs '''
#         cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (exportdir.replace('/', '\/'), exportdir)
#         # logger.info(cmd)
#         ret, output = self.runcmd(cmd, "set exporting destination dir", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % exportdir)
#         else:
#             raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % exportdir)
# 
#         cmd = "service nfs restart; sleep 10"
#         ret, output = self.runcmd(cmd, "restarting nfs service", targetmachine_ip)
#         if ret == 0 :
#             logger.info("Succeeded to restart service nfs.")
#         else:
#             raise FailException("Failed to restart service nfs.")
# 
#         cmd = "rpc.mountd"
#         ret, output = self.runcmd(cmd, "rpc.mountd", targetmachine_ip)
#         cmd = "showmount -e 127.0.0.1"
#         ret, output = self.runcmd(cmd, "showmount", targetmachine_ip)
#         if ret == 0 and (exportdir in output):
#             logger.info("Succeeded to export dir '%s' as nfs." % exportdir)
#         else:
#             raise FailException("Failed to export dir '%s' as nfs." % exportdir)
# 
# 
#     # Configure rhevm-hell, auto connect
#     def config_rhevm_shell(self, rhevmserv_ip):
#         cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s:443/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.rhevmshellrc" % rhevmserv_ip
#         ret, output = self.runcmd(cmd, "config_rhevm_shell in /root/.rhevmshellrc", rhevmserv_ip)
#         if ret == 0:
#             logger.info("Succeeded to config_rhevm_shell in /root/.rhevmshellrc.")
#         else:
#             raise FailException("Failed to config_rhevm_shell in /root/.rhevmshellrc.")
# 
# 
#     # Enter rhevm-shell mode
#     def enter_rhevm_shell(self, targetmachine_ip):
#         cmd = "rhevm-shell -c" 
#         ret, output = self.runcmd(cmd, "connect to rhevm-shell", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to connect to rhevm-shell.")
#         else:
#             raise FailException("Failed to connect to rhevm-shell.")
# 
# 
#     # Add host to rhevm
#     def rhevm_add_host(self, rhevm_host_name, rhevm_host_ip, targetmachine_ip):
#         cmd = "add host --name \"%s\" --address \"%s\" --root_password redhat; exit" % (rhevm_host_name, rhevm_host_ip)
#         ret, output = self.runcmd_rhevm(cmd, "add host to rhevm.", targetmachine_ip)
#         if ret == 0:
#             runtime = 0
#             while True:
#                 cmd = "list hosts --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list hosts in rhevm.", targetmachine_ip)
#                 runtime = runtime + 1
#                 if ret == 0 and rhevm_host_name in output:
#                     logger.info("Succeeded to list host %s." % rhevm_host_name)
#                     status = self.get_key_rhevm(output, "status-state", "name", rhevm_host_name, targetmachine_ip)
#                     if "up" in status:
#                         logger.info("Succeeded to add new host %s to rhevm" % rhevm_host_name)
#                         break
#                     else :
#                         logger.info("vm %s status-state is %s" % (rhevm_host_name, status))
#                 time.sleep(10)
#                 if runtime > 120:
#                     raise FailException("%s status has problem,status is %s." % (rhevm_host_name, status))
#         
# 
#     # Get host_id in the rhevm
#     def get_hostid_rhevm(self, hostname, targetmachine_ip=""):
#         ''' Get the hostid. '''
#         pool_dict = {}
#         self.enter_rhevm_shell(targetmachine_ip)
#         cmd = "list hosts"
#         output = self.runcmd_rhevmprocess(cmd, "list all hosts in rhevm")
#         if output is not "":
#             datalines = output.splitlines()
#             for line in datalines:
#                 line = line.strip()
#                 if line.find("id") == 0:
#                     resultid = line[(line.find(':') + 1):].strip()
#                 elif line.find("name") == 0:
#                     resultname = line[(line.find(':') + 1):].strip()
#                     pool_dict[resultname] = resultid
#             if hostname in pool_dict :
#                 logger.info("Succeeded to get the %s's hostid." % hostname)
#                 hostid = pool_dict[hostname]
#                 return hostid
#             else:
#                 raise FailException("Failed to get the %s's hostid." % hostname)
#     
#         else:
#             raise FailException("Failed to list hosts on rhevm.")
# 
# 
#     # parse rhevm-shell result to dict
#     def get_key_rhevm(self, output, non_key_value, key_value, find_value, targetmachine_ip=""):
#         pool_dict = {}
#         if output is not "":
#             datalines = output.splitlines()
#             values1 = False
#             values2 = False
#             ERROR_VALUE = "-1"
#             for line in datalines:
#                 line = line.strip()
#                 if line.find(non_key_value) == 0:
#                     result_values1 = line[(line.find(':') + 1):].strip()
#                     logger.info("Succeeded to find the non_key_value %s's result_values1 %s" % (non_key_value, result_values1))
#                     values1 = True
#                 elif line.find(key_value) == 0:
#                     result_values2 = line[(line.find(':') + 1):].strip()
#                     logger.info("Succeeded to find the key_value %s's result_values2 %s" % (key_value, result_values2))
#                     values2 = True
#                 elif (line == "") and (values2 == True) and (values1 == False):
#                     pool_dict[result_values2] = ERROR_VALUE
#                     values2 = False
#                 if (values1 == True) and (values2 == True):
#                     pool_dict[result_values2] = result_values1
#                     values1 = False
#                     values2 = False
#             if find_value in pool_dict:
#                 findout_value = pool_dict[find_value]
#                 if findout_value == ERROR_VALUE:
#                     logger.info("Failed to get the %s's %s, no value" % (find_value, non_key_value))
#                     return ERROR_VALUE
#                 else:
#                     logger.info("Succeeded to get the %s's %s." % (find_value, non_key_value))
#                     return findout_value
#             else:
#                 raise FailException("Failed to get the %s's %s" % (find_value, non_key_value))
#     
#         else:
#             raise FailException("Failed to run rhevm-shell cmd.")
# 
# 
#     # parse rhevm-result to dict
#     def rhevm_info_dict(self, output, targetmachine_ip=""):
#         rhevm_info_dict = {}
#         if output is not "":
#             datalines = output.splitlines()
#             for line in datalines:
#                 if ":" in line:
#                     key = line.strip().split(":")[0].strip()
#                     value = line.strip().split(":")[1].strip()
#                     print key + "==" + value
#                     rhevm_info_dict[key] = value
#             return rhevm_info_dict
#         else:
#             raise FailException("Failed to get output in rhevm-result file.")
# 
# 
#     # check rhevm-shell running in rhevm server finished
#     def check_rhevm_shell_finished(self, rhevm_ip=""):
#         timout = 0
#         while True:
#             timout = timout + 1
#             (ret, output) = utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "cat /tmp/rhevm_control")
#             if ret == 0 and "0" in output:
#                 logger.info("rhevm-shell command running in rhevm server has finished.")
#                 time.sleep(10)
#                 return True
#             elif timout > 60:
#                 raise FailException("Time out, running rhevm-shell command in server failed.")
#                 break
#             else:
#                 logger.info("sleep 10 in check_rhevm_shell_finished.")
#                 time.sleep(10)
# 
#     # wait for a while until expect status shown in /tmp/rhevm-result file
#     def wait_for_status(self, cmd, status_key, status_value, targetmachine_ip, timeout=600):
#         timout = 0
#         while True:
#             timout = timout + 1
#             # cmd = "list hosts --show-all; exit"
#             ret, output = self.runcmd_rhevm(cmd, "list hosts info in rhevm.", targetmachine_ip)
#             rhevm_info = self.rhevm_info_dict(output)
#             if status_value == "NotExist":
#                 if not status_key in rhevm_info.keys():
#                     logger.info("Succeded to check %s not exist." % status_key)
#                     return True
#             elif status_key in rhevm_info.keys() and rhevm_info[status_key] == status_value:
#                 logger.info("Succeeded to get %s value %s in rhevm." % (status_key, status_value))
#                 return True
#             elif status_key in rhevm_info.keys() and rhevm_info[status_key] != status_value:
#                 logger.info("Succeeded to remove %s" % status_value)
#                 return True
#             elif timout > 60:
#                 raise FailException("Time out, running rhevm-shell command in server failed.")
#                 return False
#             else:
#                 logger.info("sleep 10 in wait_for_status.")
#                 time.sleep(10)
# 
#     # Add storagedomain in rhevm
#     def add_storagedomain_to_rhevm(self, storage_name, hostname, domaintype, storage_format, NFS_server, export_dir, rhevm_host_ip): 
#         # clean storage nfs folder first
#         cmd = "rm -rf %s/*" % export_dir
#         ret, output = self.runcmd(cmd, "clean storage nfs folder", NFS_server)
#         if ret == 0:
#             logger.info("Succeeded to clean storage nfs folder: %s" % export_dir)
#         else:
#             raise FailException("Failed to clean storage nfs folder: %s" % export_dir)
# 
#         cmd = "add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter \"Default\"" % (storage_name, hostname, domaintype, storage_format, NFS_server, export_dir)
#         ret, output = self.runcmd_rhevm(cmd, "Add storagedomain in rhevm.", rhevm_host_ip)
#         if self.wait_for_status("list storagedomains --show-all; exit", "status-state", "unattached", rhevm_host_ip):
#             logger.info("Succeeded to add storagedomains %s in rhevm." % storage_name)
#         else:
#             raise FailException("Failed to add storagedomains %s in rhevm." % storage_name)
# 
#         cmd = "add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"Default\"" % (storage_name, hostname, domaintype, storage_format, NFS_server, export_dir)
#         ret, output = self.runcmd_rhevm(cmd, "Add storagedomain in rhevm.", rhevm_host_ip)
#         if self.wait_for_status("list storagedomains --show-all; exit", "status-state", "NotExist", rhevm_host_ip):
#             logger.info("Succeeded to maintenance storagedomains %s in rhevm." % storage_name)
#         else:
#             raise FailException("Failed to maintenance storagedomains %s in rhevm." % storage_name)
# 
# 
#     # activate storagedomain in rhevm
#     def activate_storagedomain(self, storage_name, rhevm_host_ip): 
#         cmd = "action storagedomain \"%s\" activate --datacenter-identifier \"Default\"" % (storage_name)
#         ret, output = self.runcmd_rhevm(cmd, "activate storagedomain in rhevm.", rhevm_host_ip)
#         if self.wait_for_status("list storagedomains --show-all; exit", "status-state", "NotExist", rhevm_host_ip):
#             logger.info("Succeeded to activate storagedomains %s in rhevm." % storage_name)
#         else:
#             raise FailException("Failed to activate storagedomains %s in rhevm." % storage_name)
# 
# 
#     # convert_guest_to_nfs with v2v tool
#     def convert_guest_to_nfs(self, NFS_server, NFS_export_dir, vm_hostname):
#         cmd = "virt-v2v -i libvirt -ic qemu:///system -o rhev -os %s:%s --network rhevm %s" % (NFS_server, NFS_export_dir, vm_hostname)
#         ret, output = self.runcmd(cmd, "convert_guest_to_nfs with v2v tool")
#         if ret == 0:
#             logger.info("Succeeded to convert_guest_to_nfs with v2v tool")
#         else:
#             raise FailException("Failed to convert_guest_to_nfs with v2v tool")
# 
#         # convert the second guest
#         cmd = "virt-v2v -i libvirt -ic qemu:///system -o rhev -os %s:%s --network rhevm %s -on \"Sec_%s\"" % (NFS_server, NFS_export_dir, vm_hostname, vm_hostname)
#         ret, output = self.runcmd(cmd, "convert_guest_to_nfs with v2v tool")
#         if ret == 0:
#             logger.info("Succeeded to convert the second guest to nfs with v2v tool")
#         else:
#             raise FailException("Failed to convert the second guest to nfs with v2v tool")
# 
# 
#     # create_storage_pool
#     def create_storage_pool(self, logger):
#         ''' wget autotest_pool.xml '''
#         cmd = "wget -P /tmp/ http://10.66.100.116/projects/sam-virtwho/autotest_pool.xml"
#         ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host")
#         if ret == 0:
#             logger.info("Succeeded to wget autotest_pool.xml")
#         else:
#             raise FailException("Failed to wget autotest_pool.xml")
# 
#         # check whether pool exist, if yes, destroy it
#         cmd = "virsh pool-list"
#         ret, output = self.runcmd(cmd, "check whether autotest_pool exist")
#         if ret == 0 and "autotest_pool" in output:
#             logger.info("autotest_pool exist.")
#             cmd = "virsh pool-destroy autotest_pool"
#             ret, output = self.runcmd(cmd, "destroy autotest_pool")
#             if ret == 0 and "autotest_pool destroyed" in output:
#                 logger.info("Succeeded to destroy autotest_pool")
#             else:
#                 raise FailException("Failed to destroy autotest_pool")
#     
# 
#         cmd = "virsh pool-create /tmp/autotest_pool.xml"
#         ret, output = self.runcmd(cmd, "import vm to rhevm.")
#         if ret == 0 and "autotest_pool created" in output:
#             logger.info("Succeeded to create autotest_pool.")
#         else:
#             raise FailException("Failed to create autotest_pool.")
# 
# 
#     # import guest to rhevm
#     def import_vm_to_rhevm(self, guest_name, nfs_dir_for_storage, nfs_dir_for_export, rhevm_host_ip):
#         # action vm "6.4_Server_x86_64" import_vm --storagedomain-identifier export_storage  --cluster-name Default --storage_domain-name data_storage
#         cmd = "action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s" % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
#         ret, output = self.runcmd_rhevm(cmd, "import guest %s in rhevm." % guest_name, rhevm_host_ip)
#         if ret == 0:
#             runtime = 0
#             while True:
#                 cmd = "list vms --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list VMS in rhevm.", rhevm_host_ip)
#                 runtime = runtime + 1
#                 if ret == 0 and guest_name in output:
#                     logger.info("Succeeded to list vm %s." % guest_name)
#                     status = self.get_key_rhevm(output, "status-state", "name", guest_name, rhevm_host_ip)
#                     if "down" in status:
#                         logger.info("Succeeded to import new vm %s to rhevm" % guest_name)
#                         break
#                     else :
#                         logger.info("vm %s status-state is %s" % (guest_name, status))
#                 time.sleep(10)
#                 if runtime > 120:
#                     raise FailException("%s status has problem,status is %s." % (guest_name, status))
#         
# 
#     # import the second guest to rhevm
#     def import_sec_vm_to_rhevm(self, guest_name, nfs_dir_for_storage, nfs_dir_for_export, rhevm_host_ip):
#         # action vm "6.4_Server_x86_64" import_vm --storagedomain-identifier export_storage  --cluster-name Default --storage_domain-name data_storage
#         cmd = "action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s" % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
#         ret, output = self.runcmd_rhevm(cmd, "import guest %s in rhevm." % guest_name, rhevm_host_ip)
#         if ret == 0:
#             runtime = 0
#             while True:
#                 cmd = "list vms --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list VMS in rhevm.", rhevm_host_ip)
#                 runtime = runtime + 1
#                 if ret == 0 and guest_name in output:
#                     logger.info("Succeeded to list vm %s." % guest_name)
#                     status = self.get_key_rhevm(output, "status-state", "name", guest_name, rhevm_host_ip)
#                     if "down" in status:
#                         logger.info("Succeeded to import new vm %s to rhevm" % guest_name)
#                         break
#                     else :
#                         logger.info("vm %s status-state is %s" % (guest_name, status))
#                 time.sleep(10)
#                 if runtime > 120:
#                     raise FailException("%s status has problem,status is %s." % (guest_name, status))
#         
# 
#     # Migrate VM on RHEVM
#     def rhevm_migrate_guest(self, vm_name, host_name, host_ip, targetmachine_ip):
#         cmd = "action vm \"%s\" migrate --host-name \"%s\"" % (vm_name, host_name)
#         ret, output = self.runcmd_rhevm(cmd, "migrate vm on rhevm.", targetmachine_ip)
#         if self.wait_for_status("list vms --show-all; exit", "status-state", "up", targetmachine_ip):
#             logger.info("Succeeded to start up vm %s." % vm_name)
#         else:
#             raise FailException("Failed to start up vm %s." % vm_name)
# 
#         if self.wait_for_status("list vms --show-all; exit", "display-address", host_ip, targetmachine_ip):
#             logger.info("Succeeded to migrate vm %s to host %s in rhevm." % (vm_name, host_name))
#         else:
#             raise FailException("Failed to migrate vm %s to host %s in rhevm." % (vm_name, host_name))
# 
# 
# # Remove VM on RHEVM
#     def rhevm_remove_vm(self, vm_name, targetmachine_ip):
#         cmd = "remove vm \"%s\" --force" % vm_name
#         ret, output = self.runcmd_rhevm(cmd, "Remove VM on RHEVM.", targetmachine_ip)
#         if ret == 0:
#             timout = 0
#             while True:
#                 timout = timout + 1
#                 cmd = "list vms; exit"
#                 (ret, output) = self.runcmd_rhevm(cmd, "list VMS in rhevm.", targetmachine_ip)
#                 if (ret == 0) and output.find(vm_name) < 0 :
#                     logger.info("Succeeded to remove vm %s" % vm_name)
#                     break
#                 elif timout > 60:
#                     raise FailException("Time out, running rhevm-shell command in server failed.")
#                     return False
#                 else:
#                     raise FailException("Failed to remove vm %s" % vm_name)
#         
# 
# # Add new VM on RHEVM
#     def rhevm_add_vm(self, vm_name, targetmachine_ip):
#         cmd = "add vm --name %s --template-name Blank --cluster-name Default --memory 536870912; exit" % vm_name
#         ret, output = self.runcmd_rhevm(cmd, "add vm to rhevm.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to add new VM %s." % vm_name)
#             runtime = 0
#             while True:
#                 cmd = "list vms --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list VMS in rhevm.", targetmachine_ip)
#                 runtime = runtime + 1
#                 if ret == 0:
#                     logger.info("Succeeded to list vm %s." % vm_name)
#                     status = self.get_key_rhevm(output, "status-state", "name", vm_name, targetmachine_ip)
#                     if "up" in status:
#                         logger.info("Succeeded to up vm %s in rhevm" % vm_name)
#                         break
#                     else :
#                         logger.info("hosts status-state is %s" % status)
#                     time.sleep(10)
#                     if runtime > 120:
#                         raise FailException("%s status has problem,status is %s." % (vm_name, status))
#             
#                 else:
#                     raise FailException("Failed to list VM %s." % vm_name)
#          
#         else:
#             raise FailException("Failed to add new VM")
# 
# 
# 
# # Get guestip
#     def rhevm_get_guest_ip(self, vm_name, targetmachine_ip):
#         cmd = "list vms --show-all; exit"
#         ret, output = self.runcmd_rhevm(cmd, "list VMS in rhevm.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to list vm %s." % vm_name)
#             guestip = self.get_key_rhevm(output, "guest_info-ips-ip-address", "name", vm_name, targetmachine_ip)
#             hostuuid = self.get_key_rhevm(output, "host-id", "name", vm_name, targetmachine_ip)
#             if guestip is not "":
#                 logger.info("vm %s ipaddress is %s" % (vm_name, guestip))
#                 return (guestip, hostuuid)
#             else:
#                 raise FailException("Failed to gest the vm %s ipaddress" % vm_name)
#         else:
#             raise FailException("Failed to list VM %s." % vm_name)
#  
# 
# # Start VM on RHEVM
#     def rhevm_start_vm(self, rhevm_vm_name, targetmachine_ip):
#         cmd = "action vm \"%s\" start; exit" % rhevm_vm_name
#         ret, output = self.runcmd_rhevm(cmd, "start vm on rhevm.", targetmachine_ip)
#         if ret == 0:
#             runtime = 0
#             while True:
#                 cmd = "list vms --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list vms in rhevm.", targetmachine_ip)
#                 runtime = runtime + 1
#                 if ret == 0:
#                     logger.info("Succeeded to list vms")
#                     status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
#                     if status.find("up") >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
#                         logger.info("Succeeded to up vm %s in rhevm" % rhevm_vm_name)
#                         time.sleep(10)
#                         break
#                     else :
#                         logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
#                     time.sleep(10)
#                     if runtime > 100:
#                         raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
#             
#                 else:
#                     raise FailException("Failed to list vm %s" % rhevm_vm_name)
#          
#         else:
#             raise FailException("Failed to start vm %s on rhevm" % rhevm_vm_name)
# 
# 
# # Stop VM on RHEVM
#     def rhevm_stop_vm(self, rhevm_vm_name, targetmachine_ip):
#         cmd = "action vm \"%s\" stop; exit" % rhevm_vm_name
#         ret, output = self.runcmd_rhevm(cmd, "stop vm on rhevm.", targetmachine_ip)
#         if ret == 0:
#             runtime = 0
#             while True:
#                 cmd = "list vms --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list vms in rhevm.", targetmachine_ip)
#                 runtime = runtime + 1
#                 if ret == 0:
#                     logger.info("Succeeded to list vms")
#                     status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
#                     if status.find("down") >= 0 and status.find("powering") < 0:
#                         logger.info("Succeeded to stop vm %s in rhevm" % rhevm_vm_name)
#                         break
#                     else :
#                         logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
#                     time.sleep(10)
#                     if runtime > 120:
#                         raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
#             
#                 else:
#                     raise FailException("Failed to list vm %s" % rhevm_vm_name)
#          
#         else:
#             raise FailException("Failed to stop vm %s on rhevm" % rhevm_vm_name)
# 
# 
# # Suspend VM on RHEVM
#     def rhevm_suspend_vm(self, rhevm_vm_name, targetmachine_ip):
#         cmd = "action vm \"%s\" suspend; exit" % rhevm_vm_name
#         ret, output = self.runcmd_rhevm(cmd, "suspend vm on rhevm.", targetmachine_ip)
#         if ret == 0:
#             runtime = 0
#             while True:
#                 cmd = "list vms --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list vms in rhevm.", targetmachine_ip)
#                 runtime = runtime + 1
#                 if ret == 0:
#                     logger.info("Succeeded to list vms")
#                     status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
#                     if status.find("suspended") >= 0:
#                         logger.info("Succeeded to suspend vm %s in rhevm" % rhevm_vm_name)
#                         break
#                     else :
#                         logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
#                     time.sleep(10)
#                     if runtime > 120:
#                         raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
#             
#                 else:
#                     raise FailException("Failed to list vm %s" % rhevm_vm_name)
#          
#         else:
#             raise FailException("Failed to suspend vm %s on rhevm" % rhevm_vm_name)
# 
# 
# # Shutdown VM on RHEVM
#     def rhevm_shutdown_vm(self, rhevm_vm_name, targetmachine_ip):
#         cmd = "action vm \"%s\" shutdown; exit" % rhevm_vm_name
#         ret, output = self.runcmd_rhevm(cmd, "shutdown vm on rhevm.", targetmachine_ip)
#         if ret == 0:
#             runtime = 0
#             while True:
#                 cmd = "list vms --show-all; exit"
#                 ret, output = self.runcmd_rhevm(cmd, "list vms in rhevm.", targetmachine_ip)
#                 runtime = runtime + 1
#                 if ret == 0:
#                     logger.info("Succeeded to list vms")
#                     status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
#                     if status.find("down") >= 0 and status.find("powering") < 0:
#                         logger.info("Succeeded to shutdown vm %s in rhevm" % rhevm_vm_name)
#                         break
#                     else :
#                         logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
#                     time.sleep(10)
#                     if runtime > 120:
#                         raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
#             
#                 else:
#                     raise FailException("Failed to list vm %s" % rhevm_vm_name)
#          
#         else:
#             raise FailException("Failed to shutdown vm %s on rhevm" % rhevm_vm_name)
# 
# 
#     def get_vm_uuid_on_rhevm(self, vm_hostname, targetmachine_ip):
#         cmd = "list vms --show-all; exit"
#         ret, output = self.runcmd_rhevm(cmd, "list all vms in the rhevm.", targetmachine_ip)
#         if ret == 0:
#             vm_uuid = self.get_key_rhevm(output, "id", "name", vm_hostname, targetmachine_ip)
#             logger.info("%s's uuid is %s" % (vm_hostname, vm_uuid))
#             return vm_uuid
# 
#     def get_host_uuid_on_rhevm(self, host_hostname, targetmachine_ip):
#         cmd = "list hosts --show-all; exit"
#         ret, output = self.runcmd_rhevm(cmd, "list all hosts in the rhevm.", targetmachine_ip)
#         if ret == 0:
#             host_uuid = self.get_key_rhevm(output, "id", "name", host_hostname, targetmachine_ip)
#             logger.info("%s's uuid is %s" % (host_hostname, host_uuid))
#             return host_uuid
# 
#     def rhevm_get_hostuuid_from_list_vm(self, vm_hostname, targetmachine_ip):
#         cmd = "list vms --show-all; exit"
#         ret, output = self.runcmd_rhevm(cmd, "list all vms in the rhevm.", targetmachine_ip)
#         if ret == 0:
#             host_uuid = self.get_key_rhevm(output, "host-id", "name", vm_hostname, targetmachine_ip)
#             logger.info("%s's host uuid is %s" % (vm_hostname, host_uuid))
#             return host_uuid
#         
#     def rhevm_get_ip_from_hostuuid(self, host_uuid, targetmachine_ip):
#         cmd = "list hosts --show-all; exit"
#         ret, output = self.runcmd_rhevm(cmd, "list all hosts in the rhevm.", targetmachine_ip)
#         if ret == 0:
#             host_ip = self.get_key_rhevm(output, "address", "id", host_uuid, targetmachine_ip)
#             logger.info("%s's ip address is %s" % (host_uuid, host_ip))
#             return host_ip
#         else:
#             raise FailException("Guest failed to auto associate host.")
# 
# 
# # Check the host and guest uuid in rhsm.log
#     def rhevm_vw_check_uuid(self, hostuuid, rhevm_mode, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
#     # def vw_check_uuid(self, params, guestname, guestuuid="Default", uuidexists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
#         ''' check if the guest uuid is correctly monitored by virt-who. '''
#         rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
#         # self.vw_restart_virtwho(logger)
#         cmd = "tail -1 %s " % rhsmlogfile
#         ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
#         if ret == 0:
#             ''' get guest uuid.list from rhsm.log '''
#             if "Sending update in hosts-to-guests mapping: " in output:
#                 log_uuid_list = output.split('Sending update in hosts-to-guests mapping:')[1]
#                 logger.info("Succeeded to get uuid.list from rhsm.log.")
#                 if hostuuid is not "":
#                     hostloc = log_uuid_list.find(hostuuid)
#                     if rhevm_mode == "rhevm":
#                         if hostloc >= 0:
#                             khrightloc = log_uuid_list.find("[", hostloc, -1)
#                             khleftloc = log_uuid_list.find("]", hostloc, -1)
#                             # logstring = log_uuid_list[khrightloc,khleftloc]
#                             ptn = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
#                             ulst = ptn.findall(log_uuid_list[khrightloc:khleftloc])
#                             guestnum = len(ulst)
#                             if guestnum >= 0:
#                             # if logstring.find(guestuuid) >= 0:
#                                 logger.info("host and guest uuid associate correct, host has %s guest" % guestnum)
#                                 return (guestnum, ulst)
#                         else:
#                             raise FailException("host hasn't find out in the log")
#                 
#                     else:
#                         khrightloc = log_uuid_list.find("[", hostloc, -1)
#                         khleftloc = log_uuid_list.find("]", hostloc, -1)
#                         # logstring = log_uuid_list[khrightloc,khleftloc]
#                         ptn = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
#                         ulst = ptn.findall(log_uuid_list[khrightloc:khleftloc])
#                         guestnum = len(ulst)
#                         if guestnum >= 0:
#                         # if logstring.find(guestuuid) >= 0:
#                             logger.info("vdsm mode, there are %s hosts" % guestnum)
#                             return (guestnum, ulst)
#             else:
#                 raise FailException("log file has problem, please check it !")
#     
#                 
# # Get host num in the rhsm.log file.
#     def get_hostnum_rhsmlog(self, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
#         ''' Get the host number. '''
#         rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
#         # self.vw_restart_virtwho(logger)
#         cmd = "tail -1 %s " % rhsmlogfile
#         ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
#         if ret == 0:
#             ''' get host number from rhsm.log '''
#             if "Sending update in hosts-to-guests mapping: " in output:
#                 log_uuid_list = output.split('Sending update in hosts-to-guests mapping:')[1]
#                 logger.info("Succeeded to get host uuid.list from rhsm.log.")
#                 if log_uuid_list is not "":
#                     hostnum = log_uuid_list.count(':')
#                     logger.info("Succeeded to get the host number, Total host is %s" % hostnum)
#                     return hostnum
#                 else:
#                     raise FailException("Succeeded to get the host number")
#                     
# 
# # Get guest uuid in the rhsm.log file.
#     def get_guestid_rhsmlog(self, hostname, targetmachine_ip=""):
#         ''' Get the guestuuid. '''
#         cmd = "grep 'Sending update in hosts-to-guests mapping' /var/log/rhsm/rhsm.log | tail -1"
#         ret, output = self.runcmd(cmd, "get guest consumer uuid", targetmachine_ip)
#         if ret == 0:
#             guestuuid = output.split("['")[1].split("']")[0].strip()
#             return guestuuid
#         else:
#             raise FailException("Failed to get guestuuid in rhsm.log.")
# 
# 
# # Get host uuid in the rhsm.log file.
#     def get_hostid_rhsmlog(self, hostname, targetmachine_ip=""):
#         ''' Get the hostuuid. '''
#         cmd = "grep 'Sending update in hosts-to-guests mapping' /var/log/rhsm/rhsm.log | tail -1"
#         ret, output = self.runcmd(cmd, "get host consumer uuid", targetmachine_ip)
#         if ret == 0:
#             hostuuid = output.split("{'")[1].split("':")[0].strip()
#             return hostuuid
#         else:
#             raise FailException("Failed to get hostuuid in rhsm.log.")
# 
# 
#     def get_hostid(self, hostname, targetmachine_ip=""):
#         ''' Get the hostid. '''
#         availhostlist = self.sub_listavailhosts(hostname, targetmachine_ip)
#         if availhostlist != None:
#             for index in range(0, len(availhostlist)):
#                 if("name" in availhostlist[index] and availhostlist[index]["name"] == hostname):
#                     rindex = index
#                     break
#             hostid = availhostlist[rindex]["id"]
#             logger.info("Succeeded to get the %s's hostid." % hostname)
#             return hostid
#         else:
#             raise FailException("Failed to get the %s's hostid." % hostname)
# 
# 
#     
#         cmd = "wget -P /tmp/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/xml/6.4_Server_x86_64.xml"
#         ret, output = self.runcmd(cmd, "wget kvm xml file", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to wget xml img file")
#         else:
#             raise FailException("Failed to wget xml img file")
# 
#         cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
#         ret, output = self.runcmd(cmd, "define kvm guest", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to define kvm guest")
#         else:
#             raise FailException("Failed to define kvm guest")
# 
#             
# # Get the host/guest association in the SAM.
#     def Rhevm_check_guestinfo_in_host_samserv(self, uuid, non_key_value, key_value, find_value, targetmachine_ip=""):
#         ''' check rhevm host exist in sam server '''
#         cmd = "headpin -u admin -p admin system info --org=ACME_Corporation --uuid=%s" % uuid
#         ret, output = self.runcmd(cmd, "list host or guest's system info in the SAM.", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to list host or guest's system info on SAM.")
#             status = self.get_key_rhevm(output, non_key_value, key_value, find_value, targetmachine_ip)
#             return status
#         else:
#             logger.info("Failed to list host or guest's system info on SAM.")
# 
# # Get the uuid in the subscription-manager after register
#     def Rhevm_get_uuid_in_submanager(self, targetmachine_ip=""):
#         cmd = "subscription-manager identity | grep identity"
#         ret, output = self.runcmd(cmd, "get host subscription-manager identity", targetmachine_ip)
#         if ret == 0:
#             uuid = output.split(':')[1].strip()
#             logger.info("Succeeded to get host %s uuid %s " % (targetmachine_ip, uuid))
#             return uuid
#         else :
#             raise FailException("Failed to get host %s uuid " % (targetmachine_ip))
# 
#     # Check the consumed subscription after auto-assigned to another hosts
#     def rhevm_check_consumed_auto_assgin(self, targetmachine_ip):
#         ''' Register the machine. '''
#         cmd = "subscription-manager refresh"
#         ret, output = self.runcmd(cmd, "subscription-manager refresh", targetmachine_ip)
#         if ret == 0 or "All local data removed" in output:
#             logger.info("Succeeded to refresh all data on the system %s" % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to refresh all data on the system %s" % self.get_hg_info(targetmachine_ip))
# 
#         ''' List consumed entitlements. '''
#         cmd = "subscription-manager list --consumed"
#         ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
#         if ret == 0 and ("No Consumed" in output or "No consumed" in output):
#             logger.info("Succeeded to check no consumed subscription %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to check no consumed subscription %s." % self.get_hg_info(targetmachine_ip))
# 
# 
#     def sub_clean(self, targetmachine_ip=""):
#         ''' Clean all local data. '''
#         cmd = "subscription-manager clean"
#         ret, output = self.runcmd(cmd, "subscription-manager clean", targetmachine_ip)
#         if ret == 0 or "All local data removed" in output:
#             logger.info("Succeeded to clean all data on the system %s" % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Failed to clean all data on the system %s" % self.get_hg_info(targetmachine_ip))
# 
# 
#     # Clean rhevm env in the rhevm machine.
#     def rhevm_clean_env(self, targetmachine_ip=""):
#         cmd = "rhevm-cleanup -u"
#         ret, output = self.runcmd(cmd, "install vdsm", targetmachine_ip)
#         if ret == 0 and "finished successfully" in output:
#             logger.info("Succeeded to clean all environment in the rhevm-machine.")
#         else:
#             logger.info("Failed to clean all environment in the rhevm-machine.")
# 
#     # Set up rhevm env in rhevm machine.
#     def rhevm_setup_env(self, hostname, username, rhevmhostname, password, cmd):
#         """ Remote exec function via pexpect """
#         user_hostname = "%s@%s" % (username, hostname)
#         child = pexpect.spawn("/usr/bin/ssh", [user_hostname, cmd], timeout=1800, maxread=2000, logfile=None)
#         while True:
#             index = child.expect(['httpd configuration', 'HTTP Port', 'HTTPS Port', 'fully qualified domain', 'password', 'default storage type', 'DB type', 'NFS share', 'iptables', '(yes\/no)', pexpect.EOF, pexpect.TIMEOUT])
#             if index == 0:
#                 child.sendline("yes")
#             elif index == 1:
#                 child.sendline("80")
#             elif index == 2:
#                 child.sendline("443")
#             elif index == 3:
#                 child.sendline(rhevmhostname)
#             elif index == 4:
#                 child.sendline(password)
#             elif index == 5:
#                 child.sendline("NFS")
#             elif index == 6:
#                 child.sendline("local")
#             elif index == 7:
#                 child.sendline("no")
#             elif index == 8:
#                 child.sendline("iptables")
#             elif index == 9:
#                 child.sendline("yes")
#             elif index == 10:
#                 child.close()
#                 return child.exitstatus, child.before
#             elif index == 11:
#                 child.close()
#                 return 1, ""
#         return 0

