from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import datetime

class tc_ID147117_verify_product_cert_validity(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'for i in $(ls /etc/pki/product/*); do openssl x509 -text -noout -in $i; done | grep -A 3 "Validity"'
            (ret, output) = self.runcmd(cmd, "check product's cert validity!")
            if ret == 0 and ("Not Before" and "Not After" in output):
                GMT_FORMAT = '%b %d %H:%M:%S %Y GMT'
                cert_start_gmt = output[output.find('Not Before') + len('Not Before') + 2:output.find('GMT') + 3]
                cert_end_gmt1 = output[output.find('Not After ') + len('Not After ') + 2:output.find('Subject')]
                cert_end_gmt = cert_end_gmt1[:cert_end_gmt1.find('\n')]
                # convert GMT time to datetime
                cert_start_datetime = datetime.datetime.strptime(cert_start_gmt, GMT_FORMAT)
                cert_end_datetime = datetime.datetime.strptime(cert_end_gmt, GMT_FORMAT)
                logger.info('Product cert validity is from %s to %s' % (cert_start_datetime, cert_end_datetime))
                # get current datetime
                date_today = datetime.datetime.today()
                logger.info('current date is %s ' % date_today)
                # compare time
                if date_today > cert_start_datetime and date_today < cert_end_datetime:
                    logger.info('%s > current date < %s ' % (cert_start_datetime, cert_end_datetime))
                    logger.info("Test Successful - It's successful to verify product's cert validity.") 
                else:
                    raise FailException("Test Failed - Failed to verify product's cert validity.")
            else:
                raise FailException("Test Failed - Failed to get product's cert validity.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
