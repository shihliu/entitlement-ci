from utils import *
import time, random, commands, paramiko
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.libvirtAPI.Python.xmlbuilder import XmlBuilder
import json
import requests

class VIRTWHOBase(unittest.TestCase):
    # ========================================================
    #       Basic Functions
    # ========================================================

    def runcmd(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        if targetmachine_ip != None and targetmachine_ip != "":
            if targetmachine_user != None and targetmachine_user != "":
                commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
            else:
                commander = Command(targetmachine_ip, "root", "red2015")
        else:
            commander = Command(get_exported_param("REMOTE_IP"), "root", "red2015")
        return commander.run(cmd, timeout, cmddesc, showlogger)

    def runcmd_esx(self, cmd, cmddesc=None, targetmachine_ip=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "qwer1234P!", timeout, showlogger)

    def runcmd_sam(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "redhat", timeout, showlogger)

    def runcmd_interact(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        if targetmachine_ip != None and targetmachine_ip != "":
            if targetmachine_user != None and targetmachine_user != "":
                commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
            else:
                commander = Command(targetmachine_ip, "root", "red2015")
        else:
            commander = Command(get_exported_param("REMOTE_IP"), "root", "red2015")
        return commander.run_interact(cmd, timeout, cmddesc)

#     def runcmd_guest(self, cmd, cmddesc=None, targetmachine_ip=None, timeout=None, showlogger=True):
#         return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "redhat", timeout, showlogger)

    def brew_virtwho_upgrate(self, targetmachine_ip=None):
        # virt-who upgrade via brew
        brew_virt_who = get_exported_param("BREW_VIRTWHO")
        cmd = "yum -y upgrade %s" % brew_virt_who
        ret, output = self.runcmd(cmd, "upgrade virt-who via brew", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to upgrade virt-who via brew.")
#         else:
#             raise FailException("Test Failed - Failed to upgrade virt-who via brew.")

    def sys_setup(self):
        # system setup for virt-who testing
        cmd = "yum install -y virt-who"
#         cmd = "yum install -y @base @core @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization @desktop-debugging @dial-up @fonts @gnome-desktop @guest-desktop-agents @input-methods @internet-browser @multimedia @print-client @x11 nmap bridge-utils tunctl rpcbind qemu-kvm-tools expect pexpect git make gcc tigervnc-server"
        ret, output = self.runcmd(cmd, "install virt-who for esx testing", showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing.")
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing.")

    def kvm_sys_setup(self, targetmachine_ip=""):
        # system setup for virt-who testing
        # cmd = "yum install -y @base @core @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization @desktop-debugging @dial-up @fonts @gnome-desktop @guest-desktop-agents @input-methods @internet-browser @multimedia @print-client @x11 nmap bridge-utils tunctl rpcbind qemu-kvm-tools expect pexpect git make gcc tigervnc-server"
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        self.kvm_bridge_setup(targetmachine_ip)
        self.kvm_permission_setup(targetmachine_ip)
        cmd = "service libvirtd start"
        ret, output = self.runcmd(cmd, "restart libvirtd service", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def install_desktop(self, targetmachine_ip=""):
        if self.get_os_serials() == "7":
            cmd = "yum install -y @gnome-desktop tigervnc-server"
            ret, output = self.runcmd(cmd, "install desktop and tigervnc", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install @gnome-desktop tigervnc-server")
            else:
                raise FailException("Test Failed - Failed to install @gnome-desktop tigervnc-server")
        else:
            cmd = "yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform'"
            ret, output = self.runcmd(cmd, "install desktop", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install 'X Window System' 'Desktop' 'Desktop Platform'")
            else:
                raise FailException("Test Failed - Failed to install 'X Window System' 'Desktop' 'Desktop Platform'")
            cmd = "yum install -y tigervnc-server"
            ret, output = self.runcmd(cmd, "install tigervnc", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install tigervnc-server")
            else:
                raise FailException("Test Failed - Failed to install tigervnc-server")
        cmd = "ps -ef | grep Xvnc | grep -v grep"
        ret, output = self.runcmd(cmd, "check whether vpncserver has started", targetmachine_ip,)
        if ret == 0:
            logger.info("vncserver already started ...")
        else:
            cmd = "vncserver -SecurityTypes None"
            ret, output = self.runcmd(cmd, "start vncserver", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to start vncserver")
            else:
                raise FailException("Test Failed - Failed to start vncserver")

    def kvm_bridge_setup(self, targetmachine_ip=""):
        network_dev = ""
        cmd = "ip route | grep `hostname -I | awk {'print $1'}` | awk {'print $3'}"
        ret, output = self.runcmd(cmd, "get network device", targetmachine_ip)
        if ret == 0:
            network_dev = output.strip()
            logger.info("Succeeded to get network device in %s." % self.get_hg_info(targetmachine_ip))
            if not "switch" in output:
                cmd = "sed -i '/^BOOTPROTO/d' /etc/sysconfig/network-scripts/ifcfg-%s; echo \"BRIDGE=switch\" >> /etc/sysconfig/network-scripts/ifcfg-%s;echo \"DEVICE=switch\nBOOTPROTO=dhcp\nONBOOT=yes\nTYPE=Bridge\"> /etc/sysconfig/network-scripts/ifcfg-br0" % (network_dev, network_dev)
                ret, output = self.runcmd(cmd, "setup bridge for kvm testing", targetmachine_ip)
                if ret == 0:
                    logger.info("Succeeded to set /etc/sysconfig/network-scripts in %s." % self.get_hg_info(targetmachine_ip))
                else:
                    raise FailException("Test Failed - Failed to /etc/sysconfig/network-scripts in %s." % self.get_hg_info(targetmachine_ip))
                self.service_command("restart_network", targetmachine_ip)
            else:
                logger.info("Bridge already setup for virt-who testing, do nothing ...")
        else:
            raise FailException("Test Failed - Failed to get network device in %s." % self.get_hg_info(targetmachine_ip))

    def kvm_permission_setup(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/#user = \"root\"/user = \"root\"/g' -e 's/#group = \"root\"/group = \"root\"/g' -e 's/#dynamic_ownership = 1/dynamic_ownership = 1/g' /etc/libvirt/qemu.conf"
        ret, output = self.runcmd(cmd, "setup kvm permission", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set /etc/libvirt/qemu.conf in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to set /etc/libvirt/qemu.conf in %s." % self.get_hg_info(targetmachine_ip))

    def stop_firewall(self, targetmachine_ip=""):
        ''' stop iptables service and setenforce as 0. '''
        # stop iptables service
        cmd = "service iptables stop"
        ret, output = self.runcmd(cmd, "Stop iptables service", targetmachine_ip)
        cmd = "service iptables status"
        ret, output = self.runcmd(cmd, "Chech iptables service status", targetmachine_ip)
        if ("Firewall is stopped" in output) or ("Firewall is not running" in output) or ("Active: inactive" in output):
            logger.info("Succeeded to stop iptables service.")
        else:
            logger.info("Failed to stop iptables service.")
        # setenforce as 0
        cmd = "setenforce 0"
        ret, output = self.runcmd(cmd, "Set setenforce 0", targetmachine_ip)
#         cmd = "sestatus"
#         ret, output = self.runcmd(cmd, "Check selinux status", targetmachine_ip)
#         if ret == 0 and "permissive" in output:
#             logger.info("Succeeded to setenforce as 0.")
#         else:
#             raise FailException("Failed to setenforce as 0.")
        # unfinished, close firewall and iptables for ever 

    def esx_setup(self):
        SAM_IP = get_exported_param("SERVER_IP")
        SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")

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
        # if host was already registered for hyperV, need to unregistered firstly, and then config and register the host again
        self.sub_unregister()
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
        SERVER_TYPE = get_exported_param("SERVER_TYPE")
        SERVER_IP = SERVER_HOSTNAME = SERVER_USER = SERVER_PASS = ""
        if SERVER_TYPE == "STAGE":
            SERVER_USER = VIRTWHOConstants().get_constant("STAGE_USER")
            SERVER_PASS = VIRTWHOConstants().get_constant("STAGE_PASS")
        else:
            SERVER_IP = get_exported_param("SERVER_IP")
            SERVER_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SERVER_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SERVER_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_host(SERVER_HOSTNAME, SERVER_IP)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_vw_configure()
        # restart virt-who service
        self.vw_restart_virtwho()
        # mount all needed guests
        self.mount_images()
        # add guests in host machine.
        self.vw_define_all_guests()
        # configure slave machine
        slave_machine_ip = get_exported_param("REMOTE_IP_2")
        if slave_machine_ip != None and slave_machine_ip != "":
            # if host already registered, unregister it first, then configure and register it
            self.sub_unregister(slave_machine_ip)
            self.configure_host(SERVER_HOSTNAME, SERVER_IP, slave_machine_ip)
            self.sub_register(SERVER_USER, SERVER_PASS, slave_machine_ip)
            image_nfs_path = VIRTWHOConstants().get_constant("nfs_image_path")
            self.mount_images_in_slave_machine(slave_machine_ip, image_nfs_path, image_nfs_path)
            self.update_vw_configure(slave_machine_ip)
            self.vw_restart_virtwho(slave_machine_ip)

    def above_7_serials(self, targetmachine_ip):
        cmd = "echo $(python -c \"import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)\" | grep 'releasever' | awk -F\":\" '{print $2}' | sed  -e \"s/^ '//\" -e \"s/'}$//\" -e \"s/',$//\")"
        ret, output = self.runcmd(cmd, "get rhel version", targetmachine_ip)
        if output[0:1] >= 7:
            logger.info("System version is above or equal 7 serials")
            return True
        else:
            logger.info("System version is bellow 7 serials")
            return False

    # ==============Satellite CLI=======================
    # List system
    def st_system_list(self):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems" % server_ip
        res = requests.get(api_url, auth=(username, password), verify=False)
        return res.json()

    # List pool list
    def st_pool_list(self, uuid):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions/available" % (server_ip, uuid)
        res = requests.get(api_url, auth=(username, password), verify=False)
        return res.json()

    # Attach pool_id 
    def st_attach(self, uuid, pool_id):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions" % (server_ip, uuid)
        post_headers = {'content-type': 'application/json'}
        json_data = json.dumps({"uuid":uuid, "subscriptions":[{"id":pool_id, "quantity":0}]})
        res = requests.post(
              api_url,
              data=json_data,
              auth=(username, password),
              verify=False,
              headers=post_headers)
        return res.json()

    # List consumed 
    def st_consumed_list(self, uuid):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions" % (server_ip, uuid)
        res = requests.get(api_url, auth=(username, password), verify=False)
        return res.json()

    # Unattach poo_id
    def st_unattach(self, uuid, pool_id):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions" % (server_ip, uuid)
        post_headers = {'content-type': 'application/json'}
        json_data = json.dumps({"uuid":uuid, "subscriptions":[{"subscription_id":pool_id}]})
        res = requests.put(
              api_url,
              data=json_data,
              auth=(username, password),
              verify=False,
              headers=post_headers,)
        return res.json()

    # only return CLI for virt-who esx mode, don't run cli 
    def virtwho_cli(self, mode):
        esx_owner = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
        esx_env = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
        esx_server = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
        esx_username = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
        esx_password = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")

        if mode == "esx":
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password)
        else:
            raise FailException("Failed to execute virt-who with one shot")
        return cmd

    # run virt-who oneshot by cli, return the output
    def virtwho_oneshot(self, mode, targetmachine_ip=""):
        cmd = self.virtwho_cli(mode) + " -o -d "
        self.service_command("stop_virtwho")
        ret, output = self.runcmd(cmd, "executing virt-who with one shot")
        self.service_command("restart_virtwho")
        if ret == 0:
            logger.info("Succeeded to execute virt-who with one shot ")
            return ret, output
        else:
            raise FailException("Failed to execute virt-who with one shot")
    
    # check uuid from oneshot output 
    def check_uuid_oneshot(self, uuid, mode, targetmachine_ip=""):
        ret, output = self.virtwho_oneshot(mode, targetmachine_ip)
        if uuid in output:
            return True
        else:
            return False 

    # check systemd service is exist or not
    def check_systemctl_service(self, keyword, targetmachine_ip=""):
        cmd = "systemctl list-units|grep %s -i" % keyword
        ret, output = self.runcmd(cmd, "check %s service by systemctl" % keyword, targetmachine_ip)
        if ret == 0:
            return True
        return False

    # check virt-who servcie status, rhel7:"active" "failed" "unknown", rhel6:"running" "stopped"
    def check_virtwho_status(self, targetmachine_ip=""):
        if self.check_systemctl_service("virt-who", targetmachine_ip):
            # will feedback "active" "failed" "unknow"
            cmd = "systemctl is-active virt-who"
            ret, output = self.runcmd(cmd, "check virt-who service by systemctl.", targetmachine_ip)
            return output.strip()
        else:
            # will feedback "running" "stopped" "failed"
            cmd = "service virt-who status"
            ret, output = self.runcmd(cmd, "check virt-who service status by sysvinit", targetmachine_ip)
            if "running" in output:
                return "running"
            elif "stopped" in output:
                return "stopped"
            else:
                return "failed"

    def service_command(self, command, targetmachine_ip="", is_return=False):
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = VIRTWHOConstants().virt_who_commands[command + "_systemd"]
        else:
            cmd = VIRTWHOConstants().virt_who_commands[command]
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if is_return == True:
            if ret == 0:
                logger.info("Succeeded to run cmd %s in %s." % (cmd, self.get_hg_info(targetmachine_ip)))
                return True
            else:
                return False
        else:
            if ret == 0:
                logger.info("Succeeded to run cmd %s in %s." % (cmd, self.get_hg_info(targetmachine_ip)))
                return output
            else:
                raise FailException("Test Failed - Failed to run cmd in %s." % (cmd, self.get_hg_info(targetmachine_ip)))

    def get_os_serials(self, targetmachine_ip=""):
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = self.runcmd(cmd, "", targetmachine_ip, showlogger=False)
        if ret == 0:
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Failed to get os serials")

    def vw_restart_virtwho(self, targetmachine_ip=""):
        ''' restart virt-who service. '''
        cmd = "service virt-who restart"
        ret, output = self.runcmd(cmd, "restart virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart virt-who service.")
        else:
            raise FailException("Test Failed - Failed to restart virt-who service.")

    def check_virtwho_thread(self, targetmachine_ip=""):
        ''' check virt-who thread number '''
        cmd = "ps -ef | grep -v grep | grep virt-who |wc -l"
        ret, output = self.runcmd(cmd, "check virt-who thread", targetmachine_ip)
        if ret == 0 and output.strip() == "2":
            logger.info("Succeeded to check virt-who thread number is 2.")
        else:
            raise FailException("Test Failed - Failed to check virt-who thread number is 2.")

    def config_virtwho_interval(self, interval_value, targetmachine_ip=""):
        # clean # for VIRTWHO_INTERVAL 
        cmd = "sed -i 's/^#VIRTWHO_INTERVAL/VIRTWHO_INTERVAL/' /etc/sysconfig/virt-who"
        (ret, output) = self.runcmd(cmd, "uncomment VIRTWHO_INTERVAL firstly in virt-who config file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to uncomment VIRTWHO_INTERVAL.")
        else:
            raise FailException("Failed to uncomment VIRTWHO_INTERVAL.")

        # set VIRTWHO_INTERVAL value
        cmd = "sed -i 's/^VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/' /etc/sysconfig/virt-who" % interval_value
        (ret, output) = self.runcmd(cmd, "set VIRTWHO_INTERVAL to %s" % interval_value, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set VIRTWHO_INTERVAL=%s" % interval_value)
        else:
            raise FailException("Failed to set VIRTWHO_INTERVAL=%s" % interval_value)

    def unset_esx_conf(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/^VIRTWHO_ESX/#VIRTWHO_ESX/g' -e 's/^VIRTWHO_ESX_OWNER/#VIRTWHO_ESX_OWNER/g' -e 's/^VIRTWHO_ESX_ENV/#VIRTWHO_ESX_ENV/g' -e 's/^VIRTWHO_ESX_SERVER/#VIRTWHO_ESX_SERVER/g' -e 's/^VIRTWHO_ESX_USERNAME/#VIRTWHO_ESX_USERNAME/g' -e 's/^VIRTWHO_ESX_PASSWORD/#VIRTWHO_ESX_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "unset virt-who configure file for disable VIRTWHO_ESX", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to disable VIRTWHO_ESX.")
        else:
            raise FailException("Test Failed - Failed to disable VIRTWHO_ESX.")

    def set_esx_conf(self, targetmachine_ip=""):
        VIRTWHO_ESX_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
        VIRTWHO_ESX_ENV = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
        VIRTWHO_ESX_SERVER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
        VIRTWHO_ESX_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
        VIRTWHO_ESX_PASSWORD = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")

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

    def set_virtwho_d_conf(self, file_name, file_data, targetmachine_ip=""):
        cmd = '''cat > %s <<EOF
%s 
EOF''' % (file_name, file_data)
        ret, output = self.runcmd(cmd, "create config file: %s" % file_name, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to create config file: %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to create config file %s" % file_name)

    def unset_virtwho_d_conf(self, file_name, targetmachine_ip=""):
        cmd = "rm -f %s" % file_name
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to remove %s" % file_name)

    def run_virt_who_password(self, input_password, timeout=None):
        import paramiko
        remote_ip = get_exported_param("REMOTE_IP")
        username = get_exported_param("REMOTE_USER")
        password = get_exported_param("REMOTE_PASSWD")
        virt_who_password_cmd = "python /usr/share/virt-who/virtwhopassword.py" 
        logger.info("run command %s in %s" % (virt_who_password_cmd, remote_ip))
        
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        channel = ssh.get_transport().open_session()
        channel.settimeout(600)
        channel.get_pty()
        channel.exec_command(virt_who_password_cmd)
        output = ""
        while True:
            data = channel.recv(1048576)
            output += data
            if channel.send_ready():
                if data.strip().endswith('Password:'):
                    channel.send(input_password + '\n')
                if channel.exit_status_ready():
                    break
        if channel.recv_ready():
            data = channel.recv(1048576)
            output += data

        if channel.recv_exit_status() == 0 and output is not None:
            logger.info("Succeeded to encode password: %s" % input_password)
            encode_password = output.split('\n')[2].strip()
            return encode_password 
        else:
            raise FailException("Failed to encode virt-who-password.")

    def vw_stop_virtwho(self, targetmachine_ip=""):
        ''' stop virt-who service. '''
        cmd = "service virt-who stop"
        ret, output = self.runcmd(cmd, "stop virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to stop virt-who service.")
        else:
            raise FailException("Failed to stop virt-who service.")

    def vw_restart_libvirtd(self, targetmachine_ip=""):
        ''' restart libvirtd service. '''
        cmd = "service libvirtd restart"
        ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart libvirtd service.")
        else:
            raise FailException("Test Failed - Failed to restart libvirtd")

    def vw_restart_virtwho_new(self, targetmachine_ip=""):
        if self.check_systemctl_service("virt-who", targetmachine_ip):
            cmd = "systemctl restart virt-who.service; sleep 10"
            ret, output = self.runcmd(cmd, "restart virt-who service by systemctl.", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart virt-who")
            else:
                raise FailException("Test Failed - Failed to restart virt-who")
        else:
            cmd = "service virt-who restart; sleep 10"
            ret, output = self.runcmd(cmd, "restart virt-who by service", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart virt-who")
            else:
                raise FailException("Test Failed - Failed to restart virt-who")

    def vw_stop_virtwho_new(self, targetmachine_ip=""):
        if self.check_systemctl_service("virt-who", targetmachine_ip):
            cmd = "systemctl stop virt-who.service; sleep 10"
            ret, output = self.runcmd(cmd, "stop virt-who service by systemctl.", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to stop virt-who")
            else:
                raise FailException("Test Failed - Failed to stop virt-who")
        else:
            cmd = "service virt-who stop; sleep 10"
            ret, output = self.runcmd(cmd, "stop virt-who by service", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to stop virt-who")
            else:
                raise FailException("Test Failed - Failed to stop virt-who")

    def vw_check_virtwho_status(self, targetmachine_ip=""):
        ''' Check the virt-who status. '''
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "systemctl status virt-who; sleep 10"
            ret, output = self.runcmd(cmd, "virt-who status", targetmachine_ip)
            if ret == 0 and "running" in output:
            # if ret == 0:
                logger.info("Succeeded to check virt-who is running.")
            else:
                raise FailException("Test Failed - Failed to check virt-who is running.")
        else:
            cmd = "service virt-who status; sleep 10"
            ret, output = self.runcmd(cmd, "virt-who status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check virt-who is running.")
            else:
                raise FailException("Test Failed - Failed to check virt-who is running.")

    def vw_check_libvirtd_status(self, targetmachine_ip=""):
        ''' Check the libvirtd status. '''
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "systemctl status libvirtd; sleep 10"
            ret, output = self.runcmd(cmd, "virt-who status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check libvirtd is running.")
            else:
                raise FailException("Test Failed - Failed to check libvirtd is running.")
        else:
            cmd = "service libvirtd status; sleep 10"
            ret, output = self.runcmd(cmd, "libvirtd status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check libvirtd is running.")
                self.SET_RESULT(0)
            else:
                raise FailException("Test Failed - Failed to check libvirtd is running.")

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

            # need to clean local data after unregister
            cmd = "subscription-manager clean"
            ret, output = self.runcmd(cmd, "clean system", targetmachine_ip)
            if ret == 0 :
                logger.info("Succeeded to clean %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to clean %s." % self.get_hg_info(targetmachine_ip))
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
        server_type = get_exported_param("SERVER_TYPE")
        if server_type == "SAM" or  server_type == "SATELLITE":
            # add sam hostip and hostname in /etc/hosts
            if "satellite" in samhostname:
                # for satellite installed in qeos
                samhostname = samhostname + ".novalocal"
            cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
            ret, output = self.runcmd(cmd, "configure /etc/hosts", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_hg_info(targetmachine_ip)))
            else:
                raise FailException("Failed to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_hg_info(targetmachine_ip)))
            # config hostname, prefix, port, baseurl and repo_ca_crt by installing candlepin-cert
            cmd = "rpm -qa | grep candlepin-cert-consumer| xargs rpm -e; rpm -qa | grep katello-ca-consumer | xargs rpm -e"
            ret, output = self.runcmd(cmd, "if sam or satellite cert package exist, remove it.", targetmachine_ip)
            cmd = "subscription-manager clean"
            ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)
            if server_type == "SATELLITE":
                cmd = "rpm -ivh http://%s/pub/katello-ca-consumer-latest.noarch.rpm" % (samhostip)
                ret, output = self.runcmd(cmd, "install katello-ca-consumer-latest.noarch.rpm", targetmachine_ip)
                if ret == 0:
                    logger.info("Succeeded to install candlepin cert and configure the system with satellite configuration as %s." % samhostip)
                else:
                    raise FailException("Failed to install candlepin cert and configure the system with satellite configuration as %s." % samhostip)
            else:
                cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
                ret, output = self.runcmd(cmd, "install candlepin-cert-consumer..rpm", targetmachine_ip)
                if ret == 0:
                    logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
                else:
                    raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        elif server_type == "STAGE":
            # configure /etc/rhsm/rhsm.conf to stage candlepin
            cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = subscription.rhn.stage.redhat.com/g' /etc/rhsm/rhsm.conf"
            ret, output = self.runcmd(cmd, "configure /etc/rhsm/rhsm.conf for stage testing", targetmachine_ip)
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

    # used to parse the output for "subscribe list --installed"
    def __parse_installed_lines(self, output):
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
            if ("Ends:" in line):
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

    def get_pool_by_SKU(self, SKU_id, guest_ip=""):
        ''' get_pool_by_SKU '''
        availpoollistguest = self.sub_listavailpools(SKU_id, guest_ip)
        if availpoollistguest != None:
            for index in range(0, len(availpoollistguest)):
                if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
                    rindex = index
                    break
            if "PoolID" in availpoollistguest[index]:
                gpoolid = availpoollistguest[rindex]["PoolID"]
            else:
                gpoolid = availpoollistguest[rindex]["PoolId"]
            return gpoolid
        else:
            logger.error("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)
            self.SET_RESULT(1)

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

    def sub_subscribe_sku(self, sku, targetmachine_ip=""):
        ''' subscribe by sku. '''
        availpoollist = self.sub_listavailpools(sku, targetmachine_ip)
        if availpoollist != None:
            rindex = -1
            for index in range(0, len(availpoollist)):
                if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku):
                    rindex = index
                    break
                elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == sku):
                    rindex = index
                    break
            if rindex == -1:
                raise FailException("Failed to show find the bonus pool")
            if "PoolID" in availpoollist[index]:
                poolid = availpoollist[rindex]["PoolID"]
            else:
                poolid = availpoollist[rindex]["PoolId"]
            self.sub_subscribetopool(poolid, targetmachine_ip)
        else:
            raise FailException("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % sku)

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

    def sub_limited_subscribetopool(self, poolid, quality, targetmachine_ip=""):
        ''' subscribe to a pool. '''
        cmd = "subscription-manager subscribe --pool=%s --quantity=%s" % (poolid, quality)
        ret, output = self.runcmd(cmd, "subscribe by --pool --quanitity", targetmachine_ip)
        if ret == 0:
            if "Successfully " in output:
                logger.info("Succeeded to subscribe to limited pool %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to show correct information after subscribing %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))

    def sub_disable_auto_subscribe(self, targetmachine_ip=""):
        ''' Disable subscribe subscribe  '''
        cmd = "subscription-manager auto-attach --disable"
        ret, output = self.runcmd(cmd, "Disable auto-attach", targetmachine_ip)
        if ret == 0 and "disabled" in output:
            logger.info("Succeeded to Disable auto-attach %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to Disable auto-attach %s." % self.get_hg_info(targetmachine_ip))

    def sub_auto_subscribe(self, targetmachine_ip=""):
        ''' subscribe to a pool by auto '''
        cmd = "subscription-manager subscribe --auto"
        ret, output = self.runcmd(cmd, "subscribe by --auto", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))

    def sub_unsubscribe(self, targetmachine_ip=""):
        ''' unsubscribe from all entitlements. '''
        cmd = "subscription-manager unsubscribe --all"
        ret, output = self.runcmd(cmd, "unsubscribe all", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to unsubscribe all in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to unsubscribe all in %s." % self.get_hg_info(targetmachine_ip))

    def sub_listconsumed(self, productname, targetmachine_ip="", productexists=True):
        ''' list consumed entitlements. '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
        if ret == 0:
            if productexists:
                if "No consumed subscription pools to list" not in output:
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

    # check "subscription-manager list --consumed" key & value 
    def check_consumed_status(self, sku_id, key="", value="", targetmachine_ip=""):
        ''' check consumed entitlements status details '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
        if ret == 0 and output is not None:
            consumed_lines = self.__parse_avail_pools(output)
            if consumed_lines != None:
                for line in range(0, len(consumed_lines)):
                    if key is not None and value is not None: 
                        if consumed_lines[line]["SKU"] == sku_id and consumed_lines[line][key] == value:
                            logger.info("Succeeded to list the right consumed subscription %s." % self.get_hg_info(targetmachine_ip))
                            return True
                    else:
                        if consumed_lines[line]["SKU"] == sku_id:
                            return True
            return False
        raise FailException("Failed to list consumed subscriptions.")

    # check "subscription-manager list --installed" key & value 
    def check_installed_status(self, key, value, targetmachine_ip=""):
        ''' check the installed entitlements. '''
        cmd = "subscription-manager list --installed"
        ret, output = self.runcmd(cmd, "list installed subscriptions", targetmachine_ip)
        if ret == 0 and output is not None :
            installed_lines = self.__parse_installed_lines(output)
            if installed_lines != None:
                for line in range(0, len(installed_lines)):
                    if installed_lines[line][key] == value:
                        return True
            return False
        raise FailException("Failed to list installed info.")

    # check ^Certificate: or ^Content: in cert file
    def check_cert_file(self, keywords, targetmachine_ip=""):
        cmd = "rct cat-cert /etc/pki/entitlement/*[^-key].pem | grep -A5 \"%s\"" % keywords
        ret, output = self.runcmd(cmd, "Check %s exist in cert file in guest" % keywords, targetmachine_ip)
        if ret == 0:
            return True
        return False

    # check ^Repo ID by subscription-manager repos --list 
    def check_yum_repo(self, keywords, targetmachine_ip=""):
        cmd = "subscription-manager repos --list | grep -A4 \"^Repo ID\""
        ret, output = self.runcmd(cmd, "Check repositories available in guest", targetmachine_ip)
        if ret == 0 and "This system has no repositories available through subscriptions." not in output:
            return True
        return False

    # get sku attribute value 
    def get_SKU_attribute(self, sku_id, attribute_key, targetmachine_ip=""):
        poollist = self.sub_listavailpools(sku_id, targetmachine_ip)
        if poollist != None:
            for index in range(0, len(poollist)):
                if("SKU" in poollist[index] and poollist[index]["SKU"] == sku_id):
                    rindex = index
                    break
            if attribute_key in poollist[index]:
                attribute_value = poollist[rindex][attribute_key]
                return attribute_value
            raise FailException("Failed to check, the attribute_key is not exist.")
        else:
            raise FailException("Failed to list available subscriptions")
                
    def sub_refresh(self, targetmachine_ip=""):
        ''' sleep 20 seconds firstly due to guest restart, and then refresh all local data. '''
        cmd = "sleep 20; subscription-manager refresh"
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

    def check_bonus_isExist(self, sku_id, bonus_quantity, targetmachine_ip=""):
        # check bonus pool is exist or not
        cmd = "subscription-manager list --available"
        ret, output = self.runcmd(cmd, "run 'subscription-manager list --available'", targetmachine_ip)
        if ret == 0:
            if "No Available subscription pools to list" not in output:
                pool_list = self.__parse_avail_pools(output)
                if pool_list != None:
                    for item in range(0, len(pool_list)):
                        if "Available" in pool_list[item]:
                            SKU_Number = "Available"
                        else:
                            SKU_Number = "Quantity"
                        if pool_list[item]["SKU"] == sku_id and self.check_type_virtual(pool_list[item]) and pool_list[item][SKU_Number] == bonus_quantity:
                            return True
                    return False
                else:
                    raise FailException("Failed to list available pool, the pool is None.")
            else:
                raise FailException("Failed to list available pool, No Available subscription pools to list.")
        else:
            raise FailException("Failed to run 'subscription-manager list --available'")

    def setup_custom_facts(self, facts_key, facts_value, targetmachine_ip=""):
        ''' setup_custom_facts '''
        cmd = "echo '{\"" + facts_key + "\":\"" + facts_value + "\"}' > /etc/rhsm/facts/custom.facts"
        ret, output = self.runcmd(cmd, "create custom.facts", targetmachine_ip)
        if ret == 0 :
            logger.info("Succeeded to create custom.facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to create custom.facts %s." % self.get_hg_info(targetmachine_ip))

        cmd = "subscription-manager facts --update"
        ret, output = self.runcmd(cmd, "update subscription facts", targetmachine_ip)
        if ret == 0 and "Successfully updated the system facts" in output:
            logger.info("Succeeded to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to update subscription facts %s." % self.get_hg_info(targetmachine_ip))

    def restore_facts(self, targetmachine_ip=""):
        ''' setup_custom_facts '''
        cmd = "rm -f /etc/rhsm/facts/custom.facts"
        ret, output = self.runcmd(cmd, "remove custom.facts", targetmachine_ip)
        if ret == 0 :
            logger.info("Succeeded to remove custom.facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to remove custom.facts %s." % self.get_hg_info(targetmachine_ip))

        cmd = "subscription-manager facts --update"
        ret, output = self.runcmd(cmd, "update subscription facts", targetmachine_ip)
        if ret == 0 and "Successfully updated the system facts" in output:
            logger.info("Succeeded to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to update subscription facts %s." % self.get_hg_info(targetmachine_ip))


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
        image_nfs_path = VIRTWHOConstants().get_constant("nfs_image_path")
        image_mount_path = VIRTWHOConstants().get_constant("local_mount_point")
        cmd = "mkdir %s" % image_mount_path
        self.runcmd(cmd, "create local images mount point")
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

    def vw_get_uuid(self, guest_name, targetmachine_ip=""):
        ''' get the guest uuid. '''
        cmd = "virsh domuuid %s" % guest_name
        ret, output = self.runcmd(cmd, "get virsh domuuid", targetmachine_ip)
        if ret == 0:
            logger.info("get the uuid %s" % output)
        else:
            raise FailException("Failed to get the uuid")
        guestuuid = output[:-1].strip()
        return guestuuid

    def vw_check_uuid(self, guestuuid, uuidexists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check if the guest uuid is correctly monitored by virt-who. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
            # ignore restart virt-who serivce since virt-who -b -d will stop
            self.vw_restart_virtwho_new(targetmachine_ip)
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
        else: 
            self.vw_restart_virtwho_new(targetmachine_ip)
            cmd = "tail -3 %s " % rhsmlogfile
            ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
        if ret == 0:
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending domain info" in output:
                log_uuid_list = output.split('Sending domain info: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update in hosts-to-guests mapping" in output:
                log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get uuid list from rhsm.log")
            if uuidexists:
                if guestuuid == "" and len(log_uuid_list) == 0:
                    logger.info("Succeeded to get none uuid list")
                else:
                    if guestuuid in log_uuid_list:
                        logger.info("Succeeded to check guestuuid %s in log_uuid_list" % guestuuid)
                    else:
                        raise FailException("Failed to check guestuuid %s in log_uuid_list" % guestuuid)
            else:
                if guestuuid not in log_uuid_list:
                    logger.info("Succeeded to check guestuuid %s not in log_uuid_list" % guestuuid)
                else:
                    raise FailException("Failed to check guestuuid %s not in log_uuid_list" % guestuuid)
        else:
            raise FailException("Failed to get rhsm.log")

    def vw_check_attr(self, guestname, guest_status, guest_type, guest_hypertype, guest_state, guestuuid, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check if the guest attributions is correctly monitored by virt-who. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
            self.vw_restart_virtwho(targetmachine_ip)
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
        else: 
            self.vw_restart_virtwho(targetmachine_ip)
            cmd = "tail -3 %s " % rhsmlogfile
            ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
        if ret == 0:
            ''' get guest uuid.list from rhsm.log '''
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending domain info" in output:
                log_uuid_list = output.split('Sending domain info: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")    
            else:
                raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
            loglist = eval(log_uuid_list[:log_uuid_list.rfind("]\n") + 1].strip())
            for item in loglist:
                if item['guestId'] == guestuuid:
                    attr_status = item['attributes']['active']
                    logger.info("guest's active status is %s." % attr_status)
                    attr_type = item['attributes']['virtWhoType']
                    logger.info("guest virtwhotype is %s." % attr_type)
                    attr_hypertype = item['attributes']['hypervisorType']
                    logger.info("guest hypervisortype is %s." % attr_hypertype)
                    attr_state = item['state']
                    logger.info("guest state is %s." % attr_state)
            if guestname != "" and (guest_status == attr_status) and (guest_type in attr_type) and (guest_hypertype in attr_hypertype) and (guest_state == attr_state):
                logger.info("successed to check guest %s attribute" % guestname)
            else:
                raise FailException("Failed to check guest %s attribute" % guestname)
        else:
            logger.error("Failed to get uuids in rhsm.log")
            self.SET_RESULT(1)

    def vw_check_message_in_rhsm_log(self, message, message_exists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check whether given message exist or not in rhsm.log. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        cmd = "tail -3 %s " % rhsmlogfile
        ret, output = self.runcmd(cmd, "tail last 3 line in rhsm.log", targetmachine_ip)
        if ret == 0:
            if message_exists:
                if message in output:
                    logger.info("Succeeded to get message in rhsm.log: %s") % message
                else:
                    raise FailException("Failed to get message in rhsm.log: %s") % message
            else:
                if message not in output:
                    logger.info("Succeeded to check message not in rhsm.log: %s") % message
                else:
                    raise FailException("Failed to check message not in rhsm.log: %s") % message
        else:
            raise FailException("Failed to get rhsm.log")

    def kvm_get_guest_ip(self, guest_name, targetmachine_ip=""):
        ''' get guest ip address in kvm host '''
        ipAddress = self.getip_vm(guest_name, targetmachine_ip)
        if ipAddress == None or ipAddress == "":
            raise FailException("Faild to get guest %s ip." % guest_name)
        else:
            return ipAddress

    def getip_vm(self, guest_name, targetmachine_ip=""):
        guestip = self.__mac_to_ip(self.__get_dom_mac_addr(guest_name, targetmachine_ip), targetmachine_ip)
        if guestip != "" and (not "can not get ip by mac" in guestip):
            return guestip
        else:
            raise FailException("Test Failed - Failed to get ip of guest %s." % guest_name)

    def vw_define_all_guests(self, targetmachine_ip=""):
        guest_path = VIRTWHOConstants().get_constant("nfs_image_path")
        for guestname in self.get_all_guests_list(guest_path, targetmachine_ip):
            self.define_vm(guestname, os.path.join(guest_path, guestname), targetmachine_ip)

    def vw_undefine_all_guests(self, targetmachine_ip=""):
        guest_path = VIRTWHOConstants().get_constant("nfs_image_path")
        for guestname in self.get_all_guests_list(guest_path, targetmachine_ip):
            self.vw_undefine_guest(guestname, targetmachine_ip)

    def vw_define_guest(self, guestname, targetmachine_ip=""):
        guest_path = VIRTWHOConstants().get_constant("nfs_image_path")
        self.define_vm(guestname, os.path.join(guest_path, guestname), targetmachine_ip)

    def get_all_guests_list(self, guest_path, targetmachine_ip=""):
        cmd = "ls %s" % guest_path
        ret, output = self.runcmd(cmd, "get all guest in images folder", targetmachine_ip)
        if ret == 0 :
            guest_list = output.strip().split("\n")
            logger.info("Succeeded to get all guest list %s in %s." % (guest_list, guest_path))
            return guest_list
        else:
            raise FailException("Failed to get all guest list in %s." % guest_path)

    def vw_start_guests(self, guestname, targetmachine_ip=""):
        self.start_vm(guestname, targetmachine_ip)

    def vw_stop_guests(self, guestname, targetmachine_ip=""):
        self.shutdown_vm(guestname, targetmachine_ip)

    def define_vm(self, guest_name, guest_path, targetmachine_ip=""):
        cmd = "[ -f /root/%s.xml ]" % (guest_name)
        ret, output = self.runcmd(cmd, "check whether define xml exist", targetmachine_ip)
        if ret != 0 :
            logger.info("Generate guest %s xml." % guest_name)
            params = {"guestname":guest_name, "guesttype":"kvm", "source": "switch", "ifacetype" : "bridge", "fullimagepath":guest_path }
            xml_obj = XmlBuilder()
            domain = xml_obj.add_domain(params)
            xml_obj.add_disk(params, domain)
            xml_obj.add_interface(params, domain)
            dom_xml = xml_obj.build_domain(domain)
            self.define_xml_gen(guest_name, dom_xml, targetmachine_ip)
        cmd = "virsh define /root/%s.xml" % (guest_name)
        ret, output = self.runcmd(cmd, "define guest", targetmachine_ip)
        if ret == 0 or "already exists" in output:
            logger.info("Succeeded to define guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to define guest %s." % guest_name)
        self.list_vm(targetmachine_ip)

    def define_xml_gen(self, guest_name, xml, targetmachine_ip=""):
        cmd = "echo '%s' > /root/%s.xml" % (xml, guest_name)
        ret, output = self.runcmd(cmd, "write define xml", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to generate virsh define xml in /root/%s.xml " % guest_name)
        else:
            raise FailException("Test Failed - Failed to generate virsh define xml in /root/%s.xml " % guest_name)

    def define_xml_del(self, guest_xml, targetmachine_ip=""):
        cmd = "rm -f /root/%s.xml" % guest_xml
        ret, output = self.runcmd(cmd, "remove generated define xml", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove generated define xml: /root/%s.xml " % guest_xml)
        else:
            raise FailException("Test Failed - Failed to remove generated define xml: /root/%s.xml " % guest_xml)

    def list_vm(self, targetmachine_ip=""):
        cmd = "virsh list --all"
        ret, output = self.runcmd(cmd, "List all existing guests:", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to list all curent guest ")
        else:
            raise FailException("Test Failed - Failed to list all curent guest ")

    def start_vm(self, guest_name, targetmachine_ip=""):
        cmd = "virsh start %s" % (guest_name)
        ret, output = self.runcmd(cmd, "start guest" , targetmachine_ip)
        if ret == 0 or "already active" in output:
            logger.info("Succeeded to start guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to start guest %s." % guest_name)
        return self.__check_vm_available(guest_name, targetmachine_ip=targetmachine_ip)

    def __check_vm_available(self, guest_name, timeout=600, targetmachine_ip=""):
        terminate_time = time.time() + timeout
        guest_mac = self.__get_dom_mac_addr(guest_name, targetmachine_ip)
        self.__generate_ipget_file(targetmachine_ip)
        while True:
            guestip = self.__mac_to_ip(guest_mac, targetmachine_ip)
            if guestip != "" and (not "can not get ip by mac" in guestip):
                return guestip
            if terminate_time < time.time():
                raise FailException("Process timeout has been reached")
            logger.debug("Check guest IP, wait 10 seconds ...")
            time.sleep(10)

    def __generate_ipget_file(self, targetmachine_ip=""):
        generate_ipget_cmd = "wget -nc http://10.66.100.116/projects/sam-virtwho/latest-manifest/ipget.sh -P /root/ && chmod 777 /root/ipget.sh"
        ret, output = self.runcmd(generate_ipget_cmd, "wget ipget file", targetmachine_ip)
        if ret == 0 or "already there" in output:
            logger.info("Succeeded to wget ipget.sh to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget ipget.sh to /root/.")

    def __get_dom_mac_addr(self, domname, targetmachine_ip=""):
        """
        Get mac address of a domain
        Return mac address on SUCCESS or None on FAILURE
        """
        cmd = "virsh dumpxml " + domname + " | grep 'mac address' | awk -F'=' '{print $2}' | tr -d \"[\'/>]\""
        ret, output = self.runcmd(cmd, "get mac address", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to get mac address of domain %s." % domname)
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Test Failed - Failed to get mac address of domain %s." % domname)

    def __mac_to_ip(self, mac, targetmachine_ip=""):
        """
        Map mac address to ip, need nmap installed and ipget.sh in /root/ target machine
        Return None on FAILURE and the mac address on SUCCESS
        """
        if not mac:
            raise FailException("Failed to get guest mac ...")
        cmd = "sh /root/ipget.sh %s | grep -v nmap" % mac
        ret, output = self.runcmd(cmd, "check whether guest ip available", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to get ip address.")
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Test Failed - Failed to get ip address.")

    def shutdown_vm(self, guest_name, targetmachine_ip=""):
        cmd = "virsh destroy %s" % (guest_name)
        ret, output = self.runcmd(cmd, "destroy guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to shutdown guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to shutdown guest %s." % guest_name)

    def pause_vm(self, guest_name, targetmachine_ip=""):
        ''' Pause a guest in host machine. '''
        cmd = "virsh suspend %s" % (guest_name)
        ret, output = self.runcmd(cmd, "pause guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to pause guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to pause guest %s." % guest_name)

    def resume_vm(self, guest_name, targetmachine_ip=""):
        ''' resume a guest in host machine. '''
        cmd = "virsh resume %s" % (guest_name)
        ret, output = self.runcmd(cmd, "resume guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to resume guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to pause guest %s.")

    def vw_migrate_guest(self, guestname, target_machine, origin_machine=""):
        ''' migrate a guest from source machine to target machine. '''
        uri = "qemu+ssh://%s/system" % target_machine
        cmd = "virsh migrate --live %s %s --undefinesource" % (guestname, uri)
        ret, output = self.runcmd_interact(cmd, "migrate guest from master to slave machine", origin_machine)
        if ret == 0:
            logger.info("Succeeded to migrate guest '%s' to %s." % (guestname, target_machine))
        else:
            raise FailException("Failed to migrate guest '%s' to %s." % (guestname, target_machine))

    def vw_undefine_guest(self, guestname, targetmachine_ip=""):
        ''' undefine guest in host machine. '''
        cmd = "virsh undefine %s" % guestname
        ret, output = self.runcmd(cmd, "undefine guest in %s" % targetmachine_ip, targetmachine_ip)
        if "Domain %s has been undefined" % guestname in output:
            logger.info("Succeeded to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))
        else:
            raise FailException("Failed to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))

    def mount_images_in_slave_machine(self, targetmachine_ip, imagenfspath, imagepath):
        ''' mount images in master machine to slave_machine. '''
        cmd = "test -d %s" % (imagepath)
        ret, output = self.runcmd(cmd, "check images dir exist", targetmachine_ip)
        if ret == 1:
            cmd = "mkdir -p %s" % (imagepath)
            ret, output = self.runcmd(cmd, "create image path in the slave_machine", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to create imagepath in the slave_machine.")
            else:
                raise FailException("Failed to create imagepath in the slave_machine.")
        # mount image path of source machine into just created image path in slave_machine
        master_machine_ip = get_exported_param("REMOTE_IP")
        cmd = "mount %s:%s %s" % (master_machine_ip, imagenfspath, imagepath)
        ret, output = self.runcmd(cmd, "mount images in the slave_machine", targetmachine_ip)
        if ret == 0 or "is busy or already mounted" in output:
            logger.info("Succeeded to mount images in the slave_machine.")
        else:
            raise FailException("Failed to mount images in the slave_machine.")


    def set_remote_libvirt_conf(self, virtwho_remote_server_ip, targetmachine_ip=""):
        VIRTWHO_LIBVIRT_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_OWNER")
        VIRTWHO_LIBVIRT_ENV = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_ENV")
        VIRTWHO_LIBVIRT_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_USERNAME")
        VIRTWHO_LIBVIRT_SERVER = "qemu+ssh:\/\/" + virtwho_remote_server_ip + "\/system"

        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/.*VIRTWHO_LIBVIRT=.*/VIRTWHO_LIBVIRT=1/g' -e 's/.*VIRTWHO_LIBVIRT_OWNER=.*/VIRTWHO_LIBVIRT_OWNER=%s/g' -e 's/.*VIRTWHO_LIBVIRT_ENV=.*/VIRTWHO_LIBVIRT_ENV=%s/g' -e 's/.*VIRTWHO_LIBVIRT_SERVER=.*/VIRTWHO_LIBVIRT_SERVER=%s/g' -e 's/.*VIRTWHO_LIBVIRT_USERNAME=.*/VIRTWHO_LIBVIRT_USERNAME=%s/g' -e 's/.*VIRTWHO_LIBVIRT_PASSWORD=.*/VIRTWHO_LIBVIRT_PASSWORD=/g' /etc/sysconfig/virt-who" % (VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_SERVER, VIRTWHO_LIBVIRT_USERNAME)
        # set remote libvirt value
        ret, output = self.runcmd(cmd, "setting value for remote libvirt conf.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set remote libvirt value.")
        else:
            raise FailException("Test Failed - Failed to set remote libvirt value.")

    def clean_remote_libvirt_conf(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/.*VIRTWHO_LIBVIRT=.*/#VIRTWHO_LIBVIRT=0/g' -e 's/.*VIRTWHO_LIBVIRT_OWNER=.*/#VIRTWHO_LIBVIRT_OWNER=/g' -e 's/.*VIRTWHO_LIBVIRT_ENV=.*/#VIRTWHO_LIBVIRT_ENV=/g' -e 's/.*VIRTWHO_LIBVIRT_SERVER=.*/#VIRTWHO_LIBVIRT_SERVER=/g' -e 's/.*VIRTWHO_LIBVIRT_USERNAME=.*/#VIRTWHO_LIBVIRT_USERNAME=/g' -e 's/.*VIRTWHO_LIBVIRT_PASSWORD=.*/#VIRTWHO_LIBVIRT_PASSWORD=/g' /etc/sysconfig/virt-who"
        # set remote libvirt value
        ret, output = self.runcmd(cmd, "Clean config of remote libvirt conf. reset to default", targetmachine_ip)
        if ret == 0:
            self.vw_restart_virtwho_new(targetmachine_ip)
            logger.info("Succeeded to reset to defualt config.")
        else:
            raise FailException("Test Failed - Failed to reset to defualt config.")

    def generate_ssh_key(self, targetmachine_ip=""):
        remote_ip_2 = get_exported_param("REMOTE_IP_2")
        remote_ip = get_exported_param("REMOTE_IP")
        username = "root"
        password = "red2015"
        # generate pub-key in host2, then copy the key to host1
        cmd = "ssh-keygen"
        ret, output = self.run_interact_sshkeygen(cmd, remote_ip_2, username, password)
        if ret == 0:
            logger.info("Succeeded to generate ssh-keygen.")
        else:
            raise FailException("Test Failed - Failed to generate ssh-keygen.")
        cmd = "ssh-copy-id -i ~/.ssh/id_rsa.pub %s" % remote_ip
        ret, output = self.run_interact_sshkeygen(cmd, remote_ip_2, username, password)
        if ret == 0:
            logger.info("Succeeded to scp id_rsa.pub to remote host")
        else:
            raise FailException("Test Failed - Failed to scp id_rsa.pub to remote host")

    def run_interact_sshkeygen(self, cmd, targetmachine_ip, username, password, timeout=None, comments=True):
        ret, output = self.run_paramiko_interact_sshkeygen(cmd, targetmachine_ip, username, password, timeout)
        return ret, output

    def run_paramiko_interact_sshkeygen(self, cmd, remote_ip, username, password, timeout=None):
        """Execute the given commands in an interactive shell."""
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        channel = ssh.get_transport().open_session()
        channel.settimeout(600)
        channel.get_pty()
        channel.exec_command(cmd)
        output = ""
        while True:
            data = channel.recv(1048576)
            output += data
            logger.debug("output: %s" % data)
            if channel.send_ready():
                if data.strip().endswith('yes/no)?'):
                    logger.debug("interactive input: yes")
                    channel.send("yes" + '\n')
                if data.strip().endswith('\'s password:'):
                    logger.debug("interactive input: red2015")
                    channel.send("red2015" + '\n')
                if data.strip().endswith('[Foreman] Username:'):
                    logger.debug("interactive input: admin")
                    channel.send("admin" + '\n')
                if data.strip().endswith('[Foreman] Password for admin:'):
                    logger.debug("interactive input: admin")
                    channel.send("admin" + '\n')
                if data.strip().endswith('(/root/.ssh/id_rsa):'):
                    logger.debug("interactive input: enter")
                    channel.send('\n')
                if data.strip().endswith('y/n)?'):
                    logger.debug("interactive input: yes")
                    channel.send("y" + '\n')
                if data.strip().endswith('(empty for no passphrase):'):
                    logger.debug("empty for no passphrase input: enter")
                    channel.send('\n')
                if data.strip().endswith('same passphrase again:'):
                    logger.debug("input same passphrase again: enter")
                    channel.send('\n')
                if channel.exit_status_ready():
                    break
        if channel.recv_ready():
            data = channel.recv(1048576)
            output += data
        return channel.recv_exit_status(), output

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
        vmware_cmd_ip = VIRTWHOConstants().get_constant("VMWARE_CMD_IP")
        if vCenter == "" and vCenter_user == "" and vCenter_pass == "":
            vCenter = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
            vCenter_user = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
            vCenter_pass = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")
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

    def get_uuid_list_in_rhsm_log(self, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check if the guest attributions is correctly monitored by virt-who. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
            self.vw_restart_virtwho(targetmachine_ip)
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
        else: 
            self.vw_restart_virtwho(targetmachine_ip)
            cmd = "tail -3 %s " % rhsmlogfile
            ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
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
            elif "Sending domain info" in output:
                # log_uuid_list = output.split('Sending domain info: ')[1].split(":")[1].strip("}").strip()
                log_uuid_list = output.split('Sending domain info: ')[1].strip()
                logger.info("log_uuid_list is %s" % log_uuid_list)
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get guest uuid.list from rhsm.log")
            return log_uuid_list
        else:
            raise FailException("Failed to get uuid list in rhsm.log")

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

    #========================================================
    #     RHEL + RHEVM Functions
    #========================================================
    def get_hostname(self, targetmachine_ip=""):
        cmd = "hostname"
        ret, output = self.runcmd(cmd, "geting the machine's hostname", targetmachine_ip)
        if ret == 0:
            hostname = output.strip(' \r\n').strip('\r\n') 
            logger.info("Succeeded to get the machine's hostname %s." % hostname) 
            return hostname
        else:
            raise FailException("Test Failed - Failed to get hostname in %s." % self.get_hg_info(targetmachine_ip))

    def configure_rhel_host_bridge(self, targetmachine_ip=""):
        # Configure rhevm bridge on RHEL host
        network_dev = ""
        cmd = "ip route | grep `hostname -I | awk {'print $1'}` | awk {'print $3'}"
        ret, output = self.runcmd(cmd, "get network device", targetmachine_ip)
        if ret == 0:
            network_dev = output.strip()
            logger.info("Succeeded to get network device in %s." % self.get_hg_info(targetmachine_ip))
            if not "rhevm" in output:
                cmd = "sed -i '/^BOOTPROTO/d' /etc/sysconfig/network-scripts/ifcfg-%s; echo \"BRIDGE=rhevm\" >> /etc/sysconfig/network-scripts/ifcfg-%s;echo \"DEVICE=rhevm\nBOOTPROTO=dhcp\nONBOOT=yes\nTYPE=Bridge\"> /etc/sysconfig/network-scripts/ifcfg-br0" % (network_dev, network_dev)
                ret, output = self.runcmd(cmd, "setup bridge for kvm testing", targetmachine_ip)
                if ret == 0:
                    logger.info("Succeeded to set /etc/sysconfig/network-scripts in %s." % self.get_hg_info(targetmachine_ip))
                else:
                    raise FailException("Test Failed - Failed to /etc/sysconfig/network-scripts in %s." % self.get_hg_info(targetmachine_ip))
                self.service_command("restart_network", targetmachine_ip)
            else:
                logger.info("Bridge already setup for virt-who testing, do nothing ...")
        else:
            raise FailException("Test Failed - Failed to get network device in %s." % self.get_hg_info(targetmachine_ip))

    def get_rhevm_repo_file(self, targetmachine_ip=""):
        ''' wget rhevm repo file and add to rhel host '''
        cmd = "wget -P /etc/yum.repos.d/ http://10.66.100.116/projects/sam-virtwho/rhevm_repo/rhevm_7.2.repo"
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))

    def conf_rhevm_shellrc(self, targetmachine_ip=""):
        ''' Config the env to login to rhevm_rhell '''
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s:443/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.rhevmshellrc" % tagetmachine_hostname
        ret, output = self.runcmd(cmd, "config rhevm_shell env on rhevm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to config rhevm_shell env on rhevm in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to config rhevm_shell env on rhevm in %s." % self.get_hg_info(targetmachine_ip))

    # Add host to rhevm
    def rhevm_add_host(self, rhevm_host_name, rhevm_host_ip, targetmachine_ip):
        cmd = " rhevm-shell -c -E 'add host --name \"%s\" --address \"%s\" --root_password redhat'" % (rhevm_host_name, rhevm_host_ip)
        ret, output = self.runcmd(cmd, "add host to rhevm.", targetmachine_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = " rhevm-shell -c -E 'list hosts --show-all'"
                ret, output = self.runcmd(cmd, "list hosts in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0 and rhevm_host_name in output:
                    logger.info("Succeeded to list host %s." % rhevm_host_name)
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_host_name, targetmachine_ip)
                    if "up" in status:
                        logger.info("Succeeded to add new host %s to rhevm" % rhevm_host_name)
                        break
                    else :
                        logger.info("vm %s status-state is %s" % (rhevm_host_name, status))
                time.sleep(10)
                if runtime > 120:
                    raise FailException("%s status has problem,status is %s." % (rhevm_host_name, status))

    # parse rhevm-shell result to dict
    def get_key_rhevm(self, output, non_key_value, key_value, find_value, targetmachine_ip=""):
        pool_dict = {}
        if output is not "":
            datalines = output.splitlines()
            values1 = False
            values2 = False
            ERROR_VALUE = "-1"
            for line in datalines:
                line = line.strip()
                if line.find(non_key_value) == 0:
                    result_values1 = line[(line.find(':') + 1):].strip()
                    logger.info("Succeeded to find the non_key_value %s's result_values1 %s" % (non_key_value, result_values1))
                    values1 = True
                elif line.find(key_value) == 0:
                    result_values2 = line[(line.find(':') + 1):].strip()
                    logger.info("Succeeded to find the key_value %s's result_values2 %s" % (key_value, result_values2))
                    values2 = True
                elif (line == "") and (values2 == True) and (values1 == False):
                    pool_dict[result_values2] = ERROR_VALUE
                    values2 = False
                if (values1 == True) and (values2 == True):
                    pool_dict[result_values2] = result_values1
                    values1 = False
                    values2 = False
            if find_value in pool_dict:
                findout_value = pool_dict[find_value]
                if findout_value == ERROR_VALUE:
                    logger.info("Failed to get the %s's %s, no value" % (find_value, non_key_value))
                    return ERROR_VALUE
                else:
                    logger.info("Succeeded to get the %s's %s." % (find_value, non_key_value))
                    return findout_value
            else:
                raise FailException("Failed to get the %s's %s" % (find_value, non_key_value))
        else:
            raise FailException("Failed to run rhevm-shell cmd.")

    # parse rhevm-result to dict
    def rhevm_info_dict(self, output, targetmachine_ip=""):
        rhevm_info_dict = {}
        if output is not "":
            datalines = output.splitlines()
            for line in datalines:
                if ":" in line:
                    key = line.strip().split(":")[0].strip()
                    value = line.strip().split(":")[1].strip()
                    print key + "==" + value
                    rhevm_info_dict[key] = value
            return rhevm_info_dict
        else:
            raise FailException("Failed to get output in rhevm-result file.")

    # wait for a while until expect status shown in /tmp/rhevm-result file
    def wait_for_status(self, cmd, status_key, status_value, targetmachine_ip, timeout=600):
        timout = 0
        while True:
            timout = timout + 1
            # cmd = "list hosts --show-all; exit"
            ret, output = self.runcmd(cmd, "list info updating in rhevm.", targetmachine_ip)
            rhevm_info = self.rhevm_info_dict(output)
            if status_value == "NotExist":
                if not status_key in rhevm_info.keys():
                    logger.info("Succeded to check %s not exist." % status_key)
                    return True
            elif status_key in rhevm_info.keys() and rhevm_info[status_key] == status_value:
                logger.info("Succeeded to get %s value %s in rhevm." % (status_key, status_value))
                return True
            elif status_key in rhevm_info.keys() and rhevm_info[status_key] != status_value:
                logger.info("Succeeded to remove %s" % status_value)
                return True
            elif timout > 60:
                logger.info("Time out, running rhevm-shell command in server failed.")
                return False
            else:
                logger.info("sleep 10 in wait_for_status.")
                time.sleep(10)

    # Add storagedomain in rhevm
    def add_storagedomain_to_rhevm(self, storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir, targetmachine_ip): 
        # Create storage nfs folder and active it
        cmd = "mkdir %s" % storage_dir
        self.runcmd(cmd, "create storage nfs folder", NFS_server)
        cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (storage_dir.replace('/', '\/'), storage_dir)
        ret, output = self.runcmd(cmd, "set /etc/exports for nfs", NFS_server)
        if ret == 0:
            logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % storage_dir)
        else:
            raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % storage_dir)
        cmd = "service nfs restart"
        ret, output = self.runcmd(cmd, "restarting nfs service", NFS_server)
        if ret == 0 :
            logger.info("Succeeded to restart service nfs.")
        else:
            raise FailException("Failed to restart service nfs.")

        cmd = "rhevm-shell -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter \"Default\"' " % (storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
        ret, output = self.runcmd(cmd, "Add storagedomain in rhevm.", targetmachine_ip)
        if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "unattached", targetmachine_ip):
            logger.info("Succeeded to add storagedomains %s in rhevm." % storage_name)
        else:
            raise FailException("Failed to add storagedomains %s in rhevm." % storage_name)
        cmd = "rhevm-shell -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"Default\"' " % (storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
        ret, output = self.runcmd(cmd, "Attaches the storage domain to the Default data center.", targetmachine_ip)
        if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "NotExist", targetmachine_ip):
            logger.info("Succeeded to maintenance storagedomains %s in rhevm." % storage_name)
        else:
            raise FailException("Failed to maintenance storagedomains %s in rhevm." % storage_name)

#     # activate storagedomain in rhevm
#     def activate_storagedomain(self, storage_name, targetmachine_ip): 
#         cmd = "rhevm-shell -c -E 'action storagedomain \"%s\" activate --datacenter-identifier \"Default\"' " % (storage_name)
#         ret, output = self.runcmd(cmd, "activate storagedomain in rhevm.", targetmachine_ip)
#         if "complete" in output:
#             if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "NotExist", targetmachine_ip):
#         #if self.wait_for_status("rhevm-shell -c -E 'action storagedomain \"%s\" activate --datacenter-identifier \"Default\"' % (storage_name)", "status-state", "complete", targetmachine_ip):
#                 logger.info("Succeeded to activate storagedomains %s in rhevm." % storage_name)
#             else:
#                 raise FailException("Failed to list activate storagedomains %s in rhevm." % storage_name)
#         else:
#             raise FailException("Failed to activate storagedomains %s in rhevm." % storage_name)

    def install_virtV2V(self, targetmachine_ip=""):
        '''install virt-V2V'''
        cmd = "rpm -q virt-v2v"
        ret, output = self.runcmd(cmd, "check whether virt-V2V exist", targetmachine_ip)
        if ret == 0:
            logger.info("virt-V2V has already exist, needn't to install it.")
        else:
            logger.info("virt-V2V hasn't been installed.")
            cmd = "yum install virt-v2v -y"
            ret, output = self.runcmd(cmd, "install vdsm", targetmachine_ip)
            if ret == 0 and "Complete!" in output:
                logger.info("Succeeded to install virt-V2V.")
            else:
                raise FailException("Failed to install virt-V2V")


    def rhevm_define_guest(self, targetmachine_ip=""):
        ''' wget kvm img and xml file, define it in execute machine for converting to rhevm '''
        cmd = "test -d /tmp/rhevm_guest/ && echo presence || echo absence"
        ret, output = self.runcmd(cmd, "check whether guest exist", targetmachine_ip)
        if "presence" in output:
            logger.info("guest has already exist")
        else:
            # cmd = "wget -P /tmp/rhevm_guest/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/6.4_Server_x86_64"
            cmd = "wget -P /tmp/rhevm_guest/ http://10.66.100.116/projects/sam-virtwho/7.1_Server_x86_64"
            ret, output = self.runcmd(cmd, "wget kvm img file", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to wget kvm img file")
            else:
                raise FailException("Failed to wget kvm img file")
        # cmd = "wget -P /tmp/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "wget -P /tmp/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/7.1_Server_x86_64.xml"
        ret, output = self.runcmd(cmd, "wget kvm xml file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget xml img file")
        else:
            raise FailException("Failed to wget xml img file")
        # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "virsh define /tmp/rhevm_guest/xml/7.1_Server_x86_64.xml"
        ret, output = self.runcmd(cmd, "define kvm guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to define kvm guest")
        else:
            raise FailException("Failed to define kvm guest")

    # create_storage_pool
    def create_storage_pool(self, targetmachine_ip=""):
        ''' wget autotest_pool.xml '''
        cmd = "wget -P /tmp/ http://10.66.100.116/projects/sam-virtwho/autotest_pool.xml"
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget autotest_pool.xml")
        else:
            raise FailException("Failed to wget autotest_pool.xml")
        # check whether pool exist, if yes, destroy it
        cmd = "virsh pool-list"
        ret, output = self.runcmd(cmd, "check whether autotest_pool exist", targetmachine_ip)
        if ret == 0 and "autotest_pool" in output:
            logger.info("autotest_pool exist.")
            cmd = "virsh pool-destroy autotest_pool"
            ret, output = self.runcmd(cmd, "destroy autotest_pool", targetmachine_ip)
            if ret == 0 and "autotest_pool destroyed" in output:
                logger.info("Succeeded to destroy autotest_pool")
            else:
                raise FailException("Failed to destroy autotest_pool")

        cmd = "virsh pool-create /tmp/autotest_pool.xml"
        ret, output = self.runcmd(cmd, "import vm to rhevm.")
        if ret == 0 and "autotest_pool created" in output:
            logger.info("Succeeded to create autotest_pool.")
        else:
            raise FailException("Failed to create autotest_pool.")

    # convert_guest_to_nfs with v2v tool
    def convert_guest_to_nfs(self, NFS_server, NFS_export_dir, vm_hostname):
        cmd = "virt-v2v -i libvirt -ic qemu:///system -o rhev -os %s:%s --network rhevm %s" % (NFS_server, NFS_export_dir, vm_hostname)
        ret, output = self.runcmd(cmd, "convert_guest_to_nfs with v2v tool")
        if ret == 0:
            logger.info("Succeeded to convert_guest_to_nfs with v2v tool")
        else:
            raise FailException("Failed to convert_guest_to_nfs with v2v tool")
        # convert the second guest
        cmd = "virt-v2v -i libvirt -ic qemu:///system -o rhev -os %s:%s --network rhevm %s -on \"Sec_%s\"" % (NFS_server, NFS_export_dir, vm_hostname, vm_hostname)
        ret, output = self.runcmd(cmd, "convert_guest_to_nfs with v2v tool")
        if ret == 0:
            logger.info("Succeeded to convert the second guest to nfs with v2v tool")
        else:
            raise FailException("Failed to convert the second guest to nfs with v2v tool")

    # import guest to rhevm
    def import_vm_to_rhevm(self, guest_name, nfs_dir_for_storage, nfs_dir_for_export, rhevm_host_ip):
        # action vm "7.1_Server_x86_64" import_vm --storagedomain-identifier export_storage  --cluster-name Default --storage_domain-name data_storage
        cmd = "rhevm-shell -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s' " % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
        ret, output = self.runcmd(cmd, "import guest %s in rhevm." % guest_name, rhevm_host_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'list vms --show-all' "
                ret, output = self.runcmd(cmd, "list VMS in rhevm.", rhevm_host_ip)
                runtime = runtime + 1
                if ret == 0 and guest_name in output:
                    logger.info("Succeeded to list vm %s." % guest_name)
                    status = self.get_key_rhevm(output, "status-state", "name", guest_name, rhevm_host_ip)
                    if "down" in status:
                        logger.info("Succeeded to import new vm %s to rhevm" % guest_name)
                        break
                    else :
                        logger.info("vm %s status-state is %s" % (guest_name, status))
                time.sleep(10)
                if runtime > 120:
                    raise FailException("%s status has problem,status is %s." % (guest_name, status))


    def rhel_rhevm_sys_setup(self, targetmachine_ip=""):
        # system setup for RHEL+RHEVM testing env
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        self.configure_rhel_host_bridge(targetmachine_ip)
        self.get_rhevm_repo_file(targetmachine_ip)
        cmd = "yum install -y vdsm"
        ret, output = self.runcmd(cmd, "install vdsm and related packages", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install vdsm and related packages in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to install vdsm and related packages in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def rhel_rhevm_setup(self):
        SAM_IP = get_exported_param("SERVER_IP")
        SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")

        SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
        SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

        RHEVM_IP = VIRTWHOConstants().get_constant("RHEVM_HOST")
        RHEL_RHEVM_GUEST_NAME = VIRTWHOConstants().get_constant("RHEL_RHEVM_GUEST_NAME")

        VIRTWHO_RHEVM_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_OWNER")
        VIRTWHO_RHEVM_ENV = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_ENV")
        # VIRTWHO_RHEVM_SERVER = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_SERVER")
        VIRTWHO_RHEVM_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_USERNAME")
        VIRTWHO_RHEVM_PASSWORD = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_PASSWORD")

        NFSserver_ip = VIRTWHOConstants().get_constant("NFSserver_ip_test")
        nfs_dir_for_storage = VIRTWHOConstants().get_constant("NFS_DIR_FOR_storage")
        nfs_dir_for_export = VIRTWHOConstants().get_constant("NFS_DIR_FOR_export")

        REMOTE_IP_NAME = self.get_hostname()
        # self.conf_rhevm_shellrc(RHEVM_IP)
        # self.rhevm_add_host(REMOTE_IP_NAME, get_exported_param("REMOTE_IP"), RHEVM_IP)
        # self.add_storagedomain_to_rhevm("data_storage", REMOTE_IP_NAME, "data", "v3", NFSserver_ip, nfs_dir_for_storage, RHEVM_IP)
        # self.add_storagedomain_to_rhevm("export_storage", REMOTE_IP_NAME, "export", "v1", NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
        # #self.rhevm_define_guest()
        # #self.create_storage_pool()
        # self.install_virtV2V()
        self.convert_guest_to_nfs(NFSserver_ip, nfs_dir_for_export, RHEL_RHEVM_GUEST_NAME)
        self.import_vm_to_rhevm(RHEL_RHEVM_GUEST_NAME, "data_storage", "export_storage", RHEVM_IP)

    def update_rhevm_vw_configure(self, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password, background=1, debug=1):
        ''' update virt-who configure file /etc/sysconfig/virt-who for enable VIRTWHO_RHEVM'''
        cmd = "sed -i -e 's/^#VIRTWHO_DEBUG/VIRTWHO_DEBUG/g' -e 's/^#VIRTWHO_RHEVM/VIRTWHO_RHEVM/g' -e 's/^#VIRTWHO_RHEVM_OWNER/VIRTWHO_RHEVM_OWNERs/g' -e 's/^#VIRTWHO_RHEVM_ENV/VIRTWHO_RHEVM_ENV/g' -e 's/^#VIRTWHO_RHEVM_SERVER/VIRTWHO_RHEVM_SERVER/g' -e 's/^#VIRTWHO_RHEVM_USERNAME/VIRTWHO_RHEVM_USERNAME/g' -e 's/^#VIRTWHO_RHEVM_PASSWORD/VIRTWHO_RHEVM_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "updating virt-who configure file for enable VIRTWHO_RHEVM")
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_RHEVM.")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_RHEVM.")
