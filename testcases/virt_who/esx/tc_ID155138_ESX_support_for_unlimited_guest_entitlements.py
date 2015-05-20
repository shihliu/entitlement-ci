import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID155138_ESX_support_for_unlimited_guest_entitlements(params):
	''' support_for_unlimited_guest_entitlements '''
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
			
			# check only physical subscription in guest
			
			# subscribe esx host with unlimited bonus subscription
			eu().esx_subscribe_host_in_samserv(logger, host_uuid, eu().get_poolid_by_SKU(logger, ee.productid_unlimited_guest) , samhostip)
			
			# List available pools of guest, check related bonus pool generated.
			new_available_poollist = eu().sub_listavailpools(logger, ee.productid_unlimited_guest, guestip)
			if new_available_poollist != None:
				bonus_pool_check = 1
				for item in range(0, len(new_available_poollist)):
					if "Available" in new_available_poollist[item]:
						SKU_Number = "Available"
					else:
						SKU_Number = "Quantity"
					if (new_available_poollist[item]["SKU"] == ee.productid_unlimited_guest and eu().check_type_virtual(new_available_poollist[item]) and (new_available_poollist[item][SKU_Number] == ee.guestlimit_unlimited_guest or new_available_poollist[item][SKU_Number] == "unlimited")):
						logger.info("Succeeded to list bonus pool of product %s" % ee.productname_unlimited_guest) 
						bonus_pool_check = 0
				eu().SET_RESULT(bonus_pool_check)
			else:
				logger.error("Failed to get available pool list from guest.")
				eu().SET_RESULT(1)
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
