#!/usr/bin/python
# CACConsole Copyright (C) 2015 foospidy
# https://github.com/foospidy/CACConsole
# See LICENSE for details
# This software includes/uses the python-cloudatcost library which
# is MIT licensed, see https://github.com/adc4392/python-cloudatcost/blob/master/LICENSE

import os
import sys
from twisted.internet import reactor, stdio
from twisted.python import log
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile
from modules.CloudAtCostConsole import CloudAtCostConsole

# prevent creation of compiled bytecode files
sys.dont_write_bytecode = True

# setup log file
log_path      = os.path.dirname(os.path.abspath(__file__)) + '/log/'
log_file_name = 'cacconsole.log'

# create log directory if it doesn't exist
if not os.path.exists(os.path.dirname(log_path)):
	os.makedirs(os.path.dirname(log_path))

log_file                     = DailyLogFile(log_file_name, log_path)
file_log_observer            = FileLogObserver(log_file)
file_log_observer.timeFormat = "%Y-%m-%d %H:%M:%S,%f,"

# start logging
log.startLoggingWithObserver(file_log_observer.emit, False)

# setup local database
dbfile = os.path.dirname(os.path.abspath(__file__)) + '/data/cacconsole.db'

# create data directory if it doesn't exist
if not os.path.exists(os.path.dirname(dbfile)):
	os.makedirs(os.path.dirname(dbfile))

# load console
stdio.StandardIO(CloudAtCostConsole(dbfile))

# start reactor
reactor.run()
