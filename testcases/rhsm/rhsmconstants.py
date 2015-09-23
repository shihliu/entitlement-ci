from utils import *
from utils.tools.shell import command
from utils.exception.failexception import FailException

class RHSMConstants(object):
    sam_cons = {
            "username": "admin",
            "password": "admin",

            "autosubprod": "CloudForms (10-pack)",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "MCT2358",

            "pid": "69",
            "pkgtoinstall": "zsh",
            "servicelevel": "Premium",

            "default_org": "ACME_Corporation",
            "default_org_sat": "Default_Organization",
            # rhel 6 constance
            "productrepo": "rhel-6-server-rpms",
            "betarepo": "rhel-6-server-beta-rpms",
            "releaselist": "6.1,6.2,6.3,6.4,6.5,6.6,6Server",
            # rhel 7 constance
            "productrepo_el7": "rhel-7-server-rpms",
            "betarepo_el7": "rhel-7-server-beta-rpms",
            "releaselist_el7": "7.0,7.1,7Server",

            "proxy_server":"10.66.128.144:3128",
            }
    stage_cons = {
            "username": "stage_test_12_new",
            "password": "redhat",
            "baseurl": "https://subscription.rhn.stage.redhat.com:443",
            "prefix": "/subscription",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "RH0103708",
            "pid": "69",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-6-server-rpms",
            "betarepo": "rhel-6-server-beta-rpms",
            "servicelevel": "PREMIUM",
            "releaselist": "6.1,6.2,6.3,6.4,6Server",
            }
    customer_portal_cons = {
            "username": "qa@redhat.com",
            "password": "uBLybd5JSmkRHebA",
            # please install a localcandlepin whose hostname is localcandlepin.redhat.com
            "baseurl": "https://localcandlepin.redhat.com:8443",
            }

    def configure_sam_host(self, samhostip, samhostname):
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
        ret, output = command.runcmd(cmd, "configure /etc/hosts")
        if ret == 0:
            logger.info("Succeeded to configure /etc/hosts")
        else:
            raise FailException("Failed to configure /etc/hosts")
        cmd = "rpm -qa | grep candlepin-cert-consumer"
        ret, output = command.runcmd(cmd, "check candlepin cert")
        if ret == 0:
            logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
            cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
            ret, output = command.runcmd(cmd, "uninstall candlepin cert")
            if ret == 0:
                logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
            else:
                raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
        cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
        ret, output = command.runcmd(cmd, "install candlepin cert")
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        else:
            raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)

    def configure_satellite_host(self, satellitehostip, satellitehostname):
        if "satellite" in satellitehostname:
            # for satellite installed in qeos
            satellitehostname = satellitehostname + ".novalocal"
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (satellitehostname, satellitehostip, satellitehostname)
        ret, output = command.runcmd(cmd, "configure /etc/hosts")
        if ret == 0:
            logger.info("Succeeded to configure /etc/hosts")
        else:
            raise FailException("Failed to configure /etc/hosts")
        cmd = "rpm -qa | grep katello-ca-consumer | xargs rpm -e"
        ret, output = command.runcmd(cmd, "if katello-ca-consumer package exist, remove it.")
        cmd = "subscription-manager clean"
        ret, output = command.runcmd(cmd, "run subscription-manager clean")
        cmd = "rpm -ivh http://%s/pub/katello-ca-consumer-latest.noarch.rpm" % (satellitehostip)
        ret, output = command.runcmd(cmd, "install katello-ca-consumer-latest.noarch.rpm")
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with satellite configuration.")
        else:
            raise FailException("Failed to install candlepin cert and configure the system with satellite configuration.")

    def configure_stage_host(self, stage_name):
        cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % stage_name
        ret, output = command.runcmd(cmd, "configure rhsm.conf for stage")
        if ret == 0:
            logger.info("Succeeded to configure rhsm.conf for stage")
        else:
            raise FailException("Failed to configure rhsm.conf for stage")

    def configure_testing_server(self):
        test_server = get_exported_param("SERVER_TYPE")
        if test_server == "SAM" :
            RHSMConstants().configure_sam_host(get_exported_param("SERVER_IP"), get_exported_param("SERVER_HOSTNAME"))
        elif test_server == "SATELLITE" :
            RHSMConstants().configure_satellite_host(get_exported_param("SERVER_IP"), get_exported_param("SERVER_HOSTNAME"))
        elif test_server == "STAGE" :
            RHSMConstants().configure_stage_host("subscription.rhn.stage.redhat.com")
        elif test_server == "CUSTOMER_PORTAL" :
            pass
        else:
            raise FailException("Test Failed - Failed to configure rhsm testing server ... ")

    def get_constant(self, name):
        test_server = get_exported_param("SERVER_TYPE")
        if test_server == "SAM":
            if self.os_serial == "7" and name + "_el7" in self.sam_cons:
                return self.sam_cons[name + "_el7"]
            else:
                return self.sam_cons[name]
        if test_server == "SATELLITE":
            if self.os_serial == "7" and name + "_el7" in self.sam_cons:
                return self.sam_cons[name + "_el7"]
            elif name + "_sat" in self.sam_cons:
                return self.sam_cons[name + "_sat"]
            else:
                return self.sam_cons[name]
        elif test_server == "STAGE" :
            return self.stage_cons[name]
        elif test_server == "CUSTOMER_PORTAL" :
            return self.customer_portal_cons[name]

    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RHSMConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if(self.__initialized):
            return
        else:
            self.os_serial = command.get_os_serials()
            self.__initialized = True
