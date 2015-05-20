import commands, os, traceback
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID289139_ESX_Datacenter_subpool_quantity_unlimited(params):
	''' tc_ID289139_ESX_Datacenter_subpool_quantity_unlimited. '''
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
			# check only physical subscription in guest # Check bonus pool not generated yet
			eu().check_datacenter_bonus_existance(logger, ee.data_center_subscription_name, guestip, False)
			# Subscribe esx host to a data center SKU
			eu().esx_subscribe_host_in_samserv(logger, host_uuid, eu().get_poolid_by_SKU(logger, ee.data_center_SKU) , samhostip)
			# Check bonus pool generated
			eu().check_datacenter_bonus_existance(logger, ee.data_center_subscription_name, guestip)
			# Check subpool quantity is unlimited
			eu().check_bonus_attribute(logger, ee.data_center_subscription_name, "Available", "Unlimited", guestip)
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
