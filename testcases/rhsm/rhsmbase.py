from utils import *
import time, random
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class RHSMBase(unittest.TestCase):
    # ========================================================
    #       0. Basic Functions
    # ========================================================

    def runcmd(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None):
        if targetmachine_ip != None and targetmachine_ip != "":
            if targetmachine_user != None and targetmachine_user != "":
                commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
            else:
                commander = Command(targetmachine_ip, "root", "redhat")
        else:
            commander = Command(get_exported_param("REMOTE_IP"), username=get_exported_param("REMOTE_USER"), password=get_exported_param("REMOTE_PASSWD"))
        return commander.run(cmd, timeout, cmddesc)

#     def runcmd_remote(self, remoteIP, username, password, cmd):
#         """ Remote exec function via pexpect """
#         if not self.check_ip(remoteIP):
#             # only for beaker machines
#             remoteIP = self.domain_to_ip(remoteIP)
#             password = "xxoo2014"
#         user_hostname = "%s@%s" % (username, remoteIP)
#         child = pexpect.spawn("/usr/bin/ssh", [user_hostname, cmd], timeout=60, maxread=2000, logfile=None)
#         while True:
#             index = child.expect(['(yes\/no)', 'password:', pexpect.EOF, pexpect.TIMEOUT])
#             if index == 0:
#                 child.sendline("yes")
#             elif index == 1:
#                 child.sendline(password)
#             elif index == 2:
#                 child.close()
#                 return child.exitstatus, child.before
#             elif index == 3:
#                 child.close()

    def check_ip(self, ip_address):
        pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(pattern, ip_address):
            return True
        else:
            return False

    def domain_to_ip(self, domain_name):
        cmd = "dig +short %s" % domain_name
        (ret, output) = self.runcmd(cmd, "unregister")
        return output.strip("\n").strip(" ")

    def restore_environment(self):
        self.sub_unregister()

    # ========================================================
    #       1. Keyword Functions
    # ========================================================
    def sub_autosubscribe(self, autosubprod):
        # cmd = "subscription-manager subscribe --auto"
        cmd = "subscription-manager attach --auto"
        (ret, output) = self.runcmd(cmd, "auto-subscribe")
        if ret == 0:
            if ("Subscribed" in output) and ("Not Subscribed" not in output):
                logger.info("It's successful to auto-subscribe.")
            else:
                raise FailException("Test Failed - Failed to auto-subscribe correct product.")
        else:
            raise FailException("Test Failed - Failed to auto-subscribe.")

    def sub_register(self, username, password, subtype=""):
        if subtype == "":
            cmd = "subscription-manager register --username=%s --password='%s'" % (username, password)
        else:
            cmd = "subscription-manager register --type=%s --username=%s --password='%s'" % (subtype, username, password)

        if self.sub_isregistered():
            logger.info("The system is already registered, need to unregister first!")
            cmd_unregister = "subscription-manager unregister"
            (ret, output) = self.runcmd(cmd_unregister, "unregister")
            if ret == 0:
                if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                    logger.info("It's successful to unregister.")
                else:
                    logger.info("The system is failed to unregister, try to use '--force'!")
                    cmd += " --force"
        (ret, output) = self.runcmd(cmd, "register")
        if ret == 0:
            if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
                logger.info("It's successful to register.")
            else:
                raise FailException("Test Failed - The information shown after registered is not correct.")
        else:
            raise FailException("Test Failed - Failed to register.")

    def sub_unregister(self):
        if self.sub_isregistered():
            cmd = "subscription-manager unregister"
            (ret, output) = self.runcmd(cmd, "unregister")
            if ret == 0:
                if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                    logger.info("It's successful to unregister.")
                else:
                    raise FailException("Test Failed - The information shown after unregistered is not correct.")
            else:
                raise FailException("Test Failed - Failed to unregister.")
        else:
            self.sub_clean_local_data()
            logger.info("The system is not registered to server now.")

    def sub_clean_local_data(self):
        cmd = "subscription-manager clean"
        (ret, output) = self.runcmd(cmd, "clean local data")
        if ret == 0 and "All local data removed" in output:
            logger.info("Local data has been cleaned in the server now.")
        else:
            raise FailException("Test Failed - Failed to clean local data.")

    def sub_isregistered(self):
        cmd = "subscription-manager identity"
        (ret, output) = self.runcmd(cmd, "identity")
        if ret == 0:
            logger.info("The system is registered to server now.")
            return True
        else:
            logger.info("The system is not registered to server now.")
            if "has been deleted" in output:
                logger.info("the system is not registered to server but has local data!")
            return False

    def sub_checkidcert(self):
        cmd = "ls /etc/pki/consumer/"
        (ret, output) = self.runcmd(cmd, "listing the files in /etc/pki/consumer/")
        if ret == 0 and "cert.pem" in output and "key.pem" in output:
            logger.info("There are identity certs in the consumer directory.")
            return True
        else:
            logger.info("There is no identity certs in the consumer directory.")
            return False

    def sub_set_servicelevel(self, service_level):
        # set service-level
        cmd = "subscription-manager service-level --set=%s" % service_level
        (ret, output) = self.runcmd(cmd, "set service-level as %s" % service_level)
        if ret == 0 and "Service level set to: %s" % service_level in output:
            logger.info("It's successful to set service-level as %s" % service_level)
        else:
            raise FailException("Test Failed - Failed to set service-level as %s" % service_level)

    def sub_checkproductcert(self, productid):
        rctcommand = self.check_rct()
        if rctcommand == 0:
            cmd = "for i in /etc/pki/product/*; do rct cat-cert $i; done"
        else:
            cmd = "for i in /etc/pki/product/*; do openssl x509 -text -noout -in $i; done"
        (ret, output) = self.runcmd(cmd, "checking product cert")
        if ret == 0:
            if ("1.3.6.1.4.1.2312.9.1.%s" % productid in output) or ("ID: %s" % productid in output and "Path: /etc/pki/product/%s.pem" % productid in output):
                logger.info("The product cert is verified.")
            else:
                raise FailException("Test Failed - The product cert is not correct.")
        else:
            raise FailException("Test Failed - Failed to check product cert.")

    def check_rct(self):
        cmd = "rct cat-cert --help"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            logger.info("rct cat-cert command can be used in the system")
            return True
        else:
            logger.info("rct cat-cert command can not be used in the system")
            return False

    def sub_unsubscribe(self):
        cmd = "subscription-manager unsubscribe --all"
        (ret, output) = self.runcmd(cmd, "unsubscribe")
        expectout = "This machine has been unsubscribed from"
        expectoutnew = "subscription removed from this system."
        expectout5101 = "subscription removed at the server."
        expectout5102 = "local certificate has been deleted."
        if ret == 0:
            if output.strip() == "" or (((expectout5101 in output) and (expectout5102 in output)) or expectout in output or expectoutnew in output):
                logger.info("It's successful to unsubscribe.")
            else:
                raise FailException("Test Failed - The information shown after unsubscribed is not correct.")
        else:
            raise FailException("Test Failed - Failed to unsubscribe.")

    def sub_getcurrentversion(self):
        version = None
        platform = None
        currentversion = None
        # get version
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = Command().run(cmd, comments=False)
        if ret == 0:
            version = output.strip("\n").strip(" ")
            logger.info("It's successful to get system version.")
        else:
            logger.info("It's failed to get system version.")
        # get paltform
        cmd = "lsb_release -i"
        (ret, output) = Command().run(cmd, comments=False)
        if ret == 0:
            platform = output.split("Enterprise")[1].strip(" ")
            logger.info("It's successful to get system platform")
        else:
            logger.info("It's failed to get system platform.")
        currentversion = version + platform
        return currentversion

    def sub_listavailpools(self, productid):
        cmd = "subscription-manager list --available"
        (ret, output) = Command().run(cmd)
        if ret == 0:
            if "no available subscription pools to list" not in output.lower():
                if productid in output:
                    logger.info("The right available pools are listed successfully.")
                    pool_list = self.__parse_listavailable_output(output)
                    return pool_list
                else:
                    raise FailException("Not the right available pools are listed!")
            else:
                logger.info("There is no Available subscription pools to list!")
                return None
        else:
            raise FailException("Test Failed - Failed to list available pools.")

    def __parse_listavailable_output(self, output):
        datalines = output.splitlines()
        data_list = []
        # split output into segmentations for each pool
        data_segs = []
        segs = []
        tmpline = ""
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                tmpline = line
            elif line and ":" not in line:
                tmpline = tmpline + ' ' + line.strip()
            elif line and ":" in line:
                segs.append(tmpline)
                tmpline = line
            if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
                segs.append(tmpline)
                data_segs.append(segs)
                segs = []
        for seg in data_segs:
            data_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(' ', '')
                valueitem = item.split(":")[1].strip()
                data_dict[keyitem] = valueitem
            data_list.append(data_dict)
        return data_list

    def get_subscription_serialnumlist(self):
        cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
        (ret, output) = self.runcmd(cmd, "list all certificates in /etc/pki/entitlement/")
        ent_certs = output.splitlines()
        serialnumlist = [line.replace('.pem', '') for line in ent_certs]
        return serialnumlist

    def sub_checkentitlementcerts(self, productid):
        rctcommand = self.check_rct()
        if rctcommand == True:
            cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do rct cat-cert /etc/pki/entitlement/$i; done | grep %s" % (productid)
        else:
            cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i; done | grep %s" % (productid)
        (ret, output) = self.runcmd(cmd, "check entitlement certs")
        if ret == 0:
            if productid in output:
                logger.info("It's successful to check entitlement certificates.")
            else:
                raise FailException("Test Failed - The information shown entitlement certificates is not correct.")
        else:
            raise FailException("Test Failed - Failed to check entitlement certificates.")

    def sub_isconsumed(self, productname):
        cmd = "subscription-manager list --consumed"
        (ret, output) = self.runcmd(cmd, "listing consumed subscriptions")
        output_join = " ".join(x.strip() for x in output.split())
        if (ret == 0) and (productname in output or productname in output_join):
            logger.info("The subscription of the product is consumed.")
            return True
        else:
            logger.info("The subscription of the product is not consumed.")
            return False

    def sub_get_consumerid(self):
        consumerid = ''
        if self.sub_isregistered():
            cmd = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd, "get consumerid")
            if ret == 0 and ("system identity:" in output or "Current identity" in output):
                consumerid_gain = output.split('\n')
                consumerid_line_split = (consumerid_gain[0]).split(":")
                consumerid = (consumerid_line_split[1]).strip()
                logger.info("consumerid is gained successfully!")
            else:
                raise FailException("Test Failed - Failed to get subscription-manager identity")
        return consumerid

    def sub_listallavailpools(self, productid):
        cmd = "subscription-manager list --available --all"
        (ret, output) = self.runcmd(cmd, "listing available pools")
        if ret == 0:
            if "no available subscription pools to list" not in output.lower():
                if productid in output:
                    logger.info("The right available pools are listed successfully.")
                    pool_list = self.parse_listavailable_output(output)
                    return pool_list
                else:
                    raise FailException("Not the right available pools are listed!")
            else:
                logger.info("There is no Available subscription pools to list!")
                return None
        else:
            raise FailException("Test Failed - Failed to list all available pools.")

    def parse_listavailable_output(self, output):
        datalines = output.splitlines()
        data_list = []
        # split output into segmentations for each pool
        data_segs = []
        segs = []
        tmpline = ""
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                tmpline = line
            elif line and ":" not in line:
                tmpline = tmpline + ' ' + line.strip()
            elif line and ":" in line:
                segs.append(tmpline)
                tmpline = line
            if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
                segs.append(tmpline)
                data_segs.append(segs)
                segs = []
        for seg in data_segs:
            data_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(' ', '')
                valueitem = item.split(":")[1].strip()
                data_dict[keyitem] = valueitem
            data_list.append(data_dict)
        return data_list

    def sam_remote_create_org(self, samserverIP, username, password, orgname):
        # create organization with orgname
        cmd = "headpin -u admin -p admin org create --name=%s" % (orgname)
        (ret, output) = self.runcmd_remote(samserverIP, username, password, cmd)
        if ret == 0 and "Successfully created org" in output:
            logger.info("It's successful to create organization %s." % orgname)
        else:
            raise FailException("Test Failed - Failed to create organization %s." % orgname)

    def sam_remote_delete_org(self, samserverIP, username, password, orgname):
        # delete an existing organization
        if self.sam_remote_is_org_exist(samserverIP, username, password, orgname):
            cmd = "headpin -u admin -p admin org delete --name=%s" % (orgname)
            (ret, output) = self.runcmd_remote(samserverIP, username, password, cmd)
            if ret == 0 and "Successfully deleted org" in output:
                logger.info("It's successful to delete organization %s." % orgname)
            else:
                raise FailException("Test Failed - Failed to delete organization %s." % orgname)
        else:
            logger.info("Org %s to be deleted does not exist." % (orgname))

    def sam_remote_is_org_exist(self, samserverIP, username, password, orgname):
        # check an organization existing or not
        cmd = "headpin -u admin -p admin org list"
        (ret, output) = self.runcmd_remote(samserverIP, username, password, cmd)
        if ret == 0 and orgname in output:
            logger.info("Organization %s exists." % orgname)
            return True
        else:
            logger.info("Organization %s does not exist." % orgname)
            return False

    def parse_listconsumed_output(self, output):
        datalines = output.splitlines()
        data_list = []
        # split output into segmentations
        data_segs = []
        segs = []
        tmpline = ""
        '''
        for line in datalines:
        if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
              segs.append(line)
        elif segs:
             segs.append(line)
        if ("Expires:" in line) or ("Ends:" in line):
                data_segs.append(segs)
                segs = []
        '''
         # new way
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                tmpline = line
            elif line and ":" not in line:
                tmpline = tmpline + ' ' + line.strip()
            elif line and ":" in line:
                segs.append(tmpline)
                tmpline = line
            if ("Expires:" in line) or ("Ends:" in line):
                segs.append(tmpline)
                data_segs.append(segs)
                segs = []

        '''# handle item with multi rows
        for seg in data_segs:
                length = len(seg)
                for index in range(0, length):
                        if ":" not in seg[index]:
                                seg[index-1] = seg[index-1] + " " + seg[index].strip()
                for item in seg:
                        if ":" not in item:
                                seg.remove(item)
        '''
            # parse detail information
        for seg in data_segs:
            data_dict = {}
        for item in seg:
           keyitem = item.split(":")[0].replace(' ', '')
           valueitem = item.split(":")[1].strip()
           data_dict[keyitem] = valueitem
        data_list.append(data_dict)
        return data_list

    def restart_rhsmcertd(self):
        cmd = "service rhsmcertd restart"
        (ret, output) = self.runcmd(cmd, "restart rhsmcertd service")
        if ret == 0 and "Redirecting to /bin/systemctl restart  rhsmcertd.service" in output:
            logger.info("It's successful to restart rhsmcertd service")
        else:
            raise FailException("Test Failed - Failed to restart rhsmcertd service.")

    def check_and_backup_yum_repos(self):
        # check if yum.repos.d is empty
        cmd = "ls /etc/yum.repos.d | wc -l"
        (ret, output) = self.runcmd(cmd, "check if yum.repos.d is empty")
        if ret == 0:
            if output.strip() != '0':
                logger.info("It's successful to verify yum.repos.d is NOT empty. Backup is needed before testing")
                backuprepo = True
            else:
                logger.info("No need to back repos.")
                backuprepo = False
        else:
            raise FailException("Test Failed - Failed to check if yum.repos.d is empty.")
        if backuprepo == True:
            cmd = "rm -rf /root/backuprepo;mkdir /root/backuprepo; mv /etc/yum.repos.d/* /root/backuprepo/"
            (ret, output) = self.runcmd(cmd, "backup repo")
            if ret == 0:
                logger.info("It's successful to backup repo.")
            else:
                raise FailException("Test Failed - Failed to backuprepo.")
        else:
            logger.info("No need to back up repos")

    def restore_repos(self):
        cmd = "ls /root/backuprepo"
        (ret, output) = self.runcmd(cmd, "check if repos' backup is empty")
        if ret == 0:
            logger.info("The repos backup exist, and need restore")
            cmd = "mv /root/backuprepo/* /etc/yum.repos.d/"
            (ret, output) = self.runcmd(cmd, "restore repos back up")
            if ret == 0:
                logger.info("It's successful to restore repos")
            else:
                raise FailException("Test Failed - Failed to restore repo.")
        else:
            logger.info("no need to restore the repos")


#     def copyfiles(self, vm, sourcepath, targetpath, cmddesc=""):
#             if vm != None:
#                     vm.copy_files_to(sourcepath, targetpath)
#             else:
#                     cmd = "cp -rf %s %s" % (sourcepath, targetpath)
#                     (ret, output) = self.runcmd(cmd, cmddesc)
# 
#     def write_proxy_to_yum_conf(self, params, env):
#             logger.info("Add proxy to /etc/yum.conf")
#             proxy_eng = "squid.corp.redhat.com:3128"
# 
#             # get proxy_eng value
#             if proxy_eng == '':
#                     pass
#             else:
#                     usrname = params.get("guest_name")
#                     rel = usrname.split('.')[0]
#                     proxy_head = 'proxy'
# 
#                     cmd = "cat /etc/yum.conf|grep 'proxy'"
#                     (ret, output) = self.runcmd(cmd, "list proxy in /etc/yum.conf")
#                     if (ret == 0):
#                             pass
#                     else:
#                             input_proxy_eng = ('%s=https://%s' % (proxy_head, proxy_eng))
#                             cmd = "echo %s >>/etc/yum.conf" % input_proxy_eng
#                             (ret, output) = self.runcmd(cmd, "cat proxy to /etc/yum.conf")
#                             if (ret == 0):
#                                     logger.info("It is success to write %s to /etc/yum.conf" % input_proxy_eng)
#                             else:
#                                     logger.error("It is failed to write %s to /etc/yum.conf" % input_proxy_eng)
#                                     return False
# 
#     def write_proxy_to_rhsm_conf(self, params, env):
#         logger.info("Add proxy to /etc/rhsm/rhsm.conf")
#         proxy_hostname = "squid.corp.redhat.com"
#         proxy_port = "3128"
#     
#         (ret, output) = self.runcmd("ifconfig", "get IP")
#         if "10.66" in output and proxy_hostname != "":
#             cmd = "cat /etc/rhsm/rhsm.conf | grep 'squid'"
#             (ret, output) = self.runcmd(cmd, "check proxy setting in /etc/rhsm/rhsm.conf")
#         if (ret == 0):
#             pass
#         else:
#             cmd = "sed -i 's/proxy_hostname =/proxy_hostname = squid.corp.redhat.com/' /etc/rhsm/rhsm.conf"
#             (ret, output) = self.runcmd(cmd, "set proxy_hostname")
#         if (ret == 0):
#                 logger.info("It is success to set proxy_hostname to /etc/rhsm/rhsm.conf")
#         else:
#                 logger.error("It is failed to set proxy_hostname to /etc/rhsm/rhsm.conf")
#                 return False
# 
#         cmd = "sed -i 's/proxy_port =/proxy_port = 3128/' /etc/rhsm/rhsm.conf"
#         (ret, output) = self.runcmd(cmd, "set proxy_port")
#         if (ret == 0):
#                 logger.info("It is success to set proxy_port to /etc/rhsm/rhsm.conf")
#         else:
#                 logger.error("It is failed to set proxy_port to /etc/rhsm/rhsm.conf")
#                 return False
#     
#     def is_file(self, file_path):
#         # confirm the file is existing or not
#         cmd = "(if [ -s '%s' ];then echo \"SUCCESS to find file %s\";else  echo \"FAIL to find file %s\"; fi)" % (file_path, file_path, file_path)
#         (ret, output) = self.runcmd(cmd, "find the file")
#         
#         if ret == 0 and 'SUCCESS' in output:
#             return True
#         else:
#             return False
# 
#     # ========================================================
#     #       1. 'Acceptance' Test Common Functions
#     # ========================================================
# 
#     def sub_configplatform(self, hostname):
#             cmd = "subscription-manager config --server.hostname=%s" % (hostname)
#             (ret, output) = self.runcmd(cmd, "configuring the system")
# 
#             if ret == 0:
#                     logger.info("It's successful to configure the system as %s." % hostname)
#             else:
#                     raise FailException("Test Failed - Failed to configure the system as %s." % hostname)
# 

# 

# 
#     def sub_get_poolid(self):
#             poolid = ''
#             if self.sub_isregistered():
#                     cmd = "subscription-manager list --consumed"
#                     (ret, output) = self.runcmd(cmd, "get poolid")
#                     if ret == 0 and "Pool ID:" in output:
#                             poolid_gain = output.split('\n')
#                             poolid_line_split = (poolid_gain[0]).split(":")
#                             poolid = (poolid_line_split[1]).strip()
#                             logger.info("poolid is gained successfully!")
#                     else:
#                             raise FailException("Test Failed - Failed to get subscription-manager poolid")
#             return poolid
# 
#     def sub_listavailpools(self, productid):
#             cmd = "subscription-manager list --available"
#             (ret, output) = self.runcmd(cmd, "listing available pools")
# 
#             if ret == 0:
#                     if "no available subscription pools to list" not in output.lower():
#                             if productid in output:
#                                     logger.info("The right available pools are listed successfully.")
#                                     pool_list = self.parse_listavailable_output(output)
#                                     return pool_list
#                             else:
#                                     raise FailException("Not the right available pools are listed!")
# 
#                     else:
#                             logger.info("There is no Available subscription pools to list!")
#                             return None
#             else:
#                     raise FailException("Test Failed - Failed to list available pools.")
# 
#     def sub_listinstalledpools(self):
#             cmd = "subscription-manager list --installed"
#             (ret, output) = self.runcmd(cmd, "listing installed pools")
#             if ret == 0:
#                     logger.info("The right installed pools are listed successfully.")
#                     pool_list = self.parse_listavailable_output(output)
#                     return pool_list
#             else:
#                     raise FailException("Test Failed - Failed to list installed pools.")
# 
#     def sub_listconsumedpools(self):
#             cmd = "subscription-manager list --consumed"
#             (ret, output) = self.runcmd(cmd, "listing consumed pools")
#             if ret == 0:
#                     logger.info("The right consumed pools are listed successfully.")
#                     pool_list = self.parse_listavailable_output(output)
#                     return pool_list
#             else:
#                     raise FailException("Test Failed - Failed to list consumed pools.")
# 

# 

# 


#     def sub_subscribetopool(self, poolid):
#             cmd = "subscription-manager subscribe --pool=%s" % (poolid)
#             (ret, output) = self.runcmd(cmd, "subscribe")
# 
#             if ret == 0:
#                     # Note: the exact output should be as below:
#                     # For 6.2: "Successfully subscribed the system to Pool"
#                     # For 5.8: "Successfully consumed a subscription from the pool with id"
#                     if "Successfully " in output:
#                             logger.info("It's successful to subscribe.")
#                     else:
#                             raise FailException("Test Failed - The information shown after subscribing is not correct.")
#             else:
#                     raise FailException("Test Failed - Failed to subscribe.")
# 



# 

# 

#     def cnt_subscribe_product_with_specified_sku(self, prodsku):
#             # subscribe with the specified prodsku
#             dictlist = self.sub_listavailpools_of_sku(prodsku)
#             odict = dictlist[0]
#             prodpool = ''
#             if odict.has_key('SKU'):
#                     if odict.get('SKU') == prodsku:
#                             if odict.has_key('Pool ID'):
#                                     prodpool = odict.get('Pool ID')
#                             elif odict.has_key('PoolId'):
#                                     prodpool = odict.get('PoolId')
#                             elif odict.has_key('PoolID'):
#                                     prodpool = odict.get('PoolID')
# 
#                             self.sub_subscribetopool(prodpool)
#                             return True
#             else:
#                     return False
# 


# 
#     def sub_checkidcert(self):
#             cmd = "ls /etc/pki/consumer/"
#             (ret, output) = self.runcmd(cmd, "listing the files in /etc/pki/consumer/")
# 
#             if ret == 0 and "cert.pem" in output and "key.pem" in output:
#                     logger.info("There are identity certs in the consumer directory.")
#                     return True
#             else:
#                     logger.info("There is no identity certs in the consumer directory.")
#                     return False
# 

# 

# 
#     def sub_getcurrentversion2(self, guestname):
#             os_version = guestname.split('-')[-1].strip()
#             return os_version
# 



#             # stop rhsmcertd because healing(autosubscribe) will run 2 mins after the machine is started, then every 24 hours after that, which will influence our content test.
#             cmd = 'service rhsmcertd status'
#             (ret, output) = self.runcmd(cmd, "check rhsmcertd service status")
#             if 'stopped' in output or 'Stopped' in output:
#                     return
# 
#             cmd = 'service rhsmcertd stop'
#             (ret, output) = self.runcmd(cmd, "stop rhsmcertd service")
#             if (ret == 0):
#                     cmd = 'service rhsmcertd status'
#                     (ret, output) = self.runcmd(cmd, "check rhsmcertd service status")
#                     if 'stopped' in output or 'Stopped' in output:
#                             logger.info("It's successful to stop rhsmcertd service.")
#                     else:
#                         logger.error("Failed to stop rhsmcertd service.")
#             else:
#                 logger.error("Failed to stop rhsmcertd service.")
# 
#     # ========================================================
#     #       3. 'SAM Server' Test Common Functions
#     # ========================================================
# 
#     def sam_create_user(self, username, password, email):
#             # create user with username, password and email address
#             cmd = "headpin -u admin -p admin user create --username=%s --password=%s --email=%s" % (username, password, email)
#             (ret, output) = self.runcmd(cmd, "creating user")
# 
#             if (ret == 0) and ("Successfully created user" in output):
#                     logger.info("It's successful to create user %s with password %s and email %s." % (username, password, email))
#             else:
#                     raise FailException("Test Failed - Failed to create user %s with password %s and email %s." % (username, password, email))
# 
#     def sam_is_user_exist(self, username):
#             # check a user exist or not
#             cmd = "headpin -u admin -p admin user list"
#             (ret, output) = self.runcmd(cmd, "listing user")
# 
#             if (ret == 0) and (username in output):
#                     logger.info("User %s exists." % (username))
#                     return True
#             else:
#                     logger.info("User %s does not exist." % (username))
#                     return False
# 
#     def sam_delete_user(self, username):
#             # delete user with username
#             if self.sam_is_user_exist(username):
#                     cmd = "headpin -u admin -p admin user delete --username=%s" % (username)
#                     (ret, output) = self.runcmd(cmd, "deleting user")
# 
#                     if (ret == 0) and ("Successfully deleted user" in output):
#                             logger.info("It's successful to delete user %s." % (username))
#                     else:
#                             raise FailException("Test Failed - Failed to delete user %s." % (username))
#             else:
#                     logger.info("User %s to be deleted does not exist." % (username))
# 
#     def sam_create_org(self, orgname):
#             # create organization with orgname
#             cmd = "headpin -u admin -p admin org create --name=%s" % (orgname)
#             (ret, output) = self.runcmd(cmd, "creating organization")
# 
#             if ret == 0 and "Successfully created org" in output:
#                     logger.info("It's successful to create organization %s." % orgname)
#             else:
#                     raise FailException("Test Failed - Failed to create organization %s." % orgname)
# 
# 
#     def sam_is_org_exist(self, orgname):
#             # check an organization existing or not
#             cmd = "headpin -u admin -p admin org list"
#             (ret, output) = self.runcmd(cmd, "list organization")
# 
#             if ret == 0 and orgname in output:
#                     logger.info("Organization %s exists." % orgname)
#                     return True
#             else:
#                     logger.info("Organization %s does not exist." % orgname)
#                     return False
# 
#     def sam_delete_org(self, orgname):
#             # delete an existing organization
#             if self.sam_is_org_exist(orgname):
#                     cmd = "headpin -u admin -p admin org delete --name=%s" % (orgname)
#                     (ret, output) = self.runcmd(cmd, "delete organization")
# 
#                     if ret == 0 and "Successfully deleted org" in output:
#                             logger.info("It's successful to delete organization %s." % orgname)
#                     else:
#                             raise FailException("Test Failed - Failed to delete organization %s." % orgname)
#             else:
#                     logger.info("Org %s to be deleted does not exist." % (orgname))
# 



# 
#     def sam_create_env(self, envname, orgname, priorenv):
#             ''' create environment belong to organizaiton with prior environment. '''
# 
#             cmd = "headpin -u admin -p admin environment create --name=%s --org=%s --prior=%s" % (envname, orgname, priorenv)
#             (ret, output) = self.runcmd(cmd, "create environment")
# 
#             if ret == 0:
#                     logger.info("It's successful to create environment '%s' - belong to organizaiton '%s' with prior environment '%s'." % (envname, orgname, priorenv))
#             else:
#                     raise FailException("Test Failed - Failed to create environment '%s' - belong to organizaiton '%s' with prior environment '%s'." % (envname, orgname, priorenv))
# 
#     def sam_check_env(self, envname, orgname, priorenv, desc='None'):
#             ''' check environment info. '''
# 
#             cmd = "headpin -u admin -p admin environment info --name=%s --org=%s" % (envname, orgname)
#             (ret, output) = self.runcmd(cmd, "check environment detail info")
# 
#             if (ret == 0) and (envname in output) and (orgname in output) and (priorenv in output) and (desc in output):
#                     logger.info("It's successful to check environment detail info.")
#             else:
#                     raise FailException("Test Failed - Failed to check environment detail info.")
# 
#     def sam_is_env_exist(self, envname, orgname):
#             ''' check if an environment of one org existing or not. '''
# 
#             cmd = "headpin -u admin -p admin environment list --org=%s" % orgname
#             (ret, output) = self.runcmd(cmd, "list environment")
# 
#             if ret == 0 and envname in output:
#                     logger.info("Environment %s exists." % envname)
#                     return True
#             else:
#                     logger.info("Environment %s does not exist." % envname)
#                     return False
# 
#     def sam_delete_env(self, envname, orgname):
#             ''' delete an existing environment. '''
# 
#             if self.sam_is_env_exist(envname, orgname):
#                     cmd = "headpin -u admin -p admin environment delete --name=%s --org=%s" % (envname, orgname)
#                     (ret, output) = self.runcmd(cmd, "delete environment")
# 
#                     if ret == 0 and "Successfully deleted environment" in output:
#                             logger.info("It's successful to delete environment %s." % envname)
#                     else:
#                             raise FailException("Test Failed - Failed to delete environment %s." % envname)
#             else:
#                     logger.info("Environment %s to be deleted does not exist." % (envname))
# 
#     def sam_create_activationkey(self, keyname, envname, orgname):
#             # create an activationkey
#             cmd = "headpin -u admin -p admin activation_key create --name=%s --org=%s --env=%s" % (keyname, orgname, envname)
#             (ret, output) = self.runcmd(cmd, "create activationkey")
# 
#             if ret == 0 and "Successfully created activation key" in output:
#                     logger.info("It's successful to create activationkey %s belong to organizaiton %s environment %s." % (keyname, orgname, envname))
#             else:
#                     raise FailException("Test Failed - Failed to create activationkey %s belong to organizaiton %s environment %s." % (keyname, orgname, envname))
# 
#     def sam_is_activationkey_exist(self, keyname, orgname):
#             # check an activationkey of one org existing or not
#             cmd = "headpin -u admin -p admin activation_key list --org=%s" % orgname
#             (ret, output) = self.runcmd(cmd, "list activationkey")
# 
#             if ret == 0 and keyname in output:
#                     logger.info("Activationkey %s exists." % keyname)
#                     return True
#             else:
#                     logger.info("Activationkey %s doesn't exist." % keyname)
#                     return False
# 
#     def sam_delete_activationkey(self, keyname, orgname):
#             # delete an existing activation key
#             if self.sam_is_activationkey_exist(keyname, orgname):
#                     cmd = "headpin -u admin -p admin activation_key delete --name=%s --org=%s" % (keyname, orgname)
#                     (ret, output) = self.runcmd(cmd, "delete activationkey")
# 
#                     if ret == 0 and "Successfully deleted activation key" in output:
#                             logger.info("It's successful to delete activation key %s." % keyname)
#                     else:
#                             raise FailException("Test Failed - Failed to delete activation key %s." % keyname)
#             else:
#                     logger.info("Activationkey %s to be deleted doesn't exist." % (keyname))
# 
#     def sam_save_option(self, optionname, optionvalue):
#             ''' save an option. '''
# 
#             cmd = "headpin -u admin -p admin client remember --option=%s --value=%s" % (optionname, optionvalue)
#             (ret, output) = self.runcmd(cmd, "save option")
# 
#             if ret == 0 and "Successfully remembered option [ %s ]" % (optionname) in output:
#                     logger.info("It's successful to save the option '%s'." % optionname)
#             else:
#                     raise FailException("Test Failed - Failed to save the option '%s'." % optionname)
# 
#     def sam_remove_option(self, optionname):
#             ''' remove an option. '''
# 
#             cmd = "headpin -u admin -p admin client forget --option=%s" % optionname
#             (ret, output) = self.runcmd(cmd, "remove option")
# 
#             if ret == 0 and "Successfully forgot option [ %s ]" % (optionname) in output:
#                     logger.info("It's successful to remove the option '%s'." % optionname)
#             else:
#                     raise FailException("Test Failed - Failed to remove the option '%s'." % optionname)
# 
#     def sam_add_pool_to_activationkey(self, orgname, keyname):
#             # find a pool belonging to the key's org
#             cmd = "curl -u admin:admin -k https://localhost/sam/api/owners/%s/pools |python -mjson.tool|grep 'pools'|awk -F'\"' '{print $4}'" % (orgname)
#             (ret, output) = self.runcmd(cmd, "finding an available pool")
# 
#             if ret == 0 and "pools" in output:
#                     poollist = self.__parse_sam_avail_pools(output)
# 
#                     # get an available entitlement pool to subscribe with random.sample
#                     poolid = random.sample(poollist, 1)[0]
#                     logger.info("It's successful to find an available pool '%s'." % (poolid))
# 
#                     # add a pool to an activationkey
#                     cmd = "headpin -u admin -p admin activation_key update --org=%s --name=%s --add_subscription=%s" % (orgname, keyname, poolid)
#                     (ret, output) = self.runcmd(cmd, "add a pool to an activationkey")
# 
#                     if ret == 0 and "Successfully updated activation key [ %s ]" % (keyname) in output:
#                             # check whether the pool is in the key
#                             cmd = "headpin -u admin -p admin activation_key info --name=%s --org=%s" % (keyname, orgname)
#                             (ret, output) = self.runcmd(cmd, "check activationkey info")
# 
#                             if ret == 0 and poolid in output:
#                                     logger.info("It's successful to add pool '%s' to activationkey '%s'." % (poolid, keyname))
#                                     return poolid
#                             else:
#                                     raise FailException("It's failed to add a pool to activationkey '%s'." % keyname)
#                     else:
#                             raise FailException("Test Failed - Failed to add a pool to activationkey '%s'." % keyname)
#             else:
#                     raise FailException("Test Failed - Failed to find an available pool")
# 
#     def __parse_sam_avail_pools(self, output):
#             datalines = output.splitlines()
#             poollist = []
#             # pick up pool lines from output
#             data_segs = []
#             for line in datalines:
#                     if "/pools/" in line:
#                             data_segs.append(line)
# 
#             # put poolids into poolist
#             for seg in data_segs:
#                     pool = seg.split("/")[2]
#                     poollist.append(pool)
#             return poollist
# 
#     def sam_import_manifest_to_org(self, filepath, orgname, provider):
#             # import a manifest to an organization
#             cmd = "headpin -u admin -p admin provider import_manifest --org=%s --name='%s' --file=%s" % (orgname, provider, filepath)
#             (ret, output) = self.runcmd(cmd, "import manifest")
# 
#             if ret == 0 and "Manifest imported" in output:
#                     logger.info("It's successful to import manifest to org '%s'." % orgname)
#             else:
#                     raise FailException("Test Failed - Failed to import manifest to org '%s'." % orgname)
# 
#     def sam_is_product_exist(self, productname, provider, orgname):
#             # check whether a product is in the product list of an org
#             cmd = "headpin -u admin -p admin product list --org=%s --provider='%s'" % (orgname, provider)
#             (ret, output) = self.runcmd(cmd, "list products of an organization")
# 
#             if ret == 0 and productname in output:
#                     logger.info("The product '%s' is in the product list of org '%s'." % (productname, orgname))
#                     return True
#             else:
#                     logger.info("The product '%s' isn't in the product list of org '%s'." % (productname, orgname))
#                     return False
# 
#     def sam_create_system(self, systemname, orgname, envname):
#             # get environment id of envname
#             cmd = "curl -u admin:admin -k https://localhost/sam/api/organizations/%s/environments/|python -mjson.tool|grep -C 2 '\"name\": \"%s\"'" % (orgname, envname)
#             (ret, output) = self.runcmd(cmd, "get environment id")
# 
#             if ret == 0 and envname in output:
#                     # get the env id from output
#                     envid = self.__parse_env_output(output)
# 
#                     if envid != "":
#                             # create a new system using candlepin api
#                             cmd = "curl -u admin:admin -k --request POST --data '{\"name\":\"%s\",\"cp_type\":\"system\",\"facts\":{\"distribution.name\":\"Red Hat Enterprise Linux Server\",\"cpu.cpu_socket(s)\":\"1\",\"virt.is_guest\":\"False\",\"uname.machine\":\"x86_64\"}}' --header 'accept: application/json' --header 'content-type: application/json' https://localhost/sam/api/environments/%s/systems|grep %s" % (systemname, envid, systemname)
# 
#                             (ret, output) = self.runcmd(cmd, "create a system")
# 
#                             if ret == 0 and systemname in output:
#                                     logger.info("It's successful to create system '%s' in org '%s'." % (systemname, orgname))
#                             else:
#                                     raise FailException("Test Failed - Failed to create system '%s' in org '%s'." % (systemname, orgname))
#                     else:
#                             raise FailException("Test Failed - Failed to get envid of env '%s' from org '%s'." % (envname, orgname))
#             else:
#                     raise FailException("Test Failed - Failed to get env info from org '%s'." % orgname)
# 
#     def __parse_env_output(self, output):
#             datalines = output.splitlines()
#             envid = ""
#             for line in datalines:
#                     if "\"id\"" in line:
#                             envid = line.split(":")[1].split(",")[0].strip()
#                             break
#             return envid
# 
#     def sam_list_system(self, orgname, systemname):
#             ''' list system and then check system list. '''
# 
#             cmd = "headpin -u admin -p admin system list --org=%s" % (orgname)
#             (ret, output) = self.runcmd(cmd, "list system")
# 
#             if (ret == 0) and (systemname in output):
#                     logger.info("It's successful to list system '%s'." % systemname)
#             else:
#                     raise FailException("Test Failed - Failed to list system '%s'." % systemname)
# 
#     def sam_is_system_exist(self, orgname, systemname):
#             ''' check if the system exists. '''
# 
#             cmd = "headpin -u admin -p admin system list --org=%s" % (orgname)
#             (ret, output) = self.runcmd(cmd, "list system")
# 
#             if (ret == 0) and (systemname in output):
#                     logger.info("The system '%s' exists." % systemname)
#                     return True
#             else:
#                     logger.info("The system %s does not exist." % systemname)
#                     return False
# 
#     def sam_list_system_detail_info(self, systemname, orgname, envname, checkinfolist):
#             ''' list system info. '''
# 
#             cmd = "headpin -u admin -p admin system info --name=%s --org=%s --environment=%s" % (systemname, orgname, envname)
#             (ret, output) = self.runcmd(cmd, "list system detail info")
# 
#             if (ret == 0):
#                     for i in checkinfolist:
#                             if i in output:
#                                     logger.info("The info '%s' is in command output." % i)
#                             else:
#                                     raise FailException("Test Failed - Failed to list system detail info - the info '%s' is not in command output." % i)
# 
#                     logger.info("It's successful to list system detail info.")
#             else:
#                     raise FailException("Test Failed - Failed to list system detail info.")
# 
#     def sam_unregister_system(self, systemname, orgname):
#             ''' unregister a system. '''
# 
#             if self.sam_is_system_exist(orgname, systemname):
#                     cmd = "headpin -u admin -p admin system unregister --name=%s --org=%s" % (systemname, orgname)
#                     (ret, output) = self.runcmd(cmd, "register system")
# 
#                     if ret == 0 and "Successfully unregistered System [ %s ]" % systemname in output:
#                             logger.info("It's successful to unregister the system '%s' - belong to organizaiton '%s'." % (systemname, orgname))
#                     else:
#                             raise FailException("Test Failed - Failed to unregister the system '%s' - belong to organizaiton '%s'." % (systemname, orgname))
#             else:
#                     logger.info("System '%s' to be unregistered does not exist." % (systemname))
# 
#     def sam_listavailpools(self, systemname, orgname):
#             ''' list available subscriptions. '''
#             cmd = "headpin -u admin -p admin system subscriptions --org=%s --name=%s --available" % (orgname, systemname)
#             (ret, output) = self.runcmd(cmd, "list available pools")
# 
#             if ret == 0 and ("Pool" in output or "PoolId" in output):
#                     logger.info("The available pools are listed successfully.")
#                     pool_list = self.__parse_sam_avail_pools_cli(output)
#                     return pool_list
#             else:
#                     raise FailException("Test Failed - Failed to list available pools.")
#                     return None
# 
#     def __parse_sam_avail_pools_cli(self, output):
#             datalines = output.splitlines()
#             pool_list = []
#             # split output into segmentations for each pool
#             data_segs = []
#             segs = []
#             for line in datalines:
#                     if "Pool:" in line or "PoolId" in line:
#                             segs.append(line)
#                     elif segs:
#                             segs.append(line)
#                     if "MultiEntitlement:" in line:
#                             data_segs.append(segs)
#                             segs = []
#             # parse detail information for each pool
#             for seg in data_segs:
#                     pool_dict = {}
#                     for item in seg:
#                             keyitem = item.split(":")[0].replace(' ', '')
#                             valueitem = item.split(":")[1].strip()
#                             pool_dict[keyitem] = valueitem
#                     pool_list.append(pool_dict)
#             return pool_list
# 
#     def sam_subscribetopool(self, systemname, orgname, poolid):
#             ''' subscribe to an available subscription. '''
#             cmd = "headpin -u admin -p admin system subscribe --name=%s --org=%s --pool=%s" % (systemname, orgname, poolid)
#             (ret, output) = self.runcmd(cmd, "subscribe to a pool")
# 
#             if ret == 0 and "Successfully subscribed System" in output:
#                     logger.info("The available pool is subscribed successfully.")
#             else:
#                     raise FailException("Test Failed - Failed to subscribe to available pool %s." % poolid)
# 
#     def sam_listconsumedsubscrips(self, systemname, orgname, poolname):
#             ''' list consumed subscriptions. '''
#             cmd = "headpin -u admin -p admin system subscriptions --org=%s --name=%s " % (orgname, systemname)
#             (ret, output) = self.runcmd(cmd, "list consumed subscriptions")
# 
#             if ret == 0 and poolname in output:
#                     logger.info("The consumed subscriptions are listed successfully.")
#                     return True
#             else:
#                     logger.info("No consumed subscriptions are listed.")
#                     return False
