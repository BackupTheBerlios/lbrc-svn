#!/usr/bin/python

import bluetooth
import sys
import os
import gobject
import dbus
import dbus.service
import dbus.glib
import logging

import LBRC.consts as co
from LBRC.path import path
from LBRC.config import config
from LBRC.UinputDispatcher import UinputDispatcher
from LBRC.CommandExecutor import CommandExecutor
from LBRC.DBUSCaller import DBUSCaller
from LBRC.ProfileSwitcher import ProfileSwitcher
from LBRC.MPlayer import MPlayer
from LBRC.BTServer import BTServer
from LBRC.l10n import _

class LBRCdbus(dbus.service.Object):
    def __init__(self):
        self.paths = path()
        bus_name = dbus.service.BusName('custom.LBRC', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/custom/LBRC")
        self.btserver = BTServer()
        
        self.config = config()

        self.event_listener = []
        
        for i in (UinputDispatcher, CommandExecutor, DBUSCaller, ProfileSwitcher, MPlayer):
            self._register_listener(i)

        #load of config data 
        self.cur_profile = None
        self.reload_config()

        self.btserver.connect('keycode', self.handler)
        self.btserver.connect('connect', lambda btserver, btadress, port: 
                                         self.connect_cb(bluetooth.lookup_name(btadress), btadress, port))
        self.btserver.connect('disconnect', lambda btserver, btadress, port:
                                         self.disconnect_cb(bluetooth.lookup_name(btadress), btadress, port))
        #load the default profile
        self._load_default_profile()

    def _register_listener(self, constructor):
        # TODO: at some point we have to do conflict resolving (when we define what is a conflict ...)
        try: 
            listener = constructor(self.config)
            try: listener.set_bluetooth_connector(self.btserver)
            except AttributeError: pass
            try: listener.set_core(self)
            except AttributeError: pass
            self.event_listener.append(listener)
        except Exception, e: 
            logging.warn("Failed to initalize " + str(constructor) + "\n" + str(e))
            return

    def _load_default_profile(self):
        #FIXME: catch error when there's no profiles
        possibilities = self.config.get_config_item("default-profile").values()
        possibilities.append(self.config.profile_index[0])
        for profile in possibilities:
            if (profile[0], profile[1]) in self.config.profile_index:
                self.set_profile(profile[0], profile[1])
                return

    @dbus.service.method('custom.LBRC', out_signature='')
    def reload_config(self): 
        self.config.reread()

        #verify if the current selected profile doesn't exist anymore
        if self.cur_profile:
            if (not self.cur_profile in self.config.profile_index):
                    self._load_default_profile()
            else:
                for listener in self.event_listener:
                    listener.set_profile(self.cur_profile[0], self.cur_profile[1]) 
                
    @dbus.service.method('custom.LBRC', in_signature='ss', out_signature=None)
    def set_profile(self, config, profileid):
        if (config, profileid) in self.config.profile_index and \
           not (config, profileid) == self.cur_profile:
            self.cur_profile = (config, profileid)
            self.config.set_config_item('default-profile', self.cur_profile)
            for listener in self.event_listener:
                listener.set_profile(self.cur_profile[0], self.cur_profile[1])
            self.profile_change(config, profileid)

    @dbus.service.method('custom.LBRC', out_signature="a(ss)")
    def get_profiles(self):
        return [i for i in self.config.profile_index]

    @dbus.service.method('custom.LBRC', out_signature="(ss)")
    def get_profile(self):
        return (self.cur_profile)

    @dbus.service.method('custom.LBRC', in_signature='as')
    def set_allowed(self, filter):
        self.btserver.set_allowed(filter)

    @dbus.service.method('custom.LBRC', in_signature='s')
    def add_allowed(self, address):
        self.btserver.add_allowed(address)

    @dbus.service.method('custom.LBRC', out_signature='as')
    def get_allowed(self):
        return self.btserver.get_allowed()

    @dbus.service.method('custom.LBRC', in_signature='s')
    def remove_allowed(self, address):
        self.btserver.remove_allowed(address)

    @dbus.service.method('custom.LBRC', out_signature='')
    def clear_allowed(self):
        self.btserver.clear_allowed()

    @dbus.service.method('custom.LBRC', out_signature='')
    def set_connectable_on(self):
        self.btserver.set_property('connectable', 'yes')

    @dbus.service.method('custom.LBRC', out_signature='')
    def set_connectable_filtered(self):
        self.btserver.set_property('connectable', 'filtered')

    @dbus.service.method('custom.LBRC', out_signature='')
    def set_connectable_off(self):
        self.btserver.set_property('connectable', 'no')

    @dbus.service.signal('custom.LBRC', signature='s')
    def connectable_event(self, state):
        pass

    @dbus.service.signal('custom.LBRC', signature='')
    def update_filter(self):
        pass

    @dbus.service.signal('custom.LBRC', signature="ssi")
    def connect_cb(self, btname, btadress, port):
        pass

    @dbus.service.signal('custom.LBRC', signature="ssi")
    def disconnect_cb(self, btname, btadress, port):
        logging.debug("disconnect_cb: " + str(btname) + " " + str(btadress) + " " + str(port))
        pass

    @dbus.service.signal('custom.LBRC', signature="ix")
    def keycode_cb(self, mapping, keycode):
        pass

    @dbus.service.signal('custom.LBRC', signature='ss')
    def profile_change(self, config, profile):
        pass

    def handler(self, btserver, map, keycode):
        for listener in self.event_listener:
            listener.keycode(map, keycode)
        return True

    def run(self):
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    @dbus.service.method('custom.LBRC')
    @dbus.service.signal('custom.LBRC')
    def shutdown(self):
        self.config.write()
        for i in self.event_listener:
            i.shutdown()
        self.btserver.shutdown()
        self.mainloop.quit()

if __name__ == '__main__':
    brs = LBRCdbus()
    try:
        brs.run()
    except:
        brs.shutdown()
