import pygtk
pygtk.require("2.0")
import gtk
import gtk.gdk
import egg.trayicon
import dbus
import dbus.glib

from LBRC.path import path
from LBRC import dinterface
from LBRC.l10n import _
from LBRC.config import config
from BlueZControl import BlueZControl
from config import ConfigWindow

class Applet(object):
    def __init__(self, bus, interface, service, **kwds):
        self.lbrc_core = dinterface(bus, service, '/core', interface)
        self.lbrc_profile = dinterface(bus, service, '/profile', interface)
        self.lbrc_connection = dinterface(bus, service, '/connection', interface)
        self._config = {}
        self.config = config()
        self.paths = path()
        try:
            proxy_obj = dbus.SessionBus().get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
            self.notify_interface = dbus.Interface(proxy_obj, 'org.freedesktop.Notifications')
            self.notify_interface.GetServerInformation()
        except:
            self.notify_interface = None
        try:
            self.bluecontrol = BlueZControl()
        except:
            self.bluecontrol = None
        self._config['icon_size'] = 24
        self.icon = gtk.gdk.pixbuf_new_from_file(self.paths.get_datafile('LBRC.svg'))
        self.trayicon = egg.trayicon.TrayIcon("LBRC")
        image = gtk.Image()
        image.set_from_pixbuf(self.icon.scale_simple(self._config['icon_size'],self._config['icon_size'], gtk.gdk.INTERP_BILINEAR))
        self._create_menu()
        eventbox = gtk.EventBox()
        self.trayicon.add(eventbox)
        eventbox.add(image)
        eventbox.add_events(gtk.gdk.BUTTON_PRESS)
        eventbox.connect('button-press-event', self.popup_menu)
        self.lbrc_core.connect_to_signal("shutdown", lambda: gtk.main_quit())
        self.lbrc_connection.connect_to_signal("connect_cb", self.connect_cb)
        self.lbrc_connection.connect_to_signal("disconnect_cb", self.disconnect_cb)
        self.lbrc_profile.connect_to_signal("profile_changed", self.profile_change_cb)
        self.pid_menu_map[self.lbrc_profile.get_current_profile()].set_active(1)
        self.trayicon.show_all()

        self.config_close_handler = None

    def _config_close_handler(self, config_dialog, changed):
        if changed:
            self.lbrc_core.reload_config()
            self.config.reread()
            self._fill_profile_menu()
            if self.bluecontrol:
                self.bluecontrol.set_menus_visible(self.config.get_config_item_fb("show-bluetooth", True))
        config_dialog.disconnect(self.config_close_handler)
        self.config_close_handler = None

    def profile_change_cb(self, config, profile):
        self.notify(_("Profile changed:\n%(profilename)s") % {"profilename": profile})
        self.pid_menu_map[(config, profile)].set_active(1)

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
            self.lbrc_profile.set_profile(item.config, item.pid)
            cp = self.lbrc_profile.get_current_profile()
            self.pid_menu_map[cp].set_active(0)

    def _fill_profile_menu(self):
        profilemenu = self.profilemenu
        
        def cleanup(menu_entry, menu):
            menu_entry.disconnect(menu_entry.handler)
            menu.remove(menu_entry)
        
        profilemenu.foreach(cleanup, profilemenu)
        
        self.pid_menu_map = {}
        group = None

        def sort_func(first, second):
            if first[0] == second[0]:
                return cmp(first[1], second[1])
            elif first[0] == 'system':
                return -1
            else:
                return 1

        for (config, profile) in sorted(self.lbrc_profile.get_profiles(), cmp=sort_func):
            itemname = None
            if config == 'system':
                itemname = "%s (%s)" % (profile, _("System"))
            else:
                itemname = profile

            menuitem = gtk.RadioMenuItem(group, itemname)
            group = menuitem
            menuitem.config = config
            menuitem.pid = profile
            id = menuitem.connect("toggled", self.profile_change)
            menuitem.handler = id
            menuitem.show_all()
            self.pid_menu_map[(config, profile)] = menuitem
            profilemenu.append(menuitem)

    def _create_menu(self):
        self.traymenu = gtk.Menu()
        
        self.profilemenu = gtk.Menu()
        menuitem = gtk.MenuItem(_("Profiles"))
        menuitem.set_submenu(self.profilemenu)
        self._fill_profile_menu()
        menuitem.show()
        self.traymenu.add(menuitem)
        
        menuitem = gtk.SeparatorMenuItem()
        menuitem.show()
        self.traymenu.append(menuitem)
        
        if self.bluecontrol:
            for menuitem in self.bluecontrol.get_menus():
                self.traymenu.append(menuitem)

        # Configuration editor 
        menuitem = gtk.ImageMenuItem(stock_id=gtk.STOCK_PREFERENCES)
        menuitem.connect("activate", self.show_config)
        menuitem.show()
        self.traymenu.append(menuitem)

        menuitem = gtk.SeparatorMenuItem()
        menuitem.show()
        self.traymenu.append(menuitem)

        menuitem = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
        menuitem.connect('activate', self.quit)
        menuitem.show()
        self.traymenu.append(menuitem)
        self.traymenu.show()

    def quit(self, *args):
        self.lbrc_core.shutdown()
    
    def show_config(self, object):
        if not self.config_close_handler:
            config_dialog = ConfigWindow()
            self.config_close_handler = config_dialog.connect("close", self._config_close_handler)

    def notify(self, message):
        if not self.notify_interface:
            return
        (x,y) = self.trayicon.window.get_origin()
        app_name = "LBRC"
        replaces_id = 0
        app_icon = "file://" + self.paths.get_datafile('LBRC.svg')
        summary = "Linux Bluetooth Remote Control"
        body = message
        actions = []
        hints = {}
        hints = {"x": x + self._config['icon_size'] / 2, "y": y + self._config['icon_size'] / 2}
        expire_timeout = -1
        self.notify_interface.Notify(app_name, 0, app_icon, summary, body, actions, hints, expire_timeout)
