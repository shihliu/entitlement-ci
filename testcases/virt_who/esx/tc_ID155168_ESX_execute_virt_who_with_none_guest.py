import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID155168_ESX_execute_virt_who_with_none_guest(params):
	''' ESX_execute_virt_who_with_none_guest '''
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			handleguest = "ESX_" + params['handleguest']
			destination_ip = ee.esx_host_ip
			vCenter = params['vcentermachine_ip']
			vCenter_user = params['vcentermachine_username']
			vCenter_pass = params['vcentermachine_password']
			host_uuid = eu().esx_get_host_uuid(logger, destination_ip)
			# delete guest
			eu().esx_remove_guest(logger, handleguest, destination_ip, vCenter, vCenter_user, vCenter_pass)
			# restart virt-who service
			eu().vw_restart_virtwho(logger)
			eu().vw_restart_virtwho(logger)
			# check log info in rhsm.log with none guest
			cmd = "sleep 30; tail -1 /var/log/rhsm/rhsm.log"
			expected_info = "Sending update in hosts-to-guests mapping: {%s: []}" % host_uuid
			(ret, output) = eu().runcmd(logger, cmd, "check log info in rhsm.log with none guest")
			if ret == 0 and expected_info in output:
				logger.info("Succeeded to execute_virt_who_with_none_guest.")
				eu().SET_RESULT(0)
			else:
				logger.error("Failed to execute_virt_who_with_none_guest.")
				eu().SET_RESULT(1)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		eu().esx_add_guest(logger, handleguest, destination_ip)
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
