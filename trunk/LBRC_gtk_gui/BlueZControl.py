import pygtk
pygtk.require("2.0")
import gtk
import gtk.gdk
import gobject
import dbus, dbus.glib

from LBRC.l10n import _
from LBRC import dinterface

class BlueZAdapter(gobject.GObject):
    __gsignals__ = {
        'mode_update': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        'timeout_update': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT,)),
    }
    def __init__(self, adapter):
        gobject.GObject.__init__(self)
        self.diface = dinterface(dbus.SystemBus(), 'org.bluez', adapter, 'org.bluez.Adapter')
        self.mode = self.diface.GetMode()
        self.discoverabletimeout = self.diface.GetDiscoverableTimeout()
        # This is a known memory leak:
        self.diface.connect_to_signal("ModeChanged", self._update_adapter_mode)
        self.diface.connect_to_signal("DiscoverableTimeoutChanged", self._update_adapter_timeout)
        # This object won't go out of scope, but we can't disconnect with 0.7 bindings
        # As the above signal is not fired ... we poll every half second
        self.timeout_poll = gobject.timeout_add(500, self._update_timeout)

    def _update_adapter_mode(self, mode):
        self.mode = mode
        self.emit('mode_update', mode)

    def _update_adapter_timeout(self, timeout):
        self.discoverabletimeout = timeout
        self.emit('timeout_update', timeout)

    def _update_timeout(self):
        timeout = self.diface.GetDiscoverableTimeout()
        if timeout != self.discoverabletimeout:
            self._update_adapter_timeout(timeout)
        return True

    def get_timeout(self):
        if self.mode != 'discoverable':
            return -1
        else:
            return self.discoverabletimeout

    def finalize(self):
        gobject.source_remove(self.timeout_poll) 
        # Prepare for 0.8 bindings, where we can go out of scope...
        pass
    
    def set_timeout(self, timeout=180):
        self.diface.SetDiscoverableTimeout(dbus.UInt32(timeout))
    
    def set_discoverable(self, discoverable):
        if discoverable:
            self.diface.SetMode("discoverable")
        else:
            self.diface.SetMode("connectable")

class BlueZControl(object):
    def __init__(self):
        self.bluez_manager = dinterface(dbus.SystemBus(), 'org.bluez', '/org/bluez' , 'org.bluez.Manager')
        self.bluez_manager.InterfaceVersion()
        self.adapter = {}
        self.menu = {}
        self.bluez_manager.connect_to_signal("AdapterAdded", self._bluez_adapter_added)
        self.bluez_manager.connect_to_signal("AdapterRemoved", self._bluez_adapter_removed)
        self.menu["bz_visible"] = {'title': _("Bluetooth visible"),
                                   'callback': (self._bluez_switch_visible, 0)}
        self.menu["bz_shorttime"] = {'title': _("Bluetooth visible (automatic hiding)"), 
                                     'callback': (self._bluez_switch_visible, 180)}
        self.menu["bz_invisible"] = {'title': _("Bluetooth invisible"), 
                                     'callback': (self._bluez_switch_visible, -1)}
        for menu in self.menu.values():
            menuitem = gtk.CheckMenuItem(menu['title'])
            menuitem.set_draw_as_radio(1)
            menuitem.set_sensitive(0)
            menu['handler'] = menuitem.connect("toggled", *menu['callback'])
            menu['menuitem'] = menuitem
        self._bluez_init_adapter()

    def get_menus(self):
        """
        Get the menus for the control of the BlueZ visibility.

        @return:    Menuitems for BlueZControl
        @rtype:     list of gtk.MenuItem
        """
        return [i['menuitem'] for i in self.menu.values()]

    def _bluez_update_menu(self, *args):
        common_timeout = None
        for adapter in self.adapter.values():
            if common_timeout == None:
                common_timeout = adapter.get_timeout()
            else:
                if common_timeout != adapter.get_timeout():
                    common_timeout = None
                    break
        for i in self.menu.values():
            i['menuitem'].handler_block(i['handler'])
            i['menuitem'].set_active(0)

        if common_timeout != None:
            if common_timeout == 0:
                self.menu['bz_visible']['menuitem'].set_active(1)
            elif common_timeout == -1:
                self.menu['bz_invisible']['menuitem'].set_active(1)
            else:
                self.menu['bz_shorttime']['menuitem'].set_active(1)
        else:
            for i in self.menu.values():
                i['menuitem'].set_inconsistent(1)
        for i in self.menu.values():
            i['menuitem'].handler_unblock(i['handler'])

    def _bluez_init_adapter(self):
        if self.bluez_manager:
            for adapter in self.bluez_manager.ListAdapters():
                self._bluez_adapter_added(adapter)

    def _bluez_adapter_added(self, adapter):
        """
        Callback for the addition of a bluetooth adapter, if there was none before, the menu
        is updated.

        @param  adapter:    DBUS object path for new adapter
        @type   adapter:    string
        """
        self.adapter[adapter] = BlueZAdapter(adapter)
        self.adapter[adapter].handler1 = self.adapter[adapter].connect('timeout_update', self._bluez_update_menu)
        self.adapter[adapter].handler2 = self.adapter[adapter].connect('mode_update', self._bluez_update_menu)
        self._bluez_update_menu()
        if len(self.adapter) == 1:
            for id in self.menu:
                self.menu[id]['menuitem'].set_sensitive(1)

    def _bluez_adapter_removed(self, adapter):
        """
        Callback for the addition of a bluetooth adapter, if there is none left, the menu
        is updated.

        @param  adapter:    DBUS object path for the removed adapter
        @type   adapter:    string
        """
        self.adapter[adapter].finalize()
        self.adapter[adapter].handler_disconnect(self.adapter[adapter].handler1)
        self.adapter[adapter].handler_disconnect(self.adapter[adapter].handler2)
        del self.adapter[adapter]
        
        self._bluez_update_menu()

        if len(self.adapter) == 0:
            for id in self.menu:
                self.menu[id]['menuitem'].set_sensitive(0)
    
    def _bluez_switch_visible(self, menuitem, timeout):
        """
        Callback for the bluetooth control menu. The timeout is used, to determine, how long
        the adapters will be visible. Special cases are 0 (the adapter never gets automaticly
        invisible) and -1 (the adapters are hidden)

        @param  menuitem:   Menu item, that activated this callback
        @type   menuitem:   gtk.MenuItem
        @param  timeout:    Visible time (0 = infty, -1 = hide, else time in seconds)
        @type   timeout:    int
        """
        for adapter in self.adapter.values():
            interface = adapter.diface
            if timeout == -1:
                adapter.set_discoverable(False)
            elif timeout >= 0:
                adapter.set_discoverable(True)
                adapter.set_timeout(timeout)
