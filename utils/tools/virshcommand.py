'''
Use virsh API to manipulate vms
'''
from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class VirshCommand(Command):

    def create_vm(self, guest_name, guest_compose):
        self.__create_storage()
#         self.__unattended_install(guest_name, guest_compose)
#         return self.__check_vm_available(guest_name), "root", "redhat"
        # here user virt-clone to get a sam guest
        # you need to install a "RHEL6.6-Server-GA-AUTO" guest manually first
        # modify eth0, remove HWADDR and UUID, or else you will be failed to get dhcp IP
        self.clone_vm("AUTO-RHEL6.6-Server-GA", guest_name)
        return self.start_vm(guest_name), "root", "redhat"

    def define_vm(self, guest_name, guest_path):
        self.define_xml_gen(guest_name, guest_path)
        cmd = "virsh define /root/%s.xml" % (guest_name)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to define guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to define guest %s." % guest_name)
        self.list_vm()

    def define_xml_gen(self, guest_name, guest_path):
        cmd = ("cat > /root/%s.xml <<EOF\n"
                "<domain type='kvm'>\n"
                "  <name>%s</name>\n"
                "  <memory unit='KiB'>1048576</memory>\n"
                "  <currentMemory unit='KiB'>1048576</currentMemory>\n"
                "  <vcpu placement='static'>1</vcpu>\n"
                "  <os>\n"
                "    <type arch='x86_64' machine='rhel6.3.0'>hvm</type>\n"
                "    <boot dev='hd'/>\n"
                "  </os>\n"
                "  <features>\n"
                "    <acpi/>\n"
                "    <apic/>\n"
                "    <pae/>\n"
                "  </features>\n"
                "  <clock offset='utc'/>\n"
                "  <on_poweroff>destroy</on_poweroff>\n"
                "  <on_reboot>restart</on_reboot>\n"
                "  <on_crash>restart</on_crash>\n"
                "  <devices>\n"
                "    <emulator>/usr/libexec/qemu-kvm</emulator>\n"
                "    <disk type='file' device='disk'>\n"
                "      <driver name='qemu' type='raw' cache='none'/>\n"
                "      <source file='%s'/>\n"
                "      <target dev='vda' bus='virtio'/>\n"
                "      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>\n"
                "    </disk>\n"
                "    <controller type='usb' index='0'>\n"
                "      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>\n"
                "    </controller>\n"
                "    <interface type='network'>\n"
                "      <mac address='52:54:00:32:97:d1'/>\n"
                "      <source network='default'/>\n"
                "      <model type='virtio'/>\n"
                "      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>\n"
                "    </interface>\n"
                "    <serial type='pty'>\n"
                "      <target port='0'/>\n"
                "    </serial>\n"
                "    <console type='pty'>\n"
                "      <target type='serial' port='0'/>\n"
                "    </console>\n"
                "    <input type='tablet' bus='usb'/>\n"
                "    <input type='mouse' bus='ps2'/>\n"
                "    <graphics type='vnc' port='-1' autoport='yes'/>\n"
                "    <sound model='ich6'>\n"
                "      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>\n"
                "    </sound>\n"
                "    <video>\n"
                "      <model type='cirrus' vram='9216' heads='1'/>\n"
                "      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>\n"
                "    </video>\n"
                "    <memballoon model='virtio'>\n"
                "      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>\n"
                "    </memballoon>\n"
                "  </devices>\n"
                "</domain>\n"
                "EOF") % (guest_name, guest_name, guest_path)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to generate virsh define xml in /root/%s.xml " % guest_name)
        else:
            raise FailException("Test Failed - Failed to generate virsh define xml in /root/%s.xml " % guest_name)

    def list_vm(self):
        cmd = "virsh list --all"
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to list all curent guest ")
        else:
            raise FailException("Test Failed - Failed to list all curent guest ")

    def start_vm(self, guest_name):
        cmd = "virsh start %s" % (guest_name)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to start guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to start guest %s." % guest_name)
        return self.__check_vm_available(guest_name)

    def getip_vm(self, guest_name):
        guestip = self.__mac_to_ip(self.__get_dom_mac_addr(guest_name))
        if guestip != "" and (not "can not get ip by mac" in guestip):
            return guestip
        else:
            raise FailException("Test Failed - Failed to get ip of guest %s." % guest_name)

    def shutdown_vm(self, guest_name):
        cmd = "virsh shutdown %s" % (guest_name)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to shutdown guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to shutdown guest %s." % guest_name)
        time.sleep(180)

    def clone_vm(self, guest_name, cloned_guest_name):
        cmd = "virt-clone --original %s --name %s --file=/home/auto-imgs/%s.img" % (guest_name, cloned_guest_name, cloned_guest_name)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to clone guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to clone guest %s." % guest_name)

    def __unattended_install(self, guest_name, guest_compose):
        '''
        install a guest with virt-install command, need virt-install tool installed:
        can not quite normally, check ip to make sure guest installed temperatelly
        '''
        # self.__create_storage()
        # self.__create_img(guest_name)
        self.remote_put("/root/workspace/entitlement/data/kickstart/unattended/minimal.ks", "/root/minimal.ks")
        cmd = ('virt-install '
#                '--network=bridge:br0 '
               '--initrd-inject=/root/minimal.ks '
               '--extra-args "ks=file:/minimal.ks" '
               '--name=%s '
               '--disk path=/home/auto-imgs/%s.img,size=20 '
               '--ram 2048 '
               '--vcpus=1 '
               '--check-cpu '
               '--accelerate '
               '--hvm '
               '--location=%s '
#                 '--nographics '
               % (guest_name, guest_name, guest_compose))
#         from utils.tools.shell.remotesh import RemoteSH
#         RemoteSH.run_pexpect(cmd, self.remote_ip, "root", "redhat")
        ret, output = self.run(cmd, timeout=600)
        if ret == 0:
            logger.info("Succeeded to unattended_install guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to unattended_install guest %s." % guest_name)
        time.sleep(120)

    def __check_vm_available(self, guest_name, timeout=600):
        terminate_time = time.time() + timeout
        while True:
            guestip = self.__mac_to_ip(self.__get_dom_mac_addr(guest_name))
            if guestip != "" and (not "can not get ip by mac" in guestip):
                return guestip
            if terminate_time < time.time():
                raise OSError("Process timeout has been reached")
            logger.debug("Check guest IP, wait 1 minute ...")
            time.sleep(60)

    def __get_dom_mac_addr(self, domname):
        """
        Get mac address of a domain
        Return mac address on SUCCESS or None on FAILURE
        """
        cmd = "virsh dumpxml " + domname + " | grep 'mac address' | awk -F'=' '{print $2}' | tr -d \"[\'/>]\""
        ret, output = self.run(cmd)
        if ret == 0:
            logger.info("Succeeded to get mac address of domain %s." % domname)
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Test Failed - Failed to get mac address of domain %s." % domname)

    def __mac_to_ip(self, mac):
        """
        Map mac address to ip, need nmap installed and ipget.sh in /root/ target machine
        Return None on FAILURE and the mac address on SUCCESS
        """
        if not mac:
            raise FailException("Failed to get guest mac ...")
        generate_ipget_cmd = "wget http://10.66.100.116/projects/sam-virtwho/latest-manifest/ipget.sh -P /root/ | chmod 777 /root/ipget.sh"
        ret, output = self.run(generate_ipget_cmd)
        if ret == 0:
            logger.info("Succeeded to wget ipget.sh to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget ipget.sh to /root/.")
        cmd = "sh /root/ipget.sh %s" % mac
        ret, output = self.run(cmd)
        if ret == 0:
            logger.info("Succeeded to get ip address.")
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Test Failed - Failed to get ip address.")

    def __create_img(self, img_name, path="/home/auto-imgs/", size=20):
        cmd = "qemu-img create -f raw %s%s.img %sG" % (path, img_name, size)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to create image %s." % img_name)
        else:
            raise FailException("Test Failed - Failed to create image %s." % img_name)

    def __create_storage(self, path="/home/auto-imgs/"):
        cmd = "mkdir -p %s" % path
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to create storage")
        else:
            raise FailException("Test Failed - Failed to create storage")

if __name__ == "__main__":
    virsh_command = VirshCommand()
    print virsh_command.create_vm("AUTO-SAM-1.4.0-RHEL-6-20140512.0")
