import ConfigParser
from utils import *

class Configs(object):
    """
    Reads configuration
    """
    def __init__(self, conf_file_name):
        self.logger = logging.getLogger(LOGGER_NAME)
        conf_parser = ConfigParser.RawConfigParser()
        conf_file = os.path.join(self.get_conf_path(), conf_file_name)
        self._confs = None

        if conf_parser.read(conf_file):
            self._confs = {}
            for section in conf_parser.sections():
                for option in conf_parser.options(section):
                    self._confs[
                        "%s" % option
                    ] = conf_parser.get(section, option)

        logger.debug(conf_file)
        self.log_confs()

    @property
    def confs(self):
        if self._confs is None:
            self.logger.error(
                'Please make sure that you have the correct configure file.')
            sys.exit(-1)
        return self._confs

    def get_conf_path(self):
        """
        Returns correct path to config file
        """
        return os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "conf"))

    def log_confs(self):
        """
        Display configures
        """
        keylist = self.confs.keys()
        keylist.sort()
        self.logger.info("")
        self.logger.info("# ** ** **begin list configures ** ** **")
        for key in keylist:
            self.logger.info("%s = %s" % (key, self.confs[key]))
        self.logger.info("# ** ** **end list configures ** ** **")
        self.logger.info("")

if __name__ == "__main__":
    conf = Configs()
