from utils.configs import Configs
import time
from utils import logger
from utils import constants
from utils.tools.xmlparser.buildsparser import BuildsParser
from utils.tools.htmlparser import htmlsource
from utils.tools.htmlparser.buildparser import BuildParser

class Install(object):
    '''
    Abstract class, template for installation
    '''
    conf_file_name = ""
    product_name = ""
    confs = None

    def __init__(self):
        '''
        Parse configure file
        '''
        self.confs = Configs(self.conf_file_name)
        self.product_name = self.confs._confs["version"]

    def start(self):
        new_build = self.check_build().strip("/")
        if new_build == "No New Build":
            logger.info("No %s new build available yet, just exit ..." % self.product_name)
        else:
            logger.info("Found %s new build %s, begin installing ..." % (self.product_name, new_build))
            self.install_host()
            if self.confs._confs["install_guest"] == "yes":
                self.install_guest(new_build)
            else:
                self.find_guest(new_build)
            self.install_product(new_build)

    def check_build(self):
        # check the last build from html, if not in xml file then it's a new build
        last_build = BuildParser().parse(self.product_name)[-1]
        if not last_build in BuildsParser().get_builds(self.product_name):
            BuildsParser().add_build(self.product_name, last_build)
            self.check_build_status(last_build)
            return 0, last_build.strip("/")
        else:
            return -1, last_build.strip("/")

    def check_build_status(self, build):
        if "RHEL5" in build or "RHEL-6.6" in build:
            pass
        else:
            # check STATUS file, if FINISHED, begin installing
            status_file = constants.get_build_tree(build) + "/" + build + "/" + "STATUS"
            logger.info("Status file is : %s." % status_file)
            while True:
                if "FINISHED" in htmlsource.get_html_source(status_file):
                    logger.info("Build %s is in Finished status, going on ..." % build)
                    break
                else:
                    time.sleep(60)
                    logger.info("Build %s is not in Finished status yet, wait 1 minute ..." % build)

    def install_host(self):
        raise NotImplementedError, "Cannot call abstract method"

    def install_guest(self, guest_name):
        raise NotImplementedError, "Cannot call abstract method"

    def find_guest(self, guest_name):
        raise NotImplementedError, "Cannot call abstract method"

    def install_product(self, machine_ip, compose):
        raise NotImplementedError, "Cannot call abstract method"
