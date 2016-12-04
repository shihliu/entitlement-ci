#!/usr/bin/env python
#
# libvirt-test-API is copyright 2010 Red Hat, Inc.
#
# libvirt-test-API is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
#
# Filename: log.py
# Summary: log file operation
# Description: The module is a tool to provide basic log file operation

import time
import os
import logging

class Log(object):
    """Log file operation"""
    counter = 0

    @staticmethod
    def get_log_name():
        """Get log file name"""
        Log.counter += 1
        logname = ''
        if Log.counter > 0 and Log.counter <= 9:
            base_str = 'libvirt_test00'
            logname = base_str + str(Log.counter)

        if Log.counter > 9 and Log.counter <= 99:
            base_str = 'libvirt_test0'
            logname = base_str + str(Log.counter)

        if Log.counter > 99 and Log.counter <= 999:
            base_str = 'libvirt_test'
            logname = base_str + str(Log.counter)
        return logname

    def __init__(self, logname, loglevel):
        self.name = logname
        self.loglevel = loglevel
        self.filehd = logging.FileHandler(self.name, 'a+')
        self.console = logging.StreamHandler()

class CaseLog(Log):

    def __init__(self, logname, loglevel):
        self.logger = logging.getLogger(logname + "_case")
        self.logger.setLevel(logging.DEBUG)
        super(CaseLog, self).__init__(logname, loglevel)

    def case_log(self):
        """Initialize log file"""
        fmt = {'file_formatter':
               '[%(asctime)s] %(levelname)-4s (%(module)s:%(lineno)d) %(message)s',
               'console_formatter':
               '%(asctime)s %(levelname)-4s %(message)s',
               'autotest_formatter':
               '%(message)s'}

        datefmt = '%H:%M:%S'
        self.filehd.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(fmt['file_formatter'], datefmt)

        self.filehd.setFormatter(file_formatter)
        self.logger.addHandler(self.filehd)

        if int(self.loglevel) != 1:
            self.console.setLevel(logging.INFO)

            if os.environ.has_key('AUTODIR'):
                console_formatter = logging.Formatter(fmt['autotest_formatter'], datefmt)
            else:
                console_formatter = logging.Formatter(fmt['console_formatter'], datefmt)

            self.console.setFormatter(console_formatter)
            self.logger.addHandler(self.console)
        return self.logger

class EnvLog(Log):

    def __init__(self, logname, loglevel):
        self.logger = logging.getLogger(logname + "_env")
        self.logger.setLevel(logging.DEBUG)
        super(EnvLog, self).__init__(logname, loglevel)

    def env_log(self):
        """Initialize log file"""
        fmt = {'file_formatter':'%(message)s',
               'console_formatter':'%(message)s'}

        self.filehd.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(fmt['file_formatter'])

        self.filehd.setFormatter(file_formatter)
        self.logger.addHandler(self.filehd)

        self.console.setLevel(logging.INFO)

        console_formatter = logging.Formatter(fmt['console_formatter'])
        self.console.setFormatter(console_formatter)
        self.logger.addHandler(self.console)
        return self.logger


