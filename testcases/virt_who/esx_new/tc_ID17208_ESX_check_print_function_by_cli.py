from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17208_ESX_check_print_function_by_cli(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            # need to sleep for a second, or else virt-who pid hung up
            cmd = self.virtwho_cli("esx") + " -p | sleep 10"
            self.vw_check_message(cmd, "DEBUG", message_exists=False)
            cmd = self.virtwho_cli("esx") + " -p -d"
            self.vw_check_message(cmd, "DEBUG")
            tmp_json = "/tmp/tmp_json.log"
            cmd = self.virtwho_cli("esx") + " -p -d > %s" % tmp_json
            json_in_log = self.vw_get_mapping_info(cmd)[0].strip("Associations found:").strip()
            cmd = "cat %s | python -mjson.tool" % tmp_json
            ret, output = self.runcmd(cmd, "parse json file generated by -p")
            json_print = output.strip()
            if json_print != json_in_log:
                self.assert_(False, case_name)
            else:
                self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
