#!/usr/bin/python
# CACConsole Copyright (C) 2015 foospidy
# https://github.com/foospidy/CACConsole
# See LICENSE for details
# This software includes/uses the python-cloudatcost library which
# is MIT licensed, see https://github.com/adc4392/python-cloudatcost/blob/master/LICENSE

from twisted.internet import reactor, stdio
from modules.CloudAtCostConsole import CloudAtCostConsole
import os
import sys

# prevent creation of compiled bytecode files
sys.dont_write_bytecode = True

# setup local database
dbfile = os.path.dirname(os.path.abspath(__file__)) + '/data/cacconsole.db'
if not os.path.exists(os.path.dirname(dbfile)):
	os.makedirs(os.path.dirname(dbfile))

# load console
stdio.StandardIO(CloudAtCostConsole(dbfile))

# start reactor
reactor.run()
