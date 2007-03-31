#!/usr/bin/python

from LBRC import dinterface
import dbus
import logging
from LBRC.config import configValueNotFound

class DBUSCall(object):
    _translator = {
                   'boolean': lambda arg: arg == 'true',
                   'byte': dbus.Byte,
                   'int16': dbus.Int16,
                   'int32': dbus.Int32,
                   'int64': dbus.Int64,
                   'uint16': dbus.UInt16,
                   'uint32': dbus.UInt32,
                   'uint64': dbus.UInt64,
                   'string': dbus.String,
                   'double': dbus.Double,
                   }
    def __init__(self, action):
        self.service = action['service']
        self.object = action['object']
        self.interface = action['interface']
        self.method = action['method']
        self.arguments = []
        if 'arguments' in action:
            for i in action['arguments']:
                sep = i.find(":")
                type = i[:sep]
                argument = i[(sep+1):]
                self.arguments.append(self._translator[type](argument))
        try:
            if action['bus'] == 'system':
                self.bus = dbus.SystemBus()
        except:
            self.bus = dbus.SessionBus()
    def call(self):
        logging.debug("DBUSCall: " + str((self.bus, self.service, self.object, self.interface)))
        iface = dinterface(self.bus, self.service, self.object, self.interface)
        iface.__getattr__(self.method).__call__(*self.arguments)

class DBUSCaller(object):
    """
    Class to handle keycodes received by BTServer and issue DBUS Calls
    according to them
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         L{LBRC.config}
        """
        self.config = config
        self.init = []
        self.actions = {}
        self.destruct = []

    def keycode(self, mapping, keycode):
        """
        The method maps the incoming keycode and mapping to the associated
        command and spawns a subprocess for them.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        int
        @param  keycode:        keycode received
        @type   keycode:        int
        """
        event_tuple = (keycode, mapping)
        if event_tuple in self.actions:
            for command in self.actions[event_tuple]:
                command.call()

    def set_profile(self, config, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        logging.debug("DBUSCaller: Init")
        for i in self.destruct:
            i.call()
        self._interpret_profile(config, profile)
        logging.debug("DBUSCaller: Init")
        for i in self.init:
            i.call()
        
    def _interpret_profile(self, config, profile):
        """
        Interpret the profile data from the profile.conf(s) and push the commands into
        an array and call it, when the appropriate keycodes and mappings are received.

        If no mapping is provided, we assume mapping = 0 => keypress
        """
        self.init = []
        self.actions = {}
        self.destruct = []

        try:
            _section = self.config.get_profile(config, profile, 'DBUSCaller')
        except configValueNotFound:
            logging.debug('DBUSCaller: no config section found for profile "%s", config "%s"', profile, config)
            return

        try:
            for action in _section['init']:
                logging.debug('DBUSCaller: Init: ' + str(action))
                self.init.append(DBUSCall(action))
        except KeyError:
            logging.debug("DBUSCaller: init subsection not found")
            
        try:
            for action in _section['destruct']:
                logging.debug('DBUSCaller: Destruct: ' + str(action))
                self.destruct.append(DBUSCall(action))
        except KeyError:
            logging.debug("DBUSCaller: destuct subsection not found")

        try:
            for action in self.config.get_profile(config, profile, 'DBUSCaller')['actions']:
                logging.debug('DBUSCaller: Action: ' + str(action))
                try:
                    mapping = int(action['mapping'])
                except:
                    mapping = 0
                event_tuple = (int(action['keycode']), mapping)
                if not event_tuple in self.actions:
                    self.actions[event_tuple] = []
                self.actions[event_tuple].append(DBUSCall(action))
                logging.debug("DBUSCaller: Added Event for : " + str(event_tuple))
        except KeyError:
            logging.debug("DBUSCaller: actions subsection not found")


    def shutdown(self):
        pass
        #for command in self.destruct:
        #    command.call()
