import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID155170_ESX_check_uuid_after_adding_guests(params):
	''' check_uuid_after_adding_guests '''
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			guest_name = "ESX_" + params['handleguest']
			destination_ip = ee.esx_host_ip
			# Start a guest by start from host machine.
			eu().esx_start_guest(logger, guest_name)
			# Get guest IP
			guestip = None
			guestip = eu().esx_get_guest_ip(logger, guest_name, destination_ip)
			if guestip == None:
				logger.error("Faild to get guest ip.")
				eu().SET_RESULT(1)
			# Get guest uuid
			guestuuid = eu().esx_get_guest_uuid(logger, guest_name, destination_ip)
			# Register guest to SAM
			if not eu().sub_isregistered(logger, guestip):
				eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"), guestip)
				eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"], guestip)
			# Check virt uuid in facts list
			cmd = "subscription-manager facts --list | grep virt.uuid"
			ret, output = eu().runcmd(logger, cmd, "list virt.uuid", guestip)
			if ret == 0:
				uuidvalue = output.split(":")[1].strip()
				if "virt.uuid" in output and uuidvalue == guestuuid:
					logger.info("Succeeded to check_uuid_after_adding_guests.")
					eu().SET_RESULT(0)
				else:
					logger.error("Failed to check_uuid_after_adding_guests.")
					eu().SET_RESULT(1)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		if guestip != None:
			eu().sub_unregister(logger, guestip)
		eu().esx_stop_guest(logger, guest_name, destination_ip)
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
