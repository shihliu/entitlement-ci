#!/usr/bin/env python
"""this script is for migration testing
   domain:migrate
       transport
           tcp|tls|ssh
       target_machine
           10.66.5.5
       username
           root
       password
           redhat
       guestname
           rhel6
       prestate
           running
       poststate
           running
       presrcconfig
           false
       postsrcconfig
           false
       predstconfig
           false
       postdstconfig
           false
       flags
           0|live

prestate and poststate is the domain state: <running|paused>
presrconfig, postsrconfig, predstconfig, postdstconfig is <true|false>
flags is the migration flags combination <0|peer2peer|tunnelled|live|paused \
                                         |persist_dest|undefine_source|>

"""
__author__ = 'Guannan Ren: gren@redhat.com'
__date__ = 'Sun June 26, 2011'
__version__ = '0.1.0'
__credits__ = 'Copyright (C) 2011 Red Hat, Inc.'
__all__ = ['usage', 'migrate']

import os
import re
import sys
import pexpect
import string
import commands
import time

def append_path(path):
    """Append root path of package"""
    if path in sys.path:
        pass
    else:
        sys.path.append(path)

pwd = os.getcwd()
result = re.search('(.*)libvirt-test-API', pwd)
append_path(result.group(0))

from utils.libvirtAPI.lib import connectAPI
from utils.libvirtAPI.lib.domainAPI import *
from utils.libvirtAPI.Python import utils
from utils.libvirtAPI.Python import xmlbuilder
from utils.libvirtAPI.exception import LibvirtAPI

SSH_KEYGEN = "ssh-keygen -t rsa"
SSH_COPY_ID = "ssh-copy-id"

def exec_command(logger, command, flag):
    """execute shell command
    """
    status, ret = commands.getstatusoutput(command)
    if not flag and status:
        logger.error("executing " + "\"" + command + "\"" + " failed")
        logger.error(ret)
    else:
    	logger.info("executing " + "\"" + command + "\"" + " succeeded")
    	logger.info(ret)
    return status, ret

def env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger):

    src.close()
    logger.info("close local hypervisor connection")
    dst.close()
    logger.info("close remote hypervisor connection")

def env_clean_vm_and_key(params):

    logger = params['logger']
    target_machine = params['target_machine']
    username = params['username']
    password = params['password']
    guestname = params['guestname']

    params.pop('target_machine')
    params.pop('username')
    params.pop('password')
     
    logger.info("destroy and undefine %s in target machine.", guestname)
    REMOTE_DESTROY = "ssh %s \"virsh destroy %s\"" % (target_machine, guestname)
    exec_command(logger, REMOTE_DESTROY, 0)
    # time.sleep(5)
    # REMOTE_UNDEFINE = "ssh %s \"virsh undefine %s\"" % (target_machine, guestname)
    # exec_command(logger, REMOTE_UNDEFINE, 0)

    REMOVE_SSH = "ssh %s \"rm -rf /root/.ssh/*\"" % (target_machine)
    logger.info("remove ssh key on remote machine")
    status, ret = exec_command(logger, REMOVE_SSH, 0)
    if status:
        logger.error("failed to remove ssh key")

    REMOVE_LOCAL_SSH = "rm -rf /root/.ssh/*"
    logger.info("remove local ssh key")
    status, ret = exec_command(logger, REMOVE_LOCAL_SSH, 0)
    if status:
        logger.error("failed to remove local ssh key")

"""
back up the original function: env_clean

def env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger):

    logger.info("destroy and undefine %s on both side if it exsits", guestname)
    exec_command(logger, "virsh destroy %s" % guestname, 1)
    exec_command(logger, "virsh undefine %s" % guestname, 1)
    REMOTE_DESTROY = "ssh %s \"virsh destroy %s\"" % (target_machine, guestname)
    exec_command(logger, REMOTE_DESTROY, 1)
    REMOTE_UNDEFINE = "ssh %s \"virsh undefine %s\"" % (target_machine, guestname)
    exec_command(logger, REMOTE_UNDEFINE, 1)

    src.close()
    logger.info("close local hypervisor connection")
    dst.close()
    logger.info("close remote hypervisor connection")

    REMOVE_SSH = "ssh %s \"rm -rf /root/.ssh/*\"" % (target_machine)
    logger.info("remove ssh key on remote machine")
    status, ret = exec_command(logger, REMOVE_SSH, 0)
    if status:
        logger.error("failed to remove ssh key")

    REMOVE_LOCAL_SSH = "rm -rf /root/.ssh/*"
    logger.info("remove local ssh key")
    status, ret = exec_command(logger, REMOVE_LOCAL_SSH, 0)
    if status:
        logger.error("failed to remove local ssh key")
"""

def check_params(params):
    """check out the arguments requried for migration"""
    logger = params['logger']
    keys = ['transport', 'target_machine', 'username', 'password', 'guestname', 'flags']
    for key in keys:
        if key not in params:
            logger.error("Argument %s is required" % key)
            return 1
    return 0

def ssh_keygen(logger):
    """using pexpect to generate RSA"""
    logger.info("generate ssh RSA \"%s\"" % SSH_KEYGEN)
    child = pexpect.spawn(SSH_KEYGEN)
    while True:
        index = child.expect(['Enter file in which to save the key ',
                              'Overwrite',
                              'Enter passphrase ',
                              'Enter same passphrase again: ',
                               pexpect.EOF,
                               pexpect.TIMEOUT])
        if index == 0:
            logger.info("Enter file in which to save the key")
            child.sendline("\r")
        elif index == 1:
            logger.info("Overwrite")
            child.sendline("yes")
        elif index == 2:
            logger.info("Enter passphrase ")           
            child.sendline("\r")
        elif index == 3:
            logger.info("Enter same passphrase again: ")     
            child.sendline("\r")
        elif index == 4:
            logger.info(string.strip(child.before))
            child.close()
            logger.info("ssh_keygen completed.")
            
            time.sleep(10)
            logger.info("list local ssh key files:")
            cmd = "ls -l /root/.ssh/"
            (ret, out) = commands.getstatusoutput(cmd)
            logger.info(out)
            for i in range(1, 5):
                if "id_rsa.pub" in out:
                    return 0
                    break
                else:
                    logger.info("id_rsa.pub does not appear, wait 10 seconds.")
                    time.sleep(10)
                    (ret, out) = commands.getstatusoutput(cmd)
                    logger.info(out)
            
            return child.exitstatus
        elif index == 5:
            logger.error("ssh_keygen timeout")
            logger.debug(string.strip(child.before))
            child.close()
            return 1
    return 0

def ssh_tunnel(hostname, username, password, logger):
    """setup a tunnel to a give host"""

    logger.info("setup ssh tunnel with host %s" % hostname)
    user_host = "%s@%s" % (username, hostname)
    child = pexpect.spawn(SSH_COPY_ID, ['-i', '/root/.ssh/id_rsa.pub', user_host])
    while True:
        index = child.expect(['yes\/no', 'password: ',
                               pexpect.EOF,
                               pexpect.TIMEOUT])
        if index == 0:
            logger.info("send 'yes'.")
            child.sendline("yes")
        elif index == 1:
            logger.info("send password '%s'." % password)
            child.sendline(password)
        elif index == 2:
            logger.info(string.strip(child.before))
            child.close()
            logger.info("setup tunnel completed.")
            return child.exitstatus
        elif index == 3:
            logger.error("setup tunnel timeout")
            logger.debug(string.strip(child.before))
            child.close()
            return 1

    return 0

def migrate(params):
    """ migrate a guest back and forth between two machines"""
    logger = params['logger']
    params_check_result = check_params(params)
    if params_check_result:
        return 1

    transport = params['transport']
    target_machine = params['target_machine']
    username = params['username']
    password = params['password']
    guestname = params['guestname']
    # poststate = params['poststate']
    # presrcconfig = params['presrcconfig']
    # postsrcconfig = params['postsrcconfig']
    # predstconfig = params['predstconfig']
    # postdstconfig = params['postdstconfig']
    flags = params['flags']


    logger.info("the flags is %s" % flags)
    flags_string = flags.split("|")

    migflags = 0
    for flag in flags_string:
        if flag == '0':
            migflags |= 0
        elif flag == 'peer2peer':
            migflags |= VIR_MIGRATE_PEER2PEER
        elif flag == 'tunnelled':
            migflags |= VIR_MIGRATE_TUNNELLED
        elif flag == 'live':
            migflags |= VIR_MIGRATE_LIVE
        elif flag == 'persist_dest':
            migflags |= VIR_MIGRATE_PERSIST_DEST
        elif flag == 'undefine_source':
            migflags |= VIR_MIGRATE_UNDEFINE_SOURCE
        elif flag == 'paused':
            migflags |= VIR_MIGRATE_PAUSED
        else:
            logger.error("unknown flag")
            return 1

    # generate ssh key pair
    ret = ssh_keygen(logger)
    if ret:
        logger.error("failed to generate RSA key")
        return 1
    else: logger.info("succeeded to generate RSA key")
    
    # setup ssh tunnel with target machine
    ret = ssh_tunnel(target_machine, username, password, logger)
    if ret:
        logger.error("failed to setup ssh tunnel with target machine %s" % target_machine)
        return 1
    else: logger.info("succeeded to setup ssh tunnel with target machine %s" % target_machine)
    
    # Connect to local hypervisor connection URI
    util = utils.Utils()

    # srcuri = "qemu:///system"
    # dsturi = "qemu+%s://%s/system" % (transport, target_machine)
    srcuri = util.get_uri("127.0.0.1")
    dsturi = util.get_uri(target_machine)

    conn = connectAPI.ConnectAPI()
    src = conn.open(srcuri)
    dst = conn.open(dsturi)

    srcdom = DomainAPI(src)
    dstdom = DomainAPI(dst)
    
    '''
    if predstconfig == "true":
        guest_names = dstdom.get_defined_list()
        if guestname in guest_names:
            logger.info("Dst VM exists")
        else:
            logger.error("Dst VM missing config, should define VM on Dst first")
            env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
            return 1
    '''
    
    try:
        if(migflags & VIR_MIGRATE_PEER2PEER):
            logger.info("use migrate_to_uri() API to migrate")
            srcdom.migrate_to_uri(guestname, dsturi, migflags)
        else:
            logger.info("use migrate() to migrate")
            srcdom.migrate(guestname, dst, migflags)
    except LibvirtAPI, e:
        logger.error("API error message: %s, error code is %s" % \
                     (e.response()['message'], e.response()['code']))
        logger.error("Migration Failed")
        env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
        return 1
        
    '''
    if postsrcconfig == "true":
        if srcdom.is_active(guestname):
            logger.error("Source VM is still active")
            env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
            return 1
        if not srcdom.is_persistent(guestname):
            logger.error("Source VM missing config")
            env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
            return 1
    else:
        guest_names = srcdom.get_list()
        guest_names += srcdom.get_defined_list()
        if guestname in guest_names:
            logger.error("Source VM still exists")
            env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
            return 1
    '''
    
    if not dstdom.is_active(guestname):
        logger.error("Dst VM is not active")
        env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
        return 1

    '''
    if postdstconfig == "true":
        if not dstdom.is_persistent(guestname):
            logger.error("Dst VM missing config")
            env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
            return 1
    
    dstdom_state = dstdom.get_state(guestname)
    if dstdom_state != poststate:
        logger.error("Dst VM wrong state %s, should be %s", dstdom_state, poststate)
        env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
        return 1
    '''

    logger.info("Migration PASS")
    env_clean(src, dst, srcdom, dstdom, target_machine, guestname, logger)
    return 0





















