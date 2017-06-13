from utils import *
from testcases.base import Base
from utils.exception.failexception import FailException

class Install_Base(Base):

    def install_sam(self, compose, targetmachine_ip=""):
        self.__stop_iptables(targetmachine_ip)
        self.__set_selinux(targetmachine_ip)
        self.__set_hosts_file(targetmachine_ip)
        self.__auto_subscribe(targetmachine_ip)
        self.__enable_sam_repo(targetmachine_ip)
        self.__install_katello(targetmachine_ip)
        self.__deploy_sam(targetmachine_ip)
        self.__import_manifest(targetmachine_ip)

    def install_sam_docker(self, compose, targetmachine_ip=""):
        self.__stop_iptables(targetmachine_ip)
        self.__set_selinux(targetmachine_ip)
        self.__set_hosts_file(targetmachine_ip)
#         self.__auto_subscribe(targetmachine_ip)
#         self.__enable_sam_repo(targetmachine_ip)
#         self.__install_katello(targetmachine_ip)
        self.__deploy_sam(targetmachine_ip)
        self.__import_manifest(targetmachine_ip)

    def install_satellite(self, compose, targetmachine_ip=""):
        self.__set_selinux(targetmachine_ip)
        self.__set_hosts_file(targetmachine_ip)
        self.__auto_subscribe(targetmachine_ip)
        self.__satellite_repo_config_6(targetmachine_ip)
        self.__add_satellite_repo(compose, targetmachine_ip)
        self.__install_satellite(targetmachine_ip)
        self.__deploy_satellite(targetmachine_ip)
        self.__import_manifest_satellite(targetmachine_ip)

    def install_satellite62_2(self, compose, targetmachine_ip=""):
        self.__set_selinux(targetmachine_ip)
        self.__set_hostname(targetmachine_ip)
        self.__set_hosts_file(targetmachine_ip)
#         self.__auto_subscribe(targetmachine_ip)
        self.__attach_satellite_subscription(targetmachine_ip)
        if "RHEL-7" in compose:
            self.__enable_satellite_repo_7(targetmachine_ip)
        else:
            self.__enable_satellite_repo_6(targetmachine_ip)
        # self.__add_satellite62_repo(compose, targetmachine_ip)
        self.__install_satellite62(targetmachine_ip)
        self.__deploy_satellite62(targetmachine_ip)
        self.__import_manifest_satellite(targetmachine_ip)
        
    def install_satellite62(self, compose, targetmachine_ip=""):
        self.__set_selinux(targetmachine_ip)
        self.__set_hostname(targetmachine_ip)
        self.__set_hosts_file(targetmachine_ip)
        # self.__auto_subscribe(targetmachine_ip)
        # self.__satellite_repo_config_6(targetmachine_ip)
        # self.__add_satellite62_repo(compose, targetmachine_ip)
#         self.__install_satellite62(targetmachine_ip)
        self.__deploy_satellite62(targetmachine_ip)
        self.__import_manifest_satellite(targetmachine_ip)

    def install_satellite_ohsnap(self, compose, targetmachine_ip=""):
        self.__set_selinux(targetmachine_ip)
        self.__set_hostname(targetmachine_ip)
        self.__set_hosts_file(targetmachine_ip)
#         self.__auto_subscribe(targetmachine_ip)
#         if "RHEL7" in compose:
#             self.__satellite_repo_config_7(targetmachine_ip)
#         else:
#             self.__satellite_repo_config_6(targetmachine_ip)
#         self.__add_satellite_ohsnap_repo(compose, targetmachine_ip)
#         self.__install_satellite62(targetmachine_ip)
        self.__deploy_satellite62(targetmachine_ip)
        #self.__import_manifest_satellite(targetmachine_ip)

    def install_rhevm35(self, compose, targetmachine_ip=""):
        self.cm_install_wget(targetmachine_ip)
        self.__auto_subscribe(targetmachine_ip)
        self.__add_rhevm_repo(compose, targetmachine_ip)
        self.__install_rhevm(targetmachine_ip)
        self.__deploy_rhevm(targetmachine_ip)

    def install_rhevm36(self, compose, targetmachine_ip=""):
        self.cm_install_wget(targetmachine_ip)
        self.__auto_subscribe(targetmachine_ip)
        self.__add_rhevm36_repo(compose, targetmachine_ip)
        self.__install_rhevm(targetmachine_ip)
        self.__deploy_rhevm36(targetmachine_ip)

    def install_rhevm40(self, compose, targetmachine_ip=""):
        self.cm_install_wget(targetmachine_ip)
        self.__rm_beaker_repo(targetmachine_ip)
        self.__auto_subscribe(targetmachine_ip)
        self.__add_rhevm40_repo(compose, targetmachine_ip)
        self.__install_rhevm(targetmachine_ip)
        self.__deploy_rhevm40(targetmachine_ip)

    def install_rhevm41(self, compose, targetmachine_ip=""):
        self.__deploy_rhevm41(targetmachine_ip)

    def __stop_iptables(self, targetmachine_ip=""):
        cmd = "service iptables stop"
        ret, output = self.runcmd(cmd, "service iptables stop", targetmachine_ip)

    def __set_selinux(self, targetmachine_ip=""):
        cmd = "setenforce 0"
        ret, output = self.runcmd(cmd, "setenforce 0", targetmachine_ip)
        logger.info("Succeeded to run setenforce 0.")
        cmd = "sed -i -e 's/SELINUX=.*/SELINUX=%s/g' /etc/sysconfig/selinux" % ("permissive")
        ret, output = self.runcmd(cmd, "set /etc/sysconfig/selinux", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set /etc/sysconfig/selinux.")
        else:
            raise FailException("Test Failed - Failed to set /etc/sysconfig/selinux.")

    def __set_hostname(self, targetmachine_ip=""):
        logger.info("=================================")
        SATELLITE_HOSTNAME = get_exported_param("SATELLITE_HOSTNAME")
        cmd = "hostname %s" % SATELLITE_HOSTNAME
        ret, output = self.runcmd(cmd, "set satellite hostname", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set satellite hostname to %s." % SATELLITE_HOSTNAME)
        else:
            raise FailException("Test Failed - Failed to set satellite hostname to %s." % SATELLITE_HOSTNAME)

    def __set_hosts_file(self, targetmachine_ip=""):
        cmd = "sed -i '/%s/d' /etc/hosts; echo \"%s `hostname`\" >> /etc/hosts" % (targetmachine_ip, targetmachine_ip)
        ret, output = self.runcmd(cmd, "set /etc/hosts", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set /etc/hosts file.")
        else:
            raise FailException("Test Failed - Failed to set /etc/hosts file.")

    def __auto_subscribe(self, targetmachine_ip=""):
        cmd = "subscription-manager register --username=QualityAssurance --password=VHVFhPS5TEG8dud9 --auto-attach"
        ret, output = self.runcmd(cmd, "auto attach", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to auto attach.")
        else:
            raise FailException("Test Failed - Failed to auto attach.")

    def __attach_satellite_subscription(self, targetmachine_ip=""):
        cmd = "subscription-manager  subscribe --pool=8a85f981519abf020151a22d3c387f2a"
        ret, output = self.runcmd(cmd, "attach Red Hat Satellite Employee Subscription", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to attach Red Hat Satellite Employee Subscription.")
        else:
            raise FailException("Test Failed - Failed to attach Red Hat Satellite Employee Subscription.")

    def __enable_sam_repo(self, targetmachine_ip=""):
        cmd = "yum-config-manager --disable; yum-config-manager --enable rhel-6-server-sam-rpms rhel-6-server-rpms"
        ret, output = self.runcmd(cmd, "enable sam repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable sam repo")
        else:
            raise FailException("Test Failed - Failed to enable sam repo")

    def __enable_satellite_repo_6(self, targetmachine_ip=""):
        cmd = "subscription-manager repos --disable=*; subscription-manager repos --enable=rhel-6-server-rpms --enable=rhel-6-server-optional-rpms --enable=rhel-server-rhscl-6-rpms --enable=rhel-6-server-satellite-capsule-6.2-rpms --enable=rhel-6-server-satellite-6.2-rpms --enable=rhel-6-server-satellite-tools-6.2-rpms"
        ret, output = self.runcmd(cmd, "enable satellite repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable satellite repo")
        else:
            raise FailException("Test Failed - Failed to enable satellite repo")

    def __enable_satellite_repo_7(self, targetmachine_ip=""):
        cmd = "subscription-manager repos --disable=*; subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-server-rhscl-7-rpms --enable=rhel-7-server-satellite-capsule-6.2-rpms --enable=rhel-7-server-satellite-6.2-rpms --enable=rhel-7-server-satellite-tools-6.2-rpms"
        ret, output = self.runcmd(cmd, "enable satellite repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable satellite repo")
        else:
            raise FailException("Test Failed - Failed to enable satellite repo")

    def __satellite_repo_config_7(self, targetmachine_ip=""):
        cmd = "subscription-manager repos --disable \"*\""
        ret, output = self.runcmd(cmd, "disable all repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to disable all repo.")
        else:
            raise FailException("Test Failed - Failed to disable all repo.")
        cmd = "subscription-manager repos --enable rhel-7-server-rpms --enable rhel-server-rhscl-7-rpms"
        ret, output = self.runcmd(cmd, "enable rhscl repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable rhscl repo.")
        else:
            raise FailException("Test Failed - Failed to enable rhscl repo.")

    def __satellite_repo_config_6(self, targetmachine_ip=""):
        cmd = "subscription-manager repos --disable \"*\""
        ret, output = self.runcmd(cmd, "disable all repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to disable all repo.")
        else:
            raise FailException("Test Failed - Failed to disable all repo.")
        cmd = "subscription-manager repos --enable rhel-6-server-rpms --enable=rhel-6-server-optional-rpms --enable rhel-server-rhscl-6-rpms"
        ret, output = self.runcmd(cmd, "enable rhscl repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable rhscl repo.")
        else:
            raise FailException("Test Failed - Failed to enable rhscl repo.")

    def __add_sam_repo(self, sam_compose, targetmachine_ip=""):
        cmd = ('cat <<EOF > /etc/yum.repos.d/sam.repo\n'
            '[sam]\n'
            'name=sam\n'
            'baseurl=http://download.eng.bos.redhat.com/released/RHEL-6-SAM/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % sam_compose
            )
        ret, output = self.runcmd(cmd, "add sam repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to add sam repo.")
        else:
            raise FailException("Test Failed - Failed to add sam repo.")

    def __add_satellite_repo(self, satellite_compose, targetmachine_ip=""):
        cmd = ('cat <<EOF > /etc/yum.repos.d/satellite.repo\n'
            '[sat6]\n'
            'name=sat6\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
             
            '[sat6-capsule]\n'
            'name=Satellite 6 Capsule Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Capsule/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
             
            '[sat6-rhcommon]\n'
            'name=Satellite 6 RH Common Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/sattools/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (satellite_compose, satellite_compose, satellite_compose)
            )
        ret, output = self.runcmd(cmd, "add satellite repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to add satellite repo.")
        else:
            raise FailException("Test Failed - Failed to add satellite repo.")

    def __add_satellite62_repo(self, satellite_compose, targetmachine_ip=""):
        cmd = ('cat <<EOF > /etc/yum.repos.d/satellite.repo\n'
            '[sat6]\n'
            'name=sat6\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/Satellite/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
              
            '[sat6-capsule]\n'
            'name=Satellite 6 Capsule Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/Capsule/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
              
            '[sat6-rhcommon]\n'
            'name=Satellite 6 RH Common Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/sattools/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (satellite_compose, satellite_compose, satellite_compose)
            )
        ret, output = self.runcmd(cmd, "add satellite repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to add satellite repo.")
        else:
            raise FailException("Test Failed - Failed to add satellite repo.")

    def __add_satellite_ohsnap_repo(self, satellite_compose, targetmachine_ip=""):
        cmd = ('cat <<EOF > /etc/yum.repos.d/satellite.repo\n'
            '[sat6]\n'
            'name=Satellite 6\n'
            'baseurl=%s\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (satellite_compose)
            )
        ret, output = self.runcmd(cmd, "add satellite ohsnap repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to add satellite repo.")
        else:
            raise FailException("Test Failed - Failed to add satellite repo.")

    def __install_katello(self, targetmachine_ip=""):
        for item in range(3):
            cmd = "yum install -y katello-headpin-all"
            ret, output = self.runcmd(cmd, "yum install -y katello-headpin-all", targetmachine_ip, timeout=7200)
            # here it always time out, need to research reason
            if ret == 0:
                logger.info("Succeeded to run %s in the %s cycle." % (cmd, item))
                break
            logger.info("Failed to run %s in the %s cycle, run it again." % (cmd, item))
        else:
            raise FailException("Test Failed - Failed to run yum install -y katello-headpin-all.")

    def __deploy_sam(self, targetmachine_ip=""):
        cmd = "katello-configure --deployment=sam --user-pass=admin"
        ret, output = self.runcmd(cmd, "katello-configure", targetmachine_ip, timeout=7200)
        if ret == 0:
            logger.info("Succeeded to run katello-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run katello-configure --deployment=sam --user-pass=admin.")

    def __install_satellite(self, targetmachine_ip=""):
        cmd = "yum install -y katello"
        ret, output = self.runcmd(cmd, "yum install -y katello", targetmachine_ip, timeout=7200)
        if ret == 0:
            logger.info("Succeeded to run yum install -y katello.")
        else:
            raise FailException("Test Failed - Failed to run yum install -y katello.")

    def __deploy_satellite(self, targetmachine_ip=""):
        cmd = "katello-installer --foreman-admin-password=admin"
#         cmd = "foreman-installer --scenario katello --foreman-admin-password=admin"
        ret, output = self.runcmd(cmd, "katello-installer", targetmachine_ip, timeout=7200)
#         if ret == 0:
#             logger.info("Succeeded to run katello-installer --foreman-admin-password=admin.")
#         else:
#             raise FailException("Test Failed - Failed to run katello-installer --foreman-admin-password=admin.")

    def __install_satellite62(self, targetmachine_ip=""):
        for item in range(3):
            cmd = "yum install -y satellite"
            ret, output = self.runcmd(cmd, "yum install -y satellite", targetmachine_ip, timeout=7200)
            if ret == 0:
                logger.info("Succeeded to run %s in the %s cycle." % (cmd, item))
                break
            logger.info("Failed to run %s in the %s cycle, run it again." % (cmd, item))
        else:
            raise FailException("Test Failed - Failed to run yum install -y satellite.")

    def __deploy_satellite62(self, targetmachine_ip=""):
        cmd = "satellite-installer --scenario satellite --foreman-admin-password=admin"
        ret, output = self.runcmd(cmd, "satellite-installer", targetmachine_ip , timeout=7200)

    def __import_manifest(self, targetmachine_ip=""):
        # only support remote run
        self.__upload_manifest(targetmachine_ip)
        cmd = "headpin -u admin -p admin provider import_manifest --org=ACME_Corporation --name='Red Hat' --file=/root/sam_install_manifest.zip"
        ret, output = self.runcmd(cmd, "import menifest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to import menifest.")
        else:
            raise FailException("Test Failed - Failed to import menifest.")

    def __import_manifest_satellite(self, targetmachine_ip=""):
        # only support remote run
        self.__upload_manifest(targetmachine_ip)
        # cmd = "hammer subscription upload --organization-label Default_Organization --file /root/sam_install_manifest.zip"
        cmd = "hammer -u admin -p admin subscription upload --organization-label Default_Organization --file /root/sam_install_manifest.zip"
        ret, output = self.runcmd(cmd, "hammer manifest upload", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to import menifest.")
            # After manifest is imported, enable repos of product(69.pem) for rhel7 and rhel6(bug 1256615 and bug 1436565)
            cmd1 = "releasever=(7Server 7.0 7.1 7.2 7.3); for i in ${releasever[@]}; do hammer -u admin -p admin repository-set enable --id 2456 --product='Red Hat Enterprise Linux Server' --organization-id 1 --releasever $i --basearch x86_64; done"
            ret, output = self.runcmd(cmd1, "enable repos of rhel7", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to enable repos of rhel7.")
            else:
                raise FailException("Test Failed - Failed to enable repos of rhel7.")
            cmd2 = "releasever=(6Server 6.1 6.2 6.3 6.4 6.5 6.6 6.7 6.8 6.9); for i in ${releasever[@]}; do hammer -u admin -p admin repository-set enable --id 168 --product='Red Hat Enterprise Linux Server' --organization-id 1 --releasever $i --basearch x86_64; done"
            ret, output = self.runcmd(cmd2, "enable repos of rhel6", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to enable repos of rhel6.")
            else:
                raise FailException("Test Failed - Failed to enable repos of rhel6.")
        else:
            raise FailException("Test Failed - Failed to import menifest.")

    def __upload_manifest(self, targetmachine_ip=""):
        # self.remote_put(sam_manifest, "/root/%s" % manifest_name)
        cmd = "wget %s/sam_install_manifest.zip -P /root/" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget manifest to /root/", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget manifest to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget manifest to /root/.")

    def __add_rhevm_repo(self, rhevm_compose, targetmachine_ip=""):
        cmd = ('cat <<EOF > /etc/yum.repos.d/rhevm355.repo\n'
            '[rhevm355]\n'
            'name=rhevm355\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'baseurl=http://bob.eng.lab.tlv.redhat.com/builds/latest_vt/el%s/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[JBoss_latest]\n'
            'name=JBoss_latest\n'
            'baseurl=http://download.eng.pnq.redhat.com/released/JBEAP-6/6.4.4/composes/JBEAP-6.4.4-RHEL-%s/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[rhevm-mgent]\n'
            'name=rhevm-mgent\n'
            'baseurl=http://download.eng.bos.redhat.com/rel-eng/RHEV/3.5.1/latest/mgmt-agents/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[RHEL_6.7_optional]\n'
            'name=RHEL_6.7_optional\n'
            'baseurl=http://download.eng.tlv.redhat.com/released/RHEL-6-Supplementary/6.7/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (rhevm_compose, rhevm_compose)
            )
        ret, output = self.runcmd(cmd, "add rhevm repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to add rhevm repo.")
        else:
            raise FailException("Test Failed - Failed to add rhevm repo.")

    def __add_rhevm36_repo(self, rhevm_compose, targetmachine_ip=""):
        cmd = ('cat <<EOF > /etc/yum.repos.d/rhevm36.repo\n'
            '[rhevm36]\n'
            'name=rhevm36\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'baseurl=http://bob.eng.lab.tlv.redhat.com/builds/latest_3.6/el%s/\n'
            'enabled=1\n'
            'gpgcheck=0\n'

            '[JBoss_latest]\n'
            'name=JBoss_latest\n'
            'baseurl=http://download.eng.tlv.redhat.com/pub/rhel/released/JBEAP-6/latest-released/JBEAP-6.4.8-RHEL-6/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'

            '[rhevm-mgent]\n'
            'name=rhevm-mgent\n'
            'baseurl=http://download.eng.bos.redhat.com/rel-eng/RHEV/3.5.1/latest/mgmt-agents/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'

            '[RHEL_6.8_optional]\n'
            'name=RHEL_6.8_optional\n'
            'baseurl=http://download.eng.tlv.redhat.com/released/RHEL-6-Supplementary/6.8/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (rhevm_compose)
            )
        ret, output = self.runcmd(cmd, "add rhevm repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to add rhevm repo.")
        else:
            raise FailException("Test Failed - Failed to add rhevm repo.")

    def __rm_beaker_repo(self, targetmachine_ip=""):
        cmd = "mkdir /etc/yum.repos.d/repo-beaker; mv /etc/yum.repos.d/beaker-* /etc/yum.repos.d/repo-beaker"
        ret, output = self.runcmd(cmd, "move all beaker repo to /etc/yum.repos.d/repo-beaker", targetmachine_ip)

    def __add_rhevm40_repo(self, rhevm_compose, targetmachine_ip=""):
        # stage issue, disabel repo temporarily
        cmd = "yum-config-manager --disable rhel-7-server-rt-beta-rpms rhel-7-server-tus-rpms"
        ret, output = self.runcmd(cmd, "disable rhel-7-server-rt-beta-rpms", targetmachine_ip)

        cmd = "rpm -qa | grep rhev-release"
        ret, output = self.runcmd(cmd, "check rhev-latest package status", targetmachine_ip)
        if "rhev-release" in output:
            logger.info("Succeeded to check rhev-latest package exist.")
        else:
            logger.info("rhev-latest package is not install, need to install.")
            cmd = "rpm -Uvh http://bob.eng.lab.tlv.redhat.com/builds/latest_4.0/rhev-release-latest-4.0.noarch.rpm"
            ret, output = self.runcmd(cmd, "install rhev-latest package", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to install rhev-latest package.")
            else:
                raise FailException("Test Failed - Failed to install rhev-latest package.")
        cmd = ('cat <<EOF > /etc/yum.repos.d/rhevm40.repo\n'
            '[rhevm40]\n'
            'name=rhevm40\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'baseurl=http://bob.eng.lab.tlv.redhat.com/builds/latest_4.0/el%s/\n'
            'enabled=1\n'
            'gpgcheck=0\n'

            '[test_rhel_z_stream]\n'
            'name=RHEL_7.2_candidate_zstream\n'
            'baseurl=http://download.eng.tlv.redhat.com/rel-eng/repos/rhel-7.2-z-candidate/x86_64/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[rhel-7.2-supplementary]\n'
            'name=rhel-7.2-supplementary\n'
            'baseurl=http://download.eng.tlv.redhat.com/pub/rhel/released/Supp-RHEL-7/7.2/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (rhevm_compose, rhevm_compose)
            )
        ret, output = self.runcmd(cmd, "add rhevm repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to add rhevm repo.")
        else:
            raise FailException("Test Failed - Failed to add rhevm repo.")

    def __install_rhevm(self, targetmachine_ip=""):
        for item in range(3):
            cmd = "yum install -y rhevm"
            ret, output = self.runcmd(cmd, "yum install -y rhevm", targetmachine_ip, timeout=36000)
            if ret == 0:
                logger.info("Succeeded to run %s in the %s cycle." % (cmd, item))
                break
            logger.info("Failed to run %s in the %s cycle, run it again." % (cmd, item))
        else:
            raise FailException("Test Failed - Failed to run yum install -y rhevm.")

    def __deploy_rhevm(self, targetmachine_ip=""):
        ''' wget rhevm config file to rhevm '''
        cmd = "wget -P /root/ %s/rhevm355_config" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget rhevm config file to rhevm")
        else:
            raise FailException("Failed to wget rhevm config file to rhevm")
        rhevm_hostname = self.get_hostname(targetmachine_ip)
        cmd = "sed -i -e 's/rhevmhostname/%s/g' /root/rhevm355_config" % rhevm_hostname
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")

        cmd = "rhevm-setup --config-append=/root/rhevm355_config"
        ret, output = self.runcmd(cmd, "rhevm-configure", targetmachine_ip, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run rhevm-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run rhevm-configure --deployment=sam --user-pass=admin.")

    def __deploy_rhevm36(self, targetmachine_ip=""):
        ''' wget rhevm config file to rhevm '''
        cmd = "wget -P /root/ %s/rhevm36_config" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget rhevm config file to rhevm")
        else:
            raise FailException("Failed to wget rhevm config file to rhevm")
        rhevm_hostname = self.get_hostname(targetmachine_ip)
        cmd = "sed -i -e 's/rhevmhostname/%s/g' /root/rhevm36_config" % rhevm_hostname
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")

        cmd = "engine-setup --config-append=/root/rhevm36_config"
        ret, output = self.runcmd(cmd, "rhevm-configure", targetmachine_ip , timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run rhevm-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run rhevm-configure --deployment=sam --user-pass=admin.")

    def __deploy_rhevm40(self, targetmachine_ip=""):
        ''' wget rhevm config file to rhevm '''
        conf_file = "rhevm_40_2.conf"
        cmd = "wget -P /root/ %s/%s" % (self.get_vw_cons("data_folder"), conf_file)
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget rhevm config file to rhevm")
        else:
            raise FailException("Failed to wget rhevm config file to rhevm")
        rhevm_hostname = self.get_hostname(targetmachine_ip)
        cmd = "sed -i -e 's/rhevmhostname/%s/g' /root/%s" % (rhevm_hostname, conf_file)
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")
        cmd = "engine-setup --config-append=/root/%s" % conf_file
        ret, output = self.runcmd(cmd, "rhevm-configure", targetmachine_ip, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run rhevm-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run rhevm-configure --deployment=sam --user-pass=admin.")

    def __deploy_rhevm41(self, targetmachine_ip=""):
        ''' wget rhevm config file to rhevm '''
        conf_file = "rhevm_41.conf"
        cmd = "wget -P /root/ %s/%s" % (self.get_vw_cons("data_folder"), conf_file)
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget rhevm config file to rhevm")
        else:
            raise FailException("Failed to wget rhevm config file to rhevm")
        rhevm_hostname = self.get_hostname(targetmachine_ip)
        cmd = "sed -i -e 's/rhevmhostname/%s/g' /root/%s" % (rhevm_hostname, conf_file)
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")
        cmd = "engine-setup --config-append=/root/%s" % conf_file
        ret, output = self.runcmd(cmd, "rhevm-configure", targetmachine_ip, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run rhevm-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run rhevm-configure --deployment=sam --user-pass=admin.")
