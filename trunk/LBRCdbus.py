#!/usr/bin/python

from LBRC.dbusinterface import LBRCdbus
import sys

brs = LBRCdbus()
brs.run()
sys.exit(0)
