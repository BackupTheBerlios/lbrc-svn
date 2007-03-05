#!/usr/bin/python

import pygtk
pygtk.require("2.0")
import gtk
import gtk.gdk
import egg.trayicon
import dbus
import dbus.glib

from LBRC import get_datafiles, get_binfile
from LBRC.l10n import _

class applet(object):
    def __init__(self, lbrc, **kwds):
        self.lbrc = lbrc
        self.config = {}
        self.config['icon_size'] = 24
        self.icon = gtk.gdk.pixbuf_new_from_file(get_datafiles('LBRC.svg')[-1])
        self.trayicon = egg.trayicon.TrayIcon("LBRC")
        image = gtk.Image()
        image.set_from_pixbuf(self.icon.scale_simple(self.config['icon_size'],self.config['icon_size'], gtk.gdk.INTERP_BILINEAR))
        self.__create_menu()
        eventbox = gtk.EventBox()
        self.trayicon.add(eventbox)
        eventbox.add(image)
        eventbox.add_events(gtk.gdk.BUTTON_PRESS)
        eventbox.connect('button-press-event', self.popup_menu)
        self.lbrc.connect_to_signal("shutdown", lambda: gtk.main_quit())
        self.lbrc.connect_to_signal("connect_cb", self.connect_cb)
        self.lbrc.connect_to_signal("disconnect_cb", self.disconnect_cb)
        self.lbrc.connect_to_signal("profile_change", self.profile_change_cb)
        self.pid_menu_map[self.lbrc.get_profile()[0]].set_active(1)
        self.trayicon.show_all()
        try:
            proxy_obj = dbus.SessionBus().get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
            self.notify_interface = dbus.Interface(proxy_obj, 'org.freedesktop.Notifications')
            self.notify_interface.GetServerInformation()
        except:
            self.notify_interface = None

    def profile_change_cb(self, id, name):
        self.notify(_("Profile changed:\n%(profilename)s") % {"profilename": name})
        self.pid_menu_map[id].set_active(1)

    def connect_cb(self, btname, btaddress, port):
        self.notify(_("Connect from:\n%(btname)s (%(btaddress)s)") % {"btname": btname, "btaddress": btaddress})

    def disconnect_cb(self, btname, btaddress, port):
        self.notify(_("Disconnect from:\n%(btname)s (%(btaddress)s)") % {"btname": btname, "btaddress": btaddress})

    def popup_menu(self, trayicon, event):
        if(event.button == 3):
            self.traymenu.set_screen(trayicon.get_screen())
            self.traymenu.popup(None, None, None, event.button, event.time)

    def profile_change(self, item):
        if item.active:
            self.lbrc.set_profile(item.pid)
            self.pid_menu_map[self.lbrc.get_profile()[0]].set_active(0)

    def __create_menu(self):
        self.traymenu = gtk.Menu()
        
        profilemenu = gtk.Menu()
        menuitem = gtk.MenuItem(_("Profiles"))
        menuitem.set_submenu(profilemenu)
        self.traymenu.add(menuitem)
        self.pid_menu_map = {}
        group = None
        for (id, name) in self.lbrc.get_profiles():
            menuitem = gtk.RadioMenuItem(group, name)
            group = menuitem
            menuitem.pid = id
            menuitem.connect("toggled", self.profile_change)
            menuitem.show_all()
            self.pid_menu_map[id] = menuitem
            profilemenu.append(menuitem)

        menuitem = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
        menuitem.connect('activate', self.quit)
        self.traymenu.append(menuitem)
        self.traymenu.show_all()

    def quit(self, *args):
        self.lbrc.shutdown()

    def notify(self, message):
        if not self.notify_interface:
            return
        (x,y) = self.trayicon.window.get_origin()
        app_name = "LBRC"
        replaces_id = 0
        app_icon = "file://" + get_datafiles('LBRC.svg')[-1]
        summary = "Linux Bluetooth Remote Control"
        body = message
        actions = []
        hints = {}
        hints = {"x": x + self.config['icon_size'] / 2, "y": y + self.config['icon_size'] / 2}
        expire_timeout = -1
        self.notify_interface.Notify(app_name, 0, app_icon, summary, body, actions, hints, expire_timeout)
