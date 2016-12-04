'''
Use virsh API to manipulate vms
'''
from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException
from utils.libvirtAPI.Python.xmlbuilder import XmlBuilder

class VirshCommand(Command):

    def create_vm(self, guest_name, guest_compose):
        self.__create_storage()
#         self.__unattended_install(guest_name, guest_compose)
#         return self.__check_vm_available(guest_name), "root", "redhat"
        # here user virt-clone to get a sam guest
        # you need to install a "RHEL6.6-Server-GA-AUTO" guest manually first
        # modify eth0, remove HWADDR and UUID, or else you will be failed to get dhcp IP
        self.clone_vm("AUTO-RHEL6.6-Server-GA", guest_name)
        return self.start_vm(guest_name), "root", "red2015"

    def define_vm(self, guest_name, guest_path):
        cmd = "[ -f /root/%s.xml ]" % (guest_name)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0 :
            logger.info("Generate guest %s xml." % guest_name)
            params = {"guestname":guest_name, "guesttype":"kvm", "source": "switch", "ifacetype" : "bridge", "fullimagepath":guest_path }
            xml_obj = XmlBuilder()
            domain = xml_obj.add_domain(params)
            xml_obj.add_disk(params, domain)
            xml_obj.add_interface(params, domain)
            dom_xml = xml_obj.build_domain(domain)
            logger.info("Succeeded to generate define xml:%s." % dom_xml)
            self.define_xml_gen(guest_name, dom_xml)
        cmd = "virsh define /root/%s.xml" % (guest_name)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0 or "already exists" in output:
            logger.info("Succeeded to define guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to define guest %s." % guest_name)
        self.list_vm()

    def define_xml_gen(self, guest_name, xml):
        cmd = "echo '%s' > /root/%s.xml" % (xml, guest_name)
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
        cmd = "virsh destroy %s" % (guest_name)
        ret, output = self.run(cmd, timeout=None)
        if ret == 0:
            logger.info("Succeeded to shutdown guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to shutdown guest %s." % guest_name)

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
        guest_mac = self.__get_dom_mac_addr(guest_name)
        while True:
            guestip = self.__mac_to_ip(guest_mac)
            if guestip != "" and (not "can not get ip by mac" in guestip):
                return guestip
            if terminate_time < time.time():
                raise OSError("Process timeout has been reached")
            logger.debug("Check guest IP, wait 10 seconds ...")
            time.sleep(10)

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
        generate_ipget_cmd = "wget -nc %s/ipget.sh -P /root/ && chmod 777 /root/ipget.sh" % self.get_vw_cons("data_folder")
        ret, output = self.run(generate_ipget_cmd)
        if ret == 0 or "already there" in output:
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
