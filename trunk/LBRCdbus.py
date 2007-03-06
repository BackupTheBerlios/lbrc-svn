#!/usr/bin/python

from LBRC.dbusinterface import LBRCdbus
import sys
brs = LBRCdbus()
try:
    brs.run()
except KeyboardInterrupt:
    brs.shutdown()
