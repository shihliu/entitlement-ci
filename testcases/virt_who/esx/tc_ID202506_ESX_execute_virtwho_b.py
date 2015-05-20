import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID202506_ESX_execute_virtwho_b(params):
	"""Execute virt-who with backgroud mode in a registered host via CLI"""
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			# (1)stop virt-who service
			eu().vw_stop_virtwho(logger)
			# (2)Execute virt-who in the background mode.
			cmd = "virt-who -b -d"
			# ret, output = eu().runcmd(logger, cmd, "execute virt-who with background mode")
			ret, output = eu().runcmd_subprocess(logger, cmd, "run virt-who -b -d command")
			if ret == 0 :
				# check the status of virt-who
				cmd = "ps -ef | grep virt-who"
				ret, output = eu().runcmd(logger, cmd, "check the process of virt-who with background mode")
				if ret == 0 and "virt-who.py -b -d" in output:
					logger.info("Succeeded to check virt-who process.")
				else:
					logger.error("Failed to check virt-who process.")
					eu().SET_RESULT(1)
				handleguest = "ESX_" + params["handleguest"]
				destination_ip = ee.esx_host_ip
				vCenter = params['vcentermachine_ip']
				vCenter_user = params['vcentermachine_username']
				vCenter_pass = params['vcentermachine_password']
				# (1) start a guest	
				eu().esx_start_guest(logger, handleguest)
				# check if the uuid is correctly monitored by virt-who.
				eu().esx_check_uuid(logger, handleguest, destination_ip)
	
				# (2)pause a guest
				eu().esx_pause_guest(logger, handleguest, destination_ip)
				# check if the uuid is correctly monitored by virt-who.
				eu().esx_check_uuid(logger, handleguest, destination_ip)
	
				# (3)resume a guest
				eu().esx_resume_guest(logger, handleguest, destination_ip)
				# check if the uuid is correctly monitored by virt-who.
				eu().esx_check_uuid(logger, handleguest, destination_ip)
	
				# (4)shutdown a guest
				eu().esx_stop_guest(logger, handleguest, destination_ip)
				# check if the uuid is correctly monitored by virt-who.
				eu().esx_check_uuid(logger, handleguest, destination_ip)
	
				# (5)delete a guest
				guestuuid = eu().esx_get_guest_uuid(logger, handleguest, destination_ip)
				# prepare test env: undefine the guest to handle
				eu().esx_remove_guest(logger, handleguest, destination_ip, vCenter, vCenter_user, vCenter_pass)
				# check if the uuid is correctly monitored by virt-who.
				eu().esx_check_uuid(logger, handleguest, destination_ip, guestuuid, uuidexists=False)
	
				# (6)add a guest.
				eu().esx_add_guest(logger, handleguest, destination_ip)
				# check if the uuid is correctly monitored by virt-who.
				eu().esx_check_uuid(logger, handleguest, destination_ip)
	
				eu().vw_stop_virtwho(logger)
				eu().SET_RESULT(0)
			else:
				logger.error("Failed to run virt-who -b -d.")
				eu().SET_RESULT(1)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
