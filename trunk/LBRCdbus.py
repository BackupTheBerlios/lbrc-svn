#!/usr/bin/python

from LBRC.dbusinterface import LBRCdbus
import sys
import logging
#logging.basicConfig(level=logging.DEBUG)
brs = LBRCdbus()
try:
    brs.run()
except KeyboardInterrupt:
    brs.shutdown()