from LBRC.Listener import Listener
import logging
import gobject

class Command(object):
    """
    Command class for the CommandExecutorModule
    """
    def __init__(self, parent, description):
        self.parent = parent
        self.logger = logging.getLogger("LBRC.Listener.CommandExecutor")
        self.description = description

    def _to_array(self):
        """
        The commandline arguments are linearized (other implementations could
        need them seperately, so we keep the format)
        """
        command_line = []
        command_line.append(self.description['command']) 
        if 'arguments' in self.description:
            command_line.extend([str(arg) for arg in self.description['arguments']])
        return command_line
    
    def call(self):
        """
        Execute the supplied command by spawning a subprozess
        """
        self.logger.debug("Calling: " + str(self._to_array()))
        gobject.spawn_async( self._to_array(), 
                             flags= gobject.SPAWN_STDOUT_TO_DEV_NULL | 
                                    gobject.SPAWN_STDERR_TO_DEV_NULL )

class CommandExecutor(Listener):
    """
    CommandExecutor class provides a mechanism to call external programms
    """
    def __init__(self, config):
        Listener.__init__(self,
                          config, 
                          "CommandExecutor", 
                          command_class=Command)