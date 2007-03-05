#!/usr/bin/python

import gobject

class CommandExecutor(object):
    """
    Class to handle keycodes received by BTServer and issue commands according to them
    """
    def __init__(self, config, profiledata):
        """
        @param  config:         configuration data
        @type   config:         dictionary
        @param  profiledata:    profile data
        @type   profiledata:    dictionary
        """
        self.config = config
        self.profiledata = profiledata
        self.profile = None
        self._interpret_profiles()

    def keycode(self, mapping, keycode):
        """
        The method maps the incoming keycode and mapping to the associated
        command and spawns a subprocess for them.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        int
        @param  keycode:        keycode received
        @type:  keycode:        int
        """
        event_tuple = (keycode, mapping)
        if event_tuple in self.profiles[self.profile]:
            for command in self.profiles[self.profile][event_tuple]:
                command_line = []
                command_line.append(command['command'])
                command_line.extend(command['argv'])
                gobject.spawn_async( command_line, 
                                     flags= gobject.SPAWN_STDOUT_TO_DEV_NULL | 
                                            gobject.SPAWN_STDERR_TO_DEV_NULL )

    
    def set_profile(self, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        self.profile = profile

    def _interpret_profiles(self):
        """
        Interpret the profile data from the profile.conf(s) and push the commands into
        an array and call it, when the appropriate keycodes and mappings are received.

        If no mapping is provided, we assume mapping = 0 => keypress
        """
        self.profiles = {}
        for profile_file in self.profiledata:
            for profile in profile_file.keys():
                pd = profile_file[profile]
                commands = {}
                if not 'commands' in pd:
                    pd['commands'] = {}
                for command in pd['commands']:
                    try:
                        mapping = int(command['mapping'])
                    except:
                        mapping = 0
                    event_tuple = (int(command['keycode']), mapping)
                    if not event_tuple in commands:
                        commands[event_tuple] = []
                    new_command = {}
                    new_command['command'] = command['command']
                    new_command['argv'] = command['argv']
                    commands[event_tuple].append(new_command)
                self.profiles[profile] = commands
