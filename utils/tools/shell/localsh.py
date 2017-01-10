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

    @classmethod
    def run_pexpect(self, cmd, password=""):
        """ run interactive command locally via pexpect """
        import utils.tools.pexpect as pexpect
        logger.info(">>>Local Interactive Run: %s" % cmd)
        child = pexpect.spawn(cmd, timeout=600, maxread=2000, logfile=None)
        while True:
            index = child.expect(['(yes\/no)', '(?i)password:', pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                child.sendline("yes")
            elif index == 1:
                child.sendline("red2015")
            elif index == 2:
                retcode, stdout = child.exitstatus, child.before
                logger.info("<<<Return Code: %s" % retcode)
                logger.info("<<<Output:\n%s" % stdout)
                return retcode, stdout
            elif index == 3:
                retcode, stdout = "-1", "Command terminated due to timeout ..."
                logger.info("<<<Return Code: %s" % retcode)
                logger.info("<<<Output:\n%s" % stdout)
                return retcode, stdout

    @classmethod
    def run_git(self, git_cmd, git_dir, password="redhat"):
        """ run git command """
        if git_dir != "":
            os.chdir(git_dir)
        return self.run_pexpect(git_cmd, password)
