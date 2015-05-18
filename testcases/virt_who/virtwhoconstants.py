from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class VIRTWHOConstants(object):
    virt_who_cons = {
                    "image_machine_ip" : "10.66.100.116:/data/projects/sam-virtwho/pub",
                    "beaker_image_machine_ip" : "10.16.96.131:/home/samdata",
                    "esx_guest_url" : "http://10.66.100.116/projects/sam-virtwho/esx_guest/",

                    "SAM_USER":"admin",
                    "SAM_PASS":"admin",
                    
                    "ESX_HOST":"10.66.128.10",
                    "ESX_GUEST_NAME":"ESX_6.5_Server_x86_64",

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
#     # used for ESX automation
#     esx_host_ip = "10.66.128.163"
#     vmware_cmd_ip = "10.66.79.88"
#     data_store_name = "datastore*"

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(VIRTWHOConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if(self.__initialized): return
        self.__initialized = True

#     def configure_sam_host(self, samhostname, samhostip):
#         ''' configure the host machine for sam '''
#         if samhostname != None and samhostip != None:
#             # add sam hostip and hostname in /etc/hosts
#             cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
#             ret, output = Command().run(cmd)
#             if ret == 0:
#                 logger.info("Succeeded to configure /etc/hosts")
#             else:
#                 raise FailException("Failed to configure /etc/hosts")
#             # config hostname, prefix, port,   and repo_ca_crt by installing candlepin-cert
#             cmd = "rpm -qa | grep candlepin-cert-consumer"
#             ret, output = Command().run(cmd)
#             if ret == 0:
#                 logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
#                 cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
#                 ret, output = Command().run(cmd)
#                 if ret == 0:
#                     logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
#                 else:
#                     raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
#             cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
#             ret, output = Command().run(cmd)
#             if ret == 0:
#                 logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
#             else:
#                 raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
# 
#     def configure_stage_host(self, stage_name):
#         ''' configure the host machine for stage '''
#         # configure /etc/rhsm/rhsm.conf to stage candlepin
#         cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % stage_name
#         ret, output = Command().run(cmd)
#         if ret == 0:
#             logger.info("Succeeded to configure rhsm.conf for stage")
#         else:
#             raise FailException("Failed to configure rhsm.conf for stage")
# 
    def get_constant(self, name):
        return self.virt_who_cons[name]
# 
#     def get_os_serials(self):
#         cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
#         (ret, output) = Command().run(cmd, comments=False)
#         if ret == 0:
#             return output.strip("\n").strip(" ")
#             logger.info("It's successful to get system serials.")
#         else:
#             logger.info("It's failed to get system serials.")
