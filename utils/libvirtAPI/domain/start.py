#!/usr/bin/env python
"""for testing the start function of domain
   mandatory arguments: guestname
"""

__author__ = "Osier Yang <jyang@redhat.com>"
__date__ = "Tue Oct 27, 2009"
__version__ = "0.1.0"
__credits__ = "Copyright (C) 2009 Red Hat, Inc."
__all__ = ['start', 'check_params', 'parse_opts',
           'usage', 'version', 'append_path']

import os
import sys
import re
import time
import commands

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
from utils.libvirtAPI.lib import domainAPI
from utils.libvirtAPI.Python import utils
from utils.libvirtAPI.exception import LibvirtAPI

NONE = 0
START_PAUSED = 1

def return_close(conn, logger, ret):
    conn.close()
    logger.info("closed hypervisor connection")
    return ret

def check_params(params):
    """Verify the input parameter"""
    if 'logger' not in params:
        print "key 'logger' is required, and it's value should \
               be an instance of logging.Logger"
        return 1

    logger = params['logger']

    keys = ['guestname', 'logger']
    for key in keys:
        if key not in params:
            logger.error("key '%s' is required" % key)
#             usage()

    if params['guestname'] == "":
        logger.error("value of guestname is empty")
#         usage()

def start(params):
    """Start domain

        Argument is a dictionary with two keys:
        {'logger': logger, 'guestname': guestname}

        logger -- an object of utils/Python/log.py
        mandatory arguments : guestname -- same as the domain name
	optional arguments : flags -- domain create flags <none|start_paused>

        Return 0 on SUCCESS or 1 on FAILURE
    """
    # Initiate and check parameters
    is_fail = True
    check_params(params)
    domname = params['guestname']
    logger = params['logger']

    flags = None
    if params.has_key('flags'):
        flags = params['flags']
        if flags != 'none' and flags != 'start_paused':
            logger.error("flags value either \"none\" or \"start_paused\"");
            return 1

    # Connect to local hypervisor connection URI
    util = utils.Utils()
    uri = util.get_uri('127.0.0.1')
    conn = connectAPI.ConnectAPI()
    virconn = conn.open(uri)

    # Start domain
    dom_obj = domainAPI.DomainAPI(virconn)
    timeout = 600
    logger.info('start domain')

    try:
        if flags == "none":
            dom_obj.start_with_flags(domname, NONE)
        elif flags == "start_paused":
            dom_obj.start_with_flags(domname, START_PAUSED)
        elif not flags:
            dom_obj.start(domname)
        else:
            logger.error("flags error")
            return (conn, logger, 1)
    except LibvirtAPI, e:
        logger.error(str(e))
        logger.error("start failed")
        return return_close(conn, logger, 1)

    if flags == "start_paused":
        state = dom_obj.get_state(domname)
        if state == "paused":
            logger.info("guest start with state paused successfully")
            return return_close(conn, logger, 0)
        else:
            logger.error("guest state error")
            return return_close(conn, logger, 1)

    while timeout:
        time.sleep(10)
        timeout -= 10
        logger.info(str(timeout) + "s left")

        state = dom_obj.get_state(domname)
        expect_states = ['running', 'no state', 'blocked']

        if state in expect_states:
            break

    if timeout <= 0:
        logger.error('The domain state is not as expected, state: ' + state)
        return return_close(conn, logger, 1)

    # Get domain ip and ping ip to check domain's status
    mac = util.get_dom_mac_addr(domname)
    logger.info("get ip by mac address")
    ip = util.mac_to_ip(mac, 500)

    for i in range(1, 4):
        if ip != None:
            break
        else:
            cmd = "service network restart"
            logger.info("restart the service network.")
            (ret, out) = commands.getstatusoutput(cmd)
            ip = util.mac_to_ip(mac, 500)

    logger.info('ping guest: ' + str(ip))
    if not util.do_ping(ip, 300):
        logger.error('Failed on ping guest, IP: ' + str(ip))
        return return_close(conn, logger, 1)

    logger.info("PASS")
    return return_close(conn, logger, 0)

def start_clean(params):
    """ clean testing environment """
    pass
