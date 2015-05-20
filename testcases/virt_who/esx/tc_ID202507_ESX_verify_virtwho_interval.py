import commands, os, traceback, time
from utils.Python import utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_ID202507_ESX_verify_virtwho_interval(params):
	""" Execute virt-who in a registered host, verify virtwho_interval can work"""
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			# config the virt-who config file
			cmd = "sed -i 's/#VIRTWHO_INTERVAL=0/VIRTWHO_INTERVAL=5/' /etc/sysconfig/virt-who"
			(ret, output) = eu().runcmd(logger, cmd, "changing interval time in virt-who config file")
			if ret == 0:
				logger.info("Succeeded to set VIRTWHO_INTERVAL=5.")
			else:
				logger.error("Failed to set VIRTWHO_INTERVAL=5.")
				eu().SET_RESULT(1)
			# restart virt-who service
			eu().vw_restart_virtwho(logger)
			# wait 30 seconds
			time.sleep(30)
			cmd = "nohup tail -f -n 0 /var/log/rhsm/rhsm.log > /tmp/tail.rhsm.log 2>&1 &"
			# (ret, output) = eu().runcmd(logger, cmd, "generate nohup.out file by tail -f")
			eu().runcmd_subprocess(logger, cmd, "got temp file /tmp/tail.rhsm.log")
			time.sleep(23)
			cmd = "killall -9 tail ; grep 'Sending update in hosts-to-guests mapping' /tmp/tail.rhsm.log | wc -l "
			(ret, output) = eu().runcmd(logger, cmd, "get log number added to rhsm.log")
			if ret == 0 and int(output) == 4:
				logger.info("Succeeded to check the log added.")
				eu().SET_RESULT(0)
			else:
				logger.error("Failed to check the log added.")
				eu().SET_RESULT(1)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		cmd = "sed -i 's/VIRTWHO_INTERVAL=5/#VIRTWHO_INTERVAL=0/' /etc/sysconfig/virt-who"
		(ret, output) = eu().runcmd(logger, cmd, "restoring the interval time as default setting in virt-who config file")
		cmd = "rm /tmp/tail.rhsm.log"
		(ret, output) = eu().runcmd(logger, cmd, "remove /tmp/tail.rhsm.log file generated")
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
