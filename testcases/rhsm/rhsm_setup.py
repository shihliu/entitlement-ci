from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException
from testcases.rhsm.rhsmconstants import RHSMConstants

class rhsm_setup(unittest.TestCase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.rhsm_gui_sys_setup()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def rhsm_sys_setup(self):
        cmd = "yum install -y @gnome-desktop tigervnc-server python-twisted pexpect pyatspi"
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to install desktop")
        else:
            raise FailException("Test Failed - Failed to install desktop")
        install_ldtp_cmd = "git clone git://anongit.freedesktop.org/git/ldtp/ldtp2.git; cd ldtp2/; python setup.py build; python setup.py install"
        ret, output = self.runcmd(install_ldtp_cmd)
        if ret == 0:
            logger.info("Succeeded to install ldtp.")
        else:
            raise FailException("Test Failed - Failed to install ldtp.")
        cmd = '''mkdir -p /root/.config/autostart; cat > /root/.config/autostart/gnome-terminal.desktop <<EOF
[Desktop Entry]
Type=Application
Exec=gnome-terminal -e ldtp
Hidden=false
X-GNOME-Autostart-enabled=true
Name=ldtpd
Comment=
EOF
'''
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to start ldtp server")
        else:
            raise FailException("Test Failed - Failed to start ldtp server")
        cmd = "service firewalld stop"
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to stop firewalld")
        else:
            raise FailException("Test Failed - Failed to stop firewalld")
        cmd = "vncserver -SecurityTypes None"
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to start vncserver")
        else:
            raise FailException("Test Failed - Failed to start vncserver")
        RHSMConstants().configure_sam_host(get_exported_param("SAM_IP"), get_exported_param("SAM_HOSTNAME"))

    def rhsm_gui_slave_setup(self):
        cmd = "yum install -y @gnome-desktop"
        ret, output = self.runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to install desktop")
        else:
            raise FailException("Test Failed - Failed to install desktop")
        install_ldtp_cmd = "git clone git://anongit.freedesktop.org/git/ldtp/ldtp2.git; cd ldtp2/; python setup.py build; python setup.py install"
        ret, output = self.runcmd(install_ldtp_cmd)
        if ret == 0:
            logger.info("Succeeded to install ldtp.")
        else:
            raise FailException("Test Failed - Failed to install ldtp.")

    def runcmd(self, cmd, timeout=None, showlogger=True):
        commander = Command(get_exported_param("REMOTE_IP"), "root", "red2015")
        return commander.run(cmd, timeout, showlogger)

if __name__ == "__main__":
    unittest.main()
