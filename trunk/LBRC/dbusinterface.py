"""Main Interface Module for LBRC - the core of the whole application"""
# pylint: disable-msg=E1101
from LBRC import dinterface
from LBRC.BTServer import BTServer
from LBRC.CommandExecutor import CommandExecutor
from LBRC.DBUSCaller import DBUSCaller
from LBRC.MPlayer import MPlayer
from LBRC.PresentationCompanion import PresentationCompanion
from LBRC.ProfileSwitcher import ProfileSwitcher
from LBRC.UinputDispatcher import UinputDispatcher, UinputDispatcher
from LBRC.VolumeControl import VolumeControl
from LBRC.XInput import XInput
from LBRC.config import config
from LBRC.path import path
import dbus
import dbus.glib
import dbus.service
import gobject
import logging
import time


DBUSNAME = 'de.berlios.lbrc'
DBUSIFACE = 'de.berlios.lbrc'

class DBUSProfileControl(dbus.service.Object):
    def __init__(self, busname, dbuspath, parent):
        dbus.service.Object.__init__(self, busname, dbuspath)
        self.parent = parent
        parent.connect("profile_changed", self.cb_profile_changed)
    
    def cb_profile_changed(self, parent, configfile, profile):
        self.profile_changed(configfile, profile)    
    
    @dbus.service.signal(DBUSIFACE, signature='ss')
    def profile_changed(self, configfile, profile):
        pass
    
    @dbus.service.method(DBUSIFACE, out_signature="a(ss)")
    def get_profiles(self):
        return [i for i in self.parent.config.profile_index]
    
    @dbus.service.method(DBUSIFACE, out_signature="(ss)")
    def get_current_profile(self):
        return self.parent.cur_profile
    
    @dbus.service.method(DBUSIFACE, in_signature='ss', out_signature=None)
    def set_profile(self, configfile, profileid):
        self.parent.set_profile(str(configfile), str(profileid))

class ProfileControl(gobject.GObject):
    __gsignals__ = {
        "profile_changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                                            (gobject.TYPE_STRING, 
                                             gobject.TYPE_STRING))
    }
    
    def __init__(self, configdata):
        gobject.GObject.__init__(self)
        self.config = configdata
        self.config.connect("config-reread", self.cb_config_reread)
        self.cur_profile = (None, None)

    def cb_config_reread(self, configfile):
        #verify if the current selected profile doesn't exist anymore
        if self.cur_profile:
            if (not self.cur_profile in self.config.profile_index):
                self._load_default_profile()
            else:
                self.emit('profile_changed', self.cur_profile[0], 
                                             self.cur_profile[1])

    def set_profile(self, configfile, profileid):
        if (configfile, profileid) in self.config.profile_index and \
           not (configfile, profileid) == self.cur_profile:
            self.cur_profile = (configfile, profileid)
            self.config.set_config_item('default-profile', self.cur_profile)
            self.emit('profile_changed', self.cur_profile[0], self.cur_profile[1])
            
    def _load_default_profile(self):
        #FIXME: catch error when there's no profiles
        possibilities = self.config.get_config_item("default-profile").values()
        possibilities.append(self.config.profile_index[0])
        for profile in possibilities:
            if (profile[0], profile[1]) in self.config.profile_index:
                self.set_profile(profile[0], profile[1])
                return

class AccessControl(dbus.service.Object):
    @dbus.service.method(DBUSIFACE, in_signature='as')
    def set_allowed(self, allowed_list):
        self.btserver.set_allowed(allowed_list)

    @dbus.service.method(DBUSIFACE, in_signature='s')
    def add_allowed(self, address):
        self.btserver.add_allowed(address)

    @dbus.service.method(DBUSIFACE, out_signature='as')
    def get_allowed(self):
        return self.btserver.get_allowed()

    @dbus.service.method(DBUSIFACE, in_signature='s')
    def remove_allowed(self, address):
        self.btserver.remove_allowed(address)

    @dbus.service.method(DBUSIFACE, out_signature='')
    def clear_allowed(self):
        self.btserver.clear_allowed()    
        
    @dbus.service.signal(DBUSIFACE, signature='')
    def update_filter(self):
        pass

class ConnectionControl(dbus.service.Object):
    def __init__(self, busname, dbuspath, btserver):
        dbus.service.Object.__init__(self,busname, dbuspath)
        self.logger = logging.getLogger("LBRC.ConnectionControl")
        self.btserver = btserver
        self.btserver.connect('connect', self._connect_cb)
        self.btserver.connect('disconnect', self._disconnect_cb)
    
    @staticmethod
    def _lookup_bluetooth_name(bluetooth_address):
        # TODO: Handle no adapters
        # TODO: Handles RequestDefered return type + NotAvailable
        bluez_manager = dinterface(dbus.SystemBus(), 
                                   'org.bluez',
                                   '/org/bluez', 
                                   'org.bluez.Manager')
        try:
            default_adapter = dinterface(dbus.SystemBus(), 'org.bluez', bluez_manager.DefaultAdapter(), 'org.bluez.Adapter')
            return default_adapter.GetRemoteName(bluetooth_address)
        except dbus.exceptions.DBusException:
            return bluetooth_address
    
    def _connect_cb(self,btserver, btadress, port):
        self.connect_cb(self._lookup_bluetooth_name(btadress), btadress, port)
        return True
        
    def _disconnect_cb(self, btserver, btadress, port):
        self.disconnect_cb(self._lookup_bluetooth_name(btadress), btadress, port)
        return True
    
    @dbus.service.method(DBUSIFACE, out_signature='')
    def set_connectable_on(self):
        self.btserver.set_property('connectable', 'yes')

    @dbus.service.method(DBUSIFACE, out_signature='')
    def set_connectable_filtered(self):
        self.btserver.set_property('connectable', 'filtered')

    @dbus.service.method(DBUSIFACE, out_signature='')
    def set_connectable_off(self):
        self.btserver.set_property('connectable', 'no')

    @dbus.service.signal(DBUSIFACE, signature='s')
    def connectable_event(self, state):
        pass

    @dbus.service.signal(DBUSIFACE, signature="ssi")
    def connect_cb(self, btname, btadress, port):
        self.logger.debug("connect_cb: " + str(btname) + " " + str(btadress) + " " + str(port))

    @dbus.service.signal(DBUSIFACE, signature="ssi")
    def disconnect_cb(self, btname, btadress, port):
        self.logger.debug("disconnect_cb: " + str(btname) + " " + str(btadress) + " " + str(port))

class DBUSLogHandler(logging.Handler, dbus.service.Object):
    def __init__(self, busname, dbuspath):
        dbus.service.Object.__init__(self, busname, dbuspath)
        logging.Handler.__init__(self)

    @dbus.service.signal(DBUSIFACE, signature='sisssssidsixsisss')
    def logemit(self, name, levelno, levelname, pathname, filename,
              module, funcName, lineno, created, asctime, msecs,
              thread, threadName, process, msg, message, fmessage):
        pass

    @dbus.service.method(DBUSIFACE, in_signature='i')
    def setLevel(self, lvl):
        logging.Handler.setLevel(self, lvl)
    
    def emit(self, lr):
        # lr = LogRecord
        lr.asctime = (time.strftime("%Y-%m-%d %H:%M:%S", 
                                    time.localtime(lr.created)) + ",%03d") % \
                                    (lr.msecs,)
        lr.message = lr.getMessage()
        lr.fmessage = self.format(lr)
        #only in 2.5
        try:
            function = lr.funcName
        except AttributeError:
            function = ""
        self.logemit(
                   lr.name,
                   lr.levelno,
                   lr.levelname,
                   lr.pathname,
                   lr.filename,
                   lr.module,
                   function,
                   lr.lineno,
                   lr.created,
                   lr.asctime,
                   lr.msecs,
                   lr.thread,
                   lr.threadName,
                   lr.process,
                   lr.msg,
                   lr.message,
                   lr.fmessage)

class Core(dbus.service.Object):
    def __init__(self, **kwds):
        self.logger = logging.getLogger('LBRC')
        self.shutdown_commands = []
        bus_name = dbus.service.BusName(DBUSNAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/core")
        
        self.loghandler = DBUSLogHandler(bus_name, "/log")
        logging.getLogger().addHandler(self.loghandler)
        if 'debug' in kwds:
            self.loghandler.setLevel(kwds['debug'])
            
        self.paths = path()
        self.btserver = BTServer()
        self.config = config()
        
        self.profile_control = ProfileControl(self.config)
        self.dbus_profile_control = DBUSProfileControl(bus_name,
                                                       "/profile",
                                                       self.profile_control)
        self.connection_control = ConnectionControl(bus_name, 
                                                    "/connection", 
                                                    self.btserver)
        
        self.event_listener = []
        
        for i in (UinputDispatcher, CommandExecutor, DBUSCaller, 
                  ProfileSwitcher, MPlayer, PresentationCompanion,
                  VolumeControl, XInput):
            self._register_listener(i)

        self.logger.debug("Register done")
        self.profile_control.connect("profile_changed", self._profile_change_cb)
        self.logger.debug("Initial Profile set")
        self.btserver.connect('keycode', self._dispatch)
        self.logger.debug("Init dispatcher")

        self.btserver.connect("connect", self._connection_established_cb)
        self.btserver.connect("disconnect", self._connection_closed_cb)

        #load of config data 
        self.reload_config()
        self.logger.debug("Reload config")

    def _connection_closed_cb(self, server, bluetoothaddress, port):
        self.logger.debug("_connection_closed_cb called")
        for listener in self.event_listener:
            if callable(listener.__getattribute__("connection_closed")):
                listener.connection_closed()
        return False
            
    def _connection_established_cb(self, server, bluetoothaddress, port):
        self.logger.debug("_connection_established_cb called")
        for listener in self.event_listener:
            if callable(listener.__getattribute__("connection_established")):
                listener.connection_established()
        return False

    def _profile_change_cb(self, profile_control, config_file, profile):
        for listener in self.event_listener:
            listener.set_profile(config_file, profile)

    def _register_listener(self, constructor):
        try: 
            listener = constructor(self.config)
            if callable(listener.__getattribute__('set_bluetooth_connector')):
                listener.set_bluetooth_connector(self.btserver)
            if callable(listener.__getattribute__('set_core')):
                listener.set_core(self)
            self.event_listener.append(listener)
            self.logger.debug("Initiablized Event Listener: %s" 
                                                     % str(constructor))
        except Exception, exception: 
            self.logger.warn("Failed to initalize %s\n%s" %(str(constructor),
                                                            str(exception)))

    def _dispatch(self, btserver, mapping, keycode):
        for listener in self.event_listener:
            listener.keycode(mapping, keycode)
        return True

    @dbus.service.method(DBUSIFACE, out_signature='')
    def reload_config(self): 
        self.config.reread()

    @dbus.service.signal(DBUSIFACE, signature="ix")
    def keycode_cb(self, mapping, keycode):
        pass

    @dbus.service.method(DBUSIFACE)
    @dbus.service.signal(DBUSIFACE)
    def shutdown(self):
        self.config.write()
        for i in self.event_listener:
            i.shutdown()
        self.btserver.shutdown()
        for command in self.shutdown_commands:
            command()