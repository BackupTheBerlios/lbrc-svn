#!/usr/bin/python

from LBRC.dbusinterface import Core
import sys
import logging
import gobject
logging.getLogger().setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)
if "--debug" in sys.argv:
    console.setLevel(logging.DEBUG)
    brs = Core(debug=logging.DEBUG)
else:
    brs = Core()
try:
    mainloop = gobject.MainLoop()
    mainloop.run()
except KeyboardInterrupt:
    brs.shutdown()
    mainloop.quit()