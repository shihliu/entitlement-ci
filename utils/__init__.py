import re
import os
import sys
import logging
import unittest
from utils.constants import *

def get_log_file():
    """
    Returns correct path to log file
    """
    return os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir)), LOGGER_FILE)

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

def get_runtime_log_file(file_name):
    """
    Returns correct path to log file
    """
    path_name = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "runtime/result/default/"))
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    runtime_file = os.path.join(path_name, file_name)
    if os.path.exists(runtime_file):
        os.remove(runtime_file)
    return os.path.join(path_name, file_name)

# create runtime file handler
runtime_fh = logging.FileHandler("%s" % get_runtime_log_file("runtime.log"))
runtime_fh.setLevel(logging.DEBUG)
runtime_fh.setFormatter(formatter)
logger.addHandler(runtime_fh)
