"""This module provides control for the bluez connection schemes"""
# pylint: disable-msg=E1101
from LBRC import dinterface
from LBRC.config import config
from LBRC.l10n import _
import dbus
import dbus.glib
import gobject
import gtk
import gtk.gdk
import pygtk
pygtk.require("2.0")


class BlueZAdapter(gobject.GObject):
    """
    BlueZAdapter controls one bluez adapter via the dbus bindings. It allows
    to control the visibilty of the adapter and control of automatic hiding
    """
    __gsignals__ = {
        'mode_update': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                        (gobject.TYPE_STRING,)),
        'timeout_update': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                        (gobject.TYPE_INT,)),
    }
    def __init__(self, adapter):
        gobject.GObject.__init__(self)
        self.diface = dinterface(dbus.SystemBus(), 
                                 'org.bluez', 
                                 adapter, 
                                 'org.bluez.Adapter')
        self.mode = self.diface.GetMode()
        self.discoverabletimeout = self.diface.GetDiscoverableTimeout()
        self.diface.connect_to_signal("ModeChanged", 
                                      self._update_adapter_mode)
        self.diface.connect_to_signal("DiscoverableTimeoutChanged", 
                                      self._update_adapter_timeout)

    def _update_adapter_mode(self, mode):
        """React to changes of the adapter modus"""
        self.mode = mode
        self.emit('mode_update', mode)

    def _update_adapter_timeout(self, timeout):
        """
        React to changes in the timeout for the duration the adapter
        stays in the discoverable state
        """
        self.discoverabletimeout = timeout
        self.emit('timeout_update', timeout)

    def get_timeout(self):
        """
        Timeout until the adapter switches discoverable state (if it is not 
        discoverable, the timeout is reported as -1)
        
        @rtype: integer
        """
        if self.mode != 'discoverable':
            return -1
        else:
            return self.discoverabletimeout
    
    def set_timeout(self, timeout=180):
        """
        Set the timeout for the duration the adapter stays in the discoverable 
        state
        
        @param  discoverable:    timeout
        @type   discoverable:    integer
        """
        self.diface.SetDiscoverableTimeout(dbus.UInt32(timeout))
    
    def set_discoverable(self, discoverable):
        """
        Switch the discoverable state of the adapter
        
        @param  discoverable:    Is adapter discoverable?
        @type   discoverable:    boolean        
        """
        if discoverable:
            self.diface.SetMode("discoverable")
        else:
            self.diface.SetMode("connectable")

class BlueZControl(object):
    """
    BlueZControl provides methods for the control of the state of bluetooth
    adapters. This class offers menu entries and controls multiple adapters.
    """
    def __init__(self):
        self.bluez_manager = dinterface(dbus.SystemBus(), 
                                        'org.bluez', 
                                        '/org/bluez' , 
                                        'org.bluez.Manager')
        self.bluez_manager.InterfaceVersion()
        self.config = config()
        self.adapter = {}
        self.menu = {}
        self.bluez_manager.connect_to_signal("AdapterAdded", 
                                             self.cb_bluez_adapter_added)
        self.bluez_manager.connect_to_signal("AdapterRemoved", 
                                             self.cb_bluez_adapter_removed)
        self.menu["bz_visible"] = {
                            'title': _("Bluetooth visible"),
                            'callback': (self.cb_bluez_switch_visible, 0)}
        self.menu["bz_shorttime"] = {
                            'title': _("Bluetooth visible (automatic hiding)"), 
                            'callback': (self.cb_bluez_switch_visible, 180)}
        self.menu["bz_invisible"] = {
                            'title': _("Bluetooth invisible"), 
                            'callback': (self.cb_bluez_switch_visible, -1)}

        for menu in self.menu.values():
            menuitem = gtk.CheckMenuItem(menu['title'])
            menuitem.set_draw_as_radio(1)
            menuitem.set_sensitive(0)
            menu['handler'] = menuitem.connect("toggled", menu['callback'][0],
                                                          menu['callback'][1])
            menu['menuitem'] = menuitem

        self.menu_list = [i['menuitem'] for i in self.menu.values()]
        menuitem = gtk.SeparatorMenuItem()
        self.menu_list.append(menuitem)
        self.set_menus_visible(self.config.get_config_item_fb("show-bluetooth", 
                                                              True))
        self._bluez_init_adapter()

    def set_menus_visible(self, state):
        """
        Make the menus visible or hide them
        
        @param  state:    show menus true/false
        @type   state:    boolean
        """
        if state:
            for i in self.menu_list:
                i.show_all()
        else:
            for i in self.menu_list:
                i.hide_all()

    def get_menus(self):
        """
        Get the menus for the control of the BlueZ visibility.

        @return:    Menuitems for BlueZControl
        @rtype:     list of gtk.MenuItem
        """
        return self.menu_list

    def cb_bluez_update_menu(self, *args):
        """Update menu with respect to the bluetooth state"""
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
        """
        Add all bluetooth adapters to the list - after init the adapters
        are added in response to bluez dbus signals
        """
        if self.bluez_manager:
            for adapter in self.bluez_manager.ListAdapters():
                self.cb_bluez_adapter_added(adapter)

    def cb_bluez_adapter_added(self, adapter):
        """
        Callback for the addition of a bluetooth adapter, if there was none 
        before, the menu is updated.

        @param  adapter:    DBUS object path for new adapter
        @type   adapter:    string
        """
        self.adapter[adapter] = BlueZAdapter(adapter)
        self.adapter[adapter].handler1 = self.adapter[adapter].connect(
                                                'timeout_update', 
                                                self.cb_bluez_update_menu)
        self.adapter[adapter].handler2 = self.adapter[adapter].connect(
                                                'mode_update', 
                                                self.cb_bluez_update_menu)
        self.cb_bluez_update_menu()
        if len(self.adapter) == 1:
            for menu_id in self.menu:
                self.menu[menu_id]['menuitem'].set_sensitive(1)

    def cb_bluez_adapter_removed(self, adapter):
        """
        Callback for the addition of a bluetooth adapter, if there is none left, 
        the menu is updated.

        @param  adapter:    DBUS object path for the removed adapter
        @type   adapter:    string
        """
        self.adapter[adapter].finalize()
        self.adapter[adapter].handler_disconnect(self.adapter[adapter].handler1)
        self.adapter[adapter].handler_disconnect(self.adapter[adapter].handler2)
        del self.adapter[adapter]
        
        self.cb_bluez_update_menu()

        if len(self.adapter) == 0:
            for menu_id in self.menu:
                self.menu[menu_id]['menuitem'].set_sensitive(0)
    
    def cb_bluez_switch_visible(self, menuitem, timeout):
        """
        Callback for the bluetooth control menu. The timeout is used, to 
        determine, how long the adapters will be visible. Special cases are 0
        (the adapter never gets automaticly invisible) and -1 
        (the adapters are hidden)

        @param  menuitem:   Menu item, that activated this callback
        @type   menuitem:   gtk.MenuItem
        @param  timeout:    Visible time (0 = infty, -1 = hide, else time in seconds)
        @type   timeout:    int
        """
        for adapter in self.adapter.values():
            if timeout == -1:
                adapter.set_discoverable(False)
            elif timeout >= 0:
                adapter.set_discoverable(True)
                adapter.set_timeout(timeout)
