import commands, os, traceback
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID173049_ESX_remove_deletion_record_of_hypervisor_to_re_register(params):
	""" remove_deletion_record_of_hypervisor_to_re_register """
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			# guest_name = "ESX_" + params['handleguest']
			samhostip = params['samhostip']
			destination_ip = ee.esx_host_ip
			# Start a guest by start from host machine.
			# eu().esx_start_guest(logger, guest_name, destination_ip)
			# Get guest IP
			# guestip = None
			# guestip = eu().esx_get_guest_ip(logger, guest_name, destination_ip)
			# if guestip == None:
			# 	logger.error("Faild to get guest ip.")
			# 	eu().SET_RESULT(1)
			# Register guest to SAM
			# if not eu().sub_isregistered(logger, guestip):
			# 	eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"), guestip)
			# 	eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"], guestip)
			# restart virt-who service
			eu().vw_restart_virtwho(logger)
			host_uuid = eu().esx_get_host_uuid(logger, destination_ip)
			eu().esx_check_host_in_samserv(logger, host_uuid, samhostip)
			eu().vw_stop_virtwho(logger)
			eu().esx_remove_host_in_samserv(logger, host_uuid, samhostip)
			eu().esx_remove_deletion_record_in_samserv(logger, host_uuid, samhostip)
			
			eu().vw_restart_virtwho(logger)
			eu().esx_check_host_in_samserv(logger, host_uuid, samhostip)
			eu().SET_RESULT(0)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		# if guestip != None:
		# 	eu().sub_unregister(logger, guestip)
		# eu().esx_stop_guest(logger, guest_name, destination_ip)
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
