from utils import *
from testcases.base import Base
from utils.exception.failexception import FailException
from utils.libvirtAPI.Python.xmlbuilder import XmlBuilder

class VIRTWHOBase(Base):
    # ========================================================
    #       Basic Functions
    # ========================================================

    def brew_virtwho_upgrate(self, targetmachine_ip=None):
        # virt-who upgrade via brew
        brew_virt_who = get_exported_param("BREW_VIRTWHO")
        cmd = "yum -y upgrade %s" % brew_virt_who
        ret, output = self.runcmd(cmd, "upgrade virt-who via brew", targetmachine_ip)

    def upstream_virtwho_install(self, targetmachine_ip=None):
        self.cm_install_basetool(targetmachine_ip)
        # virt-who install via upstream
        github_url = get_exported_param("GITHUB_URL")
        cmd = "git clone %s; cd virt-who; make install" % github_url
        ret, output = self.runcmd(cmd, "install virt-who via upstream", targetmachine_ip)

    def set_virtwho_version(self, targetmachine_ip=None):
        self.cm_set_rpm_version("VIRTWHO_VERSION", "virt-who", targetmachine_ip)

    def check_virtwho_pkg(self, rhevm_compose, server_ip=None, server_user=None, server_passwd=None):
        cmd = "rpm -qa | grep virt-who"
        ret, output = self.runcmd(cmd, "check virt-who package status", server_ip, server_user, server_passwd)
        if "virt-who" in output and "sat" not in output:
            logger.info("Succeeded to check virt-who package from original repo exist.need to delete it and deploy new one")
            cmd = "rpm -e virt-who"
            if ret == 0:
                logger.info("Succeeded to delete virt-who package from original repo")
            else:
                raise FailException("Test Failed - Failed to delete virt-who package from original repo")
        else:
            logger.info("virt-who package is not install, need to install.")

    def start_dbus_daemon(self, targetmachine_ip=""):
        cmd = "dbus-daemon --system"
        ret, output = self.runcmd(cmd, "start dbus-daemon", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to start dbus-daemon.")
        else:
            logger.info("Failed to start dbus-daemon.")

    def downgrade_libacl(self, targetmachine_ip=""):
        cmd = "yum downgrade libacl -y"
        ret, output = self.runcmd(cmd, "down-grade libacl", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to down-grade libacl.")
        else:
            logger.info("Failed to down-grade libacl.")

    def sys_setup(self, targetmachine_ip=None):
#         if "release" not in get_exported_param("RHEL_COMPOSE"):
#             self.cm_install_basetool(targetmachine_ip)
        server_compose = get_exported_param("SERVER_COMPOSE")
        hypervisor_type = get_exported_param("HYPERVISOR_TYPE")
        tool_src = get_exported_param("VIRTWHO_ORIGINAL_SRC")
        rhel_compose = get_exported_param("RHEL_COMPOSE")
        logger.info("tool_src is %s, server_compose is %s" % (tool_src, server_compose))
        # install virt-who via satellite 6 tools repo when testing ohsnap-satellite
        self.start_dbus_daemon(targetmachine_ip)
        if "release" in rhel_compose:
            if not self.sub_isregistered(targetmachine_ip):
                self.sub_register("QualityAssurance", "VHVFhPS5TEG8dud9")
                self.sub_auto_subscribe(targetmachine_ip)
            if tool_src is None or "sattool" in tool_src:
                logger.info("*****tool_src is %s" %tool_src)
                logger.info("*****os_srial is %s" %self.os_serial)
            # check if host registered to cdn server
                if self.os_serial == "6":
                    logger.info("Down-grade libacl as failed to install virt-who")
                    self.downgrade_libacl(targetmachine_ip)
                    logger.info("%s will installed on rhel6.8" %server_compose)
                    if "satellite63" in server_compose:
                        cmd = ('cat <<EOF > /etc/yum.repos.d/sat6_tools.repo\n'
                            '[sat6-tools]\n'
                            'name=Satellite 6.3 Tools\n'
                            'baseurl=http://sat-r220-02.lab.eng.rdu2.redhat.com/pulp/repos/Sat6-CI/QA/Tools_6_3_RHEL6/custom/Satellite_Tools_6_3_Composes/Satellite_Tools_6_3_RHEL6_x86_64/\n'
                            'enabled=1\n'
                            'gpgcheck=0\n'
                            'EOF'
                            )  
                    else:
                        cmd = ('cat <<EOF > /etc/yum.repos.d/sat6_tools.repo\n'
                            '[sat6-tools]\n'
                            'name=Satellite 6 Tools\n'
                            'baseurl=http://sat-r220-02.lab.eng.rdu2.redhat.com/pulp/repos/Sat6-CI/QA/Tools_RHEL6/custom/Red_Hat_Satellite_Tools_6_2_Composes/RHEL6_Satellite_Tools_x86_64_os/\n'
                            'enabled=1\n'
                            'gpgcheck=0\n'
                            'EOF'
                            )
                else:
                    logger.info("%s will installed on rhel7.3" %server_compose)
                    if "satellite63" in server_compose:
                        cmd = ('cat <<EOF > /etc/yum.repos.d/sat6_tools.repo\n'
                            '[sat6-tools]\n'
                            'name=Satellite 6.3 Tools\n'
                            'baseurl=http://sat-r220-02.lab.eng.rdu2.redhat.com/pulp/repos/Sat6-CI/QA/Tools_6_3_RHEL7/custom/Satellite_Tools_6_3_Composes/Satellite_Tools_x86_64/\n'
                            'enabled=1\n'
                            'gpgcheck=0\n'
                            'EOF'
                            )
                    else:
                        cmd = ('cat <<EOF > /etc/yum.repos.d/sat6_tools.repo\n'
                            '[sat6-tools]\n'
                            'name=Satellite 6 Tools\n'
                            'baseurl=http://sat-r220-02.lab.eng.rdu2.redhat.com/pulp/repos/Sat6-CI/QA/Tools_RHEL7/custom/Red_Hat_Satellite_Tools_6_2_Composes/RHEL7_Satellite_Tools_x86_64_os/\n'
                            'enabled=1\n'
                            'gpgcheck=0\n'
                            'EOF'
                            )      
                ret, output = self.runcmd(cmd, "add satellite ohsnap tools repo", targetmachine_ip)
                if ret == 0:
                    logger.info("Succeeded to add satellite ohsnap tools repo.")
                else:
                    raise FailException("Test Failed - Failed to add satellite ohsnap tools repo.")
            else:
                if self.os_serial == "6":
                    logger.info("Down-grade libacl as failed to install virt-who")
                    self.downgrade_libacl(targetmachine_ip)
        if "remote_libvirt" in hypervisor_type or "rhevm" in hypervisor_type:
            self.cm_update_system(targetmachine_ip)
        # system setup for virt-who testing
        cmd = "yum install -y virt-who"
        ret, output = self.runcmd(cmd, "install virt-who for virt-who testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing.")
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing.")
        self.start_dbus_daemon(targetmachine_ip)

    def stop_firewall(self, targetmachine_ip=""):
        ''' stop iptables service and setenforce as 0. '''
        # stop iptables service
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "systemctl stop firewalld.service"
            ret, output = self.runcmd(cmd, "Stop firewalld service", targetmachine_ip)
            cmd = "systemctl status firewalld.service"
            ret, output = self.runcmd(cmd, "Check firewalld service status", targetmachine_ip)
            if ("Stopped firewalld" in output) or ("inactive" in output) or ("Active: inactive" in output):
                logger.info("Succeeded to stop firewalld service.")
            else:
                logger.info("Failed to stop firewalld service.")
        else:
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

    def get_hostname(self, targetmachine_ip=""):
        cmd = "hostname"
        ret, output = self.runcmd(cmd, "geting the machine's hostname", targetmachine_ip)
        if ret == 0:
            hostname = output.strip(' \r\n').strip('\r\n') 
            logger.info("Succeeded to get the machine's hostname %s." % hostname) 
            return hostname
        else:
            raise FailException("Test Failed - Failed to get hostname in %s." % self.get_hg_info(targetmachine_ip))

    def virtwho_cli(self, mode):
        # only return CLI for virt-who esx, remote libvirt, hyperv mode, don't run cli 
        if mode == "esx":
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password)
        elif mode == "hyperv":
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            cmd = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password)
        elif mode == "xen":
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            cmd = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_env, xen_server, xen_username, xen_password)
        elif mode == "rhevm":
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
            if "rhevm-4"in rhevm_version:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443" + "\/ovirt-engine\/"
            else:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
        elif mode == "libvirt":
            libvirt_owner, libvirt_env, libvirt_username, libvirt_password = self.get_libvirt_info()
            if "remote_libvirt" in get_exported_param("HYPERVISOR_TYPE"):
                libvirt_server = get_exported_param("REMOTE_IP_1")
            else:
                libvirt_server = get_exported_param("REMOTE_IP")
            cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, libvirt_env, libvirt_server, libvirt_username, libvirt_password)
        else:
            raise FailException("Failed to get virt-who comand line with %s mode" % mode)
        return cmd

    def vw_restart_virtwho(self, targetmachine_ip=""):
        ''' restart virt-who service. '''
        ret, output = self.runcmd_service("restart_virtwho", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart virt-who service.")
        else:
            raise FailException("Test Failed - Failed to restart virt-who service.")

    def vw_stop_virtwho(self, targetmachine_ip=""):
        ''' stop virt-who service. '''
        ret, output = self.runcmd_service("stop_virtwho", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to stop virt-who service.")
        else:
            raise FailException("Failed to stop virt-who service.")

    def vw_check_virtwho_status(self, targetmachine_ip=""):
        ''' check the virt-who status. '''
        ret, output = self.runcmd_service("status_virtwho", targetmachine_ip)
        if ret == 0 and "running" in output:
            logger.info("Succeeded to check virt-who is running.")
        else:
            raise FailException("Test Failed - Failed to check virt-who is running.")

    def vw_check_libvirtd_status(self, targetmachine_ip=""):
        ''' check the libvirtd status. '''
        ret, output = self.runcmd_service("status_libvirtd", targetmachine_ip)
        if ret == 0 and "running" in output:
            logger.info("Succeeded to check libvirtd is running.")
        else:
            raise FailException("Test Failed - Failed to check libvirtd is running.")

    def vw_restart_libvirtd(self, targetmachine_ip=""):
        ''' restart libvirtd service. '''
        ret, output = self.runcmd_service("restart_libvirtd", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart libvirtd service.")
        else:
            raise FailException("Test Failed - Failed to restart libvirtd")

    def vw_restart_libvirtd_vdsm(self, targetmachine_ip=""):
        ''' restart libvirtd service. '''
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "service libvirtd restart"
            ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restart libvirtd service.")
            else:
                raise FailException("Test Failed - Failed to restart libvirtd")
        else:
            cmd = "initctl restart libvirtd"
            ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restart libvirtd service.")
            else:
                raise FailException("Failed to initctl restart libvirtd")

    # run virt-who oneshot by cli, return the output
    def virtwho_oneshot(self, mode, targetmachine_ip=""):
        cmd = self.virtwho_cli(mode) + " -o -d "
        self.service_command("stop_virtwho", targetmachine_ip)
        ret, output = self.runcmd(cmd, "executing virt-who with one shot", targetmachine_ip)
#         self.service_command("restart_virtwho")
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

    def check_virtwho_thread(self, number, targetmachine_ip=""):
        ''' check virt-who thread number '''
        cmd = "ps -ef | grep -v grep | grep virt-who | wc -l"
        ret, output = self.runcmd(cmd, "check virt-who thread", targetmachine_ip)
        if ret == 0 and int(output.strip()) == number:
            logger.info("Succeeded to check virt-who thread number is %s." % number)
        else:
            raise FailException("Test Failed - Failed to check virt-who thread number is %s." % number)

    def update_config_to_default(self, targetmachine_ip=""):
        ''' update virt-who configure file to default mode '''
        cmd = "sed -i -e 's/^.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=0/g' -e 's/^.*VIRTWHO_INTERVAL=.*/#VIRTWHO_INTERVAL=0/g' -e 's/^.*VIRTWHO_VDSM=.*/#VIRTWHO_VDSM=0/g' -e 's/^.*VIRTWHO_RHEVM=.*/#VIRTWHO_RHEVM=0/g' -e 's/^.*VIRTWHO_HYPERV=.*/#VIRTWHO_HYPERV=0/g' -e 's/^.*VIRTWHO_ESX=.*/#VIRTWHO_ESX=0/g' -e 's/^.*VIRTWHO_LIBVIRT=.*/#VIRTWHO_LIBVIRT=0/g' /etc/sysconfig/virt-who"
        ret, output = self.runcmd(cmd, "updating virt-who configure file to defualt", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file to defualt.")
        else:
            raise FailException("Failed to virt-who configure file to defualt.")

    def config_option_disable(self, option, targetmachine_ip=""):
        # comment option in /etc/sysconfig/virt-who if given option enabled
        cmd = "sed -i 's/^%s/#%s/' /etc/sysconfig/virt-who" % (option, option)
        (ret, output) = self.runcmd(cmd, "Disable %s in /etc/sysconfig/virt-who" % option, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to disable %s." % option)
        else:
            raise FailException("Failed to disable %s." % option)

    def config_option_enable(self, option, targetmachine_ip=""):
        # uncomment option in /etc/sysconfig/virt-who if given option disabled
        cmd = "sed -i 's/#%s/%s/' /etc/sysconfig/virt-who" % (option, option)
        (ret, output) = self.runcmd(cmd, "Enable %s in /etc/sysconfig/virt-who" % option, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable %s." % option)
        else:
            raise FailException("Failed to enable %s." % option)

    def config_option_setup_value(self, option, value="", targetmachine_ip=""):
        # setup value for option in /etc/sysconfig/virt-who
        self.config_option_enable(option, targetmachine_ip)
        cmd = "sed -i 's/^%s=.*/%s=%s/' /etc/sysconfig/virt-who" % (option, option, value)
        (ret, output) = self.runcmd(cmd, "set %s to %s" % (option, value), targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set %s=%s" % (option, value))
        else:
            raise FailException("Failed to set %s=%s" % (option, value))

    def set_virtwho_sec_config(self, mode, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_virtwho_sec_config_with_keyvalue(self, mode, key, value, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        pattern = re.compile(r'%s=.*?(?=\n|$)' % key)
        self.set_virtwho_d_conf(conf_file, pattern.sub("%s=%s" % (key, value), conf_data), targetmachine_ip)

    def set_virtwho_d_data(self, mode, targetmachine_ip=""):
        # prepare virt_who.d data.
        conf_file = "/etc/virt-who.d/virt-who.conf"
        if mode == "esx":
            virtwho_owner, virtwho_env, virtwho_server, virtwho_username, virtwho_password = self.get_esx_info()
        elif mode == "libvirt":
            virtwho_owner, virtwho_env, virtwho_username, virtwho_password = self.get_libvirt_info()
            if "remote_libvirt" in get_exported_param("HYPERVISOR_TYPE"):
                virtwho_server = get_exported_param("REMOTE_IP_1")
            else:
                virtwho_server = get_exported_param("REMOTE_IP")
        elif mode == "hyperv":
            virtwho_owner, virtwho_env, virtwho_server, virtwho_username, virtwho_password = self.get_hyperv_info()
        elif mode == "xen":
            virtwho_owner, virtwho_env, virtwho_server, virtwho_username, virtwho_password = self.get_xen_info()
        elif mode == "rhevm":
            virtwho_owner, virtwho_env, virtwho_username, virtwho_password = self.get_rhevm_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
            if "rhevm-4"in rhevm_version:
                virtwho_server = "https://" + get_exported_param("RHEVM_IP") + ":443" + "/ovirt-engine/"
            else:
                virtwho_server = "https://" + get_exported_param("RHEVM_IP") + ":443"
        # set conf data for all mode
        conf_data = "[%s]\n"\
                    "type=%s\n"\
                    "server=%s\n"\
                    "username=%s\n"\
                    "password=%s\n"\
                    "owner=%s\n"\
                    "env=%s\n" % (mode, mode, virtwho_server, virtwho_username, virtwho_password, virtwho_owner, virtwho_env)
        return conf_file, conf_data

    def set_virtwho_d_conf(self, file_name, file_data, targetmachine_ip=""):
        cmd = "cat > %s <<EOF\n"\
                        "%s\n"\
                        "EOF" % (file_name, file_data)
        ret, output = self.runcmd(cmd, "create config file: %s" % file_name, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to create config file: %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to create config file %s" % file_name)

    def get_host_uuids_list(self, mode, targetmachine_ip=""):
        self.set_filter_host_parents(mode, "", targetmachine_ip)
        # run virt-who one-shot with above config
        cmd = "virt-who -o -d"
        ret, output = self.runcmd(cmd, "executing virt-who with -o -d", targetmachine_ip)
        if ret == 0 and output is not None:
            host_list = re.findall(r"(?<=')host-.*?(?=')", output, re.I)
            if len(host_list) > 0:
                logger.info("Succeeded to get host_uuids_list: %s" % host_list)
                return host_list
            else:
                raise FailException("Failed, no host uuids found.")
        else:
            raise FailException("Failed to execute virt-who with -o -d")
        # remove above /etc/virt-who.d/virt.esx
        self.unset_all_virtwho_d_conf(targetmachine_ip)

    def get_host_parents_list(self, mode, targetmachine_ip=""):
        self.set_filter_host_parents(mode, "", targetmachine_ip)
        # run virt-who one-shot with above config
        cmd = "virt-who -o -d"
        ret, output = self.runcmd(cmd, "executing virt-who with -o -d", targetmachine_ip)
        if ret == 0 and output is not None:
            domain_list = re.findall(r"(?<=')domain-.*?(?=')", output, re.I)
            if len(domain_list) > 0:
                # domain_list = ','.join(list(set(domain_list))).replace("'", "\"")
                logger.info("Succeeded to get host_parents_list: %s" % domain_list)
                return domain_list
            else:
                raise FailException("Failed, no domain host found.")
        else:
            raise FailException("Failed to execute virt-who with -o -d")
        # remove above /etc/virt-who.d/virt.esx
        self.unset_all_virtwho_d_conf(targetmachine_ip)

    def set_filter_host_uuids(self, mode, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_exclude_host_uuids(self, mode, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "exclude_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_exclude_host_uuids(self, mode, filter_host_uuids, exclude_host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_uuids=%s\n" % filter_host_uuids + "exclude_host_uuids=%s\n" % exclude_host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_hypervisor_id_filter_host_uuids(self, mode, hypervisor_id, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "hypervisor_id=%s\n" % hypervisor_id + "filter_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_hypervisor_id_exclude_host_uuids(self, mode, hypervisor_id, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "hypervisor_id=%s\n" % hypervisor_id + "exclude_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_host_parents(self, mode, host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_parents=%s\n" % host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_exclude_host_parents(self, mode, host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "exclude_host_parents=%s\n" % host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_exclude_host_parents(self, mode, filter_host_parents, exclude_host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_parents=%s\n" % filter_host_parents + "exclude_host_parents=%s\n" % exclude_host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_host_uuids_exclude_parents(self, mode, filter_host_uuids, exclude_host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_uuids=%s\n" % filter_host_uuids + "exclude_host_parents=%s\n" % exclude_host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_exclude_host_uuids_filter_parents(self, mode, exclude_host_uuids, filter_host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "exclude_host_uuids=%s\n" % exclude_host_uuids + "filter_host_parents=%s\n" % filter_host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_hypervisor_id(self, mode, hypervisor_id, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "hypervisor_id=%s\n" % hypervisor_id
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_rhsm_user_pass(self, mode, rhsm_username, rhsm_password, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "rhsm_username=%s\nrhsm_password=%s" % (rhsm_username, rhsm_password)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_rhsm_hostname_prefix_port(self, mode, rhsm_username, rhsm_password, rhsm_hostname, rhsm_port, rhsm_prefix, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "rhsm_username=%s\nrhsm_password=%s\nrhsm_hostname=%s\nrhsm_port=%s\nrhsm_prefix=%s" % (rhsm_username, rhsm_password, rhsm_hostname, rhsm_port, rhsm_prefix)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_rhsm_user_encrypted_passwd(self, mode, rhsm_username, rhsm_encrypted_password, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "rhsm_username=%s\nrhsm_encrypted_password=%s" % (rhsm_username, rhsm_encrypted_password)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_encrypted_password(self, mode, encrypted_password, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        pattern = re.compile(r'password=.*?(?=\n|$)')
        self.set_virtwho_d_conf(conf_file, pattern.sub("encrypted_password=%s" % encrypted_password, conf_data), targetmachine_ip)

    def generate_fake_file(self, virtwho_mode, fake_file="/tmp/fake_file", targetmachine_ip=""):
        if "kvm" in virtwho_mode:
            cmd = "virt-who -p -d > %s" % fake_file
        elif "vdsm" in virtwho_mode:
            cmd = "virt-who -p -d --vdsm > %s" % fake_file
        else:
            cmd = self.virtwho_cli(virtwho_mode) + " -p -d > %s" % fake_file
        ret, output = self.runcmd(cmd, "Generate fake file in %s mode" % virtwho_mode, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to generate fake file in %s mode" % virtwho_mode)
            return fake_file
        else:
            raise FailException("Failed to generate fake file in %s mode" % virtwho_mode)

    def set_fake_mode_conf(self, fake_file, is_hypervisor, virtwho_owner, virtwho_env, targetmachine_ip=""):
        conf_file = "/etc/virt-who.d/fake.conf"
        conf_data = "[fake]\n"\
                    "type=fake\n"\
                    "file=%s\n"\
                    "is_hypervisor=%s\n"\
                    "owner=%s\n"\
                    "env=%s" % (fake_file, is_hypervisor, virtwho_owner, virtwho_env)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)
        return conf_file

    def unset_virtwho_d_conf(self, file_name, targetmachine_ip=""):
        # delete configure file in /etc/virt-who.d/virt-who
        cmd = "rm -f %s" % file_name
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to remove %s" % file_name)

    def unset_all_virtwho_d_conf(self, targetmachine_ip=""):
        # delete all configure file in /etc/virt-who.d/virt-who
        cmd = "rm -f /etc/virt-who.d/*"
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove all configure file in /etc/virt-who.d/virt-who.conf")
        else:
            raise FailException("Test Failed - Failed to remove all configure file in /etc/virt-who.d/virt-who.conf")

    def run_virt_who_password(self, input_password, timeout=None):
    # Get encrypted password
        import paramiko
        remote_ip = get_exported_param("REMOTE_IP")
        username = "root"
        password = "red2015"
        # virt_who_password_cmd = "python /usr/share/virt-who/virtwhopassword.py"
        virt_who_password_cmd = "virt-who-password"
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

    def sub_clean(self, targetmachine_ip=""):         
        # need to clean local data after unregister
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "clean system", targetmachine_ip)
        if ret == 0 :
            logger.info("Succeeded to clean %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to clean %s." % self.get_hg_info(targetmachine_ip))

    def sub_isregistered(self, targetmachine_ip=""):
        ''' check whether the machine is registered. '''
        cmd = "subscription-manager identity"
        ret, output = self.runcmd(cmd, "check whether the machine is registered", targetmachine_ip)
        if ret == 0:
            logger.info("System %s is registered." % self.get_hg_info(targetmachine_ip))
            return True
        elif "command not found" in output: 
            logger.info("subscription-manager isn't exist, need to install it")
            cmd = "yum install -y subscription-manager"
            ret, output = self.runcmd(cmd, "install subscription-manager", targetmachine_ip)
            if ret == 0:
                logger.info("subscription-manager has been installed on System %s " % self.get_hg_info(targetmachine_ip))
            else:
                logger.info("Failed to installed subscription-manager on System %s " % self.get_hg_info(targetmachine_ip))
            return False
        elif "has been deleted" in output:
            logger.info("System is unregistered on server side")
            self.sub_clean(targetmachine_ip)
            return False
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
            raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)

    def sub_subscribe_to_bonus_pool(self, productid, guest_ip=""):
        ''' subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
        availpoollistguest = self.sub_listavailpools(productid, guest_ip)
        if availpoollistguest != None:
            rindex = -1
            for index in range(0, len(availpoollistguest)):
                if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and self.check_type_virtual(availpoollistguest[index]) and (self.check_temporary_virtual(availpoollistguest[index]) is True)):
                    rindex = index
                    break
                elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and self.check_type_virtual(availpoollistguest[index])and (self.check_temporary_virtual(availpoollistguest[index]) is True)):
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
        self.sub_refresh(targetmachine_ip)
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

    def sub_check_consumed_pool(self, sku_id, key="PoolID", targetmachine_ip=""):
        self.sub_refresh(targetmachine_ip)
        ''' Check consumed subpool exist or not, if it is exist, return consumed pool id. '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions then get cosumed pool id", targetmachine_ip)
        if ret == 0:
            if "No consumed subscription pools to list" not in output:
                if sku_id in output:
                    consumed_lines = self.__parse_avail_pools(output)
                    if consumed_lines != None:
                        for line in range(0, len(consumed_lines)):
                            if key is not None and key != "":
                                if consumed_lines[line]["SKU"] == sku_id:
                                    logger.info("Succeeded to get consumed subscription %s pool id is %s in %s" % (sku_id, consumed_lines[line][key], self.get_hg_info(targetmachine_ip)))
                                    return consumed_lines[line][key]
                elif sku_id not in output:
                    logger.info("Succeeded to check entitlements %s - the product '%s' is not subscribed now." % (self.get_hg_info(targetmachine_ip), sku_id))
                    return True
                else:
                    raise FailException("Failed to list consumed subscription %s - Not the right consumed subscription is listed!" % self.get_hg_info(targetmachine_ip))
            else:
                return True
                logger.info("There is no consumed subscription to list!")
        else:
            raise FailException("Failed to list consumed subscriptions.")

    def sub_check_bonus_pool_after_migate(self, before_poolid, after_poolid, targetmachine_ip=""):
        if after_poolid is True:
            logger.info("Success to check bonus pool has been revoke after migration in %s" % self.get_hg_info(targetmachine_ip))
        elif before_poolid not in after_poolid:
            logger.info("Success to check bonus pool has been updated after migration in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to check bonus pool after migration in %s" % self.get_hg_info(targetmachine_ip))

    # check "subscription-manager list --consumed" key & value 
    def check_consumed_status(self, sku_id, key="", value="", targetmachine_ip=""):
        ''' check consumed entitlements status details '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
        if ret == 0 and output is not None:
            consumed_lines = self.__parse_avail_pools(output)
            if consumed_lines != None:
                for line in range(0, len(consumed_lines)):
                    if key is not None and value is not None and key != "" and value != "":
                        if consumed_lines[line]["SKU"] == sku_id and consumed_lines[line][key] == value :
                            logger.info("Succeeded to list the right consumed subscription, %s=%s %s." % (key, value, self.get_hg_info(targetmachine_ip)))
                            return
                    else:
                        if consumed_lines[line]["SKU"] == sku_id:
                            logger.info("Succeeded to list the right consumed subscription %s" % self.get_hg_info(targetmachine_ip))
                            return
                # no proper consumed subscription found
                raise FailException("Failed to list the right consumed subscriptions, %s=%s %s." % (key, value, self.get_hg_info(targetmachine_ip)))
            else:
                raise FailException("List consumed subscription: none %s" % self.get_hg_info(targetmachine_ip))
        else:
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
                        logger.info("Succeeded to check installed status: %s %s" % (value, self.get_hg_info(targetmachine_ip)))
                        return
                # no proper installed status found
                raise FailException("Failed to check installed status %s %s" % (value, self.get_hg_info(targetmachine_ip)))
            else:
                raise FailException("List installed info: none %s" % self.get_hg_info(targetmachine_ip))
        raise FailException("Failed to list installed info.")

    # check ^Certificate: or ^Content: in cert file
    def check_cert_file(self, keywords, targetmachine_ip=""):
        cmd = "rct cat-cert /etc/pki/entitlement/*[^-key].pem | grep -A5 \"%s\"" % keywords
        ret, output = self.runcmd(cmd, "Check %s exist in cert file in guest" % keywords, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to check content sets exist %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to check content sets exist %s" % self.get_hg_info(targetmachine_ip))

    # check ^Repo ID by subscription-manager repos --list 
    def check_yum_repo(self, keywords, targetmachine_ip=""):
        cmd = "subscription-manager repos --list | grep -A4 \"^Repo ID\""
        ret, output = self.runcmd(cmd, "Check repositories available in guest", targetmachine_ip)
        if ret == 0 and "This system has no repositories available through subscriptions." not in output:
            logger.info("Succeeded to check repositories available %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to check repositories available %s" % self.get_hg_info(targetmachine_ip))

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

    def check_temporary_virtual(self, pool_dict):
        if "SubscriptionType" in pool_dict.keys():
            TypeName = "SubscriptionType"
        if "temporary" in pool_dict[TypeName] or "Temporary" in pool_dict[TypeName]:
            logger.info("The sku is temporary sku")
            return False
        else:
            logger.info("The sku is not temporary sku")
            return True

    def check_bonus_exist(self, sku_id, bonus_quantity, targetmachine_ip="", bonus_exist=True):
        # check bonus pool is exist or not
        self.sub_refresh(targetmachine_ip)
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
                        if pool_list[item]["SKU"] == sku_id and self.check_type_virtual(pool_list[item]) and pool_list[item][SKU_Number] == bonus_quantity and (self.check_temporary_virtual(pool_list[item]) is True):
                            if bonus_exist:
                                logger.info("Succeeded to check the bonus pool %s exist, and bonus quantity is %s" % (sku_id, bonus_quantity))
                            else:
                                raise FailException("Failed to check the bonus pool %s exist, and bonus quantity is %s" % (sku_id, bonus_quantity))
                            return True
                    if not bonus_exist:
                        logger.info("Succeeded to check the bonus pool %s not exist" % sku_id)
                    else:
                        raise FailException("Failed to check the bonus pool %s not exist" % sku_id)
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

    def kill_virt_who_pid(self, destination_ip=""):
        pid_name = "virtwho.py"
        self.kill_pid(pid_name, destination_ip)

    def parse_uuid_list(self, output):
        ''' get guest uuid.list from given string output '''
        self.check_429_message(output)
        if "Sending update in hosts-to-guests mapping: {" in output:
            logger.info("Found: Sending update in hosts-to-guests mapping")
            rex = re.compile(r'(?<=Sending update in hosts-to-guests mapping: ){.*?}\n+(?=201|$)', re.S)
        elif "Host-to-guest mapping: {" in output:
            logger.info("Found: Host-to-guest mapping")
            rex = re.compile(r'(?<=Host-to-guest mapping: ){.*?}\n+(?=201|$)', re.S)
        elif "Domain info: [" in output:
            logger.info("Found: Domain info")
            rex = re.compile(r'(?<=Domain info: )\[.*?\]\n+(?=201|$)', re.S)
        elif "Sending domain info: [" in output:
            logger.info("Found: Sending domain info")
            rex = re.compile(r'(?<=Sending domain info: )\[.*?\]\n+(?=201|$)', re.S)
        elif "Associations found: {" in output:
            logger.info("Found: Associations found")
            rex = re.compile(r'(?<=Associations found: ){.*?}\n+(?=201|$)', re.S)
        else:
            raise FailException("Failed to find hosts-to-guests mapping info in output data")
        mapping_info = rex.findall(output)
        logger.info("all hosts-to-guests mapping as follows: \n%s" % mapping_info)
        return mapping_info
#         if "Sending list of uuids: " in output:
#             uuid_list = output.split('Sending list of uuids: ')[1]
#         elif "Sending update to updateConsumer: " in output:
#             uuid_list = output.split('Sending update to updateConsumer: ')[1]
#         elif "Sending update in hosts-to-guests mapping: " in output:
#             uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
#         elif "Sending domain info" in output:
#             uuid_list = output.split('Sending domain info: ')[1].strip()
#         elif "Domain info" in output:
#             uuid_list = output.split('Domain info: ')[1].strip()
#         else:
#             raise FailException("Failed to get guest uuid.list")
#         logger.info("Succeeded to get guest uuid.list: %s") % uuid_list
#         return uuid_list

    def vw_get_mapping_info(self, cmd, targetmachine_ip=""):
        ret, output = self.runcmd(cmd, "run command to get mapping info", targetmachine_ip)
        logger.info("===================rest is %s=============", ret)
        if ret == 0 and output is not None and ("ERROR" not in output or "Unable to read cache" in output):
            return self.parse_uuid_list(output)
        else:
            raise FailException("Failed to check, there is an error message found or no output data.")

    def get_uuid_list_in_rhsm_log(self, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check if the guest uuid is correctly monitored by virt-who. '''
        tmp_file = "/tmp/tail.rhsm.log"
        checkcmd = "restart_virtwho"
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        ret, output = self.runcmd(cmd, "get temporary log generated", targetmachine_ip)
        if ret == 0:
            return self.parse_uuid_list(output)
        else:
            raise FailException("Failed to get uuid list in rhsm.log")

    def vw_check_uuid(self, guestuuid, uuidexists=True, checkcmd="restart_virtwho", targetmachine_ip=""):
        ''' check if the guest uuid is correctly monitored by virt-who. '''
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        ret, output = self.runcmd(cmd, "get temporary log generated", targetmachine_ip)
        if ret == 0:
            log_uuid_list = self.parse_uuid_list(output)
            if uuidexists:
                if guestuuid == "" and len(log_uuid_list) == 0:
                    logger.info("Succeeded to get none uuid list")
                else:
                    if guestuuid in str(log_uuid_list):
                        logger.info("Succeeded to check guestuuid %s in log_uuid_list" % guestuuid)
                    else:
                        raise FailException("Failed to check guestuuid %s in log_uuid_list" % guestuuid)
            else:
                if guestuuid not in log_uuid_list:
                    logger.info("Succeeded to check guestuuid %s not in log_uuid_list" % guestuuid)
                else:
                    raise FailException("Failed to check guestuuid %s not in log_uuid_list" % guestuuid)
        else:
            raise FailException("Failed to get content of %s.") % tmp_file

    def hypervisor_check_uuid(self, hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd="restart_virtwho", uuidexists=True, targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
        if ret == 0:
            log_uuid_list = self.parse_uuid_list(output)
            for hypervisor in log_uuid_list:
                if hostuuid in hypervisor:
                    if uuidexists:
                        if guestuuid == "" and hypervisor[hostuuid] == []:
                            logger.info("Succeeded to get none uuid list")
                            return
                        else:
                            if guestuuid in hypervisor:
                                logger.info("Succeeded to check hostuuid %s and guestuuid %s mapping info in log_uuid_list" % (hostuuid, guestuuid))
                                return
                            else:
                                raise FailException("Failed to check hostuuid %s and guestuuid %s mapping info in log_uuid_list" % (hostuuid, guestuuid))
                    else:
                        if guestuuid not in log_uuid_list:
                            logger.info("Succeeded to check guestuuid %s not in log_uuid_list" % guestuuid)
                            return
                        else:
                            raise FailException("Failed to check guestuuid %s not in log_uuid_list" % guestuuid)
            raise FailException("Failed to get hostuuid %s in log_uuid_list" % hostuuid)
        else:
            raise FailException("Test Failed - log file has problem, please check it !")

    # def vw_check_attr(self, guestname, active, virtWhoType, hypervisorType, state, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd="restart_virtwho", waiting_time=0, targetmachine_ip=""):
    def vw_check_attr(self, guestname, active, virtWhoType, state, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd="restart_virtwho", waiting_time=0, targetmachine_ip=""):
        ''' check if the guest attributions is correctly monitored by virt-who. '''
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, waiting_time, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        mapping_info = json.loads(''.join(self.vw_get_mapping_info(cmd, targetmachine_ip)))
        if virtWhoType == "libvirt" or virtWhoType == "vdsm":
            for guest in mapping_info:
                if guest["guestId"] == guestuuid:
                    attr_state = guest['state']
                    logger.info("Guest state is %s." % attr_state)
                    attr_status = guest['attributes']['active']
                    logger.info("Guest's active status is %s." % attr_status)
                    attr_type = guest['attributes']['virtWhoType']
                    logger.info("Guest virtwhotype is %s." % attr_type)
#                     attr_hypertype = guest['attributes']['hypervisorType']
#                     logger.info("Guest hypervisortype is %s." % attr_hypertype)
        else:
            for host in mapping_info.keys():
                for guest in mapping_info[host]:
                    if guest["guestId"] == guestuuid:
                        attr_state = guest['state']
                        logger.info("Guest state is %s." % attr_state)
                        attr_status = guest['attributes']['active']
                        logger.info("Guest's active status is %s." % attr_status)
                        attr_type = guest['attributes']['virtWhoType']
                        logger.info("Guest virtwhotype is %s." % attr_type)
#                         attr_hypertype = guest['attributes']['hypervisorType']
#                         logger.info("Guest hypervisortype is %s." % attr_hypertype)
#         if guestname != "" and (active == attr_status) and (virtWhoType in attr_type) and (hypervisorType in attr_hypertype) and (state == attr_state):
        if guestname != "" and (active == attr_status) and (virtWhoType in attr_type) and (state == attr_state):
            logger.info("successed to check guest %s attribute" % guestname)
        else:
            raise FailException("Failed to check guest %s attribute" % guestname)

    def check_429_message(self, output):
        # resolve 429 received issue
        if "429 received" in output:
            logger.info("429 received, sleep 360 seconds to continue ...")
            time.sleep(360)

    def vw_check_message(self, cmd, message, message_exists=True, cmd_retcode=0, targetmachine_ip=""):
        ''' check whether given message exist or not, if multiple check needed, seperate them via '|' '''
        ret, output = self.runcmd(cmd, "check message in output", targetmachine_ip)
        if ret == cmd_retcode:
            self.check_429_message(output)
            msg_list = message.split("|")
            logger.info("msg_list is----------------------%s" % msg_list)
            if message_exists:
                for msg in msg_list:
                    # logger.info("msg is ----------------------%s" % msg)
                    # logger.info("output is ----------------------%s" % output)
                    if msg in output:
                        logger.info("Succeeded to get message in %s output: '%s'" % (cmd, msg))
                        return
                else:
                    raise FailException("Failed to get message in %s output: '%s'" % (cmd, msg))
            else:
                for msg in msg_list:
                    if msg not in output:
                        logger.info("Succeeded to check message not in %s output: '%s'" % (cmd, msg))
                    else:
                        raise FailException("Failed to check message not in %s output: '%s'" % (cmd, msg))
        else:
            raise FailException("Failed to excute virt-who cmd %s, return code is not %s" % (cmd, cmd_retcode))

    def vw_check_message_in_rhsm_log(self, message, message_exists=True, checkcmd="restart_virtwho", targetmachine_ip=""):
        ''' check whether given message exist or not in rhsm.log. if multiple check needed, seperate them via '|' '''
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_message(cmd, message, message_exists, 0, targetmachine_ip)

    def vw_check_timeout_in_rhsm_log(self, message, message_exists=True, checkcmd="restart_virtwho", targetmachine_ip=""):
        ''' check whether given message exist or not in rhsm.log. if multiple check needed, seperate them via '|' '''
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, 100, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_message(cmd, message, message_exists, 0, targetmachine_ip)

    def vw_check_message_in_debug_cmd(self, cmd, message, message_exists=True, targetmachine_ip=""):
        ''' check whether given message exist or not in virt-who -d mode.
        if multiple check needed, seperate them via '|' such as: self.vw_check_message_in_debug_cmd(cmd, "DEBUG|ERROR")'''
        tmp_file = "/tmp/virt-who.cmd.log"
        cmd = "%s &> %s & sleep 10" % (cmd, tmp_file)
        self.runcmd(cmd, "generate %s to parse virt-who -d output info" % tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_message(cmd, message, message_exists, 0, targetmachine_ip)
        self.kill_pid("virt-who", targetmachine_ip)

    def vw_check_mapping_info_in_rhsm_log(self, host_uuid, guest_uuid="", checkcmd="restart_virtwho", uuid_exist=True, targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, 0, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        mapping_info = ''.join(self.vw_get_mapping_info(cmd, targetmachine_ip))
        logger.info("-----------------mapping_info is %s" % mapping_info)
        if uuid_exist == True:
            if (host_uuid in mapping_info if host_uuid != "" else True) and (guest_uuid in mapping_info if guest_uuid != "" else True):
                logger.info("Succeeded to check, can find host_uuid '%s' and guest_uuid '%s'" % (host_uuid, guest_uuid))
            else:
                raise FailException("Failed to check, can not find host_uuid '%s' and guest_uuid '%s'" % (host_uuid, guest_uuid))
        else:
            if (host_uuid not in mapping_info if host_uuid != "" else True) and (guest_uuid not in mapping_info if guest_uuid != "" else True):
                logger.info("Succeeded to check, no host_uuid '%s' and guest_uuid '%s' found." % (host_uuid, guest_uuid))
            else:
                raise FailException("Failed to check, should be no host_uuid '%s' and guest_uuid '%s' found." % (host_uuid, guest_uuid))

    def vw_check_mapping_info_number(self, cmd, mapping_num=1, targetmachine_ip=""):
        mapping_info = self.vw_get_mapping_info(cmd, targetmachine_ip)
        if len(mapping_info) == mapping_num:
            logger.info("Succeeded to check hosts-to-guests mapping info number as %s" % mapping_num)
        else:
            raise FailException("Failed to check hosts-to-guests mapping info number as %s" % mapping_num)

    def vw_check_mapping_info_number_in_debug_cmd(self, cmd, mapping_num=1, waiting_time=0, targetmachine_ip=""):
        tmp_file = "/tmp/virt-who.cmd.log"
        cmd = "%s &> %s & sleep %s" % (cmd, tmp_file, waiting_time)
        self.runcmd(cmd, "generate %s to parse virt-who -d output info" % tmp_file, targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_mapping_info_number(cmd, mapping_num, targetmachine_ip)
        self.kill_pid("virt-who")

    def vw_check_mapping_info_number_in_rhsm_log(self, mapping_num=1, waiting_time=0, checkcmd="restart_virtwho", targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, waiting_time, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_mapping_info_number(cmd, mapping_num, targetmachine_ip)

    def vw_check_message_number(self, cmd, message, number, targetmachine_ip=""):
        ret, output = self.runcmd(cmd, "run command to get message", targetmachine_ip)
        if ret == 0 and output is not None and  "ERROR" not in output:
            self.check_429_message(output)
            rex = re.compile(r'%s' % message, re.S)
            message_list = rex.findall(output)
            logger.info("all message list as follows: \n%s" % message_list)
            if len(message_list) == number:
                logger.info("Succeeded to check message number as %s" % number)
            else:
                raise FailException("Failed to check message number as %s" % number)
            return message_list
        else:
            raise FailException("Failed to check, there is an error message found or no output data.")

    def vw_check_message_number_in_debug_cmd(self, cmd, message, msg_num=1, waiting_time=0, targetmachine_ip=""):
        tmp_file = "/tmp/virt-who.cmd.log"
        # cmd = "%s > %s 2>&1 &" % (cmd, tmp_file)
        cmd = "%s &> %s & sleep 5" % (cmd, tmp_file)
        self.runcmd(cmd, "generate %s to parse virt-who -d output info" % tmp_file, targetmachine_ip)
        self.vw_check_sending_finished(tmp_file, targetmachine_ip)
        time.sleep(waiting_time)
        cmd = "cat %s" % tmp_file
        self.vw_check_message_number(cmd, message, msg_num, targetmachine_ip)
        self.kill_pid("virt-who", targetmachine_ip)

    def vw_check_message_number_in_rhsm_log(self, message, msg_num=1, waiting_time=0, checkcmd="restart_virtwho", targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, waiting_time, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_message_number(cmd, message, msg_num, targetmachine_ip)

    def vw_check_sending_finished(self, tmp_file, targetmachine_ip=""):
        cmd = "grep -E 'Sending update in hosts-to-guests mapping|Sending update in guests lists|ERROR' %s" % tmp_file
        account = 0
        while account <= 30:
            ret, output = self.runcmd(cmd, "check virt-who sending host-guest mapping finished", showlogger=False, targetmachine_ip=targetmachine_ip)
            if ret == 0 :
                logger.info("Succeeded to check virt-who sending host-guest mapping finished")
                return
            else:
                account += 1
                time.sleep(2)
        cmd = "cat %s" % tmp_file
        ret, output = self.runcmd(cmd, "check %s file for debug message" % tmp_file, targetmachine_ip)
        raise FailException("Failed to check virt-who sending host-guest mapping finished")

    def get_poolid_by_SKU(self, sku, targetmachine_ip=""):
        ''' get_poolid_by_SKU '''
        availpoollist = self.sub_listavailpools(sku, targetmachine_ip)
        if availpoollist != None:
            for index in range(0, len(availpoollist)):
#                 if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku):
                if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku and "Temporary" not in availpoollist[index]["SubscriptionType"]):
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

    def get_host_uuid(self, targetmachine_ip=""):
        cmd = "virsh capabilities"
        ret, output = self.runcmd(cmd, "Get hypervisor's capabilities", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to get hypervisor's capabilities on %s" % self.get_hg_info(targetmachine_ip))
            datalines = output.splitlines()
            for line in datalines:
                if "uuid" in line:
                    khrightloc = line.find("<uuid>")
                    khleftloc = line.find("</uuid>")
                    uuid = line[khrightloc + 6:khleftloc].strip()
                    logger.info("Success to get hypervisor's uuid %s" % uuid)
                    return uuid
        else:
            raise FailException("Failed to get hypervisor's capabilities on %s" % self.get_hg_info(targetmachine_ip))

    def cal_virtwho_thread(self, targetmachine_ip=""):
            self.runcmd_service("restart_virtwho")
            time.sleep(1)
            self.runcmd_service("restart_virtwho")
            time.sleep(1)
            self.runcmd_service("restart_virtwho")
            time.sleep(1)
            cmd = "ps -ef | grep -v grep | grep virt-who |wc -l"
            ret, output = self.runcmd(cmd, "calculate virt-who thread", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to calculate virt-who thread. virt-who thread is %s" % output)
                return output
            else:
                raise FailException("Test Failed - Failed to calculate virt-who thread")

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
                    # logger.info("Succeeded to find the non_key_value %s's result_values1 %s" % (non_key_value, result_values1))
                    values1 = True
                elif line.find(key_value) == 0:
                    result_values2 = line[(line.find(':') + 1):].strip()
                    # logger.info("Succeeded to find the key_value %s's result_values2 %s" % (key_value, result_values2))
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
                    # logger.info("Failed to get the %s %s, no value" % (find_value, non_key_value))
                    return ERROR_VALUE
                else:
                    # logger.info("Succeeded to get the %s %s is %s" % (find_value, non_key_value, findout_value))
                    return findout_value
            else:
                raise FailException("Failed to get the %s's %s" % (find_value, non_key_value))
        else:
            raise FailException("Failed to run rhevm-shell cmd.")

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

    def run_interact_sshkeygen(self, cmd, targetmachine_ip, username, password, timeout=None, comments=True):
        ret, output = self.run_paramiko_interact_sshkeygen(cmd, targetmachine_ip, username, password, timeout)
        return ret, output

    def generate_ssh_key(self, targetmachine_ip=""):
        if "remote_libvirt" in get_exported_param("HYPERVISOR_TYPE"):
            remote_ip_2 = get_exported_param("REMOTE_IP")
            remote_ip = get_exported_param("REMOTE_IP_1")
        else:
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

    def order_mapping_info(self, obj):
        if isinstance(obj, dict):
            return sorted((k, self.order_mapping_info(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.order_mapping_info(x) for x in obj)
        else:
            return obj


    # ========================================================
    #       Basic Functions For Satellite Test
    # ========================================================
    def check_cert_privilege(self, targetmachine_ip=""):
        cmd = "ls -alt /etc/rhsm/ca/katello-default-ca.pem | awk '{print $1}'| cut -c1-10"
        ret, output = self.runcmd(cmd, "check katello-default-ca.pem's privilege", targetmachine_ip, showlogger=False)
        if ret == 0 and "-rw-r--r--" in output:
            logger.info("Succeeded to check katellot-default-ca.pem's privilege in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to check katellot-default-ca.pem's privilege in %s." % self.get_hg_info(targetmachine_ip))
        cmd = "ls -alt /etc/rhsm/ca/katello-server-ca.pem | awk '{print $1}'| cut -c1-10"
        ret, output = self.runcmd(cmd, "check katello-server-ca.pem's privilege", targetmachine_ip, showlogger=False)
        if ret == 0 and "-rw-r--r--" in output:
            logger.info("Succeeded to check katello-server-ca.pem's privilege in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to check katello-server-ca.pem.pem's privilege in %s." % self.get_hg_info(targetmachine_ip))

    def check_rhsm_config(self, server_hostname, targetmachine_ip=""):
        cmd = "grep ^hostname /etc/rhsm/rhsm.conf"
        ret, output = self.runcmd(cmd, "check hostname auto updated", targetmachine_ip, showlogger=False)
        if ret == 0 and server_hostname in output:
            logger.info("Succeeded to check hostname has been auto updated in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to check hostname has been auto updated in %s." % self.get_hg_info(targetmachine_ip))
        cmd = "grep ^baseurl /etc/rhsm/rhsm.conf"
        ret, output = self.runcmd(cmd, "check baseurl auto updated", targetmachine_ip, showlogger=False)
        baseurl = "https://" + server_hostname + "/pulp/repos"
        if ret == 0 and baseurl in output:
            logger.info("Succeeded to check baseurl has been auto updated in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to check baseurl has been auto updated in %s." % self.get_hg_info(targetmachine_ip))
        cmd = "grep ^ca_cert_dir /etc/rhsm/rhsm.conf"
        ret, output = self.runcmd(cmd, "check ca_cert_dir auto updated", targetmachine_ip, showlogger=False)
        if ret == 0 and "/etc/rhsm/ca/" in output:
            logger.info("Succeeded to check ca_cert_dir has been auto updated in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to check ca_cert_dir has been auto updated in %s." % self.get_hg_info(targetmachine_ip))

    def config_hostname_port_prefix_disable(self, hostname, port, prefix, targetmachine_ip=""):
        # Disable hostname, port, prefix in /etc/rhsm/rhsm.conf
        cmd = "sed -i -e 's/^hostname =.*/#hostname = %s/g'  -e 's/^port =.*/#port = %s/g' -e 's/^prefix =.*/#prefix = \%s/g' /etc/rhsm/rhsm.conf" % (hostname, port, prefix)
        (ret, output) = self.runcmd(cmd, "Disable %s %s %s in /etc/rhsm/rhsm.conf in %s" % (hostname, port, prefix, targetmachine_ip))
        if ret == 0:
            logger.info("Succeeded to disable %s %s %s in /etc/rhsm/rhsm.conf." % (hostname, port, prefix))
        else:
            raise FailException("Failed to disable %s %s %s in /etc/rhsm/rhsm.conf." % (hostname, port, prefix))

    def config_hostname_port_prefix_enable(self, hostname, port, prefix, targetmachine_ip=""):
        # uncomment option in /etc/sysconfig/virt-who if given option disabled
        cmd = "sed -i -e 's/^#hostname =.*/hostname = %s/g'  -e 's/^#port =.*/port = %s/g' -e 's/^#prefix =.*/prefix = \%s/g' /etc/rhsm/rhsm.conf" % (hostname, port, prefix)
        (ret, output) = self.runcmd(cmd, "Enable %s %s %s in /etc/rhsm/rhsm.conf in %s" % (hostname, port, prefix, targetmachine_ip))
        if ret == 0:
            logger.info("Succeeded to enable %s %s %s in /etc/rhsm/rhsm.conf." % (hostname, port, prefix))
        else:
            raise FailException("Failed to enable %s %s %s in /etc/rhsm/rhsm.conf." % (hostname, port, prefix))

    def conf_hammel_credential(self, username, passwd, targetmachine_ip=""):
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
#         cmd = "echo -e ':foreman:\n  :host: 'https://%s/'\n  :username: '%s'\n  :password: '%s'\n' > /root/.hammer/cli_config.yml" % (tagetmachine_hostname, username, passwd)
        cmd = "echo -e ':foreman:\n  :host: 'https://%s/'\n  :username: '%s'\n  :password: '%s'\n' > /etc/hammer/cli_config.yml" % (tagetmachine_hostname, username, passwd)
        ret, output = self.runcmd(cmd, "config hammer credentials in satellite %s", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to config hammer credentials in satellite %s" % targetmachine_ip)
        else:
            raise FailException("Failed to config hammer credentials in satellite %s" % targetmachine_ip)

    def create_active_key(self, keyname, org, targetmachine_ip=""):
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        cmd = "hammer activation-key list --organization-label=%s|grep %s" % (org, keyname)
        ret, output = self.runcmd(cmd, "list all active keys in satellite", targetmachine_ip)
        if ret == 0 and keyname in output:
            logger.info("active key %s is exist in satellite %s" % (keyname, targetmachine_ip))
            self.delete_active_key(keyname, org, targetmachine_ip)
        else:
            logger.info("active key %s is not exist in satellite %s" % (keyname, targetmachine_ip))
        cmd = "hammer activation-key create --name %s --organization-label=%s --lifecycle-environment-id=1 --content-view-id=1" % (keyname, org)
        ret, output = self.runcmd(cmd, "create an active key in satellite", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to create an active key in satellite %s" % targetmachine_ip)
        else:
            raise FailException("Failed to create an active key in satellite %s" % targetmachine_ip)

    def delete_active_key(self, keyname, org, targetmachine_ip=""):
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        cmd = "hammer activation-key delete --name %s --organization-label=%s" % (keyname, org)
        ret, output = self.runcmd(cmd, "delete an active key in satellite", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to delete an active key in satellite %s" % targetmachine_ip)
        else:
            raise FailException("Failed to delete an active key in satellite %s" % targetmachine_ip)

    def register_with_active_key(self, keyname, org, targetmachine_ip=""):
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        cmd = "subscription-manager register --org=%s --activationkey=%s" % (org, keyname)
        ret, output = self.runcmd(cmd, "Register system with defined active key", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to register system with defined active key in satellite %s" % targetmachine_ip)
        else:
            raise FailException("Failed to register system with defined active key in satellite %s" % targetmachine_ip)

    def create_org(self, orgname, orglabel, orgdesc, targetmachine_ip=""):
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        cmd = "hammer organization create --name %s --label %s --description %s" % (orgname, orglabel, orgdesc)
        ret, output = self.runcmd(cmd, "create a new org in satellite", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to create a new org in satellite %s" % targetmachine_ip)
        else:
            raise FailException("Failed to create a new org in satellite %s" % targetmachine_ip)

    def configure_http_proxy(self, mode, http_proxy, server_hostname, targetmachine_ip=""):
        if mode == "esx" or mode == "rhevm" or mode == "xen":
            proxy_prefix = "https://"
            cmd = "sed -i '/https_proxy/d' /etc/sysconfig/virt-who; echo 'https_proxy=%s%s' >> /etc/sysconfig/virt-who" % (proxy_prefix, http_proxy)
            ret, output = self.runcmd(cmd, "configure http_proxy", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to configure http_proxy to %s%s" % (proxy_prefix, http_proxy))
            else:
                raise FailException("Failed to configure http_proxy to %s%s" % (proxy_prefix, http_proxy))
        elif mode == "hyperv":
            proxy_prefix = "http://"
            cmd = "sed -i '/http_proxy/d' /etc/sysconfig/virt-who; echo 'http_proxy=%s%s' >> /etc/sysconfig/virt-who" % (proxy_prefix, http_proxy)
            ret, output = self.runcmd(cmd, "configure http_proxy", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to configure http_proxy to %s%s" % (proxy_prefix, http_proxy))
            else:
                raise FailException("Failed to configure http_proxy to %s%s" % (proxy_prefix, http_proxy))
        else:
            logger.info("Needn't to config http_proxy on %s mode" % mode)
        # remove /etc/pki/product-default/135.pem, or else auto subscribe failed
        cmd = "sed -i '/no_proxy/d' /etc/sysconfig/virt-who; echo 'no_proxy=%s' >> /etc/sysconfig/virt-who" % server_hostname
        ret, output = self.runcmd(cmd, "configure no_proxy", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure no_proxy to %s" % server_hostname)
        else:
            raise FailException("Failed to configure no_proxy to %s" % server_hostname)

    # ========================================================
    #       ESX Functions
    # ========================================================
    def esx_setup(self):
        server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
        esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
        esx_host = self.get_vw_cons("ESX_HOST")
        self.update_esx_vw_configure(esx_owner, esx_env, esx_server, esx_username, esx_password)
        self.runcmd_service("restart_virtwho")
        self.sub_unregister()
        self.configure_server(server_ip, server_hostname)
        self.sub_register(server_user, server_pass)
        self.start_dbus_daemon()
        guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
        esx_guest_url = "http://%s/projects/sam-virtwho/esx_guest/" % self.get_vw_cons("data_server")
        self.wget_images(esx_guest_url, guest_name, esx_host)
        self.esx_add_guest(guest_name, esx_host)
        self.esx_start_guest_first(guest_name, esx_host)
        # self.esx_service_restart(ESX_HOST)
        self.esx_stop_guest(guest_name, esx_host)
        self.runcmd_service("restart_virtwho")

    def unset_esx_conf(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/^VIRTWHO_ESX/#VIRTWHO_ESX/g' -e 's/^VIRTWHO_ESX_OWNER/#VIRTWHO_ESX_OWNER/g' -e 's/^VIRTWHO_ESX_ENV/#VIRTWHO_ESX_ENV/g' -e 's/^VIRTWHO_ESX_SERVER/#VIRTWHO_ESX_SERVER/g' -e 's/^VIRTWHO_ESX_USERNAME/#VIRTWHO_ESX_USERNAME/g' -e 's/^VIRTWHO_ESX_PASSWORD/#VIRTWHO_ESX_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "unset virt-who configure file for disable VIRTWHO_ESX", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to disable VIRTWHO_ESX.")
        else:
            raise FailException("Test Failed - Failed to disable VIRTWHO_ESX.")

    def set_esx_conf(self, targetmachine_ip=""):
        esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
        # clean # first
        cmd = "sed -i -e 's/^#VIRTWHO_ESX/VIRTWHO_ESX/g' -e 's/^#VIRTWHO_ESX_OWNER/VIRTWHO_ESX_OWNER/g' -e 's/^#VIRTWHO_ESX_ENV/VIRTWHO_ESX_ENV/g' -e 's/^#VIRTWHO_ESX_SERVER/VIRTWHO_ESX_SERVER/g' -e 's/^#VIRTWHO_ESX_USERNAME/VIRTWHO_ESX_USERNAME/g' -e 's/^#VIRTWHO_ESX_PASSWORD/VIRTWHO_ESX_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "set virt-who configure file for enable VIRTWHO_ESX", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_ESX.")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_ESX.")
        # set esx value
        cmd = "sed -i -e 's/^VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/^VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/^VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/^VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/^VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/^VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (esx_owner, esx_env, esx_server, esx_username, esx_password)
        ret, output = self.runcmd(cmd, "setting value for esx conf.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set esx value.")
        else:
            raise FailException("Test Failed - Failed to set esx value.")

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
        cmd = "vim-cmd vmsvc/getallvms | grep '%s' | awk '{print $1}'" % (guest_name)
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
        elif ret == 0 and "Suspended" in output:
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

#     def esx_destroy_guest(self, guest_name, esx_host):
#         ''' destroy guest from esx'''
#         cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
#         ret, output = self.runcmd_esx(cmd, "destroy guest '%s' in ESX" % guest_name, esx_host)
#         if ret == 0:
#             logger.info("Succeeded to destroy guest '%s'" % guest_name)
#         else:
#             raise FailException("Failed to destroy guest '%s'" % guest_name)

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

    def esx_start_guest(self, guest_name, destination_ip):
        ''' start guest in esx host '''
        cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
        ret, output = self.runcmd_esx(cmd, "start guest '%s' in ESX" % guest_name, destination_ip)
        if ret == 0:
            logger.info("Succeeded to start guest '%s' in ESX host" % guest_name)
        else:
            raise FailException("Failed to start guest '%s' in ESX host" % guest_name)
        ''' check whethre guest can be accessed by ip '''
        self.esx_check_ip_accessable(guest_name, destination_ip, accessable=True)

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
        ret, output = self.runcmd_esx(cmd, "get guest '%s' ip address in ESX '%s'" % (guest_name, destination_ip), destination_ip)
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
                    return
                if cycle_count == max_cycle:
                    logger.info("Time out to esx_check_ip_accessable")
                    return
                else:
                    time.sleep(30)
            else:
                time.sleep(30)
                if self.esx_get_guest_ip(guest_name, destination_ip) == "unset":
                    return
                if cycle_count == max_cycle:
                    logger.info("Time out to esx_check_ip_accessable")
                    return
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

    def esx_get_hw_uuid(self, destination_ip):
        ''' get hwuuid in esx host '''
        # not implemented yet
        pass

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

    def esx_set_encrypted_password(self, encrypted_password, esx_owner, esx_env, esx_server, esx_username, destination_ip=""):
        conf_file = "/etc/virt-who.d/virt-who.conf"
        conf_data = "[test-esx1]\n"\
                    "type=esx\n"\
                    "server=%s\n"\
                    "username=%s\n"\
                    "encrypted_password=%s\n"\
                    "owner=%s\n"\
                    "env=%s" % (esx_server, esx_username, encrypted_password, esx_owner, esx_env)
        self.set_virtwho_d_conf(conf_file, conf_data, destination_ip)

    def esx_get_hostname(self, targetmachine_ip=""):
        cmd = "hostname -f"
        ret, output = self.runcmd_esx(cmd, "geting esx machine's hostname", targetmachine_ip)
        if ret == 0:
            hostname = output.strip(' \r\n').strip('\r\n') 
            logger.info("Succeeded to get the machine's hostname %s." % hostname) 
            return hostname
        else:
            raise FailException("Test Failed - Failed to get hostname in %s." % self.get_hg_info(targetmachine_ip))

    # ========================================================
    #       Hyperv Functions
    # ========================================================
    def hyperv_setup(self):
    # Set hyperv test env. including:
    # 1. Configure virt-who run at hyperv mode
    # 2. Register system to server 
        server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
        hyperv_host = self.get_vw_cons("HYPERV_HOST")
        self.set_hyperv_conf()
        self.runcmd_service("restart_virtwho")
        self.sub_unregister()
        self.configure_server(server_ip, server_hostname)
        self.sub_register(server_user, server_pass)
        self.start_dbus_daemon()
        guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
        self.runcmd_service("restart_virtwho")

    def hyperv_run_cmd(self, cmd, targetmachine_ip=""):
    # Run cmd on hyperv
        time.sleep(3)
        hyperv_ip = self.get_vw_cons("HYPERV_HOST")
        hyperv_port = self.get_vw_cons("HYPERV_PORT")
        # listen to socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to the socket
        s.connect((hyperv_ip, hyperv_port))
        # send the command
        s.sendall(cmd)
        data = ""
        while True:
            buf = s.recv(1024)
            if not len(buf):
                break
            data = data + buf
        # logger.info ("After run %s, the output is \n%s" % (cmd, data))
        return data
        # close the socket
        s.close()

    def hyperv_get_hostname(self, guest_name, targetmachine_ip=""):
    # Get host's name
        output = self.hyperv_run_cmd("(Get-WMIObject  Win32_ComputerSystem).DNSHostName")
        if output is not "":
            hostname = output
            logger.info("hyperv hostname is %s" % hostname)
            return hostname

    def hyperv_get_guest_ip(self, guest_name, targetmachine_ip=""):
    # Get guest's IP
        output = self.hyperv_run_cmd("(Get-VMNetworkAdapter -VMName %s).IpAddresses" % guest_name)
        if output is not "":
            datalines = output.splitlines()
            for line in datalines:
                if ":" not in line:
                    guest_ip = line
                    logger.info("hyperv guest ip address is %s" % guest_ip)
                    return guest_ip

    def hyperv_get_guest_status(self, guest_name, targetmachine_ip=""):
    # Get guest's status
        output = self.hyperv_run_cmd("Get-VM %s | select *" % guest_name)
        if output is not "":
            logger.info("Success to run command to get vm %s status" % guest_name)
            status = self.get_key_rhevm(output, "State", "VMName", guest_name)
            return status
        else:
            raise FailException("Failed to run command to get vm %s status" % guest_name)

    @classmethod
    def decodeWinUUID(cls, uuid):
    # Decode host and guest uuid in hyperv
        """ Windows UUID needs to be decoded using following key
        From: {78563412-AB90-EFCD-1234-567890ABCDEF}
        To:    12345678-90AB-CDEF-1234-567890ABCDEF
        """
        if uuid[0] == "{":
            s = uuid[1:-1]
        else:
            s = uuid
        return s[6:8] + s[4:6] + s[2:4] + s[0:2] + "-" + s[11:13] + s[9:11] + "-" + s[16:18] + s[14:16] + s[18:]

    def hyperv_get_guest_id(self, guest_name, targetmachine_ip=""):
    # Get guest's id
        output = self.hyperv_run_cmd("Get-VM %s | select *" % guest_name)
        if output is not "":
            logger.info("Success to run command to get vm %s ID" % guest_name)
            guest_id = self.get_key_rhevm(output, "Id", "VMName", guest_name)
            logger.info("before decode guest uuid is %s" % guest_id)
            guest_uuid_after_decode = self.decodeWinUUID(guest_id)
            logger.info("after decode guest uuid is %s" % guest_uuid_after_decode)
            return guest_id 
        else:
            raise FailException("Failed to run command to get vm %s ID" % guest_name)

    def hyperv_get_guest_guid(self, guest_name, targetmachine_ip=""):
    # Get guest's guid
        output = self.hyperv_run_cmd('gwmi -namespace "root\\virtualization\\v2" Msvm_VirtualSystemSettingData | findstr "ElementName BIOSGUID"')
        if output is not "":
            datalines = output.splitlines()
            before_guest_uuid_line = ""
            for line in datalines:
                if guest_name in line:
                    break
                before_guest_uuid_line = line
            if before_guest_uuid_line == "":
                raise FailException("Failed to finde guest %s" % guest_name)
            else:
                before_guest_uuid = before_guest_uuid_line.split(":")[1].strip().strip("{").strip("}")
                logger.info("Before decode, guest %s guid is %s" % (guest_name, before_guest_uuid))
                guest_uuid = self.decodeWinUUID("%s" % before_guest_uuid)
                logger.info("After decode, guest %s guid is %s" % (guest_name, guest_uuid))
                return guest_uuid
        else:
            raise FailException("Failed to run command to get vm %s ID" % guest_name)

#         output = self.hyperv_run_cmd('gwmi -namespace "root\\virtualization\\v2" Msvm_VirtualSystemSettingData | select ElementName, BIOSGUID')
#         if output is not "":
#             datalines = output.splitlines()
#             segs = []
#             for line in datalines:
#                 segs.append(line)
#             for item in segs:
#                 if guest_name in item:
#                     item = item.strip()
#                     before_guest_uuid = item[item.index("{") + 1:item.index("}")].strip()
#                     logger.info("Before decode, guest %s guid is %s" % (guest_name, before_guest_uuid))
#                     guest_uuid = self.decodeWinUUID("%s" % before_guest_uuid)
#                     logger.info("After decode, guest %s guid is %s" % (guest_name, guest_uuid))
#                     return guest_uuid
#         else:
#             raise FailException("Failed to run command to get vm %s ID" % guest_name)

    def hyperv_get_host_uuid(self, targetmachine_ip=""):
    # Get host's uuid
        output = self.hyperv_run_cmd('gwmi -namespace "root/cimv2" Win32_ComputerSystemProduct | select UUID')
        datalines = output.splitlines()
        for line in datalines:
            if "--" not in line and "UUID" not in line:
                host_uuid = self.decodeWinUUID("%s" % line)
                logger.info("Success to get hyperv's uuid after decode, uuid is %s" % host_uuid)
                return host_uuid

    def hyperv_start_guest(self, guest_name, targetmachine_ip=""):
    # Start hyperv guest
        output = self.hyperv_run_cmd("Start-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run command to start vm %s" % guest_name)
            time.sleep(10)
            status = self.hyperv_get_guest_status(guest_name)
            if "Running" in status:
                logger.info("Success to show vm %s status is running" % guest_name)
                runtime = 0
                while True:
                    time.sleep(10)
                    guest_ip = self.hyperv_get_guest_ip(guest_name)
                    if guest_ip is None:
                        runtime = runtime + 1
                        time.sleep(20)
                        if runtime > 10:
                            raise FailException("Failed to start vm %s" % guest_name)
                    else:
                        logger.info("Success to start vm %s and ip is %s" % (guest_name, guest_ip))
                        break
            else:
                logger.info("Failed to show vm %s status is running" % guest_name)
        else:
            raise FailException("Failed to run command to start vm %s" % guest_name)

    def hyperv_stop_guest(self, guest_name, targetmachine_ip=""):
    # Stop hyperv guest
        output = self.hyperv_run_cmd("Stop-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run stop command vm %s" % guest_name)
            status = self.hyperv_get_guest_status(guest_name)
            if "Off" in status:
                logger.info("Success to stop vm %s" % guest_name)
            else:
                raise FailException("Failed to stop vm %s" % guest_name)
        else:
            raise FailException("Failed to stop command vm %s" % guest_name)

    def hyperv_suspend_guest(self, guest_name, targetmachine_ip=""):
    # Suspend hyperv guest
        output = self.hyperv_run_cmd("Suspend-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run suspend command vm %s" % guest_name)
            status = self.hyperv_get_guest_status(guest_name)
            if "Paused" in status:
                logger.info("Success to suspend vm %s" % guest_name)
            else:
                raise FailException("Failed to suspend vm %s" % guest_name)
        else:
            raise FailException("Failed to suspend command vm %s" % guest_name)

    def hyperv_resume_guest(self, guest_name, targetmachine_ip=""):
    # Resume hyperv guest
        output = self.hyperv_run_cmd("Resume-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run Resume command vm %s" % guest_name)
            status = self.hyperv_get_guest_status(guest_name)
            if "Running" in status:
                logger.info("Success to restart vm %s" % guest_name)
            else:
                raise FailException("Failed to restart vm %s" % guest_name)
        else:
            raise FailException("Failed to run command vm %s" % guest_name)

    def set_hyperv_conf(self, debug=1, targetmachine_ip=""):
        hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
    # Configure hyperv mode in /etc/sysconfig/virt-who
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/.*VIRTWHO_HYPERV=.*/VIRTWHO_HYPERV=1/g' -e 's/.*VIRTWHO_HYPERV_OWNER=.*/VIRTWHO_HYPERV_OWNER=%s/g' -e 's/.*VIRTWHO_HYPERV_ENV=.*/VIRTWHO_HYPERV_ENV=%s/g' -e 's/.*VIRTWHO_HYPERV_SERVER=.*/VIRTWHO_HYPERV_SERVER=%s/g' -e 's/.*VIRTWHO_HYPERV_USERNAME=.*/VIRTWHO_HYPERV_USERNAME=%s/g' -e 's/.*VIRTWHO_HYPERV_PASSWORD=.*/VIRTWHO_HYPERV_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password)
        ret, output = self.runcmd(cmd, "Setting hyperv mode in /etc/sysconfig/virt-who.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set hyperv mode in /etc/sysconfig/virt-who.")
        else:
            raise FailException("Test Failed - Failed  to set hyperv mode in /etc/sysconfig/virt-who.")

    # ========================================================
    #       Xen Functions
    # ========================================================
    def xen_setup(self):
        server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
        self.set_xen_conf()
        self.sub_unregister()
        self.configure_server(server_ip, server_hostname)
        self.sub_register(server_user, server_pass)
        self.start_dbus_daemon()
        self.runcmd_service("restart_virtwho")

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

    def __xen_generate_ipget_file(self, targetmachine_ip=""):
        generate_ipget_cmd = "wget -nc %s/ipget_xen.sh -P /root/ && chmod 777 /root/ipget_xen.sh" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd_xen(generate_ipget_cmd, "wget ipget_xen.sh file", targetmachine_ip)
        if ret == 0 or "already there" in output:
            logger.info("Succeeded to wget ipget.sh to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget ipget.sh to /root/.")

    def __xen_mac_to_ip(self, mac, targetmachine_ip=""):
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
        self.__xen_generate_ipget_file(targetmachine_ip)
        guestip = self.__xen_mac_to_ip(self.__get_vm_mac_addr(guest_name, targetmachine_ip), targetmachine_ip)
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
    #       KVM Functions
    # ========================================================
    def kvm_bridge_setup(self, targetmachine_ip=""):
        network_dev = ""
        cmd = "hostname -I | grep -E '^10.'"
        ret, output = self.runcmd(cmd, "check dev ip start with 10.", targetmachine_ip)
        if ret == 0:
            logger.info("Success to check dev ip start with 10.")
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
        else:
            logger.info("Dev ip is not start with 10.")
            cmd = "ip route | grep `hostname -I | awk {'print $2'}` | awk {'print $3'}"
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

    def mount_images(self):
        ''' mount the images prepared '''
        image_nfs_path = self.get_vw_cons("nfs_image_path")
        self.cm_set_cp_image()

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
        generate_ipget_cmd = "wget -nc %s/ipget.sh -P /root/ && chmod 777 /root/ipget.sh" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(generate_ipget_cmd, "wget ipget file", targetmachine_ip)
        if ret == 0 or "already there" in output:
            logger.info("Succeeded to wget ipget.sh to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget ipget.sh to /root/.")

    def getip_vm(self, guest_name, targetmachine_ip=""):
        guestip = self.__mac_to_ip(self.__get_dom_mac_addr(guest_name, targetmachine_ip), targetmachine_ip)
        if guestip != "" and (not "can not get ip by mac" in guestip):
            return guestip
        else:
            raise FailException("Test Failed - Failed to get ip of guest %s." % guest_name)

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
        ret, output = self.runcmd(cmd, "run command %s" % cmd, targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to get ip address.")
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Test Failed - Failed to get ip address.")

    # ========================================================
    #       KVM - virt-who test basic Functions
    # ========================================================
    def update_vw_configure(self, background=1, debug=1, targetmachine_ip=""):
        ''' update virt-who configure file /etc/sysconfig/virt-who. '''
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' /etc/sysconfig/virt-who" % (debug)
        ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file.")
        else:
            raise FailException("Failed to update virt-who configure file.")

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

    def kvm_get_guest_ip(self, guest_name, targetmachine_ip=""):
        ''' get guest ip address in kvm host '''
        ipAddress = self.getip_vm(guest_name, targetmachine_ip)
        if ipAddress == None or ipAddress == "":
            raise FailException("Faild to get guest %s ip." % guest_name)
        else:
            return ipAddress

    def vw_define_all_guests(self, targetmachine_ip=""):
        guest_path = self.get_vw_cons("nfs_image_path")
        for guestname in self.get_all_guests_list(guest_path, targetmachine_ip):
            self.define_vm(guestname, os.path.join(guest_path, guestname), targetmachine_ip)

    def vw_undefine_all_guests(self, targetmachine_ip=""):
        guest_path = self.get_vw_cons("nfs_image_path")
        for guestname in self.get_all_guests_list(guest_path, targetmachine_ip):
            self.vw_undefine_guest(guestname, targetmachine_ip)

    def vw_define_guest(self, guestname, targetmachine_ip=""):
        guest_path = self.get_vw_cons("nfs_image_path")
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
        elif "Domain not found" in output:
            self.define_vm(guest_name, targetmachine_ip)
        elif "Failed to connect socket to '/var/run/libvirt/virtlogd-sock'" in output:
            cmd = "systemctl start virtlogd.socket"
            ret, output = self.runcmd(cmd, "start virtlogd.socket" , targetmachine_ip)
            cmd = "virsh start %s" % (guest_name)
            ret, output = self.runcmd(cmd, "start guest" , targetmachine_ip)
        else:
            raise FailException("Test Failed - Failed to start guest %s." % guest_name)
        return self.__check_vm_available(guest_name, targetmachine_ip=targetmachine_ip)

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
        if "Domain %s has been undefined" % guestname in output or "failed to get domain" in output:
            logger.info("Succeeded to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))
        else:
            raise FailException("Failed to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))

    def set_remote_libvirt_conf(self, virtwho_remote_server_ip, targetmachine_ip=""):
        VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_USERNAME, VIRTWHO_LIBVIRT_PASSWORD = self.get_libvirt_info()
        VIRTWHO_LIBVIRT_SERVER = virtwho_remote_server_ip
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/.*VIRTWHO_LIBVIRT=.*/VIRTWHO_LIBVIRT=1/g' -e 's/.*VIRTWHO_LIBVIRT_OWNER=.*/VIRTWHO_LIBVIRT_OWNER=%s/g' -e 's/.*VIRTWHO_LIBVIRT_ENV=.*/VIRTWHO_LIBVIRT_ENV=%s/g' -e 's/.*VIRTWHO_LIBVIRT_SERVER=.*/VIRTWHO_LIBVIRT_SERVER=%s/g' -e 's/.*VIRTWHO_LIBVIRT_USERNAME=.*/VIRTWHO_LIBVIRT_USERNAME=%s/g' -e 's/.*VIRTWHO_LIBVIRT_PASSWORD=.*/VIRTWHO_LIBVIRT_PASSWORD=/g' /etc/sysconfig/virt-who" % (VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_SERVER, VIRTWHO_LIBVIRT_USERNAME)
        # set remote libvirt value
        ret, output = self.runcmd(cmd, "setting value for remote libvirt conf.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set remote libvirt value.")
        else:
            raise FailException("Test Failed - Failed to set remote libvirt value.")

    def clean_remote_libvirt_conf(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/^.*VIRTWHO_INTERVAL=.*/#VIRTWHO_INTERVAL=0/g' -e 's/.*VIRTWHO_LIBVIRT=.*/#VIRTWHO_LIBVIRT=0/g' -e 's/.*VIRTWHO_LIBVIRT_OWNER=.*/#VIRTWHO_LIBVIRT_OWNER=/g' -e 's/.*VIRTWHO_LIBVIRT_ENV=.*/#VIRTWHO_LIBVIRT_ENV=/g' -e 's/.*VIRTWHO_LIBVIRT_SERVER=.*/#VIRTWHO_LIBVIRT_SERVER=/g' -e 's/.*VIRTWHO_LIBVIRT_USERNAME=.*/#VIRTWHO_LIBVIRT_USERNAME=/g' -e 's/.*VIRTWHO_LIBVIRT_PASSWORD=.*/#VIRTWHO_LIBVIRT_PASSWORD=/g' /etc/sysconfig/virt-who"
        # set remote libvirt value
        ret, output = self.runcmd(cmd, "Clean config of remote libvirt conf. reset to default", targetmachine_ip)
        if ret == 0:
            self.vw_restart_virtwho(targetmachine_ip)
            logger.info("Succeeded to reset to defualt config.")
        else:
            raise FailException("Test Failed - Failed to reset to defualt config.")

    def setup_libvirtd_config(self):
        cmd = "sed -i -e 's/^#listen_tls = 0/listen_tls = 0/g' -e 's/^#listen_tcp = 1/listen_tcp = 1/g' -e 's/^#auth_tcp = \"sasl\"/auth_tcp = \"sasl\"/g' -e 's/^#tcp_port = \"16509\"/tcp_port = \"16509\"/g' /etc/libvirt/libvirtd.conf"
        ret, output = self.runcmd(cmd, "setup_libvirtd_config")
        if ret == 0 :
            logger.info("Succeeded to setup_libvirtd_config.")
        else:
            raise FailException("Test Failed - Failed to setup_libvirtd_config.")

    def restore_libvirtd_config(self):
        cmd = "sed -i -e 's/^listen_tls = 0/#listen_tls = 0/g' -e 's/^listen_tcp = 1/#listen_tcp = 1/g' -e 's/^auth_tcp = \"sasl\"/#auth_tcp = \"sasl\"/g' -e 's/^tcp_port = \"16509\"/#tcp_port = \"16509\"/g' /etc/libvirt/libvirtd.conf"
        ret, output = self.runcmd(cmd, "restore_libvirtd_config")
        if ret == 0 :
            logger.info("Succeeded to restore_libvirtd_config.")
        else:
            raise FailException("Test Failed - Failed to restore_libvirtd_config.")

    def vw_change_guest_name(self, targetmachine_ip=""):
        if "remote_libvirt" in get_exported_param("HYPERVISOR_TYPE"):
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME") 
        else:    
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
        self.vw_start_guests(guest_name, targetmachine_ip)
        guestip = self.kvm_get_guest_ip(guest_name, targetmachine_ip)
        if "remote_libvirt" in get_exported_param("HYPERVISOR_TYPE"):
            self.cm_change_static_guestname(guestip) 
        else:    
            self.cm_change_hostname(guestip)
        self.vw_stop_guests(guest_name, targetmachine_ip)

    # ========================================================
    #       KVM - test env set up function
    # ========================================================
    def remote_libvirt_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
        remote_host_1 = get_exported_param("REMOTE_IP_1")
        remote_host_2 = get_exported_param("REMOTE_IP_2")
        guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
 
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        self.start_dbus_daemon()
        # update virt-who configure file tp remote_libvirt mode
        self.set_remote_libvirt_conf(remote_host_1)
        # restart virt-who service
        self.runcmd_service("restart_virtwho")
        # add guests in host machine.
        self.vw_define_guest(guest_name, remote_host_1)
        # change target guest host name, or else satellite testing will fail due to same name
        self.vw_change_guest_name(remote_host_1)


    def kvm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_vw_configure()
        # restart virt-who service
        self.vw_restart_virtwho()
        # mount all needed guests
        self.mount_images()
        # add guests in host machine.
        self.vw_define_all_guests()
        # change target guest host name, or else satellite testing will fail due to same name
        self.vw_change_guest_name()
        # configure slave machine
        slave_machine_ip = get_exported_param("REMOTE_IP_2")
        if slave_machine_ip != None and slave_machine_ip != "":
            # if host already registered, unregister it first, then configure and register it
            self.sub_unregister(slave_machine_ip)
            self.configure_server(SERVER_IP, SERVER_HOSTNAME, slave_machine_ip)
            self.sub_register(SERVER_USER, SERVER_PASS, slave_machine_ip)
            image_nfs_path = self.get_vw_cons("nfs_image_path")
            self.mount_images_in_slave_machine(slave_machine_ip, image_nfs_path, image_nfs_path)
            self.update_vw_configure(slave_machine_ip)
            self.vw_restart_virtwho(slave_machine_ip)

    def kvm_sys_setup(self, targetmachine_ip=""):
        self.sys_setup(targetmachine_ip)
        # system setup for virt-who testing
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        self.cm_update_system(targetmachine_ip)
        self.kvm_bridge_setup(targetmachine_ip)
        self.kvm_permission_setup(targetmachine_ip)
        cmd = "service libvirtd start"
        ret, output = self.runcmd(cmd, "restart libvirtd service", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        # need to start virtlogd service, or else migration will fail
        # commented result check, sometimes virtlogd service do not exist
        cmd = "service virtlogd start"
        ret, output = self.runcmd(cmd, "restart virtlogd service", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to start service virtlogd in %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Test Failed - Failed to start service virtlogd in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def kvm_static_sys_setup(self, targetmachine_ip=""):
        self.cm_update_system(targetmachine_ip)
        cmd = "service libvirtd start"
        ret, output = self.runcmd(cmd, "restart libvirtd service", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        # need to start virtlogd service, or else migration will fail
        # commented result check, sometimes virtlogd service do not exist
        cmd = "service virtlogd start"
        ret, output = self.runcmd(cmd, "restart virtlogd service", targetmachine_ip)
#         if ret == 0:
#             logger.info("Succeeded to start service virtlogd in %s." % self.get_hg_info(targetmachine_ip))
#         else:
#             raise FailException("Test Failed - Failed to start service virtlogd in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def kvm_setup_arch(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_vw_configure()
        # restart virt-who service
        self.vw_restart_virtwho()

    def kvm_sys_setup_arch(self, targetmachine_ip=""):
        self.sys_setup(targetmachine_ip)
        # system setup for virt-who testing
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        cmd = "yum install -y libvirt"
        ret, output = self.runcmd(cmd, "install libvirt package for kvm arch testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to install libvirt package for kvm arch testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to install libvirt package for kvm arch testing in %s." % self.get_hg_info(targetmachine_ip))
        cmd = "service libvirtd start"
        ret, output = self.runcmd(cmd, "restart libvirtd service", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)


    # ========================================================
    #       VDSM Functions
    # ========================================================
    def rhel_rhevm_sys_setup(self, targetmachine_ip=""):
        rhel_compose = get_exported_param("RHEL_COMPOSE")
        rhevm_ip = get_exported_param("RHEVM_IP") 
        nfs_ip = get_exported_param("REMOTE_IP")
        rhel_rhevm_guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME") 
        vm_name =  "rhevh_" + rhel_rhevm_guest_name
        nfs_dir_for_storage = self.get_vw_cons("NFS_DIR_FOR_storage")
        nfs_dir_for_export = self.get_vw_cons("NFS_DIR_FOR_export")
        rhevm_host1_name, rhevm_host2_name = self.get_hostname(), self.get_hostname(get_exported_param("REMOTE_IP_2"))
#         rhevm_host1_name = self.get_hostname()
        if "RHEVH" not in rhel_compose:
            self.sys_setup(targetmachine_ip)
            self.install_vdsm_package(rhel_compose)
            self.install_vdsm_package(rhel_compose, get_exported_param("REMOTE_IP_2"))
        self.rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
        self.conf_rhevm_shellrc(rhevm_ip)
        self.conf_cluster_cpu("Default", "Intel Conroe Family", rhevm_ip)
        self.rhevm_add_host(rhevm_host1_name, get_exported_param("REMOTE_IP"), rhevm_ip)
#         self.rhevm_add_host(rhevm_host2_name, get_exported_param("REMOTE_IP_2"), rhevm_ip)
        self.add_storagedomain_to_rhevm("data_storage", rhevm_host1_name, "data", "v3", nfs_ip, nfs_dir_for_storage, rhevm_ip)
        self.add_storagedomain_to_rhevm("export_storage", rhevm_host1_name, "export", "v1", nfs_ip, nfs_dir_for_export, rhevm_ip)
        self.add_vm_to_rhevm(rhel_rhevm_guest_name, vm_name, rhevm_host1_name, nfs_ip, nfs_dir_for_export, rhevm_ip)
        #self.update_vm_to_host(rhel_rhevm_guest_name, rhevm_host1_name, rhevm_ip)
        if "rhevm-3.5" not in self.rhevm_version:
            if "RHEVH" not in rhel_compose:
                if self.vdsm_check_vm_nw(rhel_rhevm_guest_name, "eth0", rhevm_ip) is True:
                    self.vdsm_rm_vm_nw(rhel_rhevm_guest_name, "eth0", rhevm_ip)
                    self.vdsm_add_vm_nw(rhel_rhevm_guest_name, rhevm_ip)
        # change target guest host name, or else satellite testing will fail due to same name
                self.rhevm_change_guest_name(rhel_rhevm_guest_name, rhevm_ip)
            else:
                if self.vdsm_check_vm_nw(vm_name, "eth0", rhevm_ip) is True:
                    self.vdsm_rm_vm_nw(vm_name, "eth0", rhevm_ip)
                    self.vdsm_add_vm_nw(vm_name, rhevm_ip)
                self.rhevm_change_guest_name(vm_name, rhevm_ip)

    def rhel_rhevm_static_sys_setup(self, targetmachine_ip=""):
        RHEVM_IP = get_exported_param("RHEVM_IP")
        RHEVM_HOST1_IP = get_exported_param("RHEVM_HOST1_IP")
        RHEVM_HOST2_IP = get_exported_param("RHEVM_HOST2_IP")  
        RHEL_RHEVM_GUEST_NAME = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
        GUEST_NAME = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
        logger.info("RHEL_RHEVM_GUEST_NAME is -----%s", RHEL_RHEVM_GUEST_NAME)
        logger.info("GUEST_NAME is -----%s", GUEST_NAME)
        RHEVM_HOST1_NAME = self.get_hostname(RHEVM_HOST1_IP)
        RHEVM_HOST2_NAME = self.get_hostname(RHEVM_HOST2_IP)
        NFSserver_ip = get_exported_param("RHEVM_HOST1_IP")
        nfs_dir_for_storage = self.get_vw_cons("NFS_DIR_FOR_storage")
        nfs_dir_for_export = self.get_vw_cons("NFS_DIR_FOR_export")
        rhel_compose = get_exported_param("RHEL_HOST_COMPOSE")
        rhevm_version = self.cm_get_rpm_version("rhevm", RHEVM_IP)

        # System setup for RHEL+RHEVM(VDSM/RHEVM) testing env on two hosts
#         self.config_vdsm_env_setup(rhel_compose, rhevm_version, RHEVM_HOST1_IP)
# #         self.config_vdsm_env_setup(rhel_compose, rhevm_version, RHEVM_HOST2_IP)
#         # System setup for virt-who on two hosts
#         self.sys_setup(RHEVM_HOST1_IP)
# #         self.sys_setup(get_exported_param("REMOTE_IP_2"))
#         # Configure env on rhevm(add two host,storage,guest)
#         self.conf_rhevm_shellrc(RHEVM_IP)
#         self.conf_cluster_cpu("Default", "Intel Conroe Family", RHEVM_IP)
#         # Configure cluster and dc to 3.5 
#         if "rhevm-3.6" in rhevm_version:
#             self.update_dc_compa_version("Default", "5", "3", RHEVM_IP)
#             self.update_cluster_compa_version("Default", "5", "3", RHEVM_IP)
# #         self.update_cluster_cpu("Default", "Intel Penryn Family", RHEVM_IP)
#         self.rhevm_add_host(RHEVM_HOST1_NAME, get_exported_param("RHEVM_HOST1_IP"), RHEVM_IP)
# #         self.rhevm_add_host(RHEVM_HOST2_NAME, get_exported_param("RHEVM_HOST2_IP"), RHEVM_IP)
#         self.add_storagedomain_to_rhevm("data_storage", RHEVM_HOST1_NAME, "data", "v3", NFSserver_ip, nfs_dir_for_storage, RHEVM_IP)
#         self.add_storagedomain_to_rhevm("export_storage", RHEVM_HOST1_NAME, "export", "v1", NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
#         self.add_vm_to_rhevm(RHEL_RHEVM_GUEST_NAME, GUEST_NAME, RHEVM_HOST1_NAME, NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
#         self.update_vm_to_host(RHEL_RHEVM_GUEST_NAME, RHEVM_HOST1_NAME, RHEVM_IP)
#         self.update_vm_name(RHEL_RHEVM_GUEST_NAME, GUEST_NAME, RHEVM_IP)
        # Add network bridge "ovirtmgmt"
#         if "rhevm-3.6" in rhevm_version and "RHEL-6.8" in rhel_compose:
        if "rhevm-3.5" not in rhevm_version:
            if self.vdsm_check_vm_nw(GUEST_NAME, "eth0", RHEVM_IP) is True:
                self.vdsm_rm_vm_nw(GUEST_NAME, "eth0", RHEVM_IP)
                self.vdsm_add_vm_nw(GUEST_NAME, RHEVM_IP)
        # change target guest host name, or else satellite testing will fail due to same name
        self.rhevm_change_guest_name(GUEST_NAME, RHEVM_IP)

    def rhel_rhevm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
        RHEVM_IP = get_exported_param("RHEVM_IP")
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        self.start_dbus_daemon()
        # update virt-who to rhevm mode in /etc/sysconfig/virt-who
        self.update_config_to_default()
        self.set_rhevm_conf()
        self.service_command("restart_virtwho")

    def rhel_vdsm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_config_to_default()
        self.update_rhel_vdsm_configure(60)
        self.service_command("restart_virtwho")
        # configure slave machine
        slave_machine_ip = get_exported_param("REMOTE_IP_2")
        if slave_machine_ip != None and slave_machine_ip != "":
            # if host already registered, unregister it first, then configure and register it
            self.sub_unregister(slave_machine_ip)
            self.configure_server(SERVER_IP, SERVER_HOSTNAME, slave_machine_ip)
            self.sub_register(SERVER_USER, SERVER_PASS, slave_machine_ip)
            # update virt-who configure file
            self.update_config_to_default()
            self.update_rhel_vdsm_configure(60, slave_machine_ip)
            self.service_command("restart_virtwho", slave_machine_ip)

    def configure_rhel_host_bridge(self, targetmachine_ip=""):
        # configure rhevm bridge on rhel host
        cmd = "ip route | grep `hostname -I | awk {'print $1'}` | awk {'print $3'}"
        ret, output = self.runcmd(cmd, "get network device", targetmachine_ip)
        if ret == 0:
            network_dev = output.strip()
            logger.info("Succeeded to get network device in %s" % self.get_hg_info(targetmachine_ip))
            if not "rhevm" in output:
                cmd = "sed -i '/^BOOTPROTO/d' /etc/sysconfig/network-scripts/ifcfg-%s; echo \"BRIDGE=rhevm\" >> /etc/sysconfig/network-scripts/ifcfg-%s;echo \"DEVICE=rhevm\nBOOTPROTO=dhcp\nONBOOT=yes\nTYPE=Bridge\"> /etc/sysconfig/network-scripts/ifcfg-br0" % (network_dev, network_dev)
                ret, output = self.runcmd(cmd, "setup bridge for kvm testing", targetmachine_ip)
                if ret == 0:
                    logger.info("Succeeded to set /etc/sysconfig/network-scripts in %s" % self.get_hg_info(targetmachine_ip))
                else:
                    raise FailException("Test Failed - Failed to /etc/sysconfig/network-scripts in %s" % self.get_hg_info(targetmachine_ip))
                self.service_command("restart_network", targetmachine_ip)
            else:
                logger.info("Bridge already setup for virt-who testing, do nothing ...")
        else:
            raise FailException("Test Failed - Failed to get network device in %s" % self.get_hg_info(targetmachine_ip))

    def set_rhevm_repo_file(self, compose_name, rhevm_version, targetmachine_ip=""):
    # Get rhevm repo
        ''' wget rhevm repo file and add to rhel host '''
        if self.os_serial == "7":
            if "rhevm-4.1" in rhevm_version:
                repo = "rhevm_7.3_41.repo"
            elif "rhevm-4.0" in rhevm_version :
                if "7.2" in compose_name :
                    repo = "rhevm_7.2_40.repo"
                else:
                    repo = "rhevm_7.3_40.repo"
            else:
                repo = "rhevm_7.x.repo"
        else:
            if self.os_serial == "6" and "rhevm-3.6" in rhevm_version:
                repo = "rhevm_6.x_36.repo"
            else:
                repo = "rhevm_6.x.repo"
        cmd = "wget -P /etc/yum.repos.d/ %s/%s" % (self.get_vw_cons("data_folder"), repo)
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget rhevm repo file and add to rhel host in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to wget rhevm repo file and add to rhel host in %s" % self.get_hg_info(targetmachine_ip))
        cmd = "sed -i -e 's/rhelbuild/%s/g' /etc/yum.repos.d/%s" % (compose_name, repo)
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")

    def get_vm_cmd(self, vm_name, targetmachine_ip=""):
        if "rhevm-4" in self.rhevm_version:
            # logger.info("It is rhevm4.X build, need to use 'list vms'")
#             return "list vms %s --show-all" % vm_name
            return "list vms --query name=%s --show-all" % vm_name
        else:
            # logger.info("It is rhevm3.X build, need to use 'show vm'")
            return "show vm %s" % vm_name

    def config_vdsm_env_setup(self, rhel_compose, rhevm_version, targetmachine_ip=""):
    # System setup for RHEL+RHEVM testing env
        if not self.sub_isregistered(targetmachine_ip):
            self.sub_register("QualityAssurance", "VHVFhPS5TEG8dud9", targetmachine_ip)
            self.sub_auto_subscribe(targetmachine_ip)
        self.cm_install_basetool(targetmachine_ip)
#         self.set_rhevm_repo_file(rhel_compose, rhevm_version, targetmachine_ip)
        self.set_rhevm_repo_file(rhel_compose, targetmachine_ip)
        cmd = "subscription-manager repos --disable=*"
        ret, output = self.runcmd(cmd, "disable all repo", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to disable all repo in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to disable all repo in %s" % self.get_hg_info(targetmachine_ip))
        cmd = "subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-supplementary-rpms"
        ret, output = self.runcmd(cmd, "enable useful rhel repo", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to enable useful rhel repo in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to enable useful rhel repo in %s" % self.get_hg_info(targetmachine_ip))
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s" % self.get_hg_info(targetmachine_ip))
        vdsm_version = self.cm_get_rpm_version("vdsm", targetmachine_ip)
        if vdsm_version is "null":
            cmd = "yum install -y vdsm"
            # ret, output = self.runcmd(cmd, "install vdsm and related packages", targetmachine_ip, showlogger=False)
            ret, output = self.runcmd(cmd, "install vdsm and related packages", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install vdsm and related packages in %s" % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Test Failed - Failed to install vdsm and related packages in %s" % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def install_vdsm_package(self, rhel_compose, targetmachine_ip=""):
        if "RHEVH" not in get_exported_param("RHEL_COMPOSE"):
            cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
            ret, output = self.runcmd(cmd, "install virtualization related packages", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install virtualization related packages in %s" % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Test Failed - Failed to install virtualization related packages in %s" % self.get_hg_info(targetmachine_ip))
            self.set_rhevm_repo_file(rhel_compose, targetmachine_ip)
        cmd = "yum install -y vdsm"
        ret, output = self.runcmd(cmd, "install vdsm and related packages", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to install vdsm and related packages in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to install vdsm and related packages in %s" % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def conf_rhevm_shellrc(self, targetmachine_ip=""):
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        if "rhevm-4" in self.rhevm_version:
            cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s/ovirt-engine/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.ovirtshellrc" % tagetmachine_hostname
        else:
            cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s:443/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.rhevmshellrc" % tagetmachine_hostname
        ret, output = self.runcmd(cmd, "config rhevm_shell env on rhevm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to config rhevm_shell env on rhevm in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to config rhevm_shell env on rhevm in %s" % self.get_hg_info(targetmachine_ip))

    def conf_cluster_cpu(self, cluster_name, cpu_type, targetmachine_ip):
        if "rhevm-4" in self.rhevm_version:
            cmd = "%s -c -E \"update cluster %s --name '%s' \"" % (self.rhevm_shell, cluster_name, cpu_type)
        else:
            cmd = "%s -c -E \"update cluster %s --cpu-id '%s' \"" % (self.rhevm_shell, cluster_name, cpu_type)
        ret, output = self.runcmd(cmd, "update cluster cpu", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update cluster %s cpu to %s" % (cluster_name, cpu_type))
        else:
            raise FailException("Failed to update cluster %s cpu to %s" % (cluster_name, cpu_type))
        # configure cluster and dc to 3.5 
        if "rhevm-3.6" in self.rhevm_version:
            self.update_dc_compa_version("Default", "5", "3", targetmachine_ip)
            self.update_cluster_compa_version("Default", "5", "3", targetmachine_ip)

    def update_cluster_compa_version(self, cluster_name, min_version, major_version, targetmachine_ip):
        # Update cluster Compatibility Version 
        cmd = "%s -c -E \"update cluster %s --version-minor %s --version-major %s \"" % (self.rhevm_shell, cluster_name, min_version, major_version)
        ret, output = self.runcmd(cmd, "update cluster's Compatibility Version", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update cluster %s Compatibility Version to %s.%s" % (cluster_name, major_version, min_version))
        else:
            raise FailException("Failed to update cluster %s Compatibility Version to %s.%s" % (cluster_name, major_version, min_version))

    def update_dc_compa_version(self, dc_name, min_version, major_version, targetmachine_ip):
        # Update datacenter Compatibility Version 
        cmd = "%s -c -E \"update datacenter %s --version-minor %s --version-major %s \"" % (self.rhevm_shell, dc_name, min_version, major_version)
        ret, output = self.runcmd(cmd, "update Compatibility Version", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update datacenter's %s Compatibility Version to %s.%s" % (dc_name, major_version, min_version))
        else:
            raise FailException("Failed to update datacenter's %s Compatibility Version to %s.%s" % (dc_name, major_version, min_version))

    def vdsm_get_dc_id(self, targetmachine_ip=""):
        # get datacenter's id
        cmd = "%s -c -E 'list datacenters'" % self.rhevm_shell
        ret, output = self.runcmd(cmd, "list datacenter in rhevm", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to list datacenter")
            dcid = self.get_key_rhevm(output, "id", "name", "Default", targetmachine_ip)
            if dcid is not "":
                logger.info("Succeeded to get datacenter default id is %s" % dcid)
                return dcid
            else:
                logger.error("Failed to get datacenter default id is %s" % dcid)
        else:
            raise FailException("Failed to list datacenter")

    def rhevm_check_host_status(self, host_name, host_status, targetmachine_ip):
        cmd = " %s -c -E 'list hosts --show-all'" % self.rhevm_shell
        for item in range(30):
            ret, output = self.runcmd(cmd, "list hosts in rhevm", targetmachine_ip, showlogger=False)
            if ret == 0:
                if host_status == "deleted":
                    if host_name not in output:
                        logger.info("Succeeded to check host %s has been deleted" % host_name)
                        break
                    else:
                        logger.info("host %s still exist" % host_name)
                        time.sleep(30)
                else:
                    if host_name in output:
                        status = self.get_key_rhevm(output, "status-state", "name", host_name, targetmachine_ip)
                        if host_status == status:
                            logger.info("Succeeded to check host %s status is %s" % (host_name, host_status))
                            break
                        else :
                            logger.info("host %s status is still %s" % (host_name, status))
                            time.sleep(30)
            else:
                raise FailException("Failed to run list host %s via command: %s" % (host_name, cmd))
        else:
            raise FailException("Failed to check host %s status %s" % (host_name, host_status))

    def rhevm_check_host_exist(self, host_name, targetmachine_ip):
        cmd = "%s -c -E 'list hosts --show-all'" % self.rhevm_shell
        ret, output = self.runcmd(cmd, "list hosts in rhevm", targetmachine_ip, showlogger=False)
        if ret == 0 and host_name in output:
            logger.info("Succeeded to check host %s exist" % host_name)
            status = self.get_key_rhevm(output, "status-state", "name", host_name, targetmachine_ip)
            if "up" in status:
                logger.info("Succeeded to check host %s in up status" % host_name)
                return True
            else:
                raise FailException("Host exist but not in up status" % host_name)
        else:
            return False

    def cm_update_system(self, targetmachine_ip=""):
        cmd = "yum update -y"
        ret, output = self.runcmd(cmd, "yum update all system package", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to update all system package")
        else:
            raise FailException("Failed to update all system package")

    def rhevm_add_host(self, host_name, host_ip, targetmachine_ip):
        if not self.rhevm_check_host_exist(host_name, targetmachine_ip):
            cmd = "%s -c -E 'add host --name \"%s\" --address \"%s\" --root_password red2015'" % (self.rhevm_shell, host_name, host_ip)
            ret, output = self.runcmd(cmd, "add host to rhevm", targetmachine_ip, showlogger=False)
            if ret == 0:
                self.rhevm_check_host_status(host_name, "up", targetmachine_ip)
            else:
                if "rhevm-4" not in self.rhevm_version:
                    self.rhevm_commitnetconfig_host(host_name, targetmachine_ip)
                    self.rhevm_active_host(host_name, targetmachine_ip)
                    self.rhevm_check_host_status(host_name, "up", targetmachine_ip)
                    return True
                raise FailException("Failed to add host %s to rhevm" % host_name)

    def rhevm_commitnetconfig_host(self, host_name, targetmachine_ip):
        cmd = "%s -c -E 'action host \"%s\" commitnetconfig'" % (self.rhevm_shell, host_name)
        ret, output = self.runcmd(cmd, "commitnetconfig host on rhevm", targetmachine_ip)
#         if ret == 0:
#             self.rhevm_check_host_status( host_name, "maintenance", targetmachine_ip)
#         else:
#             raise FailException("Failed to commitnetconfig host %s on rhevm" % host_name)

    def rhevm_mantenance_host(self, host_name, targetmachine_ip):
        # Maintenance Host on RHEVM
        cmd = "%s -c -E 'action host \"%s\" deactivate'" % (self.rhevm_shell, host_name)
        ret, output = self.runcmd(cmd, "Maintenance host on rhevm", targetmachine_ip)
        if ret == 0:
            self.rhevm_check_host_status(host_name, "maintenance", targetmachine_ip)
        else:
            raise FailException("Failed to maintenance host %s on rhevm" % host_name)

    def rhevm_delete_host(self, host_name, targetmachine_ip):
        # Delete Host on RHEVM
        cmd = "%s -c -E 'action host \"%s\" delete'" % (self.rhevm_shell, host_name)
        ret, output = self.runcmd(cmd, "Maintenance host on rhevm", targetmachine_ip)
        if ret == 0:
            self.rhevm_check_host_status(host_name, "deleted", targetmachine_ip)
        else:
            raise FailException("Failed to delete host %s on rhevm" % host_name)

    def rhevm_active_host(self, host_name, targetmachine_ip):
        # Active Host on RHEVM
        cmd = "%s -c -E 'action host \"%s\" activate'" % (self.rhevm_shell, host_name)
        ret, output = self.runcmd(cmd, "Active host on rhevm", targetmachine_ip)
        if ret == 0:
            self.rhevm_check_host_status(host_name, "up", targetmachine_ip)
        else:
            raise FailException("Failed to active host %s on rhevm" % host_name)

    def update_vm_name(self, vm_name, vm_display_name, targetmachine_ip):
        # add vm to special host
        cmd = "%s -c -E 'update vm %s --name %s'" % (self.rhevm_shell, vm_name, vm_display_name)
        ret, output = self.runcmd(cmd, "update vm name", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update vm %s to name %s" % (vm_name, vm_display_name))
        else:
            raise FailException("Failed to update vm %s to name %s" % (vm_name, vm_display_name))

    def update_vm_to_host(self, vm_name, rhevm_host_name, targetmachine_ip):
        # add vm to special host
        cmd = "%s -c -E 'update vm %s --placement_policy-host-name %s'" % (self.rhevm_shell, vm_name, rhevm_host_name)
        ret, output = self.runcmd(cmd, "update vm to special host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update vm %s to host %s" % (vm_name, rhevm_host_name))
        else:
            raise FailException("Failed to update vm %s to host %s" % (vm_name, rhevm_host_name))
        time.sleep(60)
        
    def rhevm_info_dict(self, output, targetmachine_ip=""):
        # parse rhevm-result to dict
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
            raise FailException("Failed to get output in rhevm-result file")

    def wait_for_status(self, cmd, status_key, status_value, targetmachine_ip, timeout=600):
        # wait for a while until expect status shown in /tmp/rhevm-result file
        timout = 0
        while True:
            timout = timout + 1
            ret, output = self.runcmd(cmd, "list info updating in rhevm", targetmachine_ip, showlogger=False)
            rhevm_info = self.rhevm_info_dict(output)
            if status_value == "NotExist":
                if not status_key in rhevm_info.keys():
                    logger.info("Succeded to check %s not exist" % status_key)
                    return True
            elif status_key in rhevm_info.keys() and rhevm_info[status_key] == status_value:
                logger.info("Succeeded to get %s value %s in rhevm" % (status_key, status_value))
                return True
            elif status_key in rhevm_info.keys() and rhevm_info[status_key] != status_value:
                logger.info("Succeeded to remove %s" % status_value)
                return True
            elif timout > 60:
                logger.info("Time out, running rhevm-shell command in server failed")
                return False
            else:
                logger.info("sleep 10 in wait_for_status")
                time.sleep(10)

    def clean_nfs_env(self, file, targetmachine_ip): 
        cmd = "service nfs stop"
        ret, output = self.runcmd(cmd, "stop nfs service", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to stop nfs service")
        else:
            logger.info("Failed to stop nfs service")
        cmd = "umount 10.66.144.9:/data/projects/sam-virtwho/pub" 
        ret, output = self.runcmd(cmd, "umount data", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to umount data")
        else:
            logger.info("Failed to umount data")
        # Add storagedomain in rhevm and active it
        cmd = "rm -rf %s" % file
        ret, output = self.runcmd(cmd, "delete storage data", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to delete storage data %s" % file)
        else:
            logger.info("Failed to delete storage data %s" % file)
        cmd = "rm -rf /tmp/images_mnt"
        ret, output = self.runcmd(cmd, "delete tmp dat", targetmachine_ip)
        if ret == 0 :
            logger.info("Succeeded to delete tmp dat")
        else:
            logger.info("Failed to delete tmp dat")

    def add_storagedomain_to_rhevm(self, storage_name, attach_host_name, domaintype, storage_format, nfs_server, storage_dir, targetmachine_ip): 
        # check datastorage domain before add new one
        cmd = "%s -c -E 'list storagedomains' " % self.rhevm_shell
        ret, output = self.runcmd(cmd, "check storagedomain before add new one", targetmachine_ip)
        if ret == 0 and storage_name in output:
            logger.info("storagedomains %s is exist in rhevm" % storage_name)
        else:
            logger.info("storagedomains %s is not exist in rhevm" % storage_name)
            self.clean_nfs_env(storage_dir, nfs_server)
            # configure nfs env
            cmd = "mkdir %s" % storage_dir
            self.runcmd(cmd, "create storage nfs folder", nfs_server)
            cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (storage_dir.replace('/', '\/'), storage_dir)
            ret, output = self.runcmd(cmd, "set /etc/exports for nfs", nfs_server)
            if ret == 0:
                logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file" % storage_dir)
            else:
                raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file" % storage_dir)
            cmd = "chmod -R 777 %s" % storage_dir
            ret, output = self.runcmd(cmd, "Add x right to storage dir", nfs_server)
            if ret == 0 :
                logger.info("Succeeded to add right to storage dir")
            else:
                raise FailException("Failed to add right to storage dir")
            cmd = "service nfs restart"
            ret, output = self.runcmd(cmd, "restarting nfs service", nfs_server)
            if ret == 0 :
                logger.info("Succeeded to restart service nfs")
            else:
                raise FailException("Failed to restart service nfs")
            # add storagedomain in rhevm and active it
            cmd = "%s -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter \"Default\"' " % (self.rhevm_shell, storage_name, attach_host_name, domaintype, storage_format, nfs_server, storage_dir)
            ret, output = self.runcmd(cmd, "add storagedomain in rhevm", targetmachine_ip)
            wait_cmd = "%s -c -E 'list storagedomains --show-all'" % self.rhevm_shell
            if self.wait_for_status(wait_cmd, "status-state", "unattached", targetmachine_ip):
                logger.info("Succeeded to add storagedomains %s in rhevm" % storage_name)
            else:
                raise FailException("Failed to add storagedomains %s in rhevm" % storage_name)
            time.sleep(120)
            # attach datacenter to storagedomain in rhevm
            if "rhevm-3.5" not in self.rhevm_version:
                dc_attach = self.vdsm_get_dc_id(targetmachine_ip)
            else:
                dc_attach = "Default"
            cmd = "%s -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"%s\"' " % (self.rhevm_shell, storage_name, attach_host_name, domaintype, storage_format, nfs_server, storage_dir, dc_attach)
            ret, output = self.runcmd(cmd, "Attaches the storage domain to the Default data center", targetmachine_ip)
            wait_cmd = "%s -c -E 'list storagedomains --show-all'" % self.rhevm_shell
            if self.wait_for_status(wait_cmd, "status-state", "NotExist", targetmachine_ip):
                logger.info("Succeeded to active storagedomains %s in rhevm" % storage_name)
            else:
                raise FailException("Failed to active storagedomains %s in rhevm" % storage_name)
            time.sleep(60)

#     # activate storagedomain in rhevm
#      def activate_storagedomain(self, storage_name, targetmachine_ip): 
#         cmd = "rhevm-shell -c -E 'action storagedomain \"%s\" activate --datacenter-identifier \"Default\"' " % (storage_name)
#         ret, output = self.runcmd(cmd, "activate storagedomain in rhevm", targetmachine_ip)
#         if "complete" in output:
#             if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "NotExist", targetmachine_ip):
#         # if self.wait_for_status("rhevm-shell -c -E 'action storagedomain \"%s\" activate --datacenter-identifier \"Default\"' % (storage_name)", "status-state", "complete", targetmachine_ip):
#                 logger.info("Succeeded to activate storagedomains %s in rhevm" % storage_name)
#             else:
#                 raise FailException("Failed to list activate storagedomains %s in rhevm" % storage_name)
#         else:
#             raise FailException("Failed to activate storagedomains %s in rhevm" % storage_name)

    def install_virtV2V(self, targetmachine_ip=""):
        # install virt-V2V
        cmd = "rpm -q virt-v2v"
        ret, output = self.runcmd(cmd, "check whether virt-V2V exist", targetmachine_ip)
        if ret == 0:
            logger.info("virt-V2V has already exist, needn't to install it")
        else:
            logger.info("virt-V2V hasn't been installed")
            cmd = "yum install virt-v2v -y"
            ret, output = self.runcmd(cmd, "install virt-v2v", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install virt-V2V")
            else:
                raise FailException("Failed to install virt-V2V")

    def rhevm_define_guest(self, vm_name, targetmachine_ip=""):
        # define guest
        if "RHEVH" not in get_exported_param("RHEL_COMPOSE"):
            ''' wget kvm img and xml file, define it in execute machine for converting to rhevm '''
            cmd = "test -d /home/rhevm_guest/ && echo presence || echo absence"
            ret, output = self.runcmd(cmd, "check whether guest exist", targetmachine_ip)
            if "presence" in output:
                logger.info("guest has already exist")
            else:
                self.cm_set_cp_image("vdsm")
            cmd = "chmod -R 777 /home/rhevm_guest/"
            if ret == 0:
                logger.info("Success to add excute to /home/rhevm_guest")
            else:
                logger.info("Failed to add excute to /home/rhevm_guest")
            # cmd = "wget -P /tmp/rhevm_guest/xml/ http://%s/projects/sam-virtwho/rhevm_guest/xml/6.4_Server_x86_64.xml"% self.get_vw_cons("data_server")
            cmd = "wget -P /home/rhevm_guest/xml/ %s/%s.xml" % (self.get_vw_cons("data_folder"), vm_name)
            ret, output = self.runcmd(cmd, "wget kvm xml file", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to wget xml img file")
            else:
                raise FailException("Failed to wget xml img file")
            cmd = "sed -i 's/^.*auth_unix_rw/#auth_unix_rw/' /etc/libvirt/libvirtd.conf"
            (ret, output) = self.runcmd(cmd, "Disable auth_unix_rw firstly in libvirtd config file", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to Disable auth_unix_rw")
            else:
                raise FailException("Failed to Disable auth_unix_rw")
            self.vw_restart_libvirtd_vdsm()
            # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
            cmd = "virsh define /home/rhevm_guest/xml/%s.xml" % vm_name
            ret, output = self.runcmd(cmd, "define kvm guest", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to define kvm guest")
            else:
                raise FailException("Failed to define kvm guest")
        else:
            ''' wget kvm img and xml file, define it in execute machine for converting to rhevm '''
            cmd = "test -d /root/rhevm_guest/ && echo presence || echo absence"
            ret, output = self.runcmd(cmd, "check whether guest exist", targetmachine_ip)
            if "presence" in output:
                logger.info("guest has already exist")
            else:
                self.cm_set_cp_image("vdsm")
            cmd = "chmod -R 777 /root/rhevm_guest/"
            if ret == 0:
                logger.info("Success to add excute to /root/rhevm_guest/")
            else:
                logger.info("Failed to add excute to /root/rhevm_guest/")
            # cmd = "wget -P /tmp/rhevm_guest/xml/ http://%s/projects/sam-virtwho/rhevm_guest/xml/6.4_Server_x86_64.xml"% self.get_vw_cons("data_server")
            cmd = "wget -P /root/rhevm_guest/xml/ %s/%s.xml" % (self.get_vw_cons("data_folder"), vm_name)
            ret, output = self.runcmd(cmd, "wget kvm xml file", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to wget xml img file")
            else:
                raise FailException("Failed to wget xml img file")
            cmd = "sed -i 's/home/root/g' /root/rhevm_guest/xml/%s.xml" % vm_name
            ret, output = self.runcmd(cmd, "update /root folder to /home", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to update /root folder to /home")
            else:
                raise FailException("Failed to update /root folder to /home")
            cmd = "sed -i 's/^.*auth_unix_rw/#auth_unix_rw/' /etc/libvirt/libvirtd.conf"
            (ret, output) = self.runcmd(cmd, "Disable auth_unix_rw firstly in libvirtd config file", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to Disable auth_unix_rw")
            else:
                raise FailException("Failed to Disable auth_unix_rw")
            self.vw_restart_libvirtd_vdsm()
            # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
            cmd = "virsh define /root/rhevm_guest/xml/%s.xml" % vm_name
            ret, output = self.runcmd(cmd, "define kvm guest", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to define kvm guest")
            else:
                raise FailException("Failed to define kvm guest")

    def rhevm_undefine_guest(self, vm_name, targetmachine_ip=""):
        # undefine guest
        cmd = "virsh undefine %s" % vm_name
        ret, output = self.runcmd(cmd, "undefine kvm guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to undefine kvm guest")
        else:
            raise FailException("Failed to undefine kvm guest")

    def create_storage_pool(self, targetmachine_ip=""):
    # Create_storage_pool
        ''' wget autotest_pool.xml '''
        cmd = "wget -P /tmp/ %s/autotest_pool.xml" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget autotest_pool.xml")
        else:
            raise FailException("Failed to wget autotest_pool.xml")
        # check whether pool exist, if yes, destroy it
        cmd = "virsh pool-list"
        ret, output = self.runcmd(cmd, "check whether autotest_pool exist", targetmachine_ip)
        if ret == 0 and "autotest_pool" in output:
            logger.info("autotest_pool exist")
            cmd = "virsh pool-destroy autotest_pool"
            ret, output = self.runcmd(cmd, "destroy autotest_pool", targetmachine_ip)
            if ret == 0 and "autotest_pool destroyed" in output:
                logger.info("Succeeded to destroy autotest_pool")
            else:
                raise FailException("Failed to destroy autotest_pool")
        if "RHEVH" in get_exported_param("RHEL_COMPOSE"):
            cmd = "sed -i 's/home/root/g'  `grep 'home' -rl /tmp/autotest_pool.xml`"
            ret, output = self.runcmd(cmd, "update /home/ to /root", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to update /home/ to /root")
            else:
                raise FailException("Failed to update /home/ to /root")
        cmd = "virsh pool-create /tmp/autotest_pool.xml"
        ret, output = self.runcmd(cmd, "import vm to rhevm", targetmachine_ip)
        if ret == 0 and "autotest_pool created" in output:
            logger.info("Succeeded to create autotest_pool")
        else:
            raise FailException("Failed to create autotest_pool")
        if self.os_serial == "6":
            cmd = "virsh pool-define /tmp/autotest_pool.xml"
            ret, output = self.runcmd(cmd, "define storage pool", targetmachine_ip)
            if ret == 0 and "autotest_pool defined" in output:
                logger.info("Succeeded to define storage pool")
            else:
                raise FailException("Failed to define storage pool")
            cmd = "virsh pool-list"
            ret, output = self.runcmd(cmd, "list storage pool", targetmachine_ip)
            if ret == 0 and "autotest_pool" in output and "active" in output:
                logger.info("Succeeded to list storage pool")
            else:
                cmd = "virsh pool-start autotest_pool"
                ret, output = self.runcmd(cmd, "start storage pool", targetmachine_ip)
                if ret == 0 and "autotest_pool started" in output:
                    logger.info("Succeeded to start storage pool")
                else:
                    raise FailException("Failed to start storage pool")

    def convert_guest_to_nfs(self, origin_machine_ip, nfs_server, NFS_export_dir, vm_hostname, targetmachine_ip=""):
        # convert_guest_to_nfs with v2v tool
        cmd = "sed -i 's/^.*auth_unix_rw/auth_unix_rw/' /etc/libvirt/libvirtd.conf"
        (ret, output) = self.runcmd(cmd, "Enable auth_unix_rw firstly in libvirtd config file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable auth_unix_rw")
        else:
            raise FailException("Failed to enable auth_unix_rw")
        self.vw_restart_libvirtd_vdsm(targetmachine_ip)
        time.sleep(30)
#         v2v import vm from remote libvirt to rhevm
#         cmd = "virt-v2v -i libvirt -ic qemu+ssh://root@%s/system -o rhev -os %s:%s --network rhevm %s" % (origin_machine_ip, nfs_server, NFS_export_dir, vm_hostname)
#         ret, output = self.runcmd_interact(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip, showlogger=False)
#         v2v import vm from local libvirt to rhevm
        cmd = "export LIBGUESTFS_BACKEND=direct && virt-v2v -o rhev -os  %s:%s --network rhevm %s" % (nfs_server, NFS_export_dir, vm_hostname)
        (ret, output) = self.runcmd(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip)
        if ret == 0 and ("100%" in output or "configured with virtio drivers" in output):
            logger.info("Succeeded to convert_guest_to_nfs with v2v tool")
            time.sleep(10)
        else:
            raise FailException("Failed to convert_guest_to_nfs with v2v tool")

    def get_domain_id(self, storagedomain_name, targetmachine_ip):
        # get storagedomain id 
        cmd = "%s -c -E 'list storagedomains '" % self.rhevm_shell
        ret, output = self.runcmd(cmd, "list storagedomains in rhevm", targetmachine_ip)
        if ret == 0 and storagedomain_name in output:
            logger.info("Succeeded to list storagedomains %s in rhevm" % storagedomain_name)
            storagedomain_id = self.get_key_rhevm(output, "id", "name", storagedomain_name, targetmachine_ip)
            logger.info("%s id is %s" % (storagedomain_name, storagedomain_id))
            return storagedomain_id
        else :
            raise FailException("Failed to list storagedomains %s in rhevm" % storagedomain_name)

    def import_vm_to_rhevm(self, guest_name, nfs_dir_for_storage_id, nfs_dir_for_export_id, targetmachine_ip):
        # import guest to rhevm
        # cmd = "rhevm-shell -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s' " % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
        cmd = "%s -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-id %s' " % (self.rhevm_shell, guest_name, nfs_dir_for_export_id, nfs_dir_for_storage_id)
        ret, output = self.runcmd(cmd, "import guest %s in rhevm" % guest_name, targetmachine_ip)
        self.rhevm_check_vm_status(guest_name, "down", targetmachine_ip)

    def get_rhevm_shell(self, targetmachine_ip=""):
#         return "ovirt-shell"
        rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
        if "rhevm-4" in rhevm_version:
            logger.info("It is rhevm4.X build, need to user ovirt-shell")
            return "ovirt-shell"
        else:
            logger.info("It is rhevm3.X build, need to user rhevm-shell")
            return "rhevm-shell"

    def add_vm_to_rhevm(self, rhevm_vm_name, vm_name, host_name, nfsserver_ip, nfs_dir_for_export, targetmachine_ip):
#         rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
#         shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        data_storage_id = self.get_domain_id("data_storage", targetmachine_ip)
        export_storage_id = self.get_domain_id("export_storage", targetmachine_ip)
        # Add defined guest to rhevm
        cmd = "%s -c -E ' list vms'" % self.rhevm_shell
        ret, output = self.runcmd(cmd, "check vm exist or not before import vm", targetmachine_ip, showlogger=True)
#         if ret == 0 :
        if vm_name in output:
            logger.info("Succeeded to list vm %s ,it has been imported" % vm_name)
#             break
        else:        
            while True:
                cmd = "%s -c -E ' list vms --name %s'" % (self.rhevm_shell, rhevm_vm_name)
                ret, output = self.runcmd(cmd, "check vm exist or not before import vm", targetmachine_ip, showlogger=True)
                if ret == 0 :
                    if rhevm_vm_name in output and "virt-v2v" in output:
                        logger.info("Succeeded to list vm %s before import vm" % rhevm_vm_name)
                        break
                    else:
                        self.rhevm_define_guest(rhevm_vm_name, nfsserver_ip)
                        self.create_storage_pool(nfsserver_ip)
                        if "RHEVH" not in get_exported_param("RHEL_COMPOSE"): 
                            self.install_virtV2V(nfsserver_ip)
                        self.convert_guest_to_nfs(nfsserver_ip, nfsserver_ip, nfs_dir_for_export, rhevm_vm_name, nfsserver_ip)
                        self.rhevm_undefine_guest(rhevm_vm_name, nfsserver_ip)
                        self.import_vm_to_rhevm(rhevm_vm_name, data_storage_id, export_storage_id, targetmachine_ip)
            self.update_vm_to_host(rhevm_vm_name, host_name, targetmachine_ip)
            self.update_vm_name(rhevm_vm_name, vm_name, targetmachine_ip)
#             self.import_vm_to_rhevm(rhevm_vm_name, data_storage_id, export_storage_id, targetmachine_ip)
#         else:
#             raise FailException("Failed to list vm in rhevm")

    def rhevm_check_vm_key_value(self, vm_name, vm_key, vm_value, targetmachine_ip):
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        cmd = "%s -c -E '%s'" % (self.rhevm_shell, get_vm_cmd)
        for item in range(30):
            ret, output = self.runcmd(cmd, "list vms in rhevm", targetmachine_ip, showlogger=False)
            if ret == 0:
                value = self.get_key_rhevm(output, vm_key, "name", vm_name, targetmachine_ip).strip()
                if vm_value == "up" and vm_key == "status-state":
                    # if status.find(vm_status) >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
                    if value == vm_value and output.find("guest_info-ips-ip-address") > 0:
                        logger.info("Succeeded to check vm %s is %s status in rhevm" % (vm_name, vm_value))
                        break
                    else :
                        logger.info("vm %s status-state is still %s" % (vm_name, vm_value))
                    time.sleep(30)
                else:
                    if value == vm_value:
                    # if status.find(vm_status) >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
                        logger.info("Succeeded to check vm %s %s is %s in rhevm" % (vm_name, vm_key, vm_value))
                        break
                    else :
                        logger.info("vm %s %s is still %s" % (vm_name, vm_key, vm_value))
                        time.sleep(30)
            else:
                raise FailException("Failed to run list vm %s via command: %s" % (vm_name, cmd))
        else:
            if vm_value == "up" and vm_key == "status-state":
                # if failed to get rhevm guest ip, stop it and start it again
                self.rhevm_stop_vm(vm_name, targetmachine_ip)
                self.rhevm_start_vm(vm_name, targetmachine_ip)

    def rhevm_check_vm_status(self, vm_name, vm_status, targetmachine_ip):
        self.rhevm_check_vm_key_value(vm_name, "status-state", vm_status, targetmachine_ip)

    def rhevm_start_vm(self, vm_name, targetmachine_ip):
        # Start VM on RHEVM
        cmd = "%s -c -E 'action vm %s start'" % (self.rhevm_shell, vm_name)
        for item in range(10):
            ret, output = self.runcmd(cmd, "start vm on rhevm", targetmachine_ip, showlogger=False)
            if "Storage Domain cannot be accessed" in output:
                time.sleep(30)
                continue
            elif ret == 0:
                logger.info("Success to run start command %s" % cmd)
                break
        else:
            raise FailException("Failed to start vm %s on rhevm" % vm_name)
        self.rhevm_check_vm_status(vm_name, "up", targetmachine_ip)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def rhevm_stop_vm(self, vm_name, targetmachine_ip):
        # Stop VM on RHEVM
        cmd = "%s -c -E 'action vm \"%s\" stop'" % (self.rhevm_shell, vm_name)
        ret, output = self.runcmd(cmd, "stop vm on rhevm", targetmachine_ip)
        if ret == 0:
            logger.info("Success to run stop command %s" % cmd)
        else:
            raise FailException("Failed to stop vm %s on rhevm" % vm_name)
        self.rhevm_check_vm_status(vm_name, "down", targetmachine_ip)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def rhevm_pause_vm(self, vm_name, targetmachine_ip):
        # Pause VM on RHEVM
        cmd = "%s -c -E 'action vm \"%s\" suspend'" % (self.rhevm_shell, vm_name)
        for item in range(10):
            ret, output = self.runcmd(cmd, "suspend vm on rhevm", targetmachine_ip)
            if "Storage Domain cannot be accessed" in output:
                time.sleep(30)
            elif ret == 0:
                logger.info("Success to run suspend command ")
                break
        else:
            raise FailException("Failed to suspend vm %s on rhevm" % vm_name)
        self.rhevm_check_vm_status(vm_name, "suspended", targetmachine_ip)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def rhevm_migrate_vm(self, vm_name, dest_ip, dest_host_id, targetmachine_ip):
        # Migrate VM on RHEVM
        cmd = "%s -c -E 'action vm \"%s\" migrate --host-name \"%s\"'" % (self.rhevm_shell, vm_name, dest_ip)
        ret, output = self.runcmd(cmd, "migrate vm on rhevm", targetmachine_ip)
        if ret == 0 and "complete" in output:
            self.rhevm_check_vm_key_value(vm_name, "host-id", dest_host_id, targetmachine_ip)
            logger.info("Succeeded to migrate vm %s in rhevm to %s" % (vm_name, dest_host_id))
        else:
            raise FailException("Failed to run migrate vm %s in rhevm" % vm_name)
        # since virt-who changed to wait 3600 to refresh, so for xen/rhevm, restart virt-who to take effect immediately
        self.runcmd_service("restart_virtwho")

    def rhevm_get_guest_ip(self, vm_name, targetmachine_ip):
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Get guest ip
        cmd = "%s -c -E '%s'" % (self.rhevm_shell, get_vm_cmd)
        ret, output = self.runcmd(cmd, "list vms in rhevm", targetmachine_ip, showlogger=True)
        if ret == 0:
            guestip = self.get_key_rhevm(output, "guest_info-ips-ip-address", "name", vm_name, targetmachine_ip)
            hostuuid = self.get_key_rhevm(output, "host-id", "name", vm_name, targetmachine_ip)
            if guestip is not "":
                logger.info("vm %s ipaddress is %s" % (vm_name, guestip))
                return (guestip, hostuuid)
            else:
                logger.error("Failed to gest the vm %s ipaddress" % vm_name)
        else:
            raise FailException("Failed to list VM %s" % vm_name) 

    def vdsm_get_vm_uuid(self, vm_name, targetmachine_ip="", showlogger=False):
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Get the guest uuid
        cmd = "%s -c -E '%s'" % (self.rhevm_shell, get_vm_cmd)
        ret, output = self.runcmd(cmd, "list VMS in rhevm", targetmachine_ip, showlogger=showlogger)
        if ret == 0:
            guestid = self.get_key_rhevm(output, "id", "name", vm_name, targetmachine_ip)
            if guestid is not "":
                logger.info("Succeeded to get guest %s id is %s" % (vm_name, guestid))
                return guestid
            else:
                logger.error("Failed to get guest %s id is %s" % (vm_name, guestid))
        else:
            raise FailException("Failed to list VM %s" % vm_name)

    def rhevm_parse_output(self, output):
        datalines = output.splitlines()
        output_dict = {}
        for line in datalines:
            if ":" in line:
                keyitem, valueitem = line.split(":")
                output_dict[keyitem.strip()] = valueitem.strip()
        return output_dict

    def vdsm_get_vm_nw(self, vm_name, targetmachine_ip=""):
        # get vm network name
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'list nics --vm-identifier %s'" % (self.rhevm_shell, vm_id)
        ret, output = self.runcmd(cmd, "List all nics of guest in rhevm", targetmachine_ip)
        return self.rhevm_parse_output(output)["name"]

    def vdsm_check_vm_nw(self, vm_name, nw_name, targetmachine_ip=""):
        # remove vm original network
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'list nics --vm-identifier %s'" % (self.rhevm_shell, vm_id)
        ret, output = self.runcmd(cmd, "List all nics of guest in rhevm", targetmachine_ip)
        if ret == 0 and nw_name in output:
            logger.info("Success to list %s in %s" % (nw_name, vm_name))
            return True
        else:
            logger.info("Failed to list %s in %s, maybe it has been deleted" % (nw_name, vm_name))
            return False

    def vdsm_rm_vm_nw(self, vm_name, nw_name, targetmachine_ip=""):
        # remove vm original network
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'remove nic %s --vm-identifier %s'" % (self.rhevm_shell, nw_name, vm_id)
        ret, output = self.runcmd(cmd, "Remove vm's network in rhevm", targetmachine_ip)
        if ret == 0 and "complete" in output:
            logger.info("Success to remove vm %s network %s" % (vm_name, nw_name))
        else:
            raise FailException("Failed to remove vm %s network %s" % (vm_name, nw_name))

    def vdsm_add_vm_nw(self, vm_name, targetmachine_ip=""):
        # add vm new network
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'add nic --vm-identifier %s --name ovirtmgmt --network-name ovirtmgmt'" % (self.rhevm_shell, vm_id)
        ret, output = self.runcmd(cmd, "Add vm's new network in rhevm", targetmachine_ip)
        if ret == 0 and "ovirtmgmt" in output:
            logger.info("Success to add vm %s network" % vm_name)
        else:
            raise FailException("Failed to to add vm %s network" % vm_name)

    def get_host_uuid_on_rhevm(self, host_name, targetmachine_ip=""):
        # Get the host uuid
        cmd = "%s -c -E 'show host %s'" % (self.rhevm_shell, host_name)
        ret, output = self.runcmd(cmd, "list host in rhevm", targetmachine_ip)
        if ret == 0:
            hostid = self.get_key_rhevm(output, "id", "name", host_name, targetmachine_ip)
            if hostid is not "":
                logger.info("Succeeded to get host %s id is %s" % (host_name, hostid))
                return hostid
            else:
                logger.error("Failed to get guest %s id is %s" % (host_name, hostid))
        else:
            raise FailException("Failed to list HOST %s" % host_name) 

    def get_host_hwuuid_on_rhevm(self, host_name, targetmachine_ip=""):
        # Get the host hwuuid
        cmd = "%s -c -E 'show host %s'" % (self.rhevm_shell, host_name)
        ret, output = self.runcmd(cmd, "list host in rhevm", targetmachine_ip)
        if ret == 0:
            hostid = self.get_key_rhevm(output, "hardware_information-uuid", "name", host_name, targetmachine_ip)
            if hostid is not "":
                logger.info("Succeeded to get host %s hardware_information-uuid is %s" % (host_name, hostid))
                return hostid
            else:
                logger.error("Failed to get guest %s hardware_information-uuid is %s" % (host_name, hostid))
        else:
            raise FailException("Failed to list HOST %s" % host_name) 

    def vw_restart_vdsm(self, targetmachine_ip=""):
        # restart vdsmd service
        cmd = "service vdsmd restart"
        ret, output = self.runcmd(cmd, "restart vdsmd", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart vdsmd service")
        else:
            raise FailException("Test Failed - Failed to restart vdsmd")

    def vw_restart_vdsm_new(self, targetmachine_ip=""):
        if self.check_systemctl_service("vdsmd", targetmachine_ip):
            cmd = "systemctl restart vdsmd service; sleep 60"
            ret, output = self.runcmd(cmd, "restart vdsmd service by systemctl", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart vdsmd")
            else:
                raise FailException("Test Failed - Failed to restart vdsmd")
        else:
            cmd = "service vdsmd restart; sleep 60"
            ret, output = self.runcmd(cmd, "restart vdsmd by service", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart vdsmd")
            else:
                raise FailException("Test Failed - Failed to restart vdsmd")

    def vw_check_vdsm_status(self, targetmachine_ip=""):
        # check the vdsmd status
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "systemctl status vdsmd; sleep 15"
            ret, output = self.runcmd(cmd, "vdsmd status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check vdsmd is running")
            else:
                raise FailException("Test Failed - Failed to check vdsmd is running")
        else:
            cmd = "service vdsmd status; sleep 15"
            ret, output = self.runcmd(cmd, "vdsmd status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check vdsmd is running")
            else:
                raise FailException("Test Failed - Failed to check vdsmd is running")

    def update_rhel_vdsm_configure(self, interval_value, targetmachine_ip=""):
        # update virt-who configure file to vdsm mode /etc/sysconfig/virt-who
        self.update_config_to_default(targetmachine_ip)
        cmd = "sed -i -e 's/^.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/^.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/g' -e 's/^.*VIRTWHO_VDSM=.*/VIRTWHO_VDSM=1/g' /etc/sysconfig/virt-who" % interval_value
        ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file")
        else:
            raise FailException("Failed to update virt-who configure file")

    def update_rhel_rhevm_configure(self, rhevm_interval, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password, debug=1, targetmachine_ip=""):
        # update virt-who configure file /etc/sysconfig/virt-who for enable VIRTWHO_RHEVM
        self.update_config_to_default(targetmachine_ip)
        cmd = "sed -i -e 's/.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_RHEVM=.*/VIRTWHO_RHEVM=1/g' -e 's/#VIRTWHO_RHEVM_OWNER=.*/VIRTWHO_RHEVM_OWNER=%s/g' -e 's/#VIRTWHO_RHEVM_ENV=.*/VIRTWHO_RHEVM_ENV=%s/g' -e 's/#VIRTWHO_RHEVM_SERVER=.*/VIRTWHO_RHEVM_SERVER=%s/g' -e 's/#VIRTWHO_RHEVM_USERNAME=.*/VIRTWHO_RHEVM_USERNAME=%s/g' -e 's/#VIRTWHO_RHEVM_PASSWORD=.*/VIRTWHO_RHEVM_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (rhevm_interval, debug, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
        ret, output = self.runcmd(cmd, "updating virt-who configure file for enable VIRTWHO_RHEVM", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_RHEVM")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_RHEVM")

    def set_rhevm_conf(self, debug=1, targetmachine_ip=""):
        # configure rhevm mode in /etc/sysconfig/virt-who
        rhevm_ip = get_exported_param("RHEVM_IP")
        rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
        self.rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
        if "rhevm-4"in self.rhevm_version:
            rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443" + "\/ovirt-engine\/"
        else:
            rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/.*VIRTWHO_RHEVM=.*/VIRTWHO_RHEVM=1/g' -e 's/.*VIRTWHO_RHEVM_OWNER=.*/VIRTWHO_RHEVM_OWNER=%s/g' -e 's/.*VIRTWHO_RHEVM_ENV=.*/VIRTWHO_RHEVM_ENV=%s/g' -e 's/.*VIRTWHO_RHEVM_SERVER=.*/VIRTWHO_RHEVM_SERVER=%s/g' -e 's/.*VIRTWHO_RHEVM_USERNAME=.*/VIRTWHO_RHEVM_USERNAME=%s/g' -e 's/.*VIRTWHO_RHEVM_PASSWORD=.*/VIRTWHO_RHEVM_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
        ret, output = self.runcmd(cmd, "Setting rhevm mode in /etc/sysconfig/virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set rhevm mode in /etc/sysconfig/virt-who")
        else:
            raise FailException("Test Failed - Failed  to set rhevm mode in /etc/sysconfig/virt-who")

    def rhevm_change_guest_name(self, guest_name, targetmachine_ip=""):
        self.rhevm_start_vm(guest_name, targetmachine_ip)
        while True:
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, targetmachine_ip)
            try:
#                 self.cm_change_hostname(guestip)
                self.cm_change_static_guestname(guestip)
                logger.info("Succeeded to change rhevm guest hostname")
                break
            except Exception, e:
                logger.info("Failed to change rhevm guest hostname, failed to connect to guest %s" % guest_name)
                network_card = self.vdsm_get_vm_nw(guest_name, targetmachine_ip)
                self.rhevm_stop_vm(guest_name, targetmachine_ip)
                self.vdsm_rm_vm_nw(guest_name, network_card, targetmachine_ip)
                self.vdsm_add_vm_nw(guest_name, targetmachine_ip)
                self.rhevm_start_vm(guest_name, targetmachine_ip)
        self.rhevm_stop_vm(guest_name, targetmachine_ip)

