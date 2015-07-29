from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class RHSMConstants(object):
    sam_cons6 = {
            "username": "admin",
            "password": "admin",
            "baseurl": "https://samserv.redhat.com:443",
            "prefix": "/sam/api",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "SYS0395",
            "pid": "69",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-6-server-rpms",
            "betarepo": "rhel-6-server-beta-rpms",
            "servicelevel": "Premium",
            "releaselist": "6.1,6.2,6.3,6.4,6.5,6.6,6Server",
            }
    sam_cons7 = {
            "username": "admin",
            "password": "admin",
            "baseurl": "https://samserv.redhat.com:443",
            "prefix": "/sam/api",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "SYS0395",
            "pid": "69",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-7-server-rpms",
            "betarepo": "rhel-7-server-beta-rpms",
            "servicelevel": "Premium",
            "releaselist": "7.0,7Server",
            }
    stage_cons = {
            "username": "stage_test_12",
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

    samhostip = get_exported_param("SERVER_IP")

    def runcmd(self, cmd, desc=None, timeout=None, showlogger=True):
        commander = Command(get_exported_param("REMOTE_IP"), "root", "red2015")
        return commander.run(cmd, timeout, showlogger)

    def configure_sam_host(self, samhostip, samhostname):
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to configure /etc/hosts")
        else:
            raise FailException("Failed to configure /etc/hosts")
        cmd = "rpm -qa | grep candlepin-cert-consumer"
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
            cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
            ret, output = self.runcmd(cmd)
            if ret == 0:
                logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
            else:
                raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
        cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        else:
            raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)

    def configure_satellite_host(self, satellitehostip, satellitehostname):
        cmd = "rpm -qa | grep katello-ca-consumer | xargs rpm -e"
        ret, output = self.runcmd(cmd, "if katello-ca-consumer package exist, remove it.")
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean")
        cmd = "rpm -ivh http://%s/pub/katello-ca-consumer-latest.noarch.rpm" % (satellitehostip)
        ret, output = self.runcmd(cmd, "install katello-ca-consumer-latest.noarch.rpm")
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with satellite configuration.")
        else:
            raise FailException("Failed to install candlepin cert and configure the system with satellite configuration.")

    def configure_stage_host(self, stage_name):
        cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % stage_name
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to configure rhsm.conf for stage")
        else:
            raise FailException("Failed to configure rhsm.conf for stage")

    def configure_testing_server(self):
        test_server = get_exported_param("SERVER_TYPE")
        if test_server == "SAM" :
            RHSMConstants().configure_sam_host(get_exported_param("SERVER_IP"), get_exported_param("SERVER_HOSTNAME"))
        if test_server == "SATELLITE" :
            RHSMConstants().configure_satellite_host(get_exported_param("SERVER_IP"), get_exported_param("SERVER_HOSTNAME"))
        elif test_server == "STAGE_CANDLEPIN" :
            RHSMConstants().configure_stage_host("subscription.rhn.stage.redhat.com")
        elif test_server == "CUSTOMER_PORTAL" :
            pass
        else:
            raise FailException("Test Failed - Failed to configure rhsm testing server ... ")

    def get_constant(self, name):
        test_server = get_exported_param("SERVER_TYPE")
        if test_server == "SAM" or test_server == "SATELLITE":
            if self.get_os_serials() == "6":
                return self.sam_cons6[name]
            elif self.get_os_serials() == "7":
                return self.sam_cons7[name]
        elif test_server == "STAGE_CANDLEPIN" :
            return self.stage_cons[name]
        elif test_server == "CUSTOMER_PORTAL" :
            return self.customer_portal_cons[name]

    def get_os_serials(self):
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = self.runcmd(cmd, showlogger=False)
        if ret == 0:
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Failed to get os serials")
