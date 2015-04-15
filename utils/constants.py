"""
Defines various constants
"""
import os

# configure module
RHSM_CONF = "rhsm.conf"
RHSM_GUI_CONF = "rhsm_gui.conf"
SAM_INSTALLATION_CONF = "sam_installation.conf"
RHEL_INSTALLATION_CONF = "rhel_installation.conf"
VIRTWHO_KICKSTART_CONF = "virtwho_kickstart.conf"
OPENSTACK_INSTALLATION_CONF = "openstack_installation.conf"

# virt-who configure
VIRTWHO_RUN_CONF = "virtwho_run.conf"
VIRTWHO_KVM_CONF = "virtwho_kvm.conf"
VIRTWHO_ESX_CONF = "virtwho_esx.conf"
VIRTWHO_XEN_FV_CONF = "virtwho_xen_fv.conf"
VIRTWHO_ESX_PV_CONF = "virtwho_esx_pv.conf"

# beaker job
SAM_JOB = "sam_latest_install_job_sample.xml"
KVM_JOB = "virtwho_kvm_xen_job_sample.xml"
ESX_JOB = "virtwho_esx_job_sample.xml"
RHSM_JOB = "rhsm_job_sample.xml"
RHSM_GUI_JOB = "rhsm_gui_job_sample.xml"

# log module
LOGGER_NAME = "entitlement"
LOGGER_FILE = "entitlement.log"

# build location
SAM_BUILD_URL = "http://download.devel.redhat.com/devel/candidate-trees/SAM/"
RHEL_BUILD_URL = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/"

# path environments
DATA_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "data/"))
RUNTIME_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "runtime/"))
BEAKER_JOBS_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "data/beakerjobs/"))
GUI_IMG_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "runtime/captures/"))


RHEL5_PACKAGES = [
                "@admin-tools",
                "@base",
                "@core",
                "@editors",
                "@java",
                "@legacy-software-support",
                "@sound-and-video",
                "@text-internet",
                "@base-x",
                "kexec-tools",
                "iscsi-initiator-utils",
                "bridge-utils",
                "fipscheck",
                "device-mapper-multipath",
                "sgpio",
                "emacs",
                "libsane-hpaio",
                "qpixman-devel",
                "qspice-libs-devel",
                "gpxe-roms-qemu",
                "etherboot-roms",
                "etherboot-pxes",
                "libvirt-cim",
                "kvm-tools",
                "etherboot-roms-kvm",
                "libcmpiutil",
                "qcairo-devel",
                "qspice",
                "qffmpeg-devel",
                "iasl",
                "perl-Sys-Virt",
                "nmap",
                "expect",
                "pexpect",
                "qemu-img",
                "gnutls-utils",
                "gcc",
                "make",
                "tigervnc-server",
]

RHEL7_PACKAGES = [
                "@base",
                "@core",
                "@virtualization-client",
                "@virtualization-hypervisor",
                "@virtualization-platform",
                "@virtualization-tools",
                "@virtualization",
                "@desktop-debugging",
                "@dial-up",
                "@fonts",
                "@gnome-desktop",
                "@guest-desktop-agents",
                "@input-methods",
                "@internet-browser",
                "@multimedia",
                "@print-client",
                "@x11",
                "nmap",
                "bridge-utils",
                "tunctl",
                "rpcbind",
                "qemu-kvm-tools",
                "expect",
                "pexpect",
                "git",
                "make",
                "gcc",
                "tigervnc-server",
]

GUI_PACKAGES = [
              "python-twisted",
              "at-spi-python",
              ]

PACKAGES = [
            "@base",
            "@core",
            "@virtualization-client",
            "@virtualization-hypervisor",
            "@virtualization-platform",
            "@virtualization-tools",
            "@virtualization",
            "@desktop-debugging",
            "@dial-up",
            "@fonts",
            "@gnome-desktop",
            "@guest-desktop-agents",
            "@input-methods",
            "@internet-browser",
            "@multimedia",
            "@print-client",
            "@x11",
            "nmap",
            "bridge-utils",
            "tunctl",
            "rpcbind",
            "qemu-kvm-tools",
            "expect",
            "pexpect",
            "git",
            "make",
            "gcc",
            "tigervnc-server",
]

def get_build_tree(product_name):
    build_url = ""
    product_name = product_name.upper()
    if product_name.startswith("SAM"):
        build_url = SAM_BUILD_URL
    elif product_name.startswith("RHEL"):
        build_url = RHEL_BUILD_URL
    else:
        # logger.error("Unknown product name : %s " % product_name)
        build_url = "Unknown"
    return build_url
