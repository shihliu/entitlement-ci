import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID155173_ESX_check_uuid_when_guest_paused_or_shutdown(params):
	"""tc_ID155173_ESX_check_uuid_when_guest_paused_or_shutdown"""
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			guest_name = "ESX_" + params['handleguest']
			samhostip = params['samhostip']
			destination_ip = ee.esx_host_ip
			# (1) start a guest	
			eu().esx_start_guest(logger, guest_name)
			# check if the uuid is correctly monitored by virt-who.
			eu().esx_check_uuid(logger, guest_name, destination_ip)

			# (2)pause a guest
			eu().esx_pause_guest(logger, guest_name, destination_ip)
			# check if the uuid is correctly monitored by virt-who.
			eu().esx_check_uuid(logger, guest_name, destination_ip)

			# (3)resume a guest
			eu().esx_resume_guest(logger, guest_name, destination_ip)
			# check if the uuid is correctly monitored by virt-who.
			eu().esx_check_uuid(logger, guest_name, destination_ip)

			# (4)shutdown a guest
			eu().esx_stop_guest(logger, guest_name, destination_ip)
			# check if the uuid is correctly monitored by virt-who.
			eu().esx_check_uuid(logger, guest_name, destination_ip)
			eu().SET_RESULT(0)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
