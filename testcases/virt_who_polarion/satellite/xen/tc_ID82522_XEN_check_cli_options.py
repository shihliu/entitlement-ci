from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID82522_XEN_check_cli_options(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "-o" option and virt-who threads will not increase after run "-o -d" many times
            cmd = self.virtwho_cli("xen") + " -o -d"
            for i in range(1, 5):
                self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)

            # (2) Check "-d"
            # (2.1) Check "DEBUG" info is exist when run "virt-who --xen -d"
            cmd = self.virtwho_cli("xen") + " -d"
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG")
            # (2.2) Check "DEBUG" info is not exist when run "virt-who --xen",no "-d" option
            cmd = self.virtwho_cli("xen")
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG|ERROR", message_exists=False)

            # (3) Check "-i" option 
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            # (3.1) Check virt-who refresh default interval is 60s
            cmd = self.virtwho_cli("xen") + " -d"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            # (3.2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = self.virtwho_cli("xen") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            # (3.3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = self.virtwho_cli("xen") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150)
            self.check_virtwho_thread(0)

            # (4) Check "-p" option 
            #(4.1) Check "DEBUG" info will not exist when run "virt-who --xen -p"
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            # need to sleep for a second, or else virt-who pid hung up
            cmd = self.virtwho_cli("xen") + " -p | sleep 10"
            self.vw_check_message(cmd, "DEBUG", message_exists=False)
            #(4.2) Check "DEBUG" info is exist when run "virt-who --xen -p -d"
            cmd = self.virtwho_cli("xen") + " -p -d"
            self.vw_check_message(cmd, "DEBUG")
            #(4.3) Check jason info is exist in tmp_json.log
            tmp_json = "/tmp/tmp_json.log"
            cmd = self.virtwho_cli("xen") + " -p -d > %s" % tmp_json
            json_in_log = ordered(json.loads(self.vw_get_mapping_info(cmd)[0].strip()))
            cmd = "cat %s | python -mjson.tool" % tmp_json
            ret, output = self.runcmd(cmd, "parse json file generated by -p")
            json_printed = ordered(json.loads(output.strip()))
            if json_printed != json_in_log:
                logger.info("Test Failed - failed to check virt-who print json file compared with json in rhsm.log file")
                self.assert_(False, case_name)
            else:
                logger.info("Succeeded to check virt-who print json file compared with json in rhsm.log file")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


if __name__ == "__main__":
    unittest.main()
