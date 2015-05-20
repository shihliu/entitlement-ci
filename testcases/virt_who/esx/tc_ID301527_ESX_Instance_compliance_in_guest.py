import commands, os, traceback
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID301527_ESX_Instance_compliance_in_guest(params):
	''' tc_ID301527_ESX_Instance_compliance_in_guest. '''
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			guest_name = "ESX_" + params['handleguest']
			samhostip = params['samhostip']
			destination_ip = ee.esx_host_ip
			host_uuid = eu().esx_get_host_uuid(logger, destination_ip)
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
			# Set up facts
			eu().setup_custom_facts(logger, "cpu.cpu_socket(s)", "8", guestip)
			pool = eu().get_pool_by_SKU(logger, ee.instance_SKU, guestip)
			# Validate one instance-based subscription can be used for one guest
			cmd = "subscription-manager subscribe --pool=%s --quantity=1" % pool
			ret, output = eu().runcmd(logger, cmd, "Check one instance-based subscription can be used for one guest", guestip)
			if ret == 0 and "Successfully" in output:
				logger.info("Succeeded to check one instance-based subscription can be used for one guest.")
			else:
				logger.error("Failed to check one instance-based subscription can be used for one guest.")
				eu().SET_RESULT(1)
			# Check installed product status: Subscribed in guest
			cmd = "subscription-manager list --installed | grep 'Status:'"
			ret, output = eu().runcmd(logger, cmd, "Check installed product status", guestip)
			if ret == 0 and output.split(":")[1].strip() == "Subscribed":
				logger.info("Succeeded to check installed product status is Subscribed.")
			else:
				logger.error("Failed to check installed product status is Subscribed.")
				eu().SET_RESULT(1)
			# Check consumed subscription with Status Details: empty.
			cmd = "subscription-manager list --consumed | grep 'Status Details'"
			ret, output = eu().runcmd(logger, cmd, "Check consumed subscription 'Status Details'", guestip)
			if ret == 0 and output.split(":")[1].strip() == "":
				logger.info("Succeeded to check consumed subscription 'Status Details' is empty.")
			else:
				logger.error("Failed to check consumed subscription 'Status Details'is empty.")
				eu().SET_RESULT(1)
			eu().SET_RESULT(0)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		if guestip != None:
			eu().sub_unregister(logger, guestip)
		# Unregister the ESX host 
		eu().esx_unsubscribe_all_host_in_samserv(logger, host_uuid, samhostip)
		eu().esx_stop_guest(logger, guest_name, destination_ip)
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
