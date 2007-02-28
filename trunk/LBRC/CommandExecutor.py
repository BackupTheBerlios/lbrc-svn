#!/usr/bin/python

import gobject

class CommandExecutor(object):
    def __init__(self, config, profiledata):
        self.config = config
        self.profiledata = profiledata
        self.profile = None
        self.__interpret_profiles()

    def keycode(self, mapping, keycode):
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
        self.profile = profile

    def switch_profile(self):
        return 1

    def __interpret_profiles(self):
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
