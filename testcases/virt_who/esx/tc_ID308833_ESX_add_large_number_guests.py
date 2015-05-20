import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID308833_ESX_add_large_number_guests(params):
	""" Execute virt-who with large number of guests in host """
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			guest_name = "esx_auto_guest"
			vCenter = params['vcentermachine_ip']
			vCenter_user = params['vcentermachine_username']
			vCenter_pass = params['vcentermachine_password']
			destination_ip = ee.esx_host_ip
			guest_total = 100
			guest_uuid_list = []
			# add 100 guests in vCenter
			for i in range(0, guest_total):
				eu().esx_create_dummy_guest(logger, guest_name + "_" + str(i), destination_ip)
				guest_uuid = eu().esx_get_guest_uuid(logger, guest_name + "_" + str(i), destination_ip)
				guest_uuid_list.append(guest_uuid)
				# if not eu().esx_check_uuid_exist_in_rhsm_log(logger, guestuuid, destination_ip):
				# 	eu().SET_RESULT(1)
			# check all guest uuid is in rhsm.log
			guest_uuid_list_in_log = eu().get_uuid_list_in_rhsm_log(logger)
			for i in range(0, guest_total):
				if not guest_uuid_list[i] in guest_uuid_list_in_log:
					eu().SET_RESULT(1)
				else:
					logger.info("UUID of guest:%s exist in rhsm.log" % (guest_name + "_" + str(i)))
			# remove the 100 guests added in vCenter
			for i in range(0, guest_total):
				# guestuuid = eu().esx_get_guest_uuid(logger, guest_name + "_" + str(i), destination_ip)
				eu().esx_remove_guest(logger, guest_name + "_" + str(i), destination_ip, vCenter, vCenter_user, vCenter_pass)
				eu().esx_destroy_guest(logger, guest_name + "_" + str(i), destination_ip)
				# if eu().esx_check_uuid_exist_in_rhsm_log(logger, guestuuid, destination_ip):
				# 	eu().SET_RESULT(1)
			eu().SET_RESULT(0)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
