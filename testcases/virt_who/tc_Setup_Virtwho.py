import commands, os, traceback, pexpect, time
from utils.Python.utils import Utils as utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_Setup_Virtwho(params):
	""" Set up virt-who environment """
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
			if "server_hostname" in params.keys():
					# (1)set cpu socket
					eu().set_cpu_socket(logger)
					# (2)configure and register the host
					if not eu().sub_isregistered(logger):
						eu().configure_stage_host(logger, params.get("server_hostname"))
						eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"])
					# (3)update virt-who configure file
					eu().update_vw_configure(logger)
					# (4)restart virt-who service
					eu().vw_restart_virtwho(logger)
					# (5)copy all needed guests
					testtype = params['testtype']
					copyimages = params['copyimages']
					if copyimages == "yes":
						eu().copy_images(logger, testtype, ee.image_machine_ip, ee.image_machine_imagepath, ee.imagenfspath)
					# (6)export image path as nfs
					eu().export_dir_as_nfs(logger, ee.imagenfspath)
					# (7)mount image nfs path
					eu().mount_images_in_sourcemachine(logger, ee.imagenfspath, ee.imagepath)
					# (8)add some guests by define from host machine.
					eu().vw_define_all_guests(logger, testtype, params)
					# (9)set up env for migration if needed
					if params.has_key("targetmachine_ip") and params.has_key("targetmachine_hostname"):
						logger.info("-------- Begin to set up env for migration -------- ")
						targetmachine_ip = params["targetmachine_ip"]
						targetmachine_hostname = params["targetmachine_hostname"]
						# 1)mount image path in target machine
						eu().mount_images_in_targetmachine(logger, targetmachine_ip, ee.imagenfspath, ee.imagepath)
						# 2)mount the rhsm log of the target machine into source machine.
						eu().mount_rhsmlog_of_targetmachine(logger, targetmachine_ip, ee.rhsmlog_for_targetmachine)
						# 3)update /etc/hosts file
						eu().update_hosts_file(logger, targetmachine_ip, targetmachine_hostname)
						# 4)set cpu socket
						eu().set_cpu_socket(logger, targetmachine_ip=targetmachine_ip)
						# 5)stop firewall of two host machines for migration
						eu().stop_firewall(logger)
						eu().stop_firewall(logger, targetmachine_ip)
						# 6)update xen configuration file /etc/xen/xend-config.sxp of two host machines for migration to 
						# make sure contain necessary config options, and then restart service xend.
						if testtype == "xen":
							eu().update_xen_configure(logger)
							eu().update_xen_configure(logger, targetmachine_ip)
						# 7)configure and register the host
						if not eu().sub_isregistered(logger, targetmachine_ip):
							eu().configure_stage_host(logger, params.get("server_hostname"), targetmachine_ip)
							username = eu().get_env(logger)["username"]
							password = eu().get_env(logger)["password"]
							eu().sub_register(logger, username, password, targetmachine_ip)
						# 8)update virt-who configure file
						eu().update_vw_configure(logger, targetmachine_ip=targetmachine_ip)
						# 9)restart virt-who service in target machine
						eu().vw_restart_virtwho(logger, targetmachine_ip)
						logger.info("-------- End to set up env for migration -------- ")
					else:
						logger.info("There is no target machine ip/hostname provided, so does not setup env for migration.")
					# if got here, this script run well
					eu().SET_RESULT(0)
			else:
				if "vcentermachine_ip" in params.keys():
					VIRTWHO_ESX_OWNER = "ACME_Corporation"
					VIRTWHO_ESX_ENV = "Library"
					VIRTWHO_ESX_SERVER = params['vcentermachine_ip']
					VIRTWHO_ESX_USERNAME = params.get("vcentermachine_username")
					VIRTWHO_ESX_PASSWORD = params.get("vcentermachine_password")
					ESX_HOST = ee.esx_host_ip
					# update virt-who configure file
					eu().update_esx_vw_configure(logger, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD)
					# restart virt-who service
					eu().vw_restart_virtwho(logger)
					if not eu().sub_isregistered(logger):
						eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"))
						eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"])
					# wget all needed guests
					copyimages = params['copyimages']
					guest_name = "ESX_" + params['handleguest']
					if eu().esx_check_host_exist(logger, ESX_HOST, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD):
						if copyimages == "yes":
							wget_url = "http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/sam-virtwho/esx_guest/"
							# eu().esx_remove_all_guests()
							eu().wget_images(logger, wget_url, guest_name, ESX_HOST)
						# eu().esx_add_guest_first(logger, guest_name, ESX_HOST, VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, VIRTWHO_ESX_PASSWORD, vmware_cmd_ip)
						eu().esx_add_guest(logger, guest_name, ESX_HOST)
						eu().esx_start_guest_first(logger, guest_name, ESX_HOST)
						eu().esx_service_restart(logger, ESX_HOST)
						eu().esx_stop_guest(logger, guest_name, ESX_HOST)
						# restart virt-who service
						eu().vw_restart_virtwho(logger)
						# if got here, this script run well
						eu().SET_RESULT(0)
					else:
						logger.error("ESX host:'%s' has not been added to vCenter yet, add it manually first!" % ESX_HOST)
	
				if "rhevmmachine_ip" in params.keys():
					DNSserver_ip = "10.66.12.112"
					NFSserver_ip = "10.66.13.170"
					proxy_ip = "proxy=https:\/\/squid.corp.redhat.com:3128"
					nfs_dir_for_storage = "/home/vol/data5"
					nfs_dir_for_export = "/home/vol/data7"
					handleguest = params["handleguest"]
					rhevmmachine_ip = params['rhevmmachine_ip']
					rhevmmachine_name = eu().get_hostname(logger, rhevmmachine_ip)
					rhevm_host1_ip = params["rhel_host_ip"]
					rhevm_host1_name = eu().get_hostname(logger, rhevm_host1_ip)
					# virt-who configure for rhevm mode
					VIRTWHO_RHEVM_OWNER = "ACME_Corporation"
					VIRTWHO_RHEVM_ENV = "Library"
					VIRTWHO_RHEVM_SERVER = "https:\/\/" + rhevmmachine_ip + ":443"
					VIRTWHO_RHEVM_USERNAME = "admin@internal"
					VIRTWHO_RHEVM_PASSWORD = "redhat"
					copyimages = params['copyimages']
					if copyimages == "yes":
						# update virt-who configure file
						eu().rhevm_update_vw_configure(logger, VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, background=1, debug=1)
						# configure dns server, add rhel host
						eu().config_dnsserver(logger, rhevm_host1_ip, rhevm_host1_name, DNSserver_ip)
						# configure /etc/yum.conf
						eu().config_yum(logger, proxy_ip, rhevm_host1_ip)
						# add rhevm to rhel host in /etc/hosts
						eu().add_rhevm_server_to_host(logger, rhevmmachine_name, rhevmmachine_ip, rhevm_host1_ip)
						# add rhevm bridge in rhel host
						eu().configure_host_bridge(logger, rhevmmachine_name, rhevmmachine_ip, rhevm_host1_ip)
						# stop firewall
						eu().stop_firewall(logger, rhevm_host1_ip)
						if not eu().sub_isregistered(logger, rhevm_host1_ip):
							eu().conf_rhsm_candlepin(logger, rhevm_host1_ip)
							eu().sub_register(logger, ee.username_qa, ee.password_qa, rhevm_host1_ip)
							# Subscribe host to a physical pool which has a guest limit (not unlimited)
							eu().sub_subscribetopool_of_product(logger, ee.productid_guest, rhevm_host1_ip)
							# Subscribe host to Vitalization subscription
							eu().sub_subscribetopool_of_product(logger, ee.productid_Virtual_guest, rhevm_host1_ip)
						# add repo to rhel host
						eu().get_rhevm_repo_file(logger, rhevm_host1_ip)
						# Add host1 to rhevm
						eu().rhevm_add_host(logger, rhevm_host1_name, rhevm_host1_ip, rhevmmachine_ip)
						# auto connect rhevm-shell
						eu().config_rhevm_shell(logger, rhevmmachine_ip)
						# configure and register rhel host
						if eu().sub_isregistered(logger, rhevm_host1_ip):
							eu().sub_unregister(logger, rhevm_host1_ip)
							# add dns server to /etc/resolve.conf
							eu().rhevm_add_dns_to_host(logger, DNSserver_ip, rhevm_host1_ip)
							eu().conf_rhsm_sam(logger, rhevm_host1_ip)
							eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"), rhevm_host1_ip)
							eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"], rhevm_host1_ip)
							eu().sub_autosubscribe(logger, eu().get_env(logger)["autosubprod"], rhevm_host1_ip)
						# configure and register execute virt-who host
						if not eu().sub_isregistered(logger):
							eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"))
							eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"])
							eu().sub_autosubscribe(logger, eu().get_env(logger)["autosubprod"])
						# Add storagedomain to rhevm
						eu().add_storagedomain_to_rhevm(logger, "data_storage", rhevm_host1_name, "data", "v3", NFSserver_ip, nfs_dir_for_storage, rhevmmachine_ip)
						eu().add_storagedomain_to_rhevm(logger, "export_storage", rhevm_host1_name, "export", "v1", NFSserver_ip, nfs_dir_for_export, rhevmmachine_ip)
						eu().activate_storagedomain(logger, "export_storage", rhevmmachine_ip)
						eu().rhevm_define_guest(logger)
						eu().create_storage_pool(logger)
						# yum install virt-V2V
						eu().install_virtV2V(logger, rhevmmachine_name, rhevmmachine_ip)
						eu().convert_guest_to_nfs(logger, NFSserver_ip, nfs_dir_for_export, handleguest)
						eu().import_vm_to_rhevm(logger, handleguest, "data_storage", "export_storage", rhevmmachine_ip)
					eu().SET_RESULT(0)
	
				if "targetmachine_ip" in params.keys():
					# (1)set cpu socket
					eu().set_cpu_socket(logger)
					# (2)configure and register the host
					if not eu().sub_isregistered(logger):
						eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"))
						eu().sub_register(logger, eu().get_env(logger)["username"], eu().get_env(logger)["password"])
					# (3)update virt-who configure file
					eu().update_vw_configure(logger)
					# (4)restart virt-who service
					eu().vw_restart_virtwho(logger)
					# (5)copy all needed guests
					testtype = params['testtype']
					copyimages = params['copyimages']
					if copyimages == "yes":
						# if "beaker" in params.keys() and params['beaker'] == "yes":
						if "redhat.com" in params['targetmachine_ip']:
							eu().copy_images(logger, testtype, ee.beaker_image_machine_ip, ee.image_machine_imagepath, ee.imagenfspath)
						else:
							eu().copy_images(logger, testtype, ee.image_machine_ip, ee.image_machine_imagepath, ee.imagenfspath)
					# (6)export image path as nfs
					eu().export_dir_as_nfs(logger, ee.imagenfspath)
					# (7)mount image nfs path
					eu().mount_images_in_sourcemachine(logger, ee.imagenfspath, ee.imagepath)
					# (8)add some guests by define from host machine.
					eu().vw_define_all_guests(logger, testtype, params)
					# (9)set up env for migration if needed
					if params.has_key("targetmachine_ip") and params.has_key("targetmachine_hostname"):
						logger.info("-------- Begin to set up env for migration -------- ")
						targetmachine_ip = params["targetmachine_ip"]
						targetmachine_hostname = params["targetmachine_hostname"]
						# 1)mount image path in target machine
						eu().mount_images_in_targetmachine(logger, targetmachine_ip, ee.imagenfspath, ee.imagepath)
						# 2)mount the rhsm log of the target machine into source machine.
						eu().mount_rhsmlog_of_targetmachine(logger, targetmachine_ip, ee.rhsmlog_for_targetmachine)
						# 3)update /etc/hosts file
						eu().update_hosts_file(logger, targetmachine_ip, targetmachine_hostname)
						# 4)set cpu socket
						eu().set_cpu_socket(logger, targetmachine_ip=targetmachine_ip)
						# 5)stop firewall of two host machines for migration
						eu().stop_firewall(logger)
						eu().stop_firewall(logger, targetmachine_ip)
						# 6)update xen configuration file /etc/xen/xend-config.sxp of two host machines for migration to 
						# make sure contain necessary config options, and then restart service xend.
						if testtype == "xen":
							eu().update_xen_configure(logger)
							eu().update_xen_configure(logger, targetmachine_ip)
						# 7)configure and register the host
						if not eu().sub_isregistered(logger, targetmachine_ip):
							eu().configure_host(logger, params.get("samhostname"), params.get("samhostip"), targetmachine_ip)
							username = eu().get_env(logger)["username"]
							password = eu().get_env(logger)["password"]
							eu().sub_register(logger, username, password, targetmachine_ip)
						# 8)update virt-who configure file
						eu().update_vw_configure(logger, targetmachine_ip=targetmachine_ip)
						# 9)restart virt-who service in target machine
						eu().vw_restart_virtwho(logger, targetmachine_ip)
						logger.info("-------- End to set up env for migration -------- ")
					else:
						logger.info("There is no target machine ip/hostname provided, so does not setup env for migration.")
					# if got here, this script run well
					eu().SET_RESULT(0)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
