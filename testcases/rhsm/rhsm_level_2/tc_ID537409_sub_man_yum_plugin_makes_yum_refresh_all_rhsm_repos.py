from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537409_sub_man_yum_plugin_makes_yum_refresh_all_rhsm_repos(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_satellite_check():
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # back up repo
                self.back_repo('/tmp/redhat.repo.A')
                change1 = self.get_change_time()

                # yum repolist
                ycmd = 'yum -q repolist --enableplugin subscription-manager'
                self.yum_cmd_run(ycmd)
                change2 = self.get_change_time()

                # yum clean all
                ycmd = 'yum -q clean all --enableplugin subscription-manager'
                self.yum_cmd_run(ycmd)
                change3 = self.get_change_time()

                # yum list
                ycmd = 'yum -q clean all --enableplugin subscription-manager'
                self.yum_cmd_run(ycmd)
                change4 = self.get_change_time()

                # back up repo
                self.back_repo('/tmp/redhat.repo.B')

                if change1 == change2 == change3 ==change4:
                    cmd = 'diff /tmp/redhat.repo.A /tmp/redhat.repo.B'
                    (ret, output) = self.runcmd(cmd, "back up repo")
                    if ret == 0 and output.strip() == '':
                        logger.info("It's successful to check no repo refresh")
                    else:
                        raise FailException("Test Failed - Failed to check no repo refresh")
                else:
                    raise FailException("Test Failed - Failed to verify yum does not refresh")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def back_repo(self, repobk):
        cmd = 'cat /etc/yum.repos.d/redhat.repo > %s'%repobk
        (ret, output) = self.runcmd(cmd, "back up repo")
        if ret == 0:
            logger.info("It's successful to back up repo")
        else:
            raise FailException("Test Failed - Failed to back up repo")

    def get_change_time(self):
        cmd = 'stat -c %y /etc/yum.repos.d/redhat.repo'
        (ret, output) = self.runcmd(cmd, "get change time")
        return output.strip()
        if ret == 0:
            logger.info("It's successful to get change time")
        else:
            raise FailException("Test Failed - Failed to get change time")

    def yum_cmd_run(self,ycmd):
        cmd = '%s'%ycmd
        (ret, output) = self.runcmd(cmd, "run yum command")
        return output.strip()
        if ret == 0:
            logger.info("It's successful to run %s"%ycmd)
        else:
            raise FailException("Test Failed - Failed to run %s"%ycmd)

if __name__ == "__main__":
    unittest.main()
