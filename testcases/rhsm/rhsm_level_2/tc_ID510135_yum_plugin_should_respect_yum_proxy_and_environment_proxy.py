from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510135_yum_plugin_should_respect_yum_proxy_and_environment_proxy(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.check_and_backup_yum_repos()
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Check yum proxy
            cmd = "echo 'proxy=https://squid.corp.redhat.com:3128' >> /etc/yum.conf"
            (ret, output) = self.runcmd(cmd, "set yum proxy")
            if ret ==0:
               logger.info("It's successful to set yum proxy")
            else:
                raise FailException("Test Failed - Failed to set yum proxy")

            self.yum_repolist_proxy()
            self.restore_yum_conf()

            # Check env proxy
            cmd = 'export http_proxy=squid.corp.redhat.com:3128'
            (ret, output) = self.runcmd(cmd, "set env proxy")
            if ret ==0:
               logger.info("It's successful to set env proxy")
            else:
                raise FailException("Test Failed - Failed to set env proxy")

            self.yum_repolist_proxy()
            self.restore_env_proxy()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            self.restore_env_proxy()
            self.restore_yum_conf()
            self.restore_repos()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def yum_repolist_proxy(self):
        cmd = 'yum repolist | grep "repolist:"'
        (ret, output) = self.runcmd(cmd, "yum repolist with proxy")
        if ret ==0 and output.strip().split(':')[1] != '':
            logger.info("It's successful to yum repolist with proxy")
        else:
            raise FailException("Test Failed - Failed to yum repolist with proxy")

    def restore_yum_conf(self):
        cmd = "sed -i '/proxy=https:\/\/squid.corp.redhat.com:3128/d' /etc/yum.conf"
        (ret, output) = self.runcmd(cmd, "restore yum.conf")
        if ret ==0:
            logger.info("It's successful to restore yum.conf")
        else:
            raise FailException("Test Failed - Failed to restore yum.conf")

    def restore_env_proxy(self):
        cmd = 'unset http_proxy'
        (ret, output) = self.runcmd(cmd, "restore env proxy")
        if ret ==0:
            logger.info("It's successful to restore env proxy")
        else:
            raise FailException("Test Failed - Failed to restore env proxy")

if __name__ == "__main__":
    unittest.main()
