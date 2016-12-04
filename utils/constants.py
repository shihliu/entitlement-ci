"""
Defines various constants
"""
import os

# log module
LOGGER_NAME = "entitlement"
LOGGER_FILE = "entitlement.log"
PROPERTIES_FILE = "RUNTIME_INFO.txt"

GUI_IMG_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "runtime/captures/"))