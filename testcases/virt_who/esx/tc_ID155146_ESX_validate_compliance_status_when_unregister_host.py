import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID155146_ESX_validate_compliance_status_when_unregister_host(params):
	''' ESX_validate_compliance_status_when_unregister_host '''
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
			
			# subscribe esx host with limited bonus subscription
			eu().esx_subscribe_host_in_samserv(logger, host_uuid, eu().get_poolid_by_SKU(logger, ee.productid_guest) , samhostip)
			
			# Subscribe the registered guest to the corresponding bonus pool
			eu().sub_subscribe_to_bonus_pool(logger, ee.productid_guest, guestip)
			
			# List consumed subscriptions on guest
			eu().sub_listconsumed(logger, ee.productname_guest, guestip)
			
			# Unregister the ESX host 
			eu().esx_unsubscribe_all_host_in_samserv(logger, host_uuid, samhostip)
			
			# Refresh the guest
			eu().sub_refresh(logger, guestip)
			# List available subscriptions on guest
			new_available_poollist = eu().sub_listavailpools(logger, ee.productid_guest, guestip)
			if new_available_poollist != None:
				for item in range(0, len(new_available_poollist)):
					if ee.productid_guest in new_available_poollist[item] and eu().check_type_virtual(new_available_poollist[item]):
						logger.info("listed bonus pool of product %s, but is shouldn't") % ee.productname_guest
						eu().SET_RESULT(1)
					else:
						logger.info("no bonus pool been list") 
			else:
				logger.error("Failed to get available pool list from guest.")
				eu().SET_RESULT(1)
			# List consumed subscriptions on guest
			eu().sub_listconsumed(logger, ee.productname_guest, targetmachine_ip=guestip, productexists=False)
			eu().SET_RESULT(0)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		if guestip != None:
			eu().sub_unregister(logger, guestip)
		# re-register the host and then restart virt-who
		if not eu().sub_isregistered(logger):
			eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"))
			eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"])
		eu().vw_restart_virtwho(logger)
		eu().esx_stop_guest(logger, guest_name, destination_ip)
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
