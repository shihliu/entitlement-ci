from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID174961_check_virtwho_b(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            self.vw_stop_virtwho()

            cmd = "virt-who -b -d"
            ret, output = self.runcmd(cmd, "run virt-who -b -d command")
            if ret == 0 :
                # check the status of virt-who
                cmd = "ps -ef | grep virt-who"
                ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
                if ret == 0 and (("virt-who.py -b -d" in output) or ("virtwho.py -b -d" in output)):
                    logger.info("Succeeded to check virt-who process.")
                else:
                    logger.error("Failed to check virt-who process.")
                    self.assert_(False, case_name)

                if self.get_os_serials() == "7":
                    #start a guest    
                    cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
                    ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f")
                    self.vw_start_guests(guest_name)
                    # check if the uuid is correctly monitored by virt-who.
                    self.vw_check_uuid_b(guestuuid, uuidexists=True)
                    # shutdown a guest
                    cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
                    ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f")
                    self.shutdown_vm(guest_name)
                    # check if the uuid is correctly monitored by virt-who.
                    self.vw_check_uuid_b(guestuuid, uuidexists=True)
                else:
                    self.vw_start_guests(guest_name)
                    # check if the uuid is correctly monitored by virt-who.
                    self.vw_check_uuid(guestuuid, uuidexists=True)
                    # (2)pause a guest
                    self.pause_vm(guest_name)
                    # check if the uuid is correctly monitored by virt-who.
                    self.vw_check_uuid(guestuuid, uuidexists=True)
                    # (3)resume a guest
                    self.resume_vm(guest_name)
                    # check if the uuid is correctly monitored by virt-who.
                    self.vw_check_uuid(guestuuid, uuidexists=True)
                    # (4)shutdown a guest
                    self.shutdown_vm(guest_name)
                    # check if the uuid is correctly monitored by virt-who.
                    # self.vw_check_uuid("", uuidexists=True)
                    self.vw_check_uuid(guestuuid, uuidexists=True)
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to run virt-who -b -d.")
                self.assert_(False, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            #self.vw_stop_guests(guest_name)
            cmd = "ps -ef|grep virt-who|cut -c 9-15|xargs kill -9"
            ret, output = self.runcmd(cmd, "kill all virt-who thread")
            # stop virt-who command line mode
            self.vw_restart_virtwho()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def vw_check_uuid_b(self, guestuuid, uuidexists=True):
        cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
        ret, output = self.runcmd(cmd, "get log number added to rhsm.log")
        if ret == 0:
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending domain info" in output:
                log_uuid_list = output.split('Sending domain info: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get uuid list from rhsm.log")
            if uuidexists:
                if guestuuid == "" and len(log_uuid_list) == 0:
                    logger.info("Succeeded to get none uuid list")
                else:
                    if guestuuid in log_uuid_list:
                        logger.info("Succeeded to check guestuuid %s in log_uuid_list" % guestuuid)
                    else:
                        raise FailException("Failed to check guestuuid %s in log_uuid_list" % guestuuid)
            else:
                if guestuuid not in log_uuid_list:
                    logger.info("Succeeded to check guestuuid %s not in log_uuid_list" % guestuuid)
                else:
                    raise FailException("Failed to check guestuuid %s not in log_uuid_list" % guestuuid)
        else:
            raise FailException("Failed to get rhsm.log")

if __name__ == "__main__":
    unittest.main()


