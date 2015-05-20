import commands, os, traceback
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID214402_ESX_execute_virtwho_o(params):
	""" Execute virt-who -o in a registered host, verify virtwho -o can work"""
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			# (1)stop virt-who service
			eu().vw_stop_virtwho(logger)
			# run cmd virt-who with o and d option in the host
			cmd = "virt-who -o -d"
			(ret, output) = eu().runcmd(logger, cmd, "executing virt-who with one-shot mode")
			if ret == 0 and "DEBUG" in output and "ERROR" not in output:
				logger.info("Succeeded to execute virt-who with one-shot mode.")
				eu().SET_RESULT(0)
			else:
				logger.error("Failed to execute virt-who with one-shot mode.")
				eu().SET_RESULT(1)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
