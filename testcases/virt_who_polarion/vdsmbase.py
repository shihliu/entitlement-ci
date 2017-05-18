from utils import *
from testcases.virt_who_polarion.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class VDSMBase(VIRTWHOBase):
    def rhel_rhevm_sys_setup(self, targetmachine_ip=""):
        # System setup for virt-who on two hosts
        self.sys_setup(targetmachine_ip)
        RHEVM_IP = get_exported_param("RHEVM_IP")
        RHEL_RHEVM_GUEST_NAME = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
        RHEVM_HOST1_NAME, RHEVM_HOST2_NAME = self.get_hostname(), self.get_hostname(get_exported_param("REMOTE_IP_2"))
        NFSserver_ip = get_exported_param("REMOTE_IP")
        nfs_dir_for_storage = self.get_vw_cons("NFS_DIR_FOR_storage")
        nfs_dir_for_export = self.get_vw_cons("NFS_DIR_FOR_export")
        rhel_compose = get_exported_param("RHEL_COMPOSE")
        rhevm_version = self.cm_get_rpm_version("rhevm", RHEVM_IP)

        # System setup for RHEL+RHEVM(VDSM/RHEVM) testing env on two hosts
        self.config_vdsm_env_setup(rhel_compose, rhevm_version)
        self.config_vdsm_env_setup(rhel_compose, rhevm_version, get_exported_param("REMOTE_IP_2"))
        self.install_vdsm_package(rhel_compose)
        self.install_vdsm_package(rhel_compose, get_exported_param("REMOTE_IP_2"))
        # Configure env on rhevm(add two host,storage,guest)
        self.conf_rhevm_shellrc(RHEVM_IP)
        self.update_cluster_cpu("Default", "Intel Conroe Family", RHEVM_IP)
        # Configure cluster and dc to 3.5 
        if "rhevm-3.6" in rhevm_version:
            self.update_dc_compa_version("Default", "5", "3", RHEVM_IP)
            self.update_cluster_compa_version("Default", "5", "3", RHEVM_IP)
        self.update_cluster_cpu("Default", "Intel Penryn Family", RHEVM_IP)
        self.rhevm_add_host(RHEVM_HOST1_NAME, get_exported_param("REMOTE_IP"), RHEVM_IP)
#         self.rhevm_add_host(RHEVM_HOST2_NAME, get_exported_param("REMOTE_IP_2"), RHEVM_IP)
        self.add_storagedomain_to_rhevm("data_storage", RHEVM_HOST1_NAME, "data", "v3", NFSserver_ip, nfs_dir_for_storage, RHEVM_IP)
        self.add_storagedomain_to_rhevm("export_storage", RHEVM_HOST1_NAME, "export", "v1", NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
        self.add_vm_to_rhevm(RHEL_RHEVM_GUEST_NAME, NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
        self.update_vm_to_host(RHEL_RHEVM_GUEST_NAME, RHEVM_HOST1_NAME, RHEVM_IP)
        # Add network bridge "ovirtmgmt"
#         if "rhevm-3.6" in rhevm_version and "RHEL-6.8" in rhel_compose:
        if "rhevm-3.5" not in rhevm_version:
            if self.vdsm_check_vm_nw(RHEL_RHEVM_GUEST_NAME, "eth0", RHEVM_IP) is True:
                self.vdsm_rm_vm_nw(RHEL_RHEVM_GUEST_NAME, "eth0", RHEVM_IP)
                self.vdsm_add_vm_nw(RHEL_RHEVM_GUEST_NAME, RHEVM_IP)
        # change target guest host name, or else satellite testing will fail due to same name
        self.rhevm_change_guest_name(RHEL_RHEVM_GUEST_NAME, RHEVM_IP)

    def rhel_rhevm_static_sys_setup(self, targetmachine_ip=""):
        RHEVM_IP = get_exported_param("RHEVM_IP")
        RHEVM_HOST1_IP = get_exported_param("RHEVM_HOST1_IP")
        RHEVM_HOST2_IP = get_exported_param("RHEVM_HOST2_IP")  
        RHEL_RHEVM_GUEST_NAME = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
        RHEVM_HOST1_NAME = self.get_hostname(RHEVM_HOST1_IP)
        RHEVM_HOST2_NAME = self.get_hostname(RHEVM_HOST2_IP)
        NFSserver_ip = get_exported_param("RHEVM_HOST1_IP")
        nfs_dir_for_storage = self.get_vw_cons("NFS_DIR_FOR_storage")
        nfs_dir_for_export = self.get_vw_cons("NFS_DIR_FOR_export")
        rhel_compose = get_exported_param("RHEL_HOST_COMPOSE")
        rhevm_version = self.cm_get_rpm_version("rhevm", RHEVM_IP)

        # System setup for RHEL+RHEVM(VDSM/RHEVM) testing env on two hosts
        self.config_vdsm_env_setup(rhel_compose, rhevm_version, RHEVM_HOST1_IP)
        self.config_vdsm_env_setup(rhel_compose, rhevm_version, RHEVM_HOST2_IP)
        # System setup for virt-who on two hosts
        self.sys_setup(RHEVM_HOST1_IP)
        self.sys_setup(get_exported_param("REMOTE_IP_2"))
        # Configure env on rhevm(add two host,storage,guest)
        self.conf_rhevm_shellrc(RHEVM_IP)
        self.update_cluster_cpu("Default", "Intel Conroe Family", RHEVM_IP)
        # Configure cluster and dc to 3.5 
        if "rhevm-3.6" in rhevm_version:
            self.update_dc_compa_version("Default", "5", "3", RHEVM_IP)
            self.update_cluster_compa_version("Default", "5", "3", RHEVM_IP)
#         self.update_cluster_cpu("Default", "Intel Penryn Family", RHEVM_IP)
        self.rhevm_add_host(RHEVM_HOST1_NAME, get_exported_param("RHEVM_HOST1_IP"), RHEVM_IP)
        self.rhevm_add_host(RHEVM_HOST2_NAME, get_exported_param("RHEVM_HOST2_IP"), RHEVM_IP)
        self.clean_nfs_env(RHEVM_HOST1_IP)
        self.add_storagedomain_to_rhevm("data_storage", RHEVM_HOST1_NAME, "data", "v3", NFSserver_ip, nfs_dir_for_storage, RHEVM_IP)
        self.add_storagedomain_to_rhevm("export_storage", RHEVM_HOST1_NAME, "export", "v1", NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
        self.add_vm_to_rhevm(RHEL_RHEVM_GUEST_NAME, NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
        self.update_vm_to_host(RHEL_RHEVM_GUEST_NAME, RHEVM_HOST1_NAME, RHEVM_IP)
        # Add network bridge "ovirtmgmt"
#         if "rhevm-3.6" in rhevm_version and "RHEL-6.8" in rhel_compose:
        if "rhevm-3.5" not in rhevm_version:
            if self.vdsm_check_vm_nw(RHEL_RHEVM_GUEST_NAME, "eth0", RHEVM_IP) is True:
                self.vdsm_rm_vm_nw(RHEL_RHEVM_GUEST_NAME, "eth0", RHEVM_IP)
                self.vdsm_add_vm_nw(RHEL_RHEVM_GUEST_NAME, RHEVM_IP)
        # change target guest host name, or else satellite testing will fail due to same name
        self.rhevm_change_guest_name(RHEL_RHEVM_GUEST_NAME, RHEVM_IP)

    def rhel_vdsm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
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

    def rhel_rhevm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
        RHEVM_IP = get_exported_param("RHEVM_IP")
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who to rhevm mode in /etc/sysconfig/virt-who
        self.update_config_to_default()
        self.set_rhevm_conf()
        self.service_command("restart_virtwho")

    def configure_rhel_host_bridge(self, targetmachine_ip=""):
    # Configure rhevm bridge on RHEL host
        network_dev = ""
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

    def get_rhevm_shell(self, targetmachine_ip=""):
#         return "ovirt-shell"
        rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
        if "rhevm-4" in rhevm_version:
            logger.info("It is rhevm4.X build, need to user ovirt-shell")
            return "ovirt-shell"
        else:
            logger.info("It is rhevm3.X build, need to user rhevm-shell")
            return "rhevm-shell"

    def get_vm_cmd(self, vm_name, targetmachine_ip=""):
#         return "list vms %s --show-all" % vm_name
        rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
        if "rhevm-4" in rhevm_version:
            logger.info("It is rhevm4.X build, need to use 'list vms'")
            return "list vms %s --show-all" % vm_name
        else:
            logger.info("It is rhevm3.X build, need to use 'show vm'")
            return "show vm %s" % vm_name

    def config_vdsm_env_setup(self, rhel_compose, rhevm_version, targetmachine_ip=""):
    # System setup for RHEL+RHEVM testing env
        if not self.sub_isregistered(targetmachine_ip):
            self.sub_register("qa@redhat.com", "uuV4gQrtG7sfMP3q", targetmachine_ip)
            self.sub_auto_subscribe(targetmachine_ip)
        self.cm_install_basetool(targetmachine_ip)
        self.set_rhevm_repo_file(rhel_compose, rhevm_version, targetmachine_ip)
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
#         self.stop_firewall(targetmachine_ip)

    def install_vdsm_package(self, rhel_compose, targetmachine_ip=""):
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
        rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
        # Config the env to login to rhevm_rhell
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        if "rhevm-4" in rhevm_version:
            cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s/ovirt-engine/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.ovirtshellrc" % tagetmachine_hostname
        else:
            cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s:443/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.rhevmshellrc" % tagetmachine_hostname
        ret, output = self.runcmd(cmd, "config rhevm_shell env on rhevm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to config rhevm_shell env on rhevm in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to config rhevm_shell env on rhevm in %s" % self.get_hg_info(targetmachine_ip))

    def update_cluster_cpu(self, cluster_name, cpu_type, targetmachine_ip):
        rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Update cluster cpu 
        # cmd = "rhevm-shell -c -E \"update cluster %s --cpu-id '%s' \"" % (cluster_name, cpu_type)
        if "rhevm-4" in rhevm_version:
            cmd = "%s -c -E \"update cluster %s --name '%s' \"" % (shell_cmd, cluster_name, cpu_type)
        else:
            cmd = "%s -c -E \"update cluster %s --cpu-id '%s' \"" % (shell_cmd, cluster_name, cpu_type)
        ret, output = self.runcmd(cmd, "update cluster cpu", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update cluster %s cpu to %s" % (cluster_name, cpu_type))
        else:
            raise FailException("Failed to update cluster %s cpu to %s" % (cluster_name, cpu_type))

    def update_cluster_compa_version(self, cluster_name, min_version, major_version, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Update cluster Compatibility Version 
        cmd = "%s -c -E \"update cluster %s --version-minor %s --version-major %s \"" % (shell_cmd, cluster_name, min_version, major_version)
        ret, output = self.runcmd(cmd, "update cluster's Compatibility Version", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update cluster %s Compatibility Version to %s.%s" % (cluster_name, major_version, min_version))
        else:
            raise FailException("Failed to update cluster %s Compatibility Version to %s.%s" % (cluster_name, major_version, min_version))

    def update_dc_compa_version(self, dc_name, min_version, major_version, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Update datacenter Compatibility Version 
        cmd = "%s -c -E \"update datacenter %s --version-minor %s --version-major %s \"" % (shell_cmd, dc_name, min_version, major_version)
        ret, output = self.runcmd(cmd, "update Compatibility Version", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update datacenter's %s Compatibility Version to %s.%s" % (dc_name, major_version, min_version))
        else:
            raise FailException("Failed to update datacenter's %s Compatibility Version to %s.%s" % (dc_name, major_version, min_version))

    def vdsm_get_dc_id(self, targetmachine_ip=""):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Get datacenter's id
        cmd = "%s -c -E 'list datacenters'" % shell_cmd
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
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        cmd = " %s -c -E 'list hosts --show-all'" % shell_cmd
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
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        cmd = "%s -c -E 'list hosts --show-all'" % shell_cmd
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
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
#         self.cm_update_system(host_ip)
        if not self.rhevm_check_host_exist(host_name, targetmachine_ip):
            cmd = "%s -c -E 'add host --name \"%s\" --address \"%s\" --root_password red2015'" % (shell_cmd, host_name, host_ip)
            ret, output = self.runcmd(cmd, "add host to rhevm", targetmachine_ip)
            if ret == 0:
                self.rhevm_check_host_status(host_name, "up", targetmachine_ip)
            else:
                if "rhevm-4" not in rhevm_version:
                    self.rhevm_commitnetconfig_host(host_name, targetmachine_ip)
                    self.rhevm_active_host(host_name, targetmachine_ip)
                    self.rhevm_check_host_status(host_name, "up", targetmachine_ip)
                    return True
                raise FailException("Failed to add host %s to rhevm" % host_name)

    def rhevm_mantenance_host(self, host_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Maintenance Host on RHEVM
        cmd = "%s -c -E 'action host \"%s\" deactivate'" % (shell_cmd, host_name)
        ret, output = self.runcmd(cmd, "Maintenance host on rhevm", targetmachine_ip)
        if ret == 0:
            self.rhevm_check_host_status(host_name, "maintenance", targetmachine_ip)
        else:
            raise FailException("Failed to maintenance host %s on rhevm" % host_name)

    def rhevm_commitnetconfig_host(self, host_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Maintenance Host on RHEVM
        cmd = "%s -c -E 'action host \"%s\" commitnetconfig'" % (shell_cmd, host_name)
        ret, output = self.runcmd(cmd, "commitnetconfig host on rhevm", targetmachine_ip)
#         if ret == 0:
#             self.rhevm_check_host_status(host_name, "maintenance", targetmachine_ip)
#         else:
#             raise FailException("Failed to commitnetconfig host %s on rhevm" % host_name)

    def rhevm_delete_host(self, host_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Delete Host on RHEVM
        cmd = "%s -c -E 'action host \"%s\" delete'" % (shell_cmd, host_name)
        ret, output = self.runcmd(cmd, "Maintenance host on rhevm", targetmachine_ip)
        if ret == 0:
            self.rhevm_check_host_status(host_name, "deleted", targetmachine_ip)
        else:
            raise FailException("Failed to delete host %s on rhevm" % host_name)

    def rhevm_active_host(self, host_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Active Host on RHEVM
        cmd = "%s -c -E 'action host \"%s\" activate'" % (shell_cmd, host_name)
        ret, output = self.runcmd(cmd, "Active host on rhevm", targetmachine_ip)
        if ret == 0:
            self.rhevm_check_host_status(host_name, "up", targetmachine_ip)
        else:
            raise FailException("Failed to active host %s on rhevm" % host_name)

    def update_vm_to_host(self, vm_name, rhevm_host_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Add vm to special host
        cmd = "%s -c -E 'update vm %s --placement_policy-host-name %s'" % (shell_cmd, vm_name, rhevm_host_name)
        ret, output = self.runcmd(cmd, "update vm to special host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update vm %s to host %s" % (vm_name, rhevm_host_name))
        else:
            raise FailException("Failed to update vm %s to host %s" % (vm_name, rhevm_host_name))

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
    # Wait for a while until expect status shown in /tmp/rhevm-result file
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

    def clean_nfs_env(self, targetmachine_ip): 
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
        cmd = "rm -rf /root/data/ /root/export/"
        ret, output = self.runcmd(cmd, "delete storage data", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to delete storage data")
        else:
            logger.info("Failed to delete storage data")
        cmd = "rm -rf /tmp/images_mnt"
        ret, output = self.runcmd(cmd, "delete tmp dat", targetmachine_ip)
        if ret == 0 :
            logger.info("Succeeded to delete tmp dat")
        else:
            logger.info("Failed to delete tmp dat")
                
    def add_storagedomain_to_rhevm(self, storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir, targetmachine_ip): 
        rhevm_version = self.cm_get_rpm_version("rhevm", targetmachine_ip)
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Add storagedomain in rhevm and active it
        cmd = "mkdir %s" % storage_dir
        self.runcmd(cmd, "create storage nfs folder", NFS_server)
        cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (storage_dir.replace('/', '\/'), storage_dir)
        ret, output = self.runcmd(cmd, "set /etc/exports for nfs", NFS_server)
        if ret == 0:
            logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file" % storage_dir)
        else:
            raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file" % storage_dir)
        cmd = "chmod -R 777 %s" % storage_dir
        ret, output = self.runcmd(cmd, "Add x right to storage dir", NFS_server)
        if ret == 0 :
            logger.info("Succeeded to add right to storage dir")
        else:
            raise FailException("Failed to add right to storage dir")
        cmd = "service nfs restart"
        ret, output = self.runcmd(cmd, "restarting nfs service", NFS_server)
        if ret == 0 :
            logger.info("Succeeded to restart service nfs")
        else:
            raise FailException("Failed to restart service nfs")
        # check datastorage domain before add new one
        cmd = "%s -c -E 'list storagedomains' " % shell_cmd
        ret, output = self.runcmd(cmd, "check storagedomain before add new one", targetmachine_ip)
        if ret == 0 and storage_name in output:
            logger.info("storagedomains %s is exist in rhevm" % storage_name)
        else:
            logger.info("storagedomains %s is not exist in rhevm" % storage_name)
            cmd = "%s -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter \"Default\"' " % (shell_cmd, storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
            ret, output = self.runcmd(cmd, "Add storagedomain in rhevm", targetmachine_ip)
            wait_cmd = "%s -c -E 'list storagedomains --show-all'" % shell_cmd
            if self.wait_for_status(wait_cmd, "status-state", "unattached", targetmachine_ip):
                logger.info("Succeeded to add storagedomains %s in rhevm" % storage_name)
            else:
                raise FailException("Failed to add storagedomains %s in rhevm" % storage_name)
            time.sleep(120)
            # Attach datacenter to storagedomain in rhevm
            if "rhevm-3.5" not in rhevm_version:
                dc_attach = self.vdsm_get_dc_id(targetmachine_ip)
            else:
                dc_attach = "Default"
            #  cmd = "rhevm-shell -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"Default\"' " % (storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
            cmd = "%s -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"%s\"' " % (shell_cmd, storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir, dc_attach)
            ret, output = self.runcmd(cmd, "Attaches the storage domain to the Default data center", targetmachine_ip)
            wait_cmd = "%s -c -E 'list storagedomains --show-all'" % shell_cmd
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
    # Install virt-V2V
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
    # Define guest
        ''' wget kvm img and xml file, define it in execute machine for converting to rhevm '''
        cmd = "test -d /home/rhevm_guest/ && echo presence || echo absence"
        ret, output = self.runcmd(cmd, "check whether guest exist", targetmachine_ip)
        if "presence" in output:
            logger.info("guest has already exist")
        else:
            self.cm_set_cp_image("vdsm", targetmachine_ip)
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
        self.vw_restart_libvirtd_vdsm(targetmachine_ip)
        # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "virsh define /home/rhevm_guest/xml/%s.xml" % vm_name
        ret, output = self.runcmd(cmd, "define kvm guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to define kvm guest")
        else:
            raise FailException("Failed to define kvm guest")

    def rhevm_undefine_guest(self, vm_name, targetmachine_ip=""):
    # Undefine guest
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

    def convert_guest_to_nfs(self, origin_machine_ip, NFS_server, NFS_export_dir, vm_hostname, targetmachine_ip=""):
    # Convert_guest_to_nfs with v2v tool
        cmd = "sed -i 's/^.*auth_unix_rw/auth_unix_rw/' /etc/libvirt/libvirtd.conf"
        (ret, output) = self.runcmd(cmd, "Enable auth_unix_rw firstly in libvirtd config file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable auth_unix_rw")
        else:
            raise FailException("Failed to enable auth_unix_rw")
        self.vw_restart_libvirtd_vdsm(targetmachine_ip)
        time.sleep(30)
#         v2v import vm from remote libvirt to rhevm
#         cmd = "virt-v2v -i libvirt -ic qemu+ssh://root@%s/system -o rhev -os %s:%s --network rhevm %s" % (origin_machine_ip, NFS_server, NFS_export_dir, vm_hostname)
#         ret, output = self.runcmd_interact(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip, showlogger=False)
#         v2v import vm from local libvirt to rhevm
        cmd = "export LIBGUESTFS_BACKEND=direct && virt-v2v -o rhev -os  %s:%s --network rhevm %s" % (NFS_server, NFS_export_dir, vm_hostname)
        (ret, output) = self.runcmd(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip)
        if ret == 0 and ("100%" in output or "configured with virtio drivers" in output):
            logger.info("Succeeded to convert_guest_to_nfs with v2v tool")
            time.sleep(10)
        else:
            raise FailException("Failed to convert_guest_to_nfs with v2v tool")

    def get_domain_id(self, storagedomain_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Get storagedomain id 
        cmd = "%s -c -E 'list storagedomains '" % shell_cmd
        ret, output = self.runcmd(cmd, "list storagedomains in rhevm", targetmachine_ip)
        if ret == 0 and storagedomain_name in output:
            logger.info("Succeeded to list storagedomains %s in rhevm" % storagedomain_name)
            storagedomain_id = self.get_key_rhevm(output, "id", "name", storagedomain_name, targetmachine_ip)
            logger.info("%s id is %s" % (storagedomain_name, storagedomain_id))
            return storagedomain_id
        else :
            raise FailException("Failed to list storagedomains %s in rhevm" % storagedomain_name)

    def import_vm_to_rhevm(self, guest_name, nfs_dir_for_storage_id, nfs_dir_for_export_id, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Import guest to rhevm
        # cmd = "rhevm-shell -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s' " % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
        cmd = "%s -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-id %s' " % (shell_cmd, guest_name, nfs_dir_for_export_id, nfs_dir_for_storage_id)
        ret, output = self.runcmd(cmd, "import guest %s in rhevm" % guest_name, targetmachine_ip)
        self.rhevm_check_vm_status(guest_name, "down", targetmachine_ip)

    def add_vm_to_rhevm(self, rhevm_vm_name, NFSserver_ip, nfs_dir_for_export, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Add guest to rhevm
        while True:
            cmd = "%s -c -E ' list vms --name %s'" % (shell_cmd, rhevm_vm_name)
            ret, output = self.runcmd(cmd, "check vm exist or not before import vm", targetmachine_ip, showlogger=False)
            if ret == 0 :
                if rhevm_vm_name in output and "virt-v2v" in output:
                    logger.info("Succeeded to list vm %s before import vm" % rhevm_vm_name)
                    break
                else:
                    self.rhevm_define_guest(rhevm_vm_name, NFSserver_ip)
                    self.create_storage_pool(NFSserver_ip)
                    self.install_virtV2V(NFSserver_ip)
                    self.convert_guest_to_nfs(NFSserver_ip, NFSserver_ip, nfs_dir_for_export, rhevm_vm_name, NFSserver_ip)
                    self.rhevm_undefine_guest(rhevm_vm_name, NFSserver_ip)
                    data_storage_id = self.get_domain_id("data_storage", targetmachine_ip)
                    export_storage_id = self.get_domain_id("export_storage", targetmachine_ip)
                    self.import_vm_to_rhevm(rhevm_vm_name, data_storage_id, export_storage_id, targetmachine_ip)
            else:
                raise FailException("Failed to list vm in rhevm")

    def rhevm_check_vm_key_value(self, vm_name, vm_key, vm_value, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        cmd = "%s -c -E '%s'" % (shell_cmd, get_vm_cmd)
        for item in range(30):
            ret, output = self.runcmd(cmd, "list vms in rhevm", targetmachine_ip, showlogger=False)
            if ret == 0:
                value = self.get_key_rhevm(output, vm_key, "name", vm_name, targetmachine_ip).strip()
                if vm_value == "up" and vm_key == "status-state":
                    if value == vm_value and output.find("guest_info-ips-ip-address") > 0:
                    # if status.find(vm_status) >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
                        logger.info("Succeeded to check vm %s is %s status in rhevm" % (vm_name, vm_value))
                        time.sleep(60)
                        break
                    else :
                        logger.info("vm %s status-state is still %s" % (vm_name, vm_value))
                        time.sleep(10)
                else:
                    if value == vm_value:
                    # if status.find(vm_status) >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
                        logger.info("Succeeded to check vm %s %s is %s in rhevm" % (vm_name, vm_key, vm_value))
                        break
                    else :
                        logger.info("vm %s %s is still %s" % (vm_name, vm_key, vm_value))
                        time.sleep(10)
            else:
                raise FailException("Failed to run list vm %s via command: %s" % (vm_name, cmd))
        else:
            raise FailException("Failed to check vm %s status %s" % (vm_name, vm_value))

    def rhevm_check_vm_status(self, vm_name, vm_status, targetmachine_ip):
        self.rhevm_check_vm_key_value(vm_name, "status-state", vm_status, targetmachine_ip)

#     def rhevm_start_vm(self, vm_name, targetmachine_ip):
#         shell_cmd = self.get_rhevm_shell(targetmachine_ip)
#         get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
#         # Start VM on RHEVM
#         cmd = "%s -c -E 'action vm %s start'" % (shell_cmd, vm_name)
#         for item in range(10):
#             ret, output = self.runcmd(cmd, "start vm on rhevm", targetmachine_ip, showlogger=False)
#             if "Storage Domain cannot be accessed" in output:
#                 time.sleep(30)
#             elif ret == 0:
#                 logger.info("Success to run start command %s" % cmd)
#                 break
#         else:
#             raise FailException("Failed to start vm %s on rhevm" % vm_name)
#         self.rhevm_check_vm_status(vm_name, "up", targetmachine_ip)

    def rhevm_start_vm(self, vm_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Start VM on RHEVM
        cmd = "%s -c -E 'action vm %s start'" % (shell_cmd, vm_name)
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
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Stop VM on RHEVM
        cmd = "%s -c -E 'action vm \"%s\" stop'" % (shell_cmd, vm_name)
        ret, output = self.runcmd(cmd, "stop vm on rhevm", targetmachine_ip)
        if ret == 0:
            logger.info("Success to run stop command %s" % cmd)
        else:
            raise FailException("Failed to stop vm %s on rhevm" % vm_name)
        self.rhevm_check_vm_status(vm_name, "down", targetmachine_ip)

    def rhevm_pause_vm(self, vm_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Pause VM on RHEVM
        cmd = "%s -c -E 'action vm \"%s\" suspend'" % (shell_cmd, vm_name)
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

    def rhevm_migrate_vm(self, vm_name, dest_ip, dest_host_id, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Migrate VM on RHEVM
        cmd = "%s -c -E 'action vm \"%s\" migrate --host-name \"%s\"'" % (shell_cmd, vm_name, dest_ip)
        ret, output = self.runcmd(cmd, "migrate vm on rhevm", targetmachine_ip)
        if ret == 0 and "complete" in output:
            self.rhevm_check_vm_key_value(vm_name, "host-id", dest_host_id, targetmachine_ip)
            logger.info("Succeeded to migrate vm %s in rhevm to %s" % (vm_name, dest_host_id))
        else:
            raise FailException("Failed to run migrate vm %s in rhevm" % vm_name)

    def rhevm_get_guest_ip(self, vm_name, targetmachine_ip):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Get guest ip
        cmd = "%s -c -E '%s'" % (shell_cmd, get_vm_cmd)
        ret, output = self.runcmd(cmd, "list vms in rhevm", targetmachine_ip)
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

    def vdsm_get_vm_uuid(self, vm_name, targetmachine_ip=""):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        get_vm_cmd = self.get_vm_cmd(vm_name, targetmachine_ip)
        # Get the guest uuid
        cmd = "%s -c -E '%s'" % (shell_cmd, get_vm_cmd)
        ret, output = self.runcmd(cmd, "list VMS in rhevm", targetmachine_ip)
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
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # get vm network name
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'list nics --vm-identifier %s'" % (shell_cmd, vm_id)
        ret, output = self.runcmd(cmd, "List all nics of guest in rhevm", targetmachine_ip)
        return self.rhevm_parse_output(output)["name"]

    def vdsm_check_vm_nw(self, vm_name, nw_name, targetmachine_ip=""):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Remove vm original network
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'list nics --vm-identifier %s'" % (shell_cmd, vm_id)
        ret, output = self.runcmd(cmd, "List all nics of guest in rhevm", targetmachine_ip)
        if ret == 0 and nw_name in output:
            logger.info("Success to list %s in %s" % (nw_name, vm_name))
            return True
        else:
            logger.info("Failed to list %s in %s, maybe it has been deleted" % (nw_name, vm_name))
            return False

    def vdsm_rm_vm_nw(self, vm_name, nw_name, targetmachine_ip=""):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Remove vm original network
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'remove nic %s --vm-identifier %s'" % (shell_cmd, nw_name, vm_id)
        ret, output = self.runcmd(cmd, "Remove vm's network in rhevm", targetmachine_ip)
        if ret == 0 and "complete" in output:
            logger.info("Success to remove vm %s network %s" % (vm_name, nw_name))
        else:
            raise FailException("Failed to remove vm %s network %s" % (vm_name, nw_name))

    def vdsm_add_vm_nw(self, vm_name, targetmachine_ip=""):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # VM add new network
        vm_id = self.vdsm_get_vm_uuid(vm_name, targetmachine_ip)
        cmd = "%s -c -E 'add nic --vm-identifier %s --name ovirtmgmt --network-name ovirtmgmt'" % (shell_cmd, vm_id)
        ret, output = self.runcmd(cmd, "Add vm's new network in rhevm", targetmachine_ip)
        if ret == 0 and "ovirtmgmt" in output:
            logger.info("Success to add vm %s network" % vm_name)
        else:
            raise FailException("Failed to to add vm %s network" % vm_name)

    def get_host_uuid_on_rhevm(self, host_name, targetmachine_ip=""):
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Get the host uuid
        cmd = "%s -c -E 'show host %s'" % (shell_cmd, host_name)
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
        shell_cmd = self.get_rhevm_shell(targetmachine_ip)
        # Get the host hwuuid
        cmd = "%s -c -E 'show host %s'" % (shell_cmd, host_name)
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
    # Check the vdsmd status
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
    # Update virt-who configure file to vdsm mode /etc/sysconfig/virt-who
        self.update_config_to_default(targetmachine_ip)
        cmd = "sed -i -e 's/^.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/^.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/g' -e 's/^.*VIRTWHO_VDSM=.*/VIRTWHO_VDSM=1/g' /etc/sysconfig/virt-who" % interval_value
        ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file")
        else:
            raise FailException("Failed to update virt-who configure file")

    def update_rhel_rhevm_configure(self, rhevm_interval, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password, debug=1, targetmachine_ip=""):
    # Update virt-who configure file /etc/sysconfig/virt-who for enable VIRTWHO_RHEVM
        self.update_config_to_default(targetmachine_ip)
        cmd = "sed -i -e 's/.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_RHEVM=.*/VIRTWHO_RHEVM=1/g' -e 's/#VIRTWHO_RHEVM_OWNER=.*/VIRTWHO_RHEVM_OWNER=%s/g' -e 's/#VIRTWHO_RHEVM_ENV=.*/VIRTWHO_RHEVM_ENV=%s/g' -e 's/#VIRTWHO_RHEVM_SERVER=.*/VIRTWHO_RHEVM_SERVER=%s/g' -e 's/#VIRTWHO_RHEVM_USERNAME=.*/VIRTWHO_RHEVM_USERNAME=%s/g' -e 's/#VIRTWHO_RHEVM_PASSWORD=.*/VIRTWHO_RHEVM_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (rhevm_interval, debug, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
        ret, output = self.runcmd(cmd, "updating virt-who configure file for enable VIRTWHO_RHEVM", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_RHEVM")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_RHEVM")

    def set_rhevm_conf(self, debug=1, targetmachine_ip=""):
    # Configure rhevm mode in /etc/sysconfig/virt-who
        rhevm_ip = get_exported_param("RHEVM_IP")
        rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
        rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
        if "rhevm-4"in rhevm_version:
            rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443" + "\/ovirt-engine\/"
        else:
            rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/.*VIRTWHO_RHEVM=.*/VIRTWHO_RHEVM=1/g' -e 's/.*VIRTWHO_RHEVM_OWNER=.*/VIRTWHO_RHEVM_OWNER=%s/g' -e 's/.*VIRTWHO_RHEVM_ENV=.*/VIRTWHO_RHEVM_ENV=%s/g' -e 's/.*VIRTWHO_RHEVM_SERVER=.*/VIRTWHO_RHEVM_SERVER=%s/g' -e 's/.*VIRTWHO_RHEVM_USERNAME=.*/VIRTWHO_RHEVM_USERNAME=%s/g' -e 's/.*VIRTWHO_RHEVM_PASSWORD=.*/VIRTWHO_RHEVM_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
        ret, output = self.runcmd(cmd, "Setting rhevm mode in /etc/sysconfig/virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set rhevm mode in /etc/sysconfig/virt-who")
        else:
            raise FailException("Test Failed - Failed  to set rhevm mode in /etc/sysconfig/virt-who")

#     def rhevm_change_guest_name(self):
#         guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
#         rhevm_ip = get_exported_param("RHEVM_IP")
#         self.rhevm_start_vm(guest_name, rhevm_ip)
#         (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
#         network_card = self.vdsm_get_vm_nw(guest_name, rhevm_ip)
#         for item in range(2):
#             self.rhevm_stop_vm(guest_name, rhevm_ip)
#             self.vdsm_rm_vm_nw(guest_name, network_card, rhevm_ip)
#             self.vdsm_add_vm_nw(guest_name, rhevm_ip)
#             self.rhevm_start_vm(guest_name, rhevm_ip)
#             (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
#         self.cm_change_hostname(guestip)
#         self.rhevm_stop_vm(guest_name, rhevm_ip)

    def rhevm_change_guest_name(self, guest_name, targetmachine_ip=""):
        guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
        rhevm_ip = get_exported_param("RHEVM_IP")
        self.rhevm_start_vm(guest_name, targetmachine_ip)
        while True:
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, targetmachine_ip)
            try:
                self.cm_change_hostname(guestip)
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