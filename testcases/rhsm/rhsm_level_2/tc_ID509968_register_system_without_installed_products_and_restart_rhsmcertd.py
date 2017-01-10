from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509968_register_system_without_installed_products_and_restart_rhsmcertd(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # create cert destination file
            self.create_cert_destination('/root/product')
            self.create_cert_destination('/root/product-default')

            # remove product cert
            pro1 = self.check_product_cert('/etc/pki/product/')
            pro2 = self.check_product_cert('/etc/pki/product-default/')
            if pro1:
                self.move_product_cert('/etc/pki/product/', '/root/product/')
            if pro2:
                self.move_product_cert('/etc/pki/product-default/', '/root/product-default/')

            # register without product cert
            tmp_file= '/root/logfile'
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            checkcmd = 'subscription-manager register --username=%s --password=%s;service rhsmcertd restart;sleep 120'%(username, password)
            self.generate_tmp_log(checkcmd, tmp_file)
            cmd = 'grep -Ei "error|traceback" %s | grep -v "overrides.json"'%tmp_file
            (ret, output) = self.runcmd(cmd, "check error in rhsm.log")
            if ret !=0:
                logger.info("It's successful to check error in rhsm.log")
            else:
                raise FailException("Test Failed - Failed to check error in rhsm.log")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if pro1:
                self.move_product_cert('/root/product/', '/etc/pki/product/')
            if pro2:
                self.move_product_cert('/root/product-default/', '/etc/pki/product-default/')
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def create_cert_destination(self, destination):
        cmd = 'ls %s'%destination
        (ret, output) = self.runcmd(cmd, "check destination file")
        if ret == 0:
            logger.info("It's successful to check destination file exists, no need create")
        else:
            cmd = 'mkdir %s'%destination
            (ret, output) = self.runcmd(cmd, "create destination file")
            if ret == 0:
                logger.info("It's successful to create destination file")
        
    def check_product_cert(self, certfile):
        cmd = 'ls %s'%certfile
        (ret, output) = self.runcmd(cmd, "check product file")
        movement = None
        if ret == 0:
            if output.strip() == '':
                logger.info("It's successful to check product file: no product cert in product file, no need to remove")
            else:
                logger.info("It's successful to check product file: it's needed to remove cert")
                movement = True
        else:
            raise FailException("Test Failed - Failed to check product file")
        return movement

    def move_product_cert(self, certfile, destination):
        cmd = 'mv %s* %s'%(certfile, destination)
        (ret, output) = self.runcmd(cmd, "move product file")
        if ret == 0:
            logger.info("It's successful to move product cert from %s to %s"%(certfile, destination))
        else:
            raise FailException("Test Failed - Failed to move product cert from %s to %s"%(certfile, destination))

if __name__ == "__main__":
    unittest.main()
