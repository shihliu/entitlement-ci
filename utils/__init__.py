import re, os, sys, shutil, logging, time, unittest
import json, requests, paramiko
from utils.constants import *

def get_log_file():
    """
    Returns correct path to log file
    """
    return os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir)), LOGGER_FILE)

def get_properties_file():
    """
    Returns correct path to properties-file
    """
    return os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)), PROPERTIES_FILE)

# create a logger
logger = logging.getLogger("%s" % LOGGER_NAME)
logger.setLevel(logging.DEBUG)

# create file handler
fh = logging.FileHandler("%s" % get_log_file())
fh.setLevel(logging.DEBUG)

# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# turn off paramiko log off
paramiko_logger = logging.getLogger("paramiko.transport")
paramiko_logger.disabled = True

def get_exported_param(param_name):
    return os.getenv(param_name)
