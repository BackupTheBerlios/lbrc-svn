"""See  Listener Object"""
import logging
from config import configValueNotFound

class UndefinedCommandClass(Exception):
    """Raised, if the default _interpret_profile of Listener is used, but no
    command_class ist supplied"""

class ListenerInitFailedException(Exception):
    """Raised, if initialisation of Listener failed!"""

class Listener(object):
    """
    Generic parent class for action listener - Contains base functionality.
    
    Descendants of this class have to either provide a custom CommandClass,
    that is responsible for interpreting the specific actions or has to
    overwrite _interpret_profile!
    """
    def __init__(self, config, name, **kwargs):
        self.name = name
        self.logger = logging.getLogger('LBRC.Listener.' + self.name)
        self.logger.debug("__init__ begin")
        self.config = config
        if 'command_class' in kwargs:
            self.command_class = kwargs['command_class']
        else:
            self.command_class = None
        self.bluetooth_connector = None
        self.core = None
        self.init = []
        self.actions = {}
        self.destruct = []
        self.logger.debug("__init__ of baseclass done")
    
    def _interpret_profile(self, config, profile):
        """
        Interpret the profile data from the profile.conf(s) and push the commands into
        an array and call it, when the appropriate keycodes and mappings are received.

        If no mapping is provided, we assume mapping = 0 => keypress
        """
        self.logger.debug("_interpret_profile called")
        if not self.command_class:
            raise UndefinedCommandClass()
        self.init = []
        self.actions = {}
        self.destruct = []
        command_class = self.command_class
        config_section = {}
        
        try:
            config_section = self.config.get_profile(config, profile, self.name)
        except configValueNotFound:
            self.logger.debug("No config section found")
            self.logger.debug("_interpret_profile finished")
            
        try:
            for init in config_section['init']:
                self.init.append(command_class(self, init))
        except KeyError, exception:
            self.logger.debug("failure while interprating init: %s" % 
                                                           repr(exception))
        try:
            for destruct in config_section['destruct']:
                self.destruct.append(command_class(self, destruct))
        except KeyError, exception:
            self.logger.debug("failure while interprating destruct: %s" %
                                                           repr(exception))
       
        try:
            for action in config_section['actions']:
                try:
                    mapping = int(action['mapping'])
                except (TypeError, KeyError):
                    mapping = 0
                event_tuple = (int(action['keycode']), mapping)
                if not event_tuple in self.actions:
                    self.actions[event_tuple] = []
                self.actions[event_tuple].append(command_class(self, action))
        except KeyError, exception:
            self.logger.debug("failure while interprating actions: %s" % 
                                                            repr(exception))

        self.logger.debug("_interpret_profile finished")
        
    def set_bluetooth_connector(self, bluetooth_connector):
        """
        Set our bluetooth connector, that allows us to issue the presentation
        of a list, from which the user can choose the new profile
        
        @param    bc:    Bluetooth Adapter
        @type     bc:    L{BTServer}
        """
        self.bluetooth_connector = bluetooth_connector

    def set_core(self, core):
        """
        Set the core, where the administration of the profiles happens
        Currently this is dbusinterface
        
        @param   core:    Core, where profiles are handled
        @type    core:    L{dbusinterface}
        """
        self.core = core
        
    def keycode(self, mapping, keycode):
        """
        The method maps the incoming keycode and mapping to the associated
        command and spawns a subprocess for them.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        int
        @param  keycode:        keycode received
        @type   keycode:        int
        """
        self.logger.debug("keycode called")
        event_tuple = (keycode, mapping)
        if event_tuple in self.actions:
            for command in self.actions[event_tuple]:
                command.call()
        self.logger.debug("keycode finished")

    def set_profile(self, config, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        self.logger.debug("set_profile called")
        for command in self.destruct:
            command.call()
        self._interpret_profile(config, profile)
        for command in self.init:
            command.call()
        self.logger.debug("set_profile finished")
    
    def connection_closed(self):
        self.logger.debug("connection closed - running destruct actions")
        for command in self.destruct:
            command.call()
    
    def connection_established(self):
        self.logger.debug("connection established - running init actions")
        for command in self.init:
            command.call()
    
    def shutdown(self):
        pass