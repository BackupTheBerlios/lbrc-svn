#!/usr/bin/python

import logging
import gobject

class Command(object):
    def __init__(self, description):
        self.description = description

    def _to_array(self):
        command_line = []
        command_line.append(self.description['command']) 
        if 'arguments' in self.description:
            command_line.extend([str(arg) for arg in self.description['arguments']])
        return command_line
    
    def call(self):
        logging.debug("CommandExecutor - Calling: " + str(self._to_array()))
        gobject.spawn_async( self._to_array(), 
                             flags= gobject.SPAWN_STDOUT_TO_DEV_NULL | 
                                    gobject.SPAWN_STDERR_TO_DEV_NULL )

class CommandExecutor(object):
    """
    Class to handle keycodes received by BTServer and issue commands according to them
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         dictionary
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
            logging.debug("CommandExecutor: called for (%s, %s) - Action found" % (keycode, mapping))
        else:
            logging.debug("CommandExecutor: called for (%s, %s) - No Action" % (keycode, mapping))
    
    def set_profile(self, config, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        logging.debug("CommandExecutor: set_profile called with: %s %s" % (config, profile))
        for command in self.destruct:
            command.call()
        self._interpret_profile(config, profile)
        for command in self.init:
            command.call()
                                
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
            for init in self.config.get_profile(config, profile, 'CommandExecutor')['init']:
                self.init.append(Command(init))
        except:
            logging.debug("CommandExecutor: No Init Actions found")
            pass
        try:
            for destruct in self.config.get_profile(config, profile, 'CommandExecutor')['destruct']:
                self.destruct.append(Command(destruct))
        except:
            logging.debug("CommandExecutor: No Destruct Actions found")
            pass
       
        try:
            for action in self.config.get_profile(config, profile, 'CommandExecutor')['actions']:
                try:
                    mapping = int(action['mapping'])
                except:
                    mapping = 0
                event_tuple = (int(action['keycode']), mapping)
                if not event_tuple in self.actions:
                    self.actions[event_tuple] = []
                logging.debug("CommandExecutor: Registering Action for tupple: %s, %s" % event_tuple)
                self.actions[event_tuple].append(Command(action))
        except:
            logging.debug("CommandExecutor: No Actions found")
            pass

    def shutdown(self):
        for command in self.destruct:
            command.call()
