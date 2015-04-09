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
#         retcode, stdout = self.run_subprocess(cmd, timeout)
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
        import pexpect
        logger.info(">>>Local Interactive Run: %s" % cmd)
        child = pexpect.spawn(cmd, timeout=60, maxread=2000, logfile=None)
        while True:
#             print child.exitstatus, child.before
            index = child.expect(['(yes\/no)', '(?i)password:', pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                child.sendline("yes")
            elif index == 1:
                child.sendline(password)
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

    @classmethod
    def run_popen(self, cmd, timeout=None):
        import os
        output = os.popen(cmd)
        print output
    @classmethod
    def run_system(self, cmd, timeout=None):
        import os
        os.system(cmd)
    @classmethod
    def run_commands(self, cmd, timeout=None):
        import commands
        retcode, stdout = commands.getstatusoutput(cmd)
        return retcode, stdout
        
# child1 = subprocess.Popen(["dir","/w"], stdout=subprocess.PIPE,shell=True)  
# child2 = subprocess.Popen(["wc"], stdin=child1.stdout,stdout=subprocess.PIPE,shell=True)  
# out = child2.communicate()  

if __name__ == "__main__":
#     LocalSH.local_run("/usr/bin/virt-install --network=bridge:br0 --initrd-inject=/root/workspace/entitlement/data/kickstart/unattended/rhel-server-6-series.ks --extra-args \"ks=file:/rhel-server-6-series.ks\" --name=AUTO-SAM-1.4.0-RHEL-6-20140512.0 --disk path=/home/auto-imgs/AUTO-SAM-1.4.0-RHEL-6-20140512.0.img,size=20 --ram 2048 --vcpus=2 --check-cpu --accelerate --hvm --location=http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.5/Server/x86_64/os/ ", 10)
#     LocalSH.local_run("sleep 10", 5)
    LocalSH.run_pexpect("git pull")
