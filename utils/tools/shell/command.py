from utils import *
from utils.tools.shell.remotesh import RemoteSH
from utils.tools.shell.localsh import LocalSH
from utils.exception.failexception import FailException

class Command(object):
    remote_ip = username = password = ""
    def __init__(self, remote_ip=None, username=None, password=None):
        if remote_ip != "" and remote_ip != None:
            self.remote_ip = remote_ip
            self.username = username
            self.password = password
            logger.info("command run in: %s" % self.remote_ip)
        else:
            self.remote_ip = get_exported_param("REMOTE_IP")
            self.username = "root"
            self.password = "red2015"
            logger.info("command run in: %s" % self.remote_ip)

    def run(self, cmd, timeout=None, comments=True):
        if self.remote_ip == None:
            ret, output = LocalSH.local_run(cmd, timeout, comments)
        else:
            ret, output = RemoteSH.remote_run(cmd, self.remote_ip, self.username, self.password, timeout, comments)
        return ret, output

    def run_interact(self, cmd, timeout=None, comments=True):
        ret, output = RemoteSH.run_paramiko_interact(cmd, self.remote_ip, self.username, self.password, timeout)
        return ret, output
