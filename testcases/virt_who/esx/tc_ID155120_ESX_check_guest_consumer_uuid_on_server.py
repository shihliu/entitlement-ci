import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID155120_ESX_check_guest_consumer_uuid_on_server(params):
	''' Execute virt-who in a registered host to Check UUIDs of running guests '''
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
			# Register guest to SAM
			if not eu().sub_isregistered(logger, guestip):
				eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"), guestip)
				eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"], guestip)
			# Get uuid of host and guest consumer
			cmd = "grep 'Sending update in hosts-to-guests mapping' /var/log/rhsm/rhsm.log | tail -1"
			ret, output = eu().runcmd(logger, cmd, "get host consumer uuid")
			hostuuid = output.split("{")[1].split(":")[0].strip()
			cmd = "subscription-manager identity | grep identity"
			ret, output = eu().runcmd(logger, cmd, "get guest subscription-manager identity", guestip)
			guestuuid = output.split(':')[1].strip()
			# Check whether guest is included in host info
			samhostip = params["samhostip"]
			cmd = "curl -u admin:admin -k https://%s/sam/api/consumers/%s" % (samhostip, hostuuid)
			ret, output = eu().runcmd(logger, cmd, "Check whether guest is included in host info")
			if ret == 0 and guestuuid in output:
				logger.info("Succeeded to check guest in host info.")
				eu().SET_RESULT(0)
			else:
				logger.error("Failed to check guest in host info.")
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
