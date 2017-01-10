from utils import *
from utils.tools.shell import command
from utils.exception.failexception import FailException
from testcases.rhsm.rhsmconstants import RHSMConstants
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.virt_who_polarion.virtwhoconstants import VIRTWHOConstants

class Base(unittest.TestCase):
    # ========================================================
    #       Common Functions
    # ========================================================
    def cm_change_hostname(self, targetmachine_ip=""):
        suffix = time.strftime("%m%H%M%S")
        new_hostname = self.get_hostname(targetmachine_ip) + "-" + suffix
        if self.get_os_serials(targetmachine_ip) == 7:
            cmd = "hostnamectl --static set-hostname %s" % new_hostname
        else:
            cmd = "sed -i 's/^HOSTNAME=.*/HOSTNAME=%s/g' /etc/sysconfig/network" % new_hostname
        (ret, output) = self.runcmd(cmd, "change hostname as %s" % new_hostname, targetmachine_ip)

    def cm_get_consumerid(self, targetmachine_ip=""):
        # get consumer id: system identity
        cmd = "subscription-manager identity | grep identity"
        (ret, output) = self.runcmd(cmd, "get consumerid", targetmachine_ip)
        return output.split(':')[1].strip()

    def cm_install_wget(self, targetmachine_ip=""):
        cmd = "yum install -y wget"
        ret, output = self.runcmd(cmd, "install wget", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install wget in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to install wget in %s." % self.get_hg_info(targetmachine_ip))

    def cm_install_basetool(self, targetmachine_ip=""):
        cmd = "yum install -y wget git lsb ntp"
        ret, output = self.runcmd(cmd, "install base tool to support automation", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to install base tool to support automation in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to install base tool to support automation in %s." % self.get_hg_info(targetmachine_ip))

    def cm_install_desktop(self, targetmachine_ip=""):
        if self.os_serial == "7":
            cmd = "yum install -y @gnome-desktop"
        else:
            cmd = "yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform'"
        ret, output = self.runcmd(cmd, "install desktop", targetmachine_ip, showlogger=False)
        # for computenode, install desktop will fail
        if True:
        # if ret == 0:
            logger.info("Succeeded to install desktop")
        else:
            raise FailException("Test Failed - Failed to install desktop")
        cmd = "yum install -y tigervnc-server"
        ret, output = self.runcmd(cmd, "install tigervnc", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to install tigervnc-server")
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
        else:
            logger.info("Failed to install tigervnc-server")

    def cm_check_file_mode(self, file, mode, targetmachine_ip=""):
        # check file mode with given value
        cmd = "stat -c %%a %s" % file
        (ret, output) = self.runcmd(cmd, "get file mode", targetmachine_ip)
        if ret == 0 and output.strip() == mode:
            logger.info("Succeeded to check file: %s mode as: %s" % (file, mode))
        else:
            raise FailException("Test Failed - Failed to check file: %s mode as: %s" % (file, mode))

    def cm_get_rpm_version(self, rpm, targetmachine_ip=""):
        ret, output = self.runcmd("rpm -q %s" % rpm, "get %s version" % rpm, targetmachine_ip)
        version = output.strip()
        if ret == 0:
            logger.info("Succeeded to get %s version %s." % (rpm, version))
            return version
        else:
            logger.info("Failed to get %s version %s." % (rpm, version))
            return "null"

    def cm_set_rpm_version(self, rpm_key, rpm_name, targetmachine_ip=""):
        properties_file = get_properties_file()
        rpm_version = self.cm_get_rpm_version("%s" % rpm_name, targetmachine_ip)
        fileHandle = open(properties_file, 'a')
        fileHandle.write(rpm_key + "=" + rpm_version + "\n")
        fileHandle.close()
        logger.info("Succeeded to set %s version %s." % (rpm_key, rpm_name))

    def cm_set_rhsm_version(self, targetmachine_ip=""):
        self.cm_set_rpm_version("RHSM", "subscription-manager", targetmachine_ip)
        self.cm_set_rpm_version("RHSM_GUI", "subscription-manager-gui", targetmachine_ip)
        self.cm_set_rpm_version("RHSM_FIRSTBOOT", "subscription-manager-firstboot", targetmachine_ip)
        self.cm_set_rpm_version("PYTHON_RHSM", "python-rhsm", targetmachine_ip)

    def cm_set_cp_image(self, mode="kvm", targetmachine_ip=""):
        ''' mount the images prepared '''
        if get_exported_param("REMOTE_IP").startswith("hp-z220-"):
            image_server = self.get_vw_cons("local_image_server")
        else:
            image_server = self.get_vw_cons("beaker_image_server")
        if "kvm" in mode:
            image_nfs_path = self.get_vw_cons("nfs_image_path")
        else:
            image_nfs_path = '/home/rhevm_guest/'

        image_mount_path = self.get_vw_cons("local_mount_point")
        cmd = "mkdir %s" % image_mount_path
        self.runcmd(cmd, "create local images mount point", targetmachine_ip)
        cmd = "mkdir %s" % image_nfs_path
        self.runcmd(cmd, "create local nfs images directory", targetmachine_ip)

        cmd = "mount -r %s %s; sleep 10" % (image_server, image_mount_path)
        ret, output = self.runcmd(cmd, "mount images in host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to mount images from %s to %s." % (image_server, image_mount_path))
        else:
            raise FailException("Failed to mount images from %s to %s." % (image_server, image_mount_path))

        logger.info("Begin to copy guest images...")
        cmd = "cp -n %s %s" % (os.path.join(image_mount_path, "ENT_TEST_MEDIUM/images/kvm/*"), image_nfs_path)
        ret, output = self.runcmd(cmd, "copy all kvm images", targetmachine_ip)

        # cmd = "umount %s" % (image_mount_path)
        # ret, output = self.runcmd(cmd, "umount images in host")

    def generate_tmp_log(self, checkcmd, tmp_file, waiting_time=0, log_file='rhsm.log', targetmachine_ip=""):
        cmd = "tail -f -n 0 /var/log/rhsm/%s &> %s &" % (log_file, tmp_file)
        self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
        self.runcmd_service(checkcmd, targetmachine_ip)
        if "virtwho" in checkcmd:
            self.vw_check_sending_finished(tmp_file, targetmachine_ip)
        if waiting_time == 0:
            if "vdsmd" in checkcmd or "libvirtd" in checkcmd:
                time.sleep(120)
            elif "rhsmcertd" in checkcmd:
                time.sleep(100)
            elif "virsh" in checkcmd:
                time.sleep(5)
            else:
                time.sleep(20)
        else:
            logger.info("Wait %s seconds ..." % waiting_time)
            time.sleep(waiting_time)
        self.kill_pid("tail", targetmachine_ip)

    def kill_pid(self, pid_name, destination_ip=""):
        cmd = "ps -ef | grep %s -i | grep -v grep | awk '{print $2}'" % pid_name
#         ret, output = self.runcmd(cmd, "start to check %s pid" %pid_name, destination_ip)
        ret, output = self.runcmd(cmd, "start to check pid", destination_ip)
        if ret == 0 and output is not None:
            pids = output.strip().split('\n')
            for pid in pids:
                kill_cmd = "kill -9 %s" % pid
                self.runcmd(kill_cmd, "kill %s pid %s" % (pid_name, pid), destination_ip)

    # ========================================================
    #       Basic Functions
    # ========================================================

    def runcmd(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        return command.runcmd(cmd, cmddesc, targetmachine_ip, targetmachine_user, targetmachine_pass, timeout, showlogger)

    def runcmd_esx(self, cmd, cmddesc=None, targetmachine_ip=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "Welcome1", timeout, showlogger)

    def runcmd_xen(self, cmd, cmddesc=None, targetmachine_ip=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "Welcome1", timeout, showlogger)

    def runcmd_sam(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "red2015", timeout, showlogger)

    def runcmd_interact(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        return command.runcmd_interact(cmd, cmddesc, targetmachine_ip, targetmachine_user, targetmachine_pass, timeout, showlogger)

    def runcmd_service(self, command, targetmachine_ip=""):
        cmd = self.get_service_cmd(command, targetmachine_ip)
        return self.runcmd(cmd, "run service cmd: %s" % cmd, targetmachine_ip)

    def runcmd_local(self, cmd, timeout=None, showlogger=True):
        return command.runcmd_local(cmd, timeout, showlogger)

    def runcmd_local_pexpect(self, cmd, password=""):
        return command.runcmd_local_pexpect(cmd, password)

    def get_os_serials(self, targetmachine_ip=""):
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = self.runcmd(cmd, "get system version", targetmachine_ip=targetmachine_ip, showlogger=False)
        if ret == 0:
            return output.strip("\n").strip(" ")
        else: raise FailException("Failed to get os serials")

    def get_os_platform(self, targetmachine_ip=""):
        cmd = "lsb_release -i"
        (ret, output) = self.runcmd(cmd, showlogger=False)
        if ret == 0:
            platform = output.split("Enterprise")[1].strip()
            logger.info("It's successful to get system platform")
        else:
            raise FailException("Failed to get system platform.")
        return platform

    def get_server_info(self):
        # usage: server_ip, server_hostname, server_user, server_pass = self.get_server_info()
        return get_exported_param("SERVER_IP"), get_exported_param("SERVER_HOSTNAME"), self.get_vw_cons("username"), self.get_vw_cons("password")

    def get_esx_info(self):
        # usage: esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
        return self.get_vw_cons("server_owner"), self.get_vw_cons("server_env"), self.get_vw_cons("VIRTWHO_ESX_SERVER"), self.get_vw_cons("VIRTWHO_ESX_USERNAME"), self.get_vw_cons("VIRTWHO_ESX_PASSWORD")

    def get_hyperv_info(self):
        return self.get_vw_cons("server_owner"), self.get_vw_cons("server_env"), self.get_vw_cons("VIRTWHO_HYPERV_SERVER"), self.get_vw_cons("VIRTWHO_HYPERV_USERNAME"), self.get_vw_cons("VIRTWHO_HYPERV_PASSWORD")

    def get_xen_info(self):
        return self.get_vw_cons("server_owner"), self.get_vw_cons("server_env"), self.get_vw_cons("VIRTWHO_XEN_SERVER"), self.get_vw_cons("VIRTWHO_XEN_USERNAME"), self.get_vw_cons("VIRTWHO_XEN_PASSWORD")

    def get_rhevm_info(self):
        return self.get_vw_cons("server_owner"), self.get_vw_cons("server_env"), self.get_vw_cons("VIRTWHO_RHEVM_USERNAME"), self.get_vw_cons("VIRTWHO_RHEVM_PASSWORD")

    def get_libvirt_info(self):
        return self.get_vw_cons("server_owner"), self.get_vw_cons("server_env"), self.get_vw_cons("VIRTWHO_LIBVIRT_USERNAME"), self.get_vw_cons("VIRTWHO_LIBVIRT_PASSWORD")

    def get_hg_info(self, targetmachine_ip=""):
        if targetmachine_ip == "" or targetmachine_ip == None:
            host_guest_info = "in host machine"
        else:
            host_guest_info = "in guest machine %s" % targetmachine_ip
        return host_guest_info

    def get_rhsm_cons(self, name):
        rhsm_cons = RHSMConstants()
        if self.test_server == "SAM":
            if self.os_serial == "7" and name + "_el7" in rhsm_cons.sam_cons:
                return rhsm_cons.sam_cons[name + "_el7"]
            else:
                return rhsm_cons.sam_cons[name]
        elif self.test_server == "SATELLITE":
            if self.os_serial == "7" and name + "_el7" in rhsm_cons.sam_cons:
                return rhsm_cons.sam_cons[name + "_el7"]
            elif name + "_sat" in rhsm_cons.sam_cons:
                return rhsm_cons.sam_cons[name + "_sat"]
            else:
                return rhsm_cons.sam_cons[name]
        elif self.test_server == "STAGE" :
            if self.os_serial == "7" and name + "_el7" in rhsm_cons.stage_cons:
                return rhsm_cons.stage_cons[name + "_el7"]
            else:
                return rhsm_cons.stage_cons[name]
        else:
            raise FailException("Failed to get rhsm constant %s" % name)

    def get_vw_cons(self, name):
        virtwho_cons = VIRTWHOConstants()
        if self.test_server == "SAM":
            return virtwho_cons.virtwho_sam_cons[name]
        elif self.test_server == "SATELLITE":
            return virtwho_cons.virtwho_satellite_cons[name]
        elif self.test_server == "STAGE" :
            return virtwho_cons.virtwho_stage_cons[name]
        else:
            return virtwho_cons.virtwho_cons[name]
            # raise FailException("Failed to get virt-who constant %s" % name)

    def get_vw_guest_name(self, guest_name):
        return VIRTWHOConstants().virtwho_cons[guest_name] + "_" + self.test_server.capitalize()

    def get_hostname(self, targetmachine_ip=""):
        cmd = "hostname"
        ret, output = self.runcmd(cmd, "geting the machine's hostname", targetmachine_ip)
        if ret == 0:
            hostname = output.strip(' \r\n').strip('\r\n') 
            logger.info("Succeeded to get the machine's hostname %s." % hostname) 
            return hostname
        else:
            raise FailException("Test Failed - Failed to get hostname in %s." % self.get_hg_info(targetmachine_ip))

    def get_locator(self, name):
        rhsm_gui_locator = RHSMGuiLocator()
        if name + "-" + self.os_serial in rhsm_gui_locator.element_locators.keys():
            return rhsm_gui_locator.element_locators[name + "-" + self.os_serial]
        else:
            return rhsm_gui_locator.element_locators[name]

    def get_service_cmd(self, cmd_name, targetmachine_ip=""):
        virtwho_cons = VIRTWHOConstants()
        if targetmachine_ip != None and targetmachine_ip != "":
            os_serial = self.os_serial
        else:
            os_serial = self.get_os_serials(targetmachine_ip)
        if cmd_name in virtwho_cons.virt_who_commands:
            if os_serial == "7":
                cmd = virtwho_cons.virt_who_commands[cmd_name + "_systemd"]
            else:
                cmd = virtwho_cons.virt_who_commands[cmd_name]
            return cmd
        else:
            return cmd_name

    def service_command(self, command, targetmachine_ip="", is_return=False):
        ret, output = self.runcmd_service(command, targetmachine_ip)
        if is_return == True:
            if ret == 0:
                logger.info("Succeeded to run cmd %s in %s." % (command, self.get_hg_info(targetmachine_ip)))
                return True
            else:
                return False
        else:
            if ret == 0:
                logger.info("Succeeded to run cmd %s in %s." % (command, self.get_hg_info(targetmachine_ip)))
                return output
            else:
                raise FailException("Test Failed - Failed to run cmd in %s." % (command, self.get_hg_info(targetmachine_ip)))

    # ========================================================
    #       Configure Server Functions
    # ========================================================

    def configure_sam_host(self, samhostip, samhostname, targetmachine_ip=""):
        self.configure_host_file(samhostip, samhostname, targetmachine_ip)
        cmd = "rpm -qa | grep candlepin-cert-consumer | xargs rpm -e"
        ret, output = self.runcmd(cmd, "if candlepin-cert-consumer package exist, remove it.", targetmachine_ip)
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)
        cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
        ret, output = self.runcmd(cmd, "install candlepin cert", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        else:
            raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        # workaround for bug https://bugzilla.redhat.com/show_bug.cgi?id=1310827
        cmd = "echo '{\"proc_cpuinfo.common.flags\":\"*****************\"}' > /etc/rhsm/facts/cpuinfo_override.facts"
        self.runcmd(cmd, "update rhsm facts due to bug 1310827", targetmachine_ip)

    def configure_satellite_host(self, satellitehostip, satellitehostname, targetmachine_ip=""):
        if "satellite" in satellitehostname:
            # for satellite installed in qeos
            satellitehostname = satellitehostname + ".novalocal"
        self.configure_host_file(satellitehostip, satellitehostname, targetmachine_ip)
        cmd = "rpm -qa | grep katello-ca-consumer | xargs rpm -e"
        ret, output = self.runcmd(cmd, "if katello-ca-consumer package exist, remove it.", targetmachine_ip)
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)
        cmd = "rpm -ivh http://%s/pub/katello-ca-consumer-latest.noarch.rpm" % (satellitehostip)
        ret, output = self.runcmd(cmd, "install katello-ca-consumer-latest.noarch.rpm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with satellite configuration.")
        else:
            raise FailException("Failed to install candlepin cert and configure the system with satellite configuration.")

    def configure_host_file(self, server_ip, server_hostname, targetmachine_ip=""):
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (server_ip, server_ip, server_hostname)
        ret, output = self.runcmd(cmd, "configure /etc/hosts", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure /etc/hosts")
        else:
            raise FailException("Failed to configure /etc/hosts")
        # remove /etc/pki/product-default/135.pem, or else auto subscribe failed
        cmd = "rm -f /etc/pki/product-default/135.pem"
        ret, output = self.runcmd(cmd, "remove /etc/pki/product-default/135.pem", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove /etc/pki/product-default/135.pem")
        else:
            raise FailException("Failed to remove /etc/pki/product-default/135.pem")

    def configure_stage_host(self, hostname, targetmachine_ip=""):
        cmd = "sed -i -e 's/^hostname.*/hostname = %s/g' /etc/rhsm/rhsm.conf" % hostname
        ret, output = self.runcmd(cmd, "configure hostname for stage testing in rhsm.conf", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure hostname for stage testing in rhsm.conf")
        else:
            raise FailException("Failed to configure hostname for stage testing in rhsm.conf")
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)

    def configure_baseurl(self, baseurl, targetmachine_ip=""):
        cmd = "sed -i -e 's/^baseurl.*/baseurl=https:\/\/%s/g' /etc/rhsm/rhsm.conf" % baseurl
        ret, output = self.runcmd(cmd, "configure baseurl for stage", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure baseurl for stage")
        else:
            raise FailException("Failed to configure baseurl for stage")
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)

    def configure_server(self, server_ip="", server_hostname="", targetmachine_ip=""):
        if self.test_server == "STAGE" :
            self.configure_stage_host(self.get_rhsm_cons("hostname"), targetmachine_ip)
            self.configure_baseurl(self.get_rhsm_cons("baseurl"), targetmachine_ip)
        else:
            if server_ip == "" or server_hostname == "":
                server_ip = get_exported_param("SERVER_IP")
                server_hostname = get_exported_param("SERVER_HOSTNAME")
            if self.test_server == "SAM" :
                self.configure_sam_host(server_ip, server_hostname, targetmachine_ip)
            elif self.test_server == "SATELLITE" :
                self.configure_satellite_host(server_ip, server_hostname, targetmachine_ip)
            else:
                raise FailException("Test Failed - Failed to configure rhsm testing server ... ")

    # ========================================================
    #       SAM Functions
    # ========================================================
    def server_remove_system(self, system_uuid, destination_ip="", username="", password=""):
        ''' remove system in test server '''
        if self.test_server == "SAM":
            cmd = "headpin -u admin -p admin system unregister --%s=%s --org=ACME_Corporation" % (self.server_check_name(system_uuid, destination_ip, username, password), system_uuid)
            ret, output = self.runcmd_sam(cmd, "remove system in sam server", destination_ip)
            if ret == 0 and system_uuid in output:
                logger.info("Succeeded to remove system %s in sam server" % system_uuid)
            else:
                raise FailException("Failed to remove system %s in sam server" % system_uuid)
        elif self.test_server == "SATELLITE":
            self.satellite_system_remove(system_uuid)
            logger.info("Succeeded to remove system %s in satellite server" % system_uuid)
        elif self.test_server == "STAGE":
            self.stage_system_remove(system_uuid, username, password)
        else:
            raise FailException("Failed to identify test server")

    def server_subscribe_system(self, system_uuid, poolid, destination_ip="", username="", password=""):
        ''' subscribe host in test server '''
        if self.test_server == "SAM":
            cmd = "headpin -u admin -p admin system subscribe --%s=%s --org=ACME_Corporation --pool=%s " % (self.server_check_name(system_uuid, destination_ip, username, password), system_uuid, poolid)
            ret, output = self.runcmd_sam(cmd, "subscribe host in sam server", destination_ip)
            if ret == 0 and system_uuid in output:
                logger.info("Succeeded to subscribe host %s in sam server" % system_uuid)
            else:
                raise FailException("Failed to subscribe host %s in sam server" % system_uuid)
        elif self.test_server == "SATELLITE":
            self.__satellite_attach(system_uuid, poolid)
            logger.info("Succeeded to subscribe host %s in satellite server" % system_uuid)
        elif self.test_server == "STAGE":
            self.__stage_attach(system_uuid, poolid, username, password)
        else:
            raise FailException("Failed to identify test server")

    def server_unsubscribe_all_system(self, system_uuid, destination_ip="", username="", password=""):
        ''' unsubscribe host in test server '''
        if self.test_server == "SAM":
            cmd = "headpin -u admin -p admin system unsubscribe --%s=%s --org=ACME_Corporation --all" % (self.server_check_name(system_uuid, destination_ip, username, password), system_uuid)
            ret, output = self.runcmd_sam(cmd, "unsubscribe host in sam server", destination_ip)
        elif self.test_server == "SATELLITE":
            self.__satellite_unattach_all(system_uuid)
            logger.info("Succeeded to unsubscribe host %s in satellite server" % system_uuid)
        elif self.test_server == "STAGE":
            self.__stage_unattach_all(system_uuid, username, password)
        else:
            raise FailException("Failed to identify test server")

    def server_check_name(self, system_uuid, destination_ip="", username="", password=""):
        cmd = "headpin -u admin -p admin system list --org=ACME_Corporation | grep %s | awk '{print $1, $2}'" % system_uuid
        ret, output = self.runcmd_sam(cmd, "check whether provided system_uuid is name", destination_ip)
        if system_uuid == output.split()[0]:
            return "name"
        elif system_uuid == output.split()[1]:
            return "uuid"
        else:
            raise FailException("Failed to check %s exist in server") % system_uuid

    def server_system_info(self, info_key, system_uuid, username="", password=""):
        if self.test_server == "SAM":
            return self.sam_system_info(info_key, system_uuid, username, password)
        elif self.test_server == "SATELLITE":
            return self.satellite_system_info(info_key, system_uuid, username, password)
        elif self.test_server == "STAGE":
            return self.stage_system_info(info_key, system_uuid, username, password)
        else:
            raise FailException("Failed to identify test server")

    # ========================================================
    #       SAM Functions
    # ========================================================
    def sam_system_info(self, info_key, uuid, username="", password=""):
        return self.get_json("sam/api/systems/%s/subscription_status/" % uuid)[info_key]

    # ========================================================
    #       SATELLITE Functions https://***/apidoc/v2
    # ========================================================
    def __satellite_attach(self, host_uuid, pool_id):
        logger.info ("Attch server %s with pool %s" % (host_uuid, pool_id))
        host_id = self.satellite_name_to_id(host_uuid)
        katello_id = self.satellite_pool_to_id(pool_id)
        location = "api/v2/hosts/%s/subscriptions/add_subscriptions" % host_id
        json_data = json.dumps({"subscriptions":[{"id":katello_id, "quantity":1}]})
        logger.info ("Attach subscription: %s" % json_data)
        self.put_json(location, json_data)
        # consumer_pool_id = self.put_json(location, json_data)["results"][0]["id"]
        # logger.info ("Attch return consumer_pool_id is %s" % consumer_pool_id)

    def __satellite_unattach(self, host_uuid, katello_id):
        logger.info ("Unattch server %s with pool %s" % (host_uuid, katello_id))
        host_id = self.satellite_name_to_id(host_uuid)
        location = "api/v2/hosts/%s/subscriptions/remove_subscriptions" % (host_id)
        json_data = json.dumps({"subscriptions":[{"id":katello_id}]})
        self.put_json(location, json_data)

    def __satellite_unattach_all(self, uuid):
        for katello_id in self.satellite_consumed_list(uuid):
            self.__satellite_unattach(uuid, katello_id)

    def satellite_system_remove(self, uuid):
        host_id = self.satellite_name_to_id(uuid)
        return self.delete_json("api/v2/hosts/%s" % host_id)

    def satellite_name_to_id(self, name):
        systems = self.satellite_system_list()["results"]
        for item in systems:
#             logger.info("item >>>: %s" % item)
            if name.lower() in str(item):
            # if name in item["name"]:
                return item["id"]
        raise FailException("Failed to get system id by: %s" % name)

    def satellite_pool_to_id(self, pool_id):
        systems = self.satellite_pool_list()["results"]
        for item in systems:
            # logger.info("item >>>: %s" % item)
            if pool_id in item["cp_id"]:
                return item["id"]
        raise FailException("Failed to get katello id by: %s" % pool_id)

    def satellite_system_list(self):
        return self.get_json("api/v2/hosts/")

    def satellite_pool_list(self):
        satellite_pool_list = self.get_json("katello/api/organizations/1/subscriptions")
        # logger.info("satellite_pool_list >>>: %s" % satellite_pool_list)
        return satellite_pool_list

    def satellite_consumed_list(self, uuid):
        consumed_id_list = []
        host_id = self.satellite_name_to_id(uuid)
        all_consumed = self.get_json("api/v2/hosts/%s/subscriptions" % host_id)["results"]
        # logger.info("all_consumed: %s" % (all_consumed))
        for consumed in all_consumed:
            logger.info("system %s has consumed: %s" % (uuid, consumed["id"]))
            consumed_id_list.append(consumed["id"])
        return consumed_id_list

    def satellite_system_info(self, info_key, uuid, username="", password=""):
        host_id = self.satellite_name_to_id(uuid)
        return self.get_json("api/v2/hosts/%s" % host_id)[info_key]

    # ========================================================
    #       STAGE Functions https://hosted.englab.nay.redhat.com/issues/11373
    # ========================================================
    def __stage_attach(self, host_name, pool_id, username="", password=""):
        logger.info ("Attch system %s with pool %s" % (host_name, pool_id))
        host_uuid_list = self.stage_name_to_uuid(host_name, username, password)
        for host_uuid in host_uuid_list:
            location = "subscription/consumers/%s/entitlements?pool=%s" % (host_uuid, pool_id)
            logger.info ("Attach %s with subscription: %s" % (host_name, pool_id))
            self.post_json(location, username, password)

    def __stage_unattach_all(self, host_name, username="", password=""):
        logger.info ("Unattch all for system %s" % host_name)
        host_uuid_list = self.stage_name_to_uuid(host_name, username, password)
        for host_uuid in host_uuid_list:
            location = "subscription/consumers/%s/entitlements" % host_uuid
            self.delete_json(location, username, password)

    def stage_system_remove(self, host_name, username="", password=""):
        host_uuid_list = self.stage_name_to_uuid(host_name, username, password)
        for host_uuid in host_uuid_list:
            logger.info ("Remove system %s" % host_name)
            location = "subscription/consumers/%s" % host_uuid
            self.delete_json(location, username, password)

    def stage_name_to_uuid(self, name, username="", password=""):
        systems = self.stage_system_list(username, password)
        uuid_list = []
        for item in systems:
            # logger.info("item >>>: %s" % item)
            if name in item["name"]:
                uuid_list.append(item["uuid"])
        if len(uuid_list):
            # logger.info("uuid_list >>>: %s" % uuid_list)
            return uuid_list
        else:
            raise FailException("Failed to get system uuid by: %s" % name)

    def stage_system_list(self, username="", password=""):
        if username != None and username != "":
            owner = self.get_rhsm_cons("default_org")
            return self.get_json("subscription/owners/%s/consumers" % owner, username, password)
        else:
            owner = self.get_vw_cons("server_owner")
            return self.get_json("subscription/owners/%s/hypervisors" % owner, username, password)

    # clean stage env, remove all systems
    def stage_system_remove_all(self, username, password):
        rhsm_cons = RHSMConstants()
        if username == rhsm_cons.stage_cons["username"]:
            owner = self.get_rhsm_cons("default_org")
        else:
            owner = self.get_vw_cons("server_owner")
        systems = self.stage_system_list_all(username, password, owner)
        for item in systems:
            location = "subscription/consumers/%s" % item["uuid"]
            self.delete_json(location, username, password)

    def stage_system_list_all(self, username, password, owner):
        all_units = self.get_json("subscription/owners/%s/consumers" % owner, username, password) + self.get_json("subscription/owners/%s/hypervisors" % owner, username, password)
        logger.info ("all units is : %s" % all_units)
        return all_units

    def stage_system_info(self, info_key, host_name, username="", password=""):
        host_uuid_list = self.stage_name_to_uuid(host_name, username, password)
        for host_uuid in host_uuid_list:
            logger.info ("get system %s product status" % host_name)
            location = "subscription/consumers/%s" % host_uuid
            return self.get_json(location, username, password)[info_key]

    # ========================================================
    #       REQUESTS CRUD
    # ========================================================
    def get_auth(self, username="", password=""):
        if self.test_server == "STAGE":
            if username != None and username != "":
                return "subscription.rhsm.stage.redhat.com", username, password
            else:
                return "subscription.rhsm.stage.redhat.com", self.get_vw_cons("username"), self.get_vw_cons("password")
        else:
            return get_exported_param("SERVER_IP"), self.get_vw_cons("username"), self.get_vw_cons("password")

    def get_json(self, location, username="", password=""):
        """
        Performs a GET using the passed URL location
        """
        server_ip, username, password = self.get_auth(username, password)
        sat_api = "https://%s/%s" % (server_ip, location)
        result = requests.get(
            sat_api,
            auth=(username, password),
            verify=False)
        ret, output = result.status_code, result.json()
        logger.info("Status Code >>>: %s" % ret)
        # logger.info("Result >>>: %s" % output)
        if ret not in (200,):
            raise FailException("Failed to run requests get: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests get: %s" % sat_api)
            return output

    def post_json(self, location, json_data=None, username="", password=""):
        """
        Performs a POST and passes the data to the URL location
        """
        server_ip, username, password = self.get_auth(username, password)
        sat_api = "https://%s/%s" % (server_ip, location)
        post_headers = {'content-type': 'application/json'}
        result = requests.post(
            sat_api,
            data=json_data,
            auth=(username, password),
            verify=False,
            headers=post_headers)
        ret, output = result.status_code, result.json()
        logger.info("Status Code >>>: %s" % ret)
        # logger.info("Result >>>: %s" % output)
        if ret not in (200, 201):
            raise FailException("Failed to run requests post: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests post: %s" % sat_api)
            return output

    def put_json(self, location, json_data=None, username="", password=""):
        """
        Performs a PUT and passes the data to the URL location
        """
        server_ip, username, password = self.get_auth(username, password)
        sat_api = "https://%s/%s" % (server_ip, location)
        post_headers = {'content-type': 'application/json'}
        result = requests.put(
            sat_api,
            data=json_data,
            auth=(username, password),
            verify=False,
            headers=post_headers)
        ret, output = result.status_code, result.json()
        logger.info("Status Code >>>: %s" % ret)
        # logger.info("Result >>>: %s" % output)
        if ret not in (200,):
            raise FailException("Failed to run requests put: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests put: %s" % sat_api)
            return output

    def delete_json(self, location, username="", password=""):
        """
        Performs a DELETE using the passed URL location
        """
        server_ip, username, password = self.get_auth(username, password)
        sat_api = "https://%s/%s" % (server_ip, location)
        result = requests.delete(
            sat_api,
            auth=(username, password),
            verify=False)
        ret, output = result.status_code, result
        logger.info("Status Code >>>: %s" % ret)
        # logger.info("Result >>>: %s" % output)
        if ret not in (200, 202, 204):
            raise FailException("Failed to run requests delete: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests delete: %s" % sat_api)
            return output

    # ========================================================
    #       Skip Test Functions
    # ========================================================

    def skip_rhel7_check(self):
        if self.os_serial == "7" :
            logger.info("rhel 7.x do not support, this test case is skipped ...")
            return True
        else: return False

    def skip_satellite_check(self):
        if self.test_server == "SATELLITE" :
            logger.info("satellite do not support, this test case is skipped ...")
            return True
        else: return False

    def skip_stage_check(self):
        if self.test_server == "STAGE" :
            logger.info("stage do not support, this test case is skipped ...")
            return True
        else: return False

    def skip_sam_check(self):
        if self.test_server == "SAM" :
            logger.info("sam do not support, this test case is skipped ...")
            return True
        else: return False

    # ========================================================
    #       unittest setup
    # ========================================================
    def setUp(self):
        # show log in unittest report
        self.unittest_handler = logging.StreamHandler(sys.stdout)
        self.unittest_handler.setFormatter(formatter)
        logger.addHandler(self.unittest_handler)
        # turn paramiko log off
        # paramiko_logger = logging.getLogger("paramiko.transport")
        # paramiko_logger.disabled = True
        logger.info(" ")
        logger.info("**************************************************************************************************************")
        # for install case, ignore this
        # case_name = sys.argv[1]
        # logger.info("running %s" % case_name)
        # if "_install.py" in case_name:
        #    logger.info("begin running install ...")
        #    self.os_serial = "*"
        # else:
        #    self.os_serial = self.get_os_serials()
        self.os_serial = self.get_os_serials()
        self.test_server = get_exported_param("SERVER_TYPE")
        logger.info("********** Begin Running ...**** OS: RHEL %s **** Server: %s **********" % (self.os_serial, self.test_server))
        SERVER_IP = get_exported_param("SERVER_IP")
        SERVER_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
        REMOTE_IP = get_exported_param("REMOTE_IP")
        REMOTE_IP_2 = get_exported_param("REMOTE_IP_2")
        RHEL_COMPOSE = get_exported_param("RHEL_COMPOSE")
        BREW_VIRTWHO = get_exported_param("BREW_VIRTWHO")
        logger.info("**************************************************************************************************************")

    def tearDown(self):
        logger.removeHandler(self.unittest_handler)

#     def test_self(self):
#         self.__satellite_attach("aee4ff00-8c33-11e2-994a-6c3be51d959a", "8ac213ab55f1c6470155f1d8c32d026f")
#         self.__satellite_unattach_all("aee4ff00-8c33-11e2-994a-6c3be51d959a")
#         self.__stage_attach("aee4ff00-8c33-11e2-994a-6c3be51d959a", "8a99f9865558436a01556be3f6b30815")
#         self.__stage_unattach_all("aee4ff00-8c33-11e2-994a-6c3be51d959a")
#         self.stage_system_remove("aee4ff00-8c33-11e2-994a-6c3be51d959a")
#         self.stage_system_remove_all()
#         logger.info (self.server_system_info("entitlementStatus", "hp-z220-13.qe.lab.eng.nay.redhat.com", username="new_test", password="redhat"))
#         logger.info (self.server_system_info("subscription_status_label", "149902d6-72aa-4ef5-b69e-32ef2fbc6755", username="admin", password="admin"))
#         logger.info (self.server_system_info("status", "f25af795-87c0-49a6-9c47-1c371583ee88", username="admin", password="admin"))

if __name__ == "__main__":
    unittest.main()
