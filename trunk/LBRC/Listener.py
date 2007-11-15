import logging

class UndefinedCommandClass(Exception):
    """Raised, if the default _interpret_profile of Listener is used, but no
    command_class ist supplied"""

class Listener(object):
    def __init__(self, config, name, **kwargs):
        logging.debug(name + ": __init__ begin")
        self.config = config
        self.name = name
        if 'command_class' in kwargs:
            self.command_class = kwargs['command_class']
        else:
            self.command_class = None
        self.bluetooth_connector = None
        self.core = None
        self.init = []
        self.actions = {}
        self.destruct = []
        logging.debug(name + ": __init__ done")
        
    def _interpret_profile(self, config, profile):
        """
        Interpret the profile data from the profile.conf(s) and push the commands into
        an array and call it, when the appropriate keycodes and mappings are received.

        If no mapping is provided, we assume mapping = 0 => keypress
        """
        logging.debug(self.name + ": _interpret_profile called")
        if not self.command_class:
            raise UndefinedCommandClass()
        self.init = []
        self.actions = {}
        self.destruct = []
        try:
            for init in self.config.get_profile(config, profile, self.name)['init']:
                self.init.append(self.command_class(self, init))
        except:
            logging.debug(self.name + ": failure while interprating init")
            
        try:
            for destruct in self.config.get_profile(config, profile, self.name)['destruct']:
                self.destruct.append(self.command_class(self, destruct))
        except:
            logging.debug(self.name + ": failure while interprating destruct")
       
        try:
            for action in self.config.get_profile(config, profile, self.name)['actions']:
                try:
                    mapping = int(action['mapping'])
                except:
                    mapping = 0
                event_tuple = (int(action['keycode']), mapping)
                if not event_tuple in self.actions:
                    self.actions[event_tuple] = []
                self.actions[event_tuple].append(self.command_class(self, action))
        except:
            logging.debug(self.name + ": failure while interprating actions")
        logging.debug(self.name + ": _interpret_profile finished")
        
    def set_bluetooth_connector(self, bc):
        """
        Set our bluetooth connector, that allows us to issue the presentation
        of a list, from which the user can choose the new profile
        
        @param    bc:    Bluetooth Adapter
        @type     bc:    L{BTServer}
        """
        self.bluetooth_connector = bc        

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
        logging.debug(self.name + ": keycode called")
        event_tuple = (keycode, mapping)
        if event_tuple in self.actions:
            for command in self.actions[event_tuple]:
                command.call()
        logging.debug(self.name + ": set_profile finished")

    def set_profile(self, config, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        logging.debug(self.name + ": set_profile called")
        for command in self.destruct:
            command.call()
        self._interpret_profile(config, profile)
        for command in self.init:
            command.call()
        logging.debug(self.name + ": set_profile finished")
                
    def shutdown(self):
        pass