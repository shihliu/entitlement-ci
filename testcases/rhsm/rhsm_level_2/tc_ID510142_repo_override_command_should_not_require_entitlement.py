from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510142_repo_override_command_should_not_require_entitlement(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # make sure there is no repo override before test
            repo_ovrd_list = self.list_all_repo_override()
            if repo_ovrd_list.strip() == '':
                logger.info('there is no repo override')
            else:
                self.remove_all_override()

            self.check_and_backup_yum_repos()
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Add an override for any repo (existing or not).
            cmd = 'subscription-manager repo-override --add=foo:bar --repo=non-existing-repo'
            (ret, output) = self.runcmd(cmd, "add override")
            if ret ==0 and "Repository 'non-existing-repo' does not currently exist, but the override has been added" in output:
                logger.info("It's successful to add override for non-existing repo")
            else:
                raise FailException("Test Failed - Failed to add override for non-existing repo")

            # Auto attach
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Add an override for a existing repo.
            productrepo = self.get_rhsm_cons("productrepo")
            cmd = 'subscription-manager repo-override --add=enabled:1 --repo=%s'%productrepo
            (ret, output) = self.runcmd(cmd, "Add an override for a existing repo")
            if ret ==0:
                logger.info("It's successful to add an override for a existing repo")
            else:
                raise FailException("Test Failed - Failed to add an override for a existing repo")

            # check all repo-override
            self.check_all_repo_override(productrepo, 'non-existing-repo')

            # remove all subscriptions
            self.sub_unsubscribe()

            # check all repo-override after remove all subscription
            self.check_all_repo_override(productrepo, 'non-existing-repo')

            # remove all override
            self.remove_all_override()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            self.restore_repos()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_all_repo_override(self, existing_repo, non_existing_repo):
        overrides_list = self.list_all_repo_override()
        if 'Repository: %s'%existing_repo in overrides_list and 'Repository: %s'%non_existing_repo in overrides_list:
            logger.info("It's successful to list all repo-override")
        else:
            raise FailException("Test Failed - Failed to list all repo-override")

if __name__ == "__main__":
    unittest.main()
