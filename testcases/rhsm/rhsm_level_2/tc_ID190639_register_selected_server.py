from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID190639_register_selected_server(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            baseurl = get_exported_param("SERVER_HOSTNAME")
            server_ip = get_exported_param("SERVER_IP")
            server_type=self.test_server
            # register to sam candlepin server
            if server_type == 'SAM':
                serverurl = baseurl + ':443/sam/api'
                cmd = "subscription-manager register --username=%s --password=%s --serverurl=%s --org=ACME_Corporation --force" % (username, password, serverurl)
            elif server_type == 'SATELLITE':
                if 'satellite' in baseurl:
                    baseurl = baseurl + '.novalocal'
                serverurl = baseurl + ':443/rhsm'
                cmd = "subscription-manager register --username=%s --password=%s --serverurl=%s --org=Default_Organization --force" % (username, password, serverurl)
            # register to stage/product candlepin server
            else:
                serverurl = baseurl + '/subscription'
                cmd = "subscription-manager register --username=%s --password=%s --serverurl=%s" % (username, password, serverurl)
            (ret, output) = self.runcmd(cmd, "register to selected server")
            if ret == 0 and ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
                logger.info("It is successful to register system to selected server.")
            else:
                raise FailException("Test Failed - Failed to rigster system to selected server.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
