from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class VDSMBase(VIRTWHOBase):
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

    def get_rhevm_repo_file(self, compose_name, targetmachine_ip=""):
        ''' wget rhevm repo file and add to rhel host '''
        if self.os_serial == "7":
            cmd = "wget -P /etc/yum.repos.d/ http://10.66.100.116/projects/sam-virtwho/rhevm_repo/rhevm_7.x.repo"
            ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))
            cmd = "sed -i -e 's/rhelbuild/%s/g' /etc/yum.repos.d/rhevm_7.x.repo" % compose_name
            ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to update repo file to the latest rhel repo")
            else:
                raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")
        else:
            cmd = "wget -P /etc/yum.repos.d/ http://10.66.100.116/projects/sam-virtwho/rhevm_repo/rhevm_6.x.repo"
            ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))
            cmd = "sed -i -e 's/rhelbuild/%s/g' /etc/yum.repos.d/rhevm_6.x.repo" % compose_name
            ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to update repo file to the latest rhel repo")
            else:
                raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")

    def config_vdsm_env_setup(self, rhel_compose, targetmachine_ip=""):
        self.cm_install_basetool(targetmachine_ip)
        # system setup for RHEL+RHEVM testing env
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        self.get_rhevm_repo_file(rhel_compose, targetmachine_ip)
        cmd = "yum install -y vdsm"
        ret, output = self.runcmd(cmd, "install vdsm and related packages", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to install vdsm and related packages in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to install vdsm and related packages in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def conf_rhevm_shellrc(self, targetmachine_ip=""):
        ''' Config the env to login to rhevm_rhell '''
#         tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s:443/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.rhevmshellrc" % tagetmachine_hostname
        ret, output = self.runcmd(cmd, "config rhevm_shell env on rhevm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to config rhevm_shell env on rhevm in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to config rhevm_shell env on rhevm in %s." % self.get_hg_info(targetmachine_ip))

    # Add cluster cpu 
    def update_cluster_cpu(self, cluster_name, cpu_type, targetmachine_ip):
        # cmd = "rhevm-shell -c -E 'update cluster %s --cpu-id \"%s\"'" % (cluster_name, cpu_type)
        cmd = "rhevm-shell -c -E \"update cluster %s --cpu-id '%s' \"" % (cluster_name, cpu_type)
        ret, output = self.runcmd(cmd, "update cluster cpu", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update cluster %s cpu to %s." % (cluster_name, cpu_type))
        else:
            raise FailException("Failed to update cluster %s cpu to %s." % (cluster_name, cpu_type))

    # Add host to rhevm
    def rhevm_add_host(self, rhevm_host_name, rhevm_host_ip, targetmachine_ip):
        while True:
            cmd = " rhevm-shell -c -E 'list hosts --show-all'"
            ret, output = self.runcmd(cmd, "list hosts in rhevm before add host", targetmachine_ip)
            if ret == 0 and rhevm_host_name in output:
                logger.info("Succeeded to list host %s before add host" % rhevm_host_name)
                status = self.get_key_rhevm(output, "status-state", "name", rhevm_host_name, targetmachine_ip)
                if "up" in status:
                    logger.info("Succeeded to show host %s at up mode in rhevm" % rhevm_host_name)
                    break
            else:
                cmd = " rhevm-shell -c -E 'add host --name \"%s\" --address \"%s\" --root_password red2015'" % (rhevm_host_name, rhevm_host_ip)
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
                            # elif "install_failed":
                            #    raise FailException("Failed to add host since status is %s" % (rhevm_host_name, status))
                            else :
                                logger.info("vm %s status-state is %s" % (rhevm_host_name, status))
                        else:
                            raise FailException("Failed to list host %s in rhevm" % rhevm_host_name)
                        time.sleep(60)
                        if runtime > 20:
                            raise FailException("%s status has problem,status is %s." % (rhevm_host_name, status))
                else:
                    raise FailException("Failed to add host %s to rhevm" % rhevm_host_name)

# Maintenance Host on RHEVM
    def rhevm_mantenance_host(self, rhevm_host_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'action host \"%s\" deactivate'" % rhevm_host_name
        ret, output = self.runcmd(cmd, "Maintenance host on rhevm.", targetmachine_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'show host \"%s\"'" % rhevm_host_name
                ret, output = self.runcmd(cmd, "list host in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0:
                    logger.info("Succeeded to list host")
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_host_name, targetmachine_ip)
                    if status.find("maintenance") >= 0:
                        logger.info("Succeeded to maintenance host %s in rhevm" % rhevm_host_name)
                        break
                    else :
                        logger.info("Host %s status-state is %s" % (rhevm_host_name, status))
                    time.sleep(20)
                    if runtime > 30:
                        raise FailException("%s's status has problem,status is %s." % (rhevm_host_name, status))
                else:
                    raise FailException("Failed to list host %s" % rhevm_host_name)
        else:
            raise FailException("Failed to maintenance host %s on rhevm" % rhevm_host_name)

# Active Host on RHEVM
    def rhevm_active_host(self, rhevm_host_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'action host \"%s\" activate'" % rhevm_host_name
        ret, output = self.runcmd(cmd, "Active host on rhevm.", targetmachine_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'show host \"%s\"'" % rhevm_host_name
                ret, output = self.runcmd(cmd, "list host in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0:
                    logger.info("Succeeded to list host")
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_host_name, targetmachine_ip)
                    if status.find("up") >= 0:
                        logger.info("Succeeded to active host %s in rhevm" % rhevm_host_name)
                        break
                    else :
                        logger.info("Host %s status-state is %s" % (rhevm_host_name, status))
                    time.sleep(20)
                    if runtime > 30:
                        raise FailException("%s's status has problem,status is %s." % (rhevm_host_name, status))
                else:
                    raise FailException("Failed to list host %s" % rhevm_host_name)
        else:
            raise FailException("Failed to active host %s on rhevm" % rhevm_host_name)

    # Add vm to special host
    def update_vm_to_host(self, vm_name, rhevm_host_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'update vm %s --placement_policy-host-name %s'" % (vm_name, rhevm_host_name)
        ret, output = self.runcmd(cmd, "update vm to special host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update vm %s to host %s." % (vm_name, rhevm_host_name))
        else:
            raise FailException("Failed to update vm %s to host %s." % (vm_name, rhevm_host_name))

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
        cmd = "chmod -R 777 %s" % storage_dir
        ret, output = self.runcmd(cmd, "Add x right to storage dir", NFS_server)
        if ret == 0 :
            logger.info("Succeeded to add right to storage dir.")
        else:
            raise FailException("Failed to add right to storage dir.")
        cmd = "service nfs restart"
        ret, output = self.runcmd(cmd, "restarting nfs service", NFS_server)
        if ret == 0 :
            logger.info("Succeeded to restart service nfs.")
        else:
            raise FailException("Failed to restart service nfs.")
        # check datastorage domain before add new one
        cmd = "rhevm-shell -c -E 'list storagedomains' "
        ret, output = self.runcmd(cmd, "check storagedomain before add new one.", targetmachine_ip)
        if ret == 0 and storage_name in output:
            logger.info("storagedomains %s is exist in rhevm." % storage_name)
        else:
            logger.info("storagedomains %s is not exist in rhevm." % storage_name)
            cmd = "rhevm-shell -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter \"Default\"' " % (storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
            ret, output = self.runcmd(cmd, "Add storagedomain in rhevm.", targetmachine_ip)
            if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "unattached", targetmachine_ip):
                logger.info("Succeeded to add storagedomains %s in rhevm." % storage_name)
            else:
                raise FailException("Failed to add storagedomains %s in rhevm." % storage_name)
            time.sleep(120)
    #     # Attach datacenter to storagedomain in rhevm
            cmd = "rhevm-shell -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"Default\"' " % (storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
            ret, output = self.runcmd(cmd, "Attaches the storage domain to the Default data center.", targetmachine_ip)
            if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "NotExist", targetmachine_ip):
                logger.info("Succeeded to active storagedomains %s in rhevm." % storage_name)
            else:
                raise FailException("Failed to active storagedomains %s in rhevm." % storage_name)
            time.sleep(60)
    #     # activate storagedomain in rhevm
    #      def activate_storagedomain(self, storage_name, targetmachine_ip): 
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
            ret, output = self.runcmd(cmd, "install virt-v2v", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install virt-V2V.")
            else:
                raise FailException("Failed to install virt-V2V")

    def rhevm_define_guest(self, vm_name, targetmachine_ip=""):
        ''' wget kvm img and xml file, define it in execute machine for converting to rhevm '''
        cmd = "test -d /home/rhevm_guest/ && echo presence || echo absence"
        ret, output = self.runcmd(cmd, "check whether guest exist", targetmachine_ip)
        if "presence" in output:
            logger.info("guest has already exist")
        else:
            # Get vm from 10.66.100.116
#             cmd = "wget -P /home/rhevm_guest/ http://10.66.100.116/projects/sam-virtwho/%s" % vm_name
#             ret, output = self.runcmd(cmd, "wget kvm img file", targetmachine_ip, showlogger=False)
#             if ret == 0:
#                 logger.info("Succeeded to wget kvm img file")
#             else:
#                 raise FailException("Failed to wget kvm img file")
#             image_nfs_path = self.get_vw_cons("nfs_image_path")
            # Get image from beaker NFS server
            image_server = self.get_vw_cons("beaker_image_server")
            image_nfs_path = '/home/rhevm_guest/'
            image_mount_path = self.get_vw_cons("local_mount_point")
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

        cmd = "chmod -R 777 /home/rhevm_guest/"
        if ret == 0:
            logger.info("Success to add excute to /home/rhevm_guest")
        else:
            logger.info("Failed to add excute to /home/rhevm_guest")
        # cmd = "wget -P /tmp/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "wget -P /home/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/%s.xml" % vm_name
        ret, output = self.runcmd(cmd, "wget kvm xml file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget xml img file")
        else:
            raise FailException("Failed to wget xml img file")
        cmd = "sed -i 's/^.*auth_unix_rw/#auth_unix_rw/' /etc/libvirt/libvirtd.conf"
        (ret, output) = self.runcmd(cmd, "Disable auth_unix_rw firstly in libvirtd config file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to Disable auth_unix_rw.")
        else:
            raise FailException("Failed to Disable auth_unix_rw.")
        self.vw_restart_libvirtd_vdsm()
        # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "virsh define /home/rhevm_guest/xml/%s.xml" % vm_name
        ret, output = self.runcmd(cmd, "define kvm guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to define kvm guest")
        else:
            raise FailException("Failed to define kvm guest")

    def rhevm_undefine_guest(self, vm_name, targetmachine_ip=""):
        # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "virsh undefine %s" % vm_name
        ret, output = self.runcmd(cmd, "undefine kvm guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to undefine kvm guest")
        else:
            raise FailException("Failed to undefine kvm guest")
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
        if self.os_serial == "6":
            cmd = "virsh pool-define /tmp/autotest_pool.xml"
            ret, output = self.runcmd(cmd, "define storage pool.")
            if ret == 0 and "autotest_pool defined" in output:
                logger.info("Succeeded to define storage pool.")
            else:
                raise FailException("Failed to define storage pool.")
            cmd = "virsh pool-list"
            ret, output = self.runcmd(cmd, "list storage pool.")
            if ret == 0 and "autotest_pool" in output and "active" in output:
                logger.info("Succeeded to list storage pool.")
            else:
                cmd = "virsh pool-start autotest_pool"
                ret, output = self.runcmd(cmd, "start storage pool.")
                if ret == 0 and "autotest_pool started" in output:
                    logger.info("Succeeded to start storage pool.")
                else:
                    raise FailException("Failed to start storage pool.")

    # convert_guest_to_nfs with v2v tool
    def convert_guest_to_nfs(self, origin_machine_ip, NFS_server, NFS_export_dir, vm_hostname, targetmachine_ip=""):
        cmd = "sed -i 's/^.*auth_unix_rw/auth_unix_rw/' /etc/libvirt/libvirtd.conf"
        (ret, output) = self.runcmd(cmd, "Enable auth_unix_rw firstly in libvirtd config file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable auth_unix_rw.")
        else:
            raise FailException("Failed to enable auth_unix_rw.")
        self.vw_restart_libvirtd_vdsm()
        time.sleep(30)
#        # v2v import vm from remote libvirt to rhevm
#         cmd = "virt-v2v -i libvirt -ic qemu+ssh://root@%s/system -o rhev -os %s:%s --network rhevm %s" % (origin_machine_ip, NFS_server, NFS_export_dir, vm_hostname)
#         ret, output = self.runcmd_interact(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip, showlogger=False)
        # v2v import vm from local libvirt to rhevm
        cmd = "export LIBGUESTFS_BACKEND=direct && virt-v2v -o rhev -os  %s:%s --network rhevm %s" % (NFS_server, NFS_export_dir, vm_hostname)
        (ret, output) = self.runcmd(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip)
        if ret == 0 and ("100%" in output or "configured with virtio drivers" in output):
            logger.info("Succeeded to convert_guest_to_nfs with v2v tool")
            time.sleep(10)
        else:
            raise FailException("Failed to convert_guest_to_nfs with v2v tool")

    # Get storagedomain id 
    def get_domain_id(self, storagedomain_name, rhevm_host_ip):
        cmd = "rhevm-shell -c -E 'list storagedomains ' "
        ret, output = self.runcmd(cmd, "list storagedomains in rhevm.", rhevm_host_ip)
        if ret == 0 and storagedomain_name in output:
            logger.info("Succeeded to list storagedomains %s in rhevm." % storagedomain_name)
            storagedomain_id = self.get_key_rhevm(output, "id", "name", storagedomain_name, rhevm_host_ip)
            logger.info("%s id is %s" % (storagedomain_name, storagedomain_id))
            return storagedomain_id
        else :
            raise FailException("Failed to list storagedomains %s in rhevm." % storagedomain_name)

    # import guest to rhevm
    def import_vm_to_rhevm(self, guest_name, nfs_dir_for_storage_id, nfs_dir_for_export_id, rhevm_host_ip):
        # action vm "7.1_Server_x86_64" import_vm --storagedomain-identifier export_storage  --cluster-name Default --storage_domain-name data_storage
        # cmd = "rhevm-shell -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s' " % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
        cmd = "rhevm-shell -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-id %s' " % (guest_name, nfs_dir_for_export_id, nfs_dir_for_storage_id)
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
                time.sleep(120)
                if runtime > 60:
                    raise FailException("%s status has problem,status is %s." % (guest_name, status))

    def add_vm_to_rhevm(self, rhevm_vm_name, NFSserver_ip, nfs_dir_for_export, targetmachine_ip):
        while True:
            cmd = "rhevm-shell -c -E ' list vms --name %s'" % rhevm_vm_name
            ret, output = self.runcmd(cmd, "check vm exist or not before import vm", targetmachine_ip)
            if ret == 0 :
                if rhevm_vm_name in output and "virt-v2v" in output:
                    logger.info("Succeeded to list vm %s before import vm" % rhevm_vm_name)
                    break
                else:
                    self.rhevm_define_guest(rhevm_vm_name)
                    self.create_storage_pool()
                    self.install_virtV2V()
                    self.convert_guest_to_nfs(get_exported_param("REMOTE_IP"), NFSserver_ip, nfs_dir_for_export, rhevm_vm_name)
                    self.rhevm_undefine_guest(rhevm_vm_name)
                    data_storage_id = self.get_domain_id ("data_storage", targetmachine_ip)
                    export_storage_id = self.get_domain_id ("export_storage", targetmachine_ip)
                    self.import_vm_to_rhevm(rhevm_vm_name, data_storage_id, export_storage_id, targetmachine_ip)
            else:
                raise FailException("Failed to list vm in rhevm")

# Start VM on RHEVM
    def rhevm_start_vm(self, rhevm_vm_name, rhevm_host_ip):
        runtime_start = 0
        while True:
            cmd = "rhevm-shell -c -E 'action vm %s start'" % rhevm_vm_name
            ret, output = self.runcmd(cmd, "start vm on rhevm.", rhevm_host_ip)            
            if "Storage Domain cannot be accessed" in output:
                runtime_start = runtime_start + 1
                time.sleep(30)
                if runtime_start > 10:
                    raise FailException("Failed to run start command as storage is not active")
            elif ret == 0:
                logger.info("Success to run start command ")
                break
            else:
                raise FailException("Failed to start vm %s on rhevm" % rhevm_vm_name)
        runtime = 0
        while True:
            cmd = "rhevm-shell -c -E 'show vm %s'" % rhevm_vm_name
            ret, output = self.runcmd(cmd, "list vms in rhevm.", rhevm_host_ip)
            runtime = runtime + 1
            if ret == 0:
                logger.info("Succeeded to list vms")
                status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, rhevm_host_ip)
                if status.find("up") >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
                    logger.info("Succeeded to up vm %s in rhevm" % rhevm_vm_name)
                    time.sleep(60)
                    break
                else :
                    logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
                time.sleep(10)
                if runtime > 30:
                    raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
            else:
                raise FailException("Failed to list vm %s" % rhevm_vm_name)

# Stop VM on RHEVM
    def rhevm_stop_vm(self, rhevm_vm_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'action vm \"%s\" stop'" % rhevm_vm_name
        ret, output = self.runcmd(cmd, "stop vm on rhevm.", targetmachine_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'show vm %s'" % rhevm_vm_name
                ret, output = self.runcmd(cmd, "list vms in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0:
                    logger.info("Succeeded to list vms")
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
                    if status.find("down") >= 0 and status.find("powering") < 0:
                        logger.info("Succeeded to stop vm %s in rhevm" % rhevm_vm_name)
                        break
                    else :
                        logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
                    time.sleep(60)
                    if runtime > 30:
                        raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
                else:
                    raise FailException("Failed to list vm %s" % rhevm_vm_name)
        else:
            raise FailException("Failed to stop vm %s on rhevm" % rhevm_vm_name)

# Pause VM on RHEVM
    def rhevm_pause_vm(self, rhevm_vm_name, targetmachine_ip):
        runtime_suspend = 0
        while True:
            cmd = "rhevm-shell -c -E 'action vm \"%s\" suspend'" % rhevm_vm_name
            ret, output = self.runcmd(cmd, "suspend vm on rhevm.", targetmachine_ip)
            if "Storage Domain cannot be accessed" in output:
                runtime_suspend = runtime_suspend + 1
                time.sleep(30)
                if runtime_suspend > 10:
                    raise FailException("Failed to run suspend command as storage is not active")
            elif ret == 0:
                logger.info("Success to run suspend command ")
                break
            else:
                raise FailException("Failed to suspended vm %s in rhevm" % rhevm_vm_name)
        runtime = 0
        while True:
            cmd = "rhevm-shell -c -E 'show vm %s'" % rhevm_vm_name
            ret, output = self.runcmd(cmd, "list vms in rhevm.", targetmachine_ip)
            runtime = runtime + 1
            if ret == 0:
                logger.info("Succeeded to list vms")
                status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
#                     if status.find("suspended") >= 0 and status.find("saving_state") < 0:
                if "suspended" in status :
                    logger.info("Succeeded to suspended vm %s in rhevm" % rhevm_vm_name)
                    break
                else :
                    logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
                time.sleep(30)
                if runtime > 20:
                    raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
            else:
                raise FailException("Failed to list vm %s" % rhevm_vm_name)
    
# Migrate VM on RHEVM
    def rhevm_migrate_vm(self, rhevm_vm_name, dest_ip, dest_host_id, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'action vm \"%s\" migrate --host-name \"%s\"'" % (rhevm_vm_name, dest_ip)
        ret, output = self.runcmd(cmd, "migrate vm on rhevm.", targetmachine_ip)
        if ret == 0 and "complete" in output:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'show vm %s'" % rhevm_vm_name
                ret, output = self.runcmd(cmd, "list vms in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0:
                    logger.info("Succeeded to list vms")
                    dest_host_id_value = self.get_key_rhevm(output, "host-id", "name", rhevm_vm_name, targetmachine_ip)
                    if dest_host_id_value == dest_host_id :
                        logger.info("Succeeded to migrate vm %s in rhevm" % rhevm_vm_name)
                        break
                    else :
                        logger.info("vm %s is migrating in rhevm" % (rhevm_vm_name))
                    time.sleep(60)
                    if runtime > 120:
                        raise FailException("Failed to migrate vm %s in rhevm" % rhevm_vm_name)
                else:
                    raise FailException("Failed to list vm %s" % rhevm_vm_name)
        else:
            raise FailException("Failed to run migrate vm %s in rhevm" % rhevm_vm_name)

    # get guest ip
    def rhevm_get_guest_ip(self, vm_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'show vm %s'" % vm_name
        ret, output = self.runcmd(cmd, "list VMS in rhevm.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to list vm %s." % vm_name)
            guestip = self.get_key_rhevm(output, "guest_info-ips-ip-address", "name", vm_name, targetmachine_ip)
            hostuuid = self.get_key_rhevm(output, "host-id", "name", vm_name, targetmachine_ip)
            if guestip is not "":
                logger.info("vm %s ipaddress is %s" % (vm_name, guestip))
                return (guestip, hostuuid)
            else:
                logger.error("Failed to gest the vm %s ipaddress" % vm_name)
        else:
            raise FailException("Failed to list VM %s." % vm_name) 

    def vdsm_get_vm_uuid(self, vm_name, targetmachine_ip=""):
        ''' get the guest uuid. '''
        cmd = "rhevm-shell -c -E 'show vm %s'" % vm_name
        ret, output = self.runcmd(cmd, "list VMS in rhevm.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to list vm %s." % vm_name)
            guestid = self.get_key_rhevm(output, "id", "name", vm_name, targetmachine_ip)
            if guestid is not "":
                logger.info("Succeeded to get guest %s id is %s" % (vm_name, guestid))
                return guestid
            else:
                logger.error("Failed to get guest %s id is %s" % (vm_name, guestid))
        else:
            raise FailException("Failed to list VM %s." % vm_name) 

    def get_host_uuid_on_rhevm(self, host_name, targetmachine_ip=""):
        ''' get the guest uuid. '''
        cmd = "rhevm-shell -c -E 'show host %s'" % host_name
        ret, output = self.runcmd(cmd, "list host in rhevm.", targetmachine_ip)
        if ret == 0:
            hostid = self.get_key_rhevm(output, "id", "name", host_name, targetmachine_ip)
            if hostid is not "":
                logger.info("Succeeded to get host %s id is %s" % (host_name, hostid))
                return hostid
            else:
                logger.error("Failed to get guest %s id is %s" % (host_name, hostid))
        else:
            raise FailException("Failed to list HOST %s." % host_name) 

    def vw_restart_vdsm(self, targetmachine_ip=""):
        ''' restart vdsmd service. '''
        cmd = "service vdsmd restart"
        ret, output = self.runcmd(cmd, "restart vdsmd", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart vdsmd service.")
        else:
            raise FailException("Test Failed - Failed to restart vdsmd")

    def vw_restart_vdsm_new(self, targetmachine_ip=""):
        if self.check_systemctl_service("vdsmd", targetmachine_ip):
            cmd = "systemctl restart vdsmd service; sleep 15"
            ret, output = self.runcmd(cmd, "restart vdsmd service by systemctl.", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart vdsmd")
            else:
                raise FailException("Test Failed - Failed to restart vdsmd")
        else:
            cmd = "service vdsmd restart; sleep 15"
            ret, output = self.runcmd(cmd, "restart vdsmd by service", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart vdsmd")
            else:
                raise FailException("Test Failed - Failed to restart vdsmd")

    def vw_check_vdsm_status(self, targetmachine_ip=""):
        ''' Check the vdsmd status. '''
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "systemctl status vdsmd; sleep 15"
            ret, output = self.runcmd(cmd, "vdsmd status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check vdsmd is running.")
            else:
                raise FailException("Test Failed - Failed to check vdsmd is running.")
        else:
            cmd = "service vdsmd status; sleep 15"
            ret, output = self.runcmd(cmd, "vdsmd status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check vdsmd is running.")
                self.SET_RESULT(0)
            else:
                raise FailException("Test Failed - Failed to check vdsmd is running.")

    def update_rhel_vdsm_configure(self, interval_value, targetmachine_ip=""):
        ''' update virt-who configure file to vdsm mode /etc/sysconfig/virt-who. '''
        cmd = "sed -i -e 's/^.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/^.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/g' -e 's/^.*VIRTWHO_VDSM=.*/VIRTWHO_VDSM=1/g' /etc/sysconfig/virt-who" % interval_value
        ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file.")
        else:
            raise FailException("Failed to update virt-who configure file.")

    def update_rhel_rhevm_configure(self, rhevm_interval, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password, debug=1, targetmachine_ip=""):
        ''' update virt-who configure file /etc/sysconfig/virt-who for enable VIRTWHO_RHEVM'''
        cmd = "sed -i -e 's/.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_RHEVM=.*/VIRTWHO_RHEVM=1/g' -e 's/#VIRTWHO_RHEVM_OWNER=.*/VIRTWHO_RHEVM_OWNER=%s/g' -e 's/#VIRTWHO_RHEVM_ENV=.*/VIRTWHO_RHEVM_ENV=%s/g' -e 's/#VIRTWHO_RHEVM_SERVER=.*/VIRTWHO_RHEVM_SERVER=%s/g' -e 's/#VIRTWHO_RHEVM_USERNAME=.*/VIRTWHO_RHEVM_USERNAME=%s/g' -e 's/#VIRTWHO_RHEVM_PASSWORD=.*/VIRTWHO_RHEVM_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (rhevm_interval, debug, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
        ret, output = self.runcmd(cmd, "updating virt-who configure file for enable VIRTWHO_RHEVM", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_RHEVM.")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_RHEVM.")

    def hypervisor_check_uuid(self, hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', uuidexists=True, targetmachine_ip=""):
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
            hostloc = log_uuid_list.find(hostuuid)
            if hostloc >= 0:
                if uuidexists:
                    khrightloc = log_uuid_list.find("[", hostloc, -1)
                    khleftloc = log_uuid_list.find("]", hostloc, -1)
                    ulst = log_uuid_list[khrightloc:khleftloc - 1]
                    if guestuuid == "" and len(ulst) == 0:
                        logger.info("Succeeded to get none uuid list")
                    else:
                        if guestuuid in ulst:
                            logger.info("Succeeded to check guestuuid %s in host %s" % (guestuuid, hostuuid))
                        else:
                            raise FailException("Failed to check guestuuid %s in host %s" % (guestuuid, hostuuid))
                else:
                    khrightloc = log_uuid_list.find("[", hostloc, -1)
                    khleftloc = log_uuid_list.find("]", hostloc, -1)
                    ulst = log_uuid_list[khrightloc:khleftloc + 1]
                    if guestuuid not in ulst:
                        logger.info("Succeeded to check guestuuid %s not in host %s" % (guestuuid, hostuuid))
                    else:
                        raise FailException("Failed to check guestuuid %s not in log_uuid_list" % guestuuid)
            else:
                raise FailException("Failed to get rhsm.log")
        else:
            raise FailException("Test Failed - log file has problem, please check it !")

    def hypervisor_check_attr(self, hostuuid, guestname, guest_status, guest_type, guest_hypertype, guest_state, guestuuid, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
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
            elif "Sending update in hosts-to-guests mapping"in output:
                log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
            hostloc = log_uuid_list.find(hostuuid)
            khrightloc = log_uuid_list.find("[", hostloc, -1)
            khleftloc = log_uuid_list.find("]", hostloc, -1)
            ulst = log_uuid_list[khrightloc:khleftloc + 1]
            logger.info("ulst is %s" % ulst)
#             loglist = eval(ulst[:ulst.rfind("]\n") + 1].strip())
            loglist = eval(ulst[:ulst.rfind("]") + 1].strip())
            logger.info("loglist is %s" % loglist)
#             loglist = eval(log_uuid_list[:log_uuid_list.rfind("]\n") + 1].strip())
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

    def rhel_rhevm_sys_setup(self, targetmachine_ip=""):
        self.cm_install_basetool(targetmachine_ip)
        RHEVM_IP = get_exported_param("RHEVM_IP")
        RHEL_RHEVM_GUEST_NAME = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
        RHEVM_HOST1_NAME = self.get_hostname()
        RHEVM_HOST2_NAME = self.get_hostname(get_exported_param("REMOTE_IP_2"))
        NFSserver_ip = get_exported_param("REMOTE_IP")
        nfs_dir_for_storage = self.get_vw_cons("NFS_DIR_FOR_storage")
        nfs_dir_for_export = self.get_vw_cons("NFS_DIR_FOR_export")
        rhel_compose = get_exported_param("RHEL_COMPOSE")

        # system setup for RHEL+RHEVM(VDSM) testing env on two hosts
#         self.config_vdsm_env_setup(rhel_compose)
        self.config_vdsm_env_setup(rhel_compose, get_exported_param("REMOTE_IP_2"))
        # configure env on rhevm(add two host,storage,guest)
        self.conf_rhevm_shellrc(RHEVM_IP)
        self.update_cluster_cpu("Default", "Intel Conroe Family", RHEVM_IP)
#         self.rhevm_add_host(RHEVM_HOST1_NAME, get_exported_param("REMOTE_IP"), RHEVM_IP)
        self.rhevm_add_host(RHEVM_HOST2_NAME, get_exported_param("REMOTE_IP_2"), RHEVM_IP)
#         self.add_storagedomain_to_rhevm("data_storage", RHEVM_HOST1_NAME, "data", "v3", NFSserver_ip, nfs_dir_for_storage, RHEVM_IP)
#         self.add_storagedomain_to_rhevm("export_storage", RHEVM_HOST1_NAME, "export", "v1", NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
#         self.add_vm_to_rhevm(RHEL_RHEVM_GUEST_NAME, NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
#         self.update_vm_to_host(RHEL_RHEVM_GUEST_NAME, RHEVM_HOST1_NAME, RHEVM_IP)

    def rhel_vdsm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_rhel_vdsm_configure(5)
        self.vw_restart_virtwho_new()
        # configure slave machine
        slave_machine_ip = get_exported_param("REMOTE_IP_2")
        if slave_machine_ip != None and slave_machine_ip != "":
            # if host already registered, unregister it first, then configure and register it
            self.sub_unregister(slave_machine_ip)
            self.configure_server(SERVER_IP, SERVER_HOSTNAME, slave_machine_ip)
            self.sub_register(SERVER_USER, SERVER_PASS, slave_machine_ip)
            # update virt-who configure file
            self.update_rhel_vdsm_configure(5, slave_machine_ip)
            self.vw_restart_virtwho_new(slave_machine_ip)

    def rhel_rhevm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
        RHEVM_IP = get_exported_param("RHEVM_IP")

        VIRTWHO_RHEVM_OWNER = self.get_vw_cons("VIRTWHO_RHEVM_OWNER")
        VIRTWHO_RHEVM_ENV = self.get_vw_cons("VIRTWHO_RHEVM_ENV")
        VIRTWHO_RHEVM_SERVER = "https:\/\/" + RHEVM_IP + ":443"
        VIRTWHO_RHEVM_USERNAME = self.get_vw_cons("VIRTWHO_RHEVM_USERNAME")
        VIRTWHO_RHEVM_PASSWORD = self.get_vw_cons("VIRTWHO_RHEVM_PASSWORD")
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_rhel_rhevm_configure("5", VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, debug=1)
        self.service_command("restart_virtwho")
