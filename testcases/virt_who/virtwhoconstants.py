from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class VIRTWHOConstants(object):
    virt_who_cons = {
                    "KVM_GUEST_NAME":"6.5_Server_x86_64",

                    "beaker_image_server" : "10.16.96.131:/home/samdata",
#                     "local_image_path" : "/root/images",
                    "nfs_image_path" : "/root/images_nfs",
                    "local_mount_point" : "/tmp/images_mnt",

                    "esx_guest_url" : "http://10.66.100.116/projects/sam-virtwho/esx_guest/",

                    "SAM_USER":"admin",
                    "SAM_PASS":"admin",

                    "ESX_HOST":"10.66.128.77",
                    "ESX_GUEST_NAME":"ESX_7.1_Server_x86_64",

                    "VIRTWHO_ESX_OWNER" : "ACME_Corporation",
                    "VIRTWHO_ESX_ENV" : "Library",
                    "VIRTWHO_ESX_SERVER" : "10.66.78.27",
                    "VIRTWHO_ESX_USERNAME" : "administrator@vsphere.local",
                    "VIRTWHO_ESX_PASSWORD" : "qwer1234P!",


                    # limited subscription
                    "productid_guest" : "RH0604852",
                    "productname_guest" : "Red Hat Enterprise Linux Server for HPC Compute Node",
                    "guestlimit" : "1",
                    # unlimited subscription
                    "productid_unlimited_guest" : "SYS0395",
                    "productname_unlimited_guest" : "Red Hat Employee Subscription",
                    "guestlimit_unlimited_guest" : "Unlimited",

                    }
#     image_machine_imagepath = "ENT_TEST_MEDIUM/images"
#     # Note: make sure all the guest names are different with each other.
#     imagenfspath = "/home/ENT_TEST_MEDIUM/imagenfs"
#     imagepath = "/home/ENT_TEST_MEDIUM/images"
#     imagepath_kvm = "/home/ENT_TEST_MEDIUM/images/kvm"
#     imagepath_xen_pv = "/home/ENT_TEST_MEDIUM/images/xen/xen-pv"
#     imagepath_xen_fv = "/home/ENT_TEST_MEDIUM/images/xen/xen-fv"

    def get_constant(self, name):
        return self.virt_who_cons[name]
