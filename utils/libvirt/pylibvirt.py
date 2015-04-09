'''
Manage vms by python libvirt API
depends: libvirt module
'''

import os, sys, re, shutil, traceback
from utils import logger

try:
    import libvirt
except ImportError:
    logger.error("Please install libvirt ...")
    sys.exit(-1)

def __get_conn():
    '''
    '''
    try:
        conn = libvirt.open('qemu:///system')
    except Exception, e:
        logger.error("Failed to connect qemu: " + str(e))
        logger.error(traceback.format_exc())
    return conn
