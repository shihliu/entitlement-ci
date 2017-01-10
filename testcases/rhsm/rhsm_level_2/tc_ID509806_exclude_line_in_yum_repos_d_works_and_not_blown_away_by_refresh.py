from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509806_exclude_line_in_yum_repos_d_works_and_not_blown_away_by_refresh(RHSMBase):
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

            # Disable all repos
            self.disable_all_repos()

            # Enabled default repo
            defaultrepo = self.get_rhsm_cons("productrepo")
            self.enable_repo(defaultrepo)

            # Add exclude line in default repo
            pkgtoinstall = self.get_rhsm_cons("pkgtoinstall")
            excludeline = 'exclude = %s*'%pkgtoinstall
            datumline = '\[%s\]'%defaultrepo
            self.add_line_after_a_line(datumline, excludeline, '/etc/yum.repos.d/redhat.repo')

            # Check yum list all for pkg
            self.check_excluded_pkg(pkgtoinstall)
            
            # Refresh
            self.refresh_client_server()

            # Check exclude line
            cmd = "grep 'exclude' /etc/yum.repos.d/redhat.repo"
            (ret, output) = self.runcmd(cmd, "check exclude line")
            if ret ==0 and 'exclude = zsh*' in output:
                logger.info("It's successful to check exclude line")
            else:
                raise FailException("Test Failed - Failed to check exclude line")

            # Check yum list all for pkg
            self.check_excluded_pkg(pkgtoinstall)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_repos()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_excluded_pkg(self, pkg):
        cmd = 'yum list all | grep %s'%pkg
        (ret, output) = self.runcmd(cmd, "check excluded pkg")
        if ret !=0 and ''==output:
            logger.info("It's successful to check excluded pkg")
        else:
            raise FailException("Test Failed - Failed to check excluded pkg")

if __name__ == "__main__":
    unittest.main()
