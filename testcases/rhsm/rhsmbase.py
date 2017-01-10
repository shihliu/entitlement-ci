from utils import *
from testcases.base import Base
from utils.exception.failexception import FailException

class RHSMBase(Base):
    # ========================================================
    #       0. Basic Functions
    # ========================================================

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
            cmd = "subscription-manager register --username=%s --password=%s" % (username, password)
        else:
            cmd = "subscription-manager register --type=%s --username=%s --password=%s" % (subtype, username, password)

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

    #list release should be used after register
    def sub_list_releaseinfo(self):
        cmd = "subscription-manager release --list"
        (ret, output) = self.runcmd(cmd)
        if ret == 0 and output:
            logger.info("It's successful to list release list.")
            return output
        else:
            raise FailException("It's failed to list release list.")

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
        if rctcommand:
            cmd = "for i in /etc/pki/product-default/*; do rct cat-cert $i; done"
        else:
            cmd = "for i in /etc/pki/product-default/*; do openssl x509 -text -noout -in $i; done"
        (ret, output) = self.runcmd(cmd, "checking product cert")
        if ret == 0:
            if ("1.3.6.1.4.1.2312.9.1.%s" % productid in output) or ("ID: %s" % productid in output and "Path: /etc/pki/product-default/%s.pem" % productid in output):
                logger.info("The product cert is verified.")
            else:
                raise FailException("Test Failed - The product cert is not correct.")
        else:
            raise FailException("Test Failed - Failed to check product cert.")

    def check_rct(self):
        cmd = "rct cat-cert --help"
        (ret, output) = self.runcmd(cmd, "run rct cat-cert --help")
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
        expect_more_subscriptions = "subscriptions removed at the server."
        expect_more_certs = "local certificates have been deleted."
        if ret == 0:
            if output.strip() == "" or ((expectout5101 in output and expectout5102 in output) or expectout in output or expectoutnew in output or (expect_more_subscriptions in output and expect_more_certs in output)):
                logger.info("It's successful to unsubscribe.")
            else:
                raise FailException("Test Failed - The information shown after unsubscribed is not correct.")
        else:
            raise FailException("Test Failed - Failed to unsubscribe.")

    def sub_list_availablepool_list(self):
        cmd = "subscription-manager list --available | grep 'Pool ID:'"
        (ret, output) = self.runcmd(cmd)
        if ret == 0:
            if "no available subscription pools to list" not in output.lower():
                poollist=output.strip().split("\n")
                for i in range(len(poollist)):
                    poollist[i]=poollist[i].strip("Pool ID:             ")
                return poollist

    # Check if specified pool is available
    def sub_listavailpools(self, productid):
        cmd = "subscription-manager list --available"
        (ret, output) = self.runcmd(cmd)
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

    def get_entitlementcerts_list(self):
        rctcommand = self.check_rct()
        if rctcommand == True:
            cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
            (ret, output) = self.runcmd(cmd, "get entitlement certs list")
            if ret == 0:
                return output.strip()
            else:
                raise FailException("Test Failed - Failed to list entitlement certs list.")

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

    def sub_isconsumed(self, autosubprod):
        cmd = "subscription-manager list --consumed"
        (ret, output) = self.runcmd(cmd, "listing consumed subscriptions")
        if ret == 0 and autosubprod in output.strip() or 'Pool ID' in output:
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

    # Check if specified pool is available
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

    # can set date also restore date on server
    def sam_remote_set_time(self, samhostip, date_cmd):
        # create organization with orgname
        cmd = "%s" % (date_cmd)
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0:
            logger.info("It's successful to set server date.")
        else:
            raise FailException("Test Failed - Failed to set server date")

    def sam_remote_create_org(self, samhostip, orgname):
        # create organization with orgname
        cmd = "headpin -u admin -p admin org create --name=%s" % (orgname)
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0 and "Successfully created org" in output:
            logger.info("It's successful to create organization %s." % orgname)
        else:
            raise FailException("Test Failed - Failed to create organization %s." % orgname)

    def sam_remote_delete_org(self, samhostip, orgname):
        # delete an existing organization
        if self.sam_remote_is_org_exist(samhostip, orgname):
            cmd = "headpin -u admin -p admin org delete --name=%s" % (orgname)
            (ret, output) = self.runcmd_sam(cmd, '', samhostip)
            if ret == 0 and "Successfully deleted org" in output:
                logger.info("It's successful to delete organization %s." % orgname)
            else:
                raise FailException("Test Failed - Failed to delete organization %s." % orgname)
        else:
            logger.info("Org %s to be deleted does not exist." % (orgname))

    def sam_remote_is_org_exist(self, samhostip, orgname):
        # check an organization existing or not
        cmd = "headpin -u admin -p admin org list"
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0 and orgname in output:
            logger.info("Organization %s exists." % orgname)
            return True
        else:
            logger.info("Organization %s does not exist." % orgname)
            return False

# All test focus on activationkey "qq",fetching pool id dynamicly in sam1.4 and subscription-id is 7 in satellite6.2
    def sam_remote_fetch_pool(self, samhostip,orgname):
        poolid = ''
        if self.test_server == "SAM":
            cmd = 'headpin -u admin -p admin org subscriptions --name=%s | grep -A8 "Subscription    : CloudForms (10-pack)" | grep "ID"'%orgname
            (ret, output) = self.runcmd_sam(cmd, '', samhostip)
            if ret == 0:
                poolid = output.strip().split(":")[1].strip()
                logger.info("It's successful to fetch pool id from SAM server.")
            else:
                logger.info(" to fetch pool id from SAM server.")
        elif self.test_server == 'SATELLITE':
            cmd = "hammer -u admin -p admin subscription list --organization-label=%s | grep 'CloudForms (10-pack)'"%orgname
            (ret, output) = self.runcmd_sam(cmd, '', samhostip)
            if ret == 0:
                poolid = output.strip().split('|')[1].strip()
                logger.info("It's successful to fetch pool id from satellite server.")
            else:
                logger.info(" to fetch pool id.")
        return poolid


    def sam_remote_activationkey_exist(self, samhostip, orgname):
        if self.test_server == "SAM":
            cmd = "headpin -u admin -p admin activation_key list --org=%s"%orgname
        elif self.test_server == 'SATELLITE':
            cmd = "hammer -u admin -p admin activation-key list --organization-label=%s"%orgname
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if 'qq' in output.split():
            logger.info("activationkey qq exists. please check it's pool.")
            return True
        else:
            logger.info("activationkey qq does not exist. please create it.")
            return False

    def sam_remote_activationkey_check_pool(self, samhostip, orgname, poolid):
        if self.test_server == "SAM":
            cmd = "headpin -u admin -p admin activation_key info --org=%s --name=qq"%orgname
        elif self.test_server == 'SATELLITE':
            cmd = "hammer -u admin -p admin activation-key info --id=1"
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if '%s'%poolid in output.split() or 'Auto Attach:           true' in output:
            logger.info("activationkey qq is attached with pool id or attached by subscription-id 7")
            return True
        else:
            logger.info("activationkey qq is not attached. please attach it.")
            return False

    def sam_remote_activationkey_attach_pool(self, samhostip, orgname, poolid):
        #activation key on satellite6.2, does not need to attach pool manually
        if self.test_server == "SAM":
            cmd = "headpin -u admin -p admin activation_key update --org=%s --name=qq --add_subscription=%s"%(orgname, poolid)
            (ret, output) = self.runcmd_sam(cmd, '', samhostip)
            if ret == 0:
                logger.info("It's successful to attach pool to activationkey qq")
            else:
                raise FailException("Test Failed - Failed to attach pool to activationkey.")
        elif self.test_server == "SATELLITE":
            pass

    def sam_remote_activationkey_creation(self, samhostip, orgname):
        if self.test_server == "SAM":
            cmd = "headpin -u admin -p admin activation_key create --org=%s --name=qq"%orgname
        elif self.test_server == 'SATELLITE':
            cmd = "hammer -u admin -p admin activation-key create --name=qq --organization-id=1 --content-view='Default Organization View' --lifecycle-environment=Library"
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0 and ("Successfully created activation key" in output or "Activation key created" in output):
            logger.info("It's successful to create activationkey qq. please attach a pool for it.")
        else:
            raise FailException("Test Failed - Failed to create activationkey.")

    def set_system_time(self, system_time):
        cmd = 'date -s %s'%system_time
        (ret, output) = self.runcmd(cmd, "set system time expired")
        if ret ==0:
            logger.info("It's successful to set system time expired")
        else:
            raise FailException("Test Failed - failed to set system time expired")

    def restore_system_time(self):
        cmd = 'hwclock --hctosys'
        (ret, output) = self.runcmd(cmd, "restore system time")
        if ret ==0:
            logger.info("It's successful to restore system time")
        else:
            raise FailException("Test Failed - failed to restore system time")


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
        if ret == 0 and output != None:
            logger.info("It's successful to restart rhsmcertd service")
        else:
            raise FailException("Test Failed - Failed to restart rhsmcertd service.")

    def stop_rhsmcertd(self):
        cmd = "service rhsmcertd stop"
        (ret, output) = self.runcmd(cmd, "stop rhsmcertd service")
        if ret == 0 and "Redirecting to /bin/systemctl stop  rhsmcertd.service" in output or 'Stopping rhsmcertd...[  OK  ]' in output:
            logger.info("It's successful to stop rhsmcertd service")
        else:
            raise FailException("Test Failed - Failed to restart rhsmcertd service.")

    # Return auto-attach interval
    def check_auto_attach_interval(self, log_file='/var/log/rhsm/rhsmcertd.log'):
        cmd = "grep 'Auto-attach interval' %s | tail -1"%log_file
        (ret, output) = self.runcmd(cmd, "get auto attach interval value")
        if ret == 0 and output != None:
            logger.info("It's successful to check interval")
            return output.split('interval: ')[1].split(' ')[0]
        else:
            raise FailException("Test Failed - Failed to check interval")

    def set_auto_attach_interval(self, interval):
        cmd = "sed -i '/autoAttachInterval/d' /etc/rhsm/rhsm.conf;sed -i '66a autoAttachInterval = %s' /etc/rhsm/rhsm.conf" %(interval)
        (ret, output) = self.runcmd(cmd,'set interval')
        if ret == 0:
            logger.info("It's successful to set interval")
        else:
            raise FailException("Test Failed - Failed to set interval")

    # Return insecure value of rhsm.conf: 0 or 1
    def check_insecure_value(self):
        cmd = "grep insecure /etc/rhsm/rhsm.conf"
        (ret, output) = self.runcmd(cmd,'get insecure value')
        if ret == 0:
            logger.info("It's successful to get insecure value")
            return output.split('=')[1].strip()
        else:
            raise FailException("Test Failed - Failed to check interval")

    def set_insecure_value(self, insecurevalue):
        cmd="sed -i '/insecure/d' /etc/rhsm/rhsm.conf;sed -i '/# Set to 1 to disable certificate validation:/a\insecure = %s' /etc/rhsm/rhsm.conf"%insecurevalue
        (ret, output) = self.runcmd(cmd,'set insecure value')
        if ret == 0 and self.check_insecure_value() == insecurevalue:
            logger.info("It's successful to set insecure value")
        else:
            raise FailException("Test Failed - Failed to set insecure value")

    def check_and_backup_yum_repos(self):
        # check if /root/backuprepo/ exists
        cmd = "ls /root/backuprepo/"
        (ret, output) = self.runcmd(cmd, "make dir /root/backuprepo")
        if ret ==0:
            logger.info("It's successful to check /root/backuprepo exists.")
        else:
            cmd = 'mkdir /root/backuprepo'
            (ret, output) = self.runcmd(cmd, "make dir /root/backuprepo")
            if ret ==0:
                logger.info("It's successful to make dir /root/backuprepo.")
            else:
                raise FailException("Test Failed - Failed to make dir /root/backuprepo.")
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
            cmd = "rm -rf /root/backuprepo/*;mv /etc/yum.repos.d/* /root/backuprepo/"
            (ret, output) = self.runcmd(cmd, "backup repo")
            if ret == 0:
                logger.info("It's successful to backup repo.")
            else:
                raise FailException("Test Failed - Failed to backuprepo.")
        else:
            logger.info("No need to back up repos")

    def restore_repos(self):
        cmd = "ls /root/backuprepo/*"
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

    def clear_file_content(self, logfile):
        cmd = 'echo "" > %s'%logfile
        (ret, output) = self.runcmd(cmd, "clear file content")
        if ret == 0:
            logger.info("It's successful to clear content of %s"%logfile)
        else:
            raise FailException("Test Failed - Failed to clear content.")

    def install_pkg(self, pkgname):
        cmd = "yum install -y %s"%pkgname
        (ret, output) = self.runcmd(cmd, "install package")
        if ret ==0:
            logger.info("It's successful to install package %s"%pkgname)
        else:
            raise FailException("Test Failed - Failed to install package %s"%pkgname)

    def remove_pkg(self, pkgname):
        cmd ="yum remove -y %s"%pkgname
        (ret, output) = self.runcmd(cmd, "remove package")
        if ret ==0:
            logger.info("It's successful to remove package %s"%pkgname)
        else:
            raise FailException("Test Failed - Failed to remove package %s"%pkgname)

    def refresh_client_server(self):
        cmd = 'subscription-manager refresh'
        (ret, output) = self.runcmd(cmd, "refresh")
        if ret ==0 and 'All local data refreshed' in output:
            logger.info("It's successful to refresh")
        else:
            raise FailException("Test Failed - Failed to refresh")

    def disable_all_repos(self):
        cmd = 'subscription-manager repos --disable=*'
        no_repo_msg = "Error: '*' does not match a valid repository ID. Use \"subscription-manager repos --list\" to see valid repositories."
        (ret, output) = self.runcmd(cmd, "disable all repos")
        if ret ==0 and 'is disabled for this system' in output:
            logger.info("It's successful to disable all repos")
        elif ret != 0 and no_repo_msg in output:
            logger.info("No repos available, disabling all repos is not needed")
        else:
            raise FailException("Test Failed - Failed to disable all repos")

    def enable_repo(self, reponame):
        cmd = 'subscription-manager repos --enable=%s'%reponame
        (ret, output) = self.runcmd(cmd, "enable a repo")
        if ret ==0 and 'is enabled for this system' in output:
            logger.info("It's successful to enable a repo")
        else:
            raise FailException("Test Failed - Failed to enable a repo")

    def add_line_after_a_line(self, datumline, targetline, targetfile):
        cmd = "sed -i '/%s/a\%s' %s"%(datumline, targetline, targetfile)
        (ret, output) = self.runcmd(cmd, "add a line")
        if ret ==0:
            logger.info("It's successful to add a line")
        else:
            raise FailException("Test Failed - Failed to add a line")

    def remove_all_subscriptions(self):
        cmd = 'subscription-manager remove --all'
        (ret, output) = self.runcmd(cmd, "remove all subscriptions")
        if ret ==0:
            logger.info("It's successful to remove all subscriptions")
        else:
            raise FailException("Test Failed - Failed to remove all subscriptions")

    def remove_all_override(self):
        cmd = 'subscription-manager repo-override --remove-all'
        (ret, output) = self.runcmd(cmd, "remove all repo override")
        if ret ==0:
            logger.info("It's successful to remove all repo override")
        else:
            raise FailException("Test Failed - Failed to remove all repo override")

    def list_all_repo_override(self):
        repo_overrides=''
        cmd = 'subscription-manager repo-override --list | grep Repository:'
        (ret, output) = self.runcmd(cmd, "list all repo override")
        if ret !=0:
            logger.info("No repo override")
        elif ret == 0:
            repo_overrides = output.strip()
            logger.info("It's successful to list all repo override")
        return repo_overrides

    def sync_times(self, samhostip):
        cmd = "service ntpd stop;ntpdate clock.util.phx2.redhat.com"
        # server time
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0:
            logger.info("It's sync server time.")
        else:
            raise FailException("Test Failed - Failed to sync server time.")
        # client time
        (ret, output) = self.runcmd(cmd, "client time")
        if ret ==0:
            logger.info("It's successful to sync client time.")
        else:
            raise FailException("Test Failed - Failed to sync client time.")

    def get_manifest(self):
        cmd = "cd /root;wget http://10.66.144.9/projects/sam-virtwho/bak-migrated/latest-manifest/sam_install_manifest.zip"
        (ret, output) = self.runcmd(cmd, "download manifest to client")
        if ret ==0:
            logger.info("It's successful to download manifest.")
        else:
            raise FailException("Test Failed - Failed to download manifest.")

    def remove_manifest(self):
        cmd = "cd /root;rm -f sam_install_manifest.zip"
        (ret, output) = self.runcmd(cmd, "download manifest to client")
        if ret ==0:
            logger.info("It's successful to remove manifest.")
        else:
            raise FailException("Test Failed - Failed to remove manifest.")

    def check_installed_status(self):
        cmd = "subscription-manager list --installed | grep Status:"
        (ret, output) = self.runcmd(cmd, "check status")
        return output.strip().split(":")[1].strip()
        if ret == 0:
            logger.info("It's successful to check partial subscription status")
        else:
            raise FailException("Test Failed - Failed to check partial subscription status")

    def auto_heal_set_interval(self, intervals):
        cmd = "subscription-manager config --rhsmcertd.autoattachinterval=%s"%intervals
        (ret, output) = self.runcmd(cmd, "set auto heal interval")
        if ret == 0:
            logger.info("It's successful to set auto heal interval")
        else:
            raise FailException("Test Failed - Failed to set auto heal interval")

    def set_facts(self, facts_value):
        cmd = facts_value
        (ret, output) = self.runcmd(cmd, "set facts value")
        if ret == 0:
            logger.info("It's successful to set facts value")
        else:
            raise FailException("Test Failed - Failed to set facts value")

    def remove_facts_value(self):
        cmd = "rm -rf /etc/rhsm/facts/custom.facts;subscription-manager facts --update"
        (ret, output) = self.runcmd(cmd, "set facts value")
        if ret == 0:
            logger.info("It's successful to remove facts value")
        else:
            raise FailException("Test Failed - Failed to remove facts value")

    def disable_autoheal(self):
        cmd = "subscription-manager auto-attach --disable"
        (ret, output) = self.runcmd(cmd, "disable autoheal")
        if ret == 0 and 'Auto-attach preference: disabled' in output:
            logger.info("It's successful to disable autoheal")
        else:
            raise FailException("Test Failed - Failed to disable autoheal")

    def enable_autoheal(self):
        cmd = "subscription-manager auto-attach --enable"
        (ret, output) = self.runcmd(cmd, "enable autoheal")
        if ret == 0 and 'Auto-attach preference: enabled' in output:
            logger.info("It's successful to enable autoheal")
        else:
            raise FailException("Test Failed - Failed to enable autoheal")

    def add_new_product_cert(self):
        cmd = 'cd /etc/pki/product/;wget http://10.66.144.9/projects/sub-man/product_cert/1.pem'
        (ret, output) = self.runcmd(cmd, "add new product cert")
        if ret == 0:
            logger.info("It's successful to add new product cert")
        else:
            raise FailException("Test Failed - Failed to add new product cert")

    def rm_new_product_cert(self):
        cmd = 'cd /etc/pki/product/;rm -rf *'
        (ret, output) = self.runcmd(cmd, "remove new product cert")
        if ret == 0:
            logger.info("It's successful to remove new product cert")
        else:
            raise FailException("Test Failed - Failed to remove new product cert")

    def get_hostname_from_config(self):
        hn_sv = None
        cmd = "subscription-manager config | grep '\[server\]' -A1|grep hostname"
        (ret, output) = self.runcmd(cmd, "get server hostname")
        hn_sv = output.strip().split('=')[1].strip()
        return hn_sv
        if ret == 0:
            logger.info("It's successful to get server hostname")
        else:
            raise FailException("Test Failed - Failed to get server hostname")

    def set_server_hostname(self, hostname):
        cmd = "subscription-manager config --server.hostname=%s"%hostname
        (ret, output) = self.runcmd(cmd, "set server hostname")
        if ret == 0:
            logger.info("It's successful to set server hostname")
        else:
            raise FailException("Test Failed - Failed to set server hostname")

    def off_server_connection(self):
        active_hn = self.get_hostname_from_config()
        inactive_hn = active_hn + '1'
        cmd = "subscription-manager config --server.hostname=%s"%inactive_hn
        (ret, output) = self.runcmd(cmd, "cut off connection between server and client")
        if ret == 0:
            return active_hn
            logger.info("It's successful to off server connection")
        else:
            raise FailException("Test Failed - Failed to off server connection")
