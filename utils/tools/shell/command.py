from utils import *
from utils.tools.shell.remotesh import RemoteSH
from utils.tools.shell.localsh import LocalSH
from utils.exception.failexception import FailException

class Command(object):
    def __init__(self, remote_ip=None, username=None, password=None):
        if remote_ip != "" and remote_ip != None:
            logger.info("command run in: %s" % remote_ip)
            self.remote_ip = remote_ip
            self.username = username
            self.password = password

    def run(self, cmd, timeout=None, comments=True):
        if self.remote_ip == None:
            ret, output = LocalSH.local_run(cmd, timeout, comments)
        else:
            ret, output = RemoteSH.remote_run(cmd, self.remote_ip, self.username, self.password, timeout, comments)
        return ret, output
