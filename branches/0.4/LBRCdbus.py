#!/usr/bin/python

from LBRC.dbusinterface import LBRCdbus
import sys
import logging
if "--debug" in sys.argv:
    logging.basicConfig(level=logging.DEBUG)
brs = LBRCdbus()
try:
    brs.run()
except KeyboardInterrupt:
    brs.shutdown()