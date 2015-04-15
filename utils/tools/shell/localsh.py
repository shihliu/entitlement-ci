import time, os, signal
import subprocess
from utils import logger

class LocalSH(object):
    """
    Run shell in local machine via subprocess
    """

    @classmethod
    def local_run(self, cmd, timeout=None, comments=True):
        """
        Executes SSH command on local machine.
        """
        if comments:
            logger.info(">>>Local Run: %s" % cmd)
        retcode, stdout = self.run_subprocess(cmd, timeout)
        if comments:
            logger.info("<<<Return Code: %s" % retcode)
            logger.info("<<<Output:\n%s" % stdout)
        return retcode, stdout

    @classmethod
    def run_subprocess(self, cmd, timeout=None):
        """
        Executes SSH command on local machine.
        """
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        # if timeout is not set wait for process to complete
        if timeout == None:
            retcode = process.wait()
            stdout, stderr = process.communicate()
        else:
            terminate_time = time.time() + timeout
            while process.poll() == None:
                logger.debug("Command running, wait 1 minute ...")
                time.sleep(60)
                if terminate_time < time.time():
                    logger.debug("Kill process, return -1 ...")
                    process.kill()
                    retcode = -1
                    stdout = "Command terminated due to timeout ..."
                    return retcode, stdout
            retcode = process.wait()
            stdout = process.communicate()
        return retcode, stdout