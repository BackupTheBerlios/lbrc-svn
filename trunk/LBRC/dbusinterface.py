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
from LBRC import read_config, write_config
from LBRC.path import path
from LBRC.UinputDispatcher import UinputDispatcher
from LBRC.CommandExecutor import CommandExecutor
from LBRC.BTServer import BTServer
from LBRC.l10n import _

class LBRCdbus(dbus.service.Object):
    def __init__(self):
        self.paths = path()
        bus_name = dbus.service.BusName('custom.LBRC', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/custom/LBRC")
        self.btserver = BTServer()
        
        self.config = {}
        self._read_config()

        self.event_listener = []
        self.event_listener.append(UinputDispatcher(self.config))
        self.event_listener.append(CommandExecutor(self.config))

        #load of config data 
        self.cur_profile = None
        self.force_reload()

        self.btserver.connect('keycode', self.handler)
        self.btserver.connect('connect', lambda btserver, btadress, port: 
                                         self.connect_cb(bluetooth.lookup_name(btadress), btadress, port))
        self.btserver.connect('disconnect', lambda btserver, btadress, port:
                                         self.disconnect_cb(bluetooth.lookup_name(btadress), btadress, port))
        #load the default profile
        self._load_default_profile()


    def _load_default_profile(self):
        #FIXME: catch error when there's no profiles
        if ( "default-profile" in self.config['user']['generic-config'] and
             tuple(self.config['user']['generic-config']['default-profile']) in self.profile_index):
            self.set_profile(self.config['user']['generic-config']['default-profile'][0], 
                             self.config['user']['generic-config']['default-profile'][1])
        elif ( "default-profile" in self.config['system']['generic-config'] and
              tuple(self.config['system']['generic-config']['default-profile']) in self.profile_index):
            self.set_profile(self.config['system']['generic-config']['default-profile'][0], 
                             self.config['system']['generic-config']['default-profile'][1])
        else:
            self.set_profile(self.profile_index[0][0], self.profile_index[0][1])

    @dbus.service.method('custom.LBRC', out_signature='')
    def force_reload(self): 
        self._read_config()
        for i in self.event_listener:
            i.shutdown()
        self.event_listener = []

        #verify if the current selected profile doesn't exist anymore
        if (not self.cur_profile in self.profile_index):
                self._load_default_profile()
        else:
            for listener in self.event_listener:
                listener.set_profile(self.cur_profile[0], self.cur_profile[1]) 
                
    @dbus.service.method('custom.LBRC', in_signature='ss', out_signature=None)
    def set_profile(self, config, profileid):
        if (config, profileid) in self.profile_index and \
           not (config, profileid) == self.cur_profile:
            self.cur_profile = (config, profileid)
            self.config['user']['generic-config']['default-profile'] = self.cur_profile
            for listener in self.event_listener:
                listener.set_profile(self.cur_profile[0], self.cur_profile[1])
            self.profile_change(config, profileid)

    @dbus.service.method('custom.LBRC', out_signature="a(ss)")
    def get_profiles(self):
        return [i for i in self.profile_index]

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
        pass

    @dbus.service.signal('custom.LBRC', signature="ix")
    def keycode_cb(self, mapping, keycode):
        pass

    @dbus.service.signal('custom.LBRC', signature='ss')
    def profile_change(self, config, profile):
        pass

    def _write_config(self):
        try:
            write_config(self.paths.get_userconfigfile(), self.config['user'])
        except Exception, e:
            logging.error(_("Could not write config file: %s"), self.paths.get_userconfigfile())

    def _read_config(self):
        try:
            self.config['user'] = read_config(self.paths.get_userconfigfile())
        except IOError:
            logging.debug(_("Could not open config file: %s"), self.paths.get_userconfigfile())
            self.config['user'] = {}
            self.config['user']['generic-config'] = {}
            self.config['user']['profiles'] = {}
        try:
            self.config['system'] = read_config(self.paths.get_systemconfigfile())
        except IOError:
            logging.debug(_("Could not open config file: %s"), self.paths.get_systemconfigfile())
            self.config['system'] = {}
            self.config['system']['generic-config'] = {}
            self.config['system']['profiles'] = {}

        self.profile_index = []
        self.profile_index.extend([('system', profile_name) for profile_name in self.config['system']['profiles']])
        self.profile_index.extend([('user', profile_name) for profile_name in self.config['user']['profiles']])
        for i in self.profile_index:
            print i
    
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
        self._write_config()
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
