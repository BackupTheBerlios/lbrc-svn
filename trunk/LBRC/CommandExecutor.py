from LBRC.Listener import Listener
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

class CommandExecutor(Listener):
    def __init__(self, config):
        Listener.__init__(self, config, "CommandExecutor", command_class=Command);
                                
    def shutdown(self):
        for command in self.destruct:
            command.call()