from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1001_check_virtwho_from_repo(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            rhel_compose = get_exported_param("RHEL_COMPOSE")
            repo_file_name = "virt-who-all.repo"
            cmd = ('cat <<EOF > /etc/yum.repos.d/%s\n'
                '[virt-who-Client]\n'
                'name=virt-who-Client\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/Client/x86_64/os/\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                '[virt-who-ComputeNode]\n'
                'name=virt-who-ComputeNode\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/ComputeNode/x86_64/os/\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                '[virt-who-Workstation]\n'
                'name=virt-who-Workstation\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/Workstation/x86_64/os/\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                '[virt-who-Server-x86_64]\n'
                'name=virt-who-Server-x86_64\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/Server/x86_64/os/\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                '[virt-who-Server-ppc64]\n'
                'name=virt-who-Server-ppc64\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/Server/ppc64/os\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                '[virt-who-Server-ppc64le]\n'
                'name=virt-who-Server-ppc64le\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/Server/ppc64le/os\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                '[virt-who-Server-aarch64]\n'
                'name=virt-who-Server-aarch64\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/Server/aarch64/os\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                '[virt-who-Server-s390x]\n'
                'name=virt-who-Server-s390x\n'
                'baseurl=http://download-node-02.eng.bos.redhat.com/rel-eng/%s/compose/Server/s390x/os\n'
                'enabled=1\n'
                'gpgcheck=0\n'
                'EOF'
                ) % (repo_file_name, rhel_compose, rhel_compose, rhel_compose, rhel_compose, rhel_compose, rhel_compose, rhel_compose, rhel_compose)
            # No virt-who package in "virt-who-ComputeNode" and "virt-who-Server-aarch64" repo with Bug 1373391 - closed as NOTABUG.
            ret, output = self.runcmd(cmd, "enable virt-who all arch/variant repo")
            for item in ("virt-who-Client", "virt-who-Workstation", "virt-who-Server-x86_64", "virt-who-Server-ppc64", "virt-who-Server-ppc64le", "virt-who-Server-s390x"):
                cmd = "repoquery -a --repoid=%s | grep virt-who" % item
                ret, output = self.runcmd(cmd, "check virt-who package exist in %s" % item)
                if ret == 0:
                    logger.info("Succeeded to check virt-who package exist in %s" % item)
                else:
                    raise FailException("Test Failed - Failed to check virt-who package exist in %s" % item)
            self.assert_(True, case_name)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            cmd = "rm -f /etc/yum.repos.d/%s" % repo_file_name
            ret, output = self.runcmd(cmd, "remove temp repo file")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
