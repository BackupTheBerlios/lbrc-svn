#!/usr/bin/python

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import dbus
import dbus.glib
import time
import sys
import logging
from LBRC import dinterface
from LBRC.path import path
from LBRC_gtk_gui.applet import Applet
from LBRC.l10n import _

formatter = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
console = logging.StreamHandler()
logging.getLogger().addHandler(console)
console.setLevel(logging.WARN)
console.setFormatter(formatter)

def dbusloghandler(name, levelno, levelname, pathname, filename,
                   module, funcName, lineno, created, asctime,
                   msecs, thread, threadName, process, msg,
                   message, fmessage):
    dbuslogger = logging.getLogger('dbus')
    record = logging.LogRecord('dbus', 
                               levelno,
                               pathname,
                               lineno,
                               message,
                               (),
                               None)
    #if dbuslogger.filter(record):
    dbuslogger.handle(record)

b = dbus.SessionBus()
b.add_signal_receiver(dbusloghandler, signal_name='logemit')

count = 0
ok = 0
while count < 10:
    try:
        lbrc_interface = dinterface(dbus.SessionBus(), 'de.berlios.lbrc', '/profile', 'de.berlios.lbrc')
        lbrc_interface.get_profiles()
        ok = 1
        break
    except dbus.DBusException, e:
        if count == 0:
            # We got an dbus exception => our service is not running, so
            # try to invoke it (if dbus activation would have worked, we
            # the get_profiles call would have blocked till it was started)
            # But we try the invokation only once!
            gobject.spawn_async([path().get_binfile("LBRCdbus.py")], 
                                flags= gobject.SPAWN_STDOUT_TO_DEV_NULL | 
                                       gobject.SPAWN_STDERR_TO_DEV_NULL )

        count += 1
        time.sleep(0.5)
if not ok:
    print _("Could not connect to DBUS component of LBRC")
    # We have to process the pending gtk events, as there the
    # dbus messages are stored.
    while(gtk.events_pending()):
        gtk.main_iteration(False)
    sys.exit(1)
else:
    lbrc = Applet(dbus.SessionBus(), 'de.berlios.lbrc', 'de.berlios.lbrc')
    try:
        gtk.main()
    except KeyboardInterrupt:
        lbrc.quit()
        gtk.mainquit()
