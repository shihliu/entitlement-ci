from utils import *
import time, random, commands
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.tools.virshcommand import VirshCommand

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

    def sys_setup(self):
        # system setup for virt-who testing
        cmd = "yum install -y virt-who"
#         cmd = "yum install -y @base @core @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization @desktop-debugging @dial-up @fonts @gnome-desktop @guest-desktop-agents @input-methods @internet-browser @multimedia @print-client @x11 nmap bridge-utils tunctl rpcbind qemu-kvm-tools expect pexpect git make gcc tigervnc-server"
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing.")
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing.")

    def kvm_sys_setup(self, targetmachine_ip=""):
        # system setup for virt-who testing
        # cmd = "yum install -y @base @core @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization @desktop-debugging @dial-up @fonts @gnome-desktop @guest-desktop-agents @input-methods @internet-browser @multimedia @print-client @x11 nmap bridge-utils tunctl rpcbind qemu-kvm-tools expect pexpect git make gcc tigervnc-server"
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, targetmachine_ip, targetmachine_user="root", targetmachine_pass="xxoo2014")
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        cmd = "service libvirtd start"
        ret, output = self.runcmd(cmd, targetmachine_ip, targetmachine_user="root", targetmachine_pass="xxoo2014")
        if ret == 0:
            logger.info("Succeeded to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))

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

    def kvm_setup(self):
        SAM_IP = get_exported_param("SAM_IP")
        SAM_HOSTNAME = get_exported_param("SAM_HOSTNAME")

        SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
        SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

        # configure and register the host
        if not self.sub_isregistered():
            self.configure_host(SAM_HOSTNAME, SAM_IP)
            self.sub_register(SAM_USER, SAM_PASS)
        # update virt-who configure file
        self.update_vw_configure()
        # restart virt-who service
        self.vw_restart_virtwho()
        # mount all needed guests
        self.mount_images()
        # add guests in host machine.
        self.vw_define_all_guests()


# (9)set up env for migration if needed
# if params.has_key("targetmachine_ip") and params.has_key("targetmachine_hostname"):
# logger.info("-------- Begin to set up env for migration -------- ")
# targetmachine_ip = params["targetmachine_ip"]
# targetmachine_hostname = params["targetmachine_hostname"]
# # 1)mount image path in target machine
# eu().mount_images_in_targetmachine( targetmachine_ip, ee.imagenfspath, ee.imagepath)
# # 2)mount the rhsm log of the target machine into source machine.
# eu().mount_rhsmlog_of_targetmachine( targetmachine_ip, ee.rhsmlog_for_targetmachine)
# # 3)update /etc/hosts file
# eu().update_hosts_file( targetmachine_ip, targetmachine_hostname)
# # 4)set cpu socket
# eu().set_cpu_socket( targetmachine_ip=targetmachine_ip)
# # 5)stop firewall of two host machines for migration
# eu().stop_firewall(logger)
# eu().stop_firewall( targetmachine_ip)
# # 6)update xen configuration file /etc/xen/xend-config.sxp of two host machines for migration to 
# # make sure contain necessary config options, and then restart service xend.
# if testtype == "xen":
# eu().update_xen_configure(logger)
# eu().update_xen_configure( targetmachine_ip)
# # 7)configure and register the host
# if not eu().sub_isregistered( targetmachine_ip):
# eu().configure_host( params.get("samhostname"), params.get("samhostip"), targetmachine_ip)
# username = eu().get_env(logger)["username"]
# password = eu().get_env(logger)["password"]
# eu().sub_register( username, password, targetmachine_ip)
# # disable autopool on remote host
# eu().sub_autopool( "disable", targetmachine_ip)
# # 8)update virt-who configure file
# eu().update_vw_configure( targetmachine_ip=targetmachine_ip)
# # 9)restart virt-who service in target machine
# eu().vw_restart_virtwho( targetmachine_ip)
# logger.info("-------- End to set up env for migration -------- ")
# else:
# logger.info("There is no target machine ip/hostname provided, so does not setup env for migration.")

    def vw_restart_virtwho(self, targetmachine_ip=""):
        ''' restart virt-who service. '''
        cmd = "service virt-who restart"
        ret, output = self.runcmd(cmd, "restart virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart virt-who service.")
        else:
            raise FailException("Test Failed - Failed to restart virt-who service.")

    def vw_stop_virtwho(self, targetmachine_ip=""):
        ''' stop virt-who service. '''
        cmd = "service virt-who stop"
        ret, output = self.runcmd(cmd, "stop virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to stop virt-who service.")
        else:
            raise FailException("Failed to stop virt-who service.")

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

    def sub_subscribe_to_bonus_pool(self, productid, guest_ip=""):
        ''' subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
        availpoollistguest = self.sub_listavailpools(productid, guest_ip)
        if availpoollistguest != None:
            rindex = -1
            for index in range(0, len(availpoollistguest)):
                if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and self.check_type_virtual(availpoollistguest[index])):
                    rindex = index
                    break
                elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and self.check_type_virtual(availpoollistguest[index])):
                    rindex = index
                    break
            if rindex == -1:
                raise FailException("Failed to show find the bonus pool")
            if "PoolID" in availpoollistguest[index]:
                gpoolid = availpoollistguest[rindex]["PoolID"]
            else:
                gpoolid = availpoollistguest[rindex]["PoolId"]
            self.sub_subscribetopool(gpoolid, guest_ip)
        else:
            raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % productid)

    def sub_subscribetopool(self, poolid, targetmachine_ip=""):
        ''' subscribe to a pool. '''
        cmd = "subscription-manager subscribe --pool=%s" % (poolid)
        ret, output = self.runcmd(cmd, "subscribe by --pool", targetmachine_ip)
        if ret == 0:
            if "Successfully " in output:
                logger.info("Succeeded to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to show correct information after subscribing %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))

    def sub_listconsumed(self, productname, targetmachine_ip="", productexists=True):
        ''' list consumed entitlements. '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
        if ret == 0:
            if productexists:
                if "No Consumed subscription pools to list" not in output:
                    if productname in output:
                        logger.info("Succeeded to list the right consumed subscription %s." % self.get_hg_info(targetmachine_ip))
                    else:
                        raise FailException("Failed to list consumed subscription %s - Not the right consumed subscription is listed!" % self.get_hg_info(targetmachine_ip))
                else:
                    raise FailException("Failed to list consumed subscription %s - There is no consumed subscription to list!")
            else:
                if productname not in output:
                    logger.info("Succeeded to check entitlements %s - the product '%s' is not subscribed now." % (self.get_hg_info(targetmachine_ip), productname))
                else:
                    raise FailException("Failed to check entitlements %s - the product '%s' is still subscribed now." % (self.get_hg_info(targetmachine_ip), productname))
        else:
            raise FailException("Failed to list consumed subscriptions.")

    def sub_refresh(self, targetmachine_ip=""):
        ''' refresh all local data. '''
        cmd = "subscription-manager refresh; sleep 10"
        ret, output = self.runcmd(cmd, "subscription fresh", targetmachine_ip)
        if ret == 0 and "All local data refreshed" in output:
            logger.info("Succeeded to refresh all local data %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to refresh all local data %s." % self.get_hg_info(targetmachine_ip))

    def check_type_virtual(self, pool_dict):
        if "MachineType" in pool_dict.keys():
            TypeName = "MachineType"
        elif "SystemType" in pool_dict.keys():
            TypeName = "SystemType"
        return pool_dict[TypeName] == "Virtual" or pool_dict[TypeName] == "virtual"

    #========================================================
    #     KVM Functions
    #========================================================
    def update_vw_configure(self, background=1, debug=1, targetmachine_ip=""):
        ''' update virt-who configure file /etc/sysconfig/virt-who. '''
        cmd = "sed -i -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' /etc/sysconfig/virt-who" % (debug)
        ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file.")
        else:
            raise FailException("Failed to update virt-who configure file.")

    def mount_images(self):
        ''' mount the images prepared '''
        image_server = VIRTWHOConstants().get_constant("beaker_image_server")
#         image_path = VIRTWHOConstants().get_constant("local_image_path")
        image_nfs_path = VIRTWHOConstants().get_constant("nfs_image_path")
        image_mount_path = VIRTWHOConstants().get_constant("local_mount_point")
        cmd = "mkdir %s" % image_mount_path
        self.runcmd(cmd, "create local images mount point")
#         cmd = "mkdir %s" % image_path
#         self.runcmd(cmd, "create local images directory")
        cmd = "mkdir %s" % image_nfs_path
        self.runcmd(cmd, "create local nfs images directory")
        cmd = "mount -r %s %s; sleep 10" % (image_server, image_mount_path)
        ret, output = self.runcmd(cmd, "mount images in host")
        if ret == 0:
            logger.info("Succeeded to mount images from %s to %s." % (image_server, image_mount_path))
        else:
            raise FailException("Failed to mount images from %s to %s." % (image_server, image_mount_path))

        logger.info("Begin to copy guest images...")

        cmd = "cp -n %s %s" % (os.path.join(image_mount_path, "ENT_TEST_MEDIUM/images/kvm/*"), image_nfs_path)
        ret, output = self.runcmd(cmd, "copy all kvm images")
#         if ret == 0:
#             logger.info("Succeeded to copy guest images to host machine.")
#         else:
#             raise FailException("Failed to copy guest images to host machine.")

        cmd = "umount %s" % (image_mount_path)
        ret, output = self.runcmd(cmd, "umount images in host")

        cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (image_nfs_path.replace('/', '\/'), image_nfs_path)
        ret, output = self.runcmd(cmd, "set /etc/exports for nfs")
        if ret == 0:
            logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % image_nfs_path)
        else:
            raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % image_nfs_path)
        cmd = "service nfs restart"
        ret, output = self.runcmd(cmd, "restarting nfs service")
        if ret == 0 :
            logger.info("Succeeded to restart service nfs.")
        else:
            raise FailException("Failed to restart service nfs.")
        cmd = "rpc.mountd"
        ret, output = self.runcmd(cmd, "rpc.mountd")
        cmd = "showmount -e 127.0.0.1"
        ret, output = self.runcmd(cmd, "showmount")
        if ret == 0 and (image_nfs_path in output):
            logger.info("Succeeded to export dir '%s' as nfs." % image_nfs_path)
        else:
            raise FailException("Failed to export dir '%s' as nfs." % image_nfs_path)

#         cmd = "mount %s:%s %s" % ("127.0.0.1", image_nfs_path, image_path)
#         ret, output = self.runcmd(cmd, "mount nfs images in host machine")
#         if ret == 0 or "is busy or already mounted" in output:
#             logger.info("Succeeded to mount nfs images in host machine.")
#         else:
#             raise FailException("Failed to mount nfs images in host machine.")

    def vw_define_all_guests(self, targetmachine_ip=""):
        guest_path = VIRTWHOConstants().get_constant("nfs_image_path")
        for guestname in self.get_all_guests_list(guest_path):
            VirshCommand().define_vm(guestname, os.path.join(guest_path, guestname))

    def get_all_guests_list(self, guest_path, targetmachine_ip=""):
        cmd = "ls %s" % guest_path
        ret, output = self.runcmd(cmd, "get all guest in images folder", targetmachine_ip)
        if ret == 0 :
            guest_list = output.strip().split("\n")
            logger.info("Succeeded to get all guest list %s in %s." % (guest_list, guest_path))
            return guest_list
        else:
            raise FailException("Failed to get all guest list in %s." % guest_path)


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

    def esx_remove_guest(self, guest_name, destination_ip):
        ''' remove guest from esx '''
        cmd = "vim-cmd vmsvc/unregister /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "remove guest '%s' from ESX" % guest_name, destination_ip)
        if ret == 0:
            logger.info("Succeeded to remove guest '%s' from ESX" % guest_name)
        else:
            raise FailException("Failed to remove guest '%s' from ESX" % guest_name)

    def esx_destroy_guest(self, guest_name, esx_host):
        ''' destroy guest from esx'''
        cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
        ret, output = self.runcmd_esx(cmd, "destroy guest '%s' in ESX" % guest_name, esx_host)
        if ret == 0:
            logger.info("Succeeded to destroy guest '%s'" % guest_name)
        else:
            raise FailException("Failed to destroy guest '%s'" % guest_name)
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
        self.vw_restart_virtwho()
        self.vw_restart_virtwho()
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
        self.vw_restart_virtwho()
        self.vw_restart_virtwho()
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
        self.vw_restart_virtwho()
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
