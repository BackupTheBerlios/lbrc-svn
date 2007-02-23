#!/usr/bin/python

import pygtk
pygtk.require("2.0")
import gtk
import pynotify
pynotify.init("BlueRemote")
import gtk.gdk
import gobject
import egg.trayicon
import time
import dbus
import os
import sys

scriptpath = os.path.dirname(os.path.abspath(sys.argv[0]))

class LBRC(gobject.GObject):
    def __init__(self, lbrc, **kwds):
        gobject.GObject.__init__(self)
        self.lbrc = lbrc
        self.config = {}
        self.config['icon_size'] = 24
        self.config['abspath'] = scriptpath
        self.icon = gtk.gdk.pixbuf_new_from_file(self.config['abspath'] + "/BlueRemote.svg")
        self.trayicon = egg.trayicon.TrayIcon("BlueRemote")
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

    def profile_change_cb(self, id, name):
        self.notify("Profile changed.\n" + name)
        self.pid_menu_map[id].set_active(1)

    def connect_cb(self, btname, btadress, port):
        self.notify("Connect from:\n" + btname + " (" + btadress + ")")

    def disconnect_cb(self, btname, btadress, port):
        self.notify("Disconnect from:\n" + btname + " (" + btadress + ")")

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
        menuitem = gtk.MenuItem("Profile")
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
        (x,y) = self.trayicon.window.get_origin()
        n = pynotify.Notification("BlueRemote", message, "file://" + self.config['abspath'] + "/BlueRemote.svg")
        n.set_timeout(5000)
        n.set_hint("x", x + self.config['icon_size'] / 2)
        n.set_hint("y", y + self.config['icon_size'] / 2)
        n.show()

if __name__=="__main__":
    gobject.spawn_async([scriptpath+"/LBRCdbus.py"], 
                       flags= gobject.SPAWN_STDOUT_TO_DEV_NULL | 
                              gobject.SPAWN_STDERR_TO_DEV_NULL )
    bus = dbus.SessionBus()
    proxy_obj = None
    count = 0
    proxy_obj = dbus.SessionBus().get_object('custom.LBRC', '/custom/LBRC')
    lbrc_interface = dbus.Interface(proxy_obj, 'custom.LBRC')
    ok = 0
    while count < 10:
        try:
            lbrc_interface.get_profiles()
            ok = 1
            break
        except dbus.DBusException:
            count += 1
            time.sleep(0.5)
    if not ok:
        print "Could not connect to DBUS component of LBRC"
        sys.exit(1)
    else:
        lbrc = LBRC(lbrc_interface)
        gtk.main()
        sys.exit(0)
