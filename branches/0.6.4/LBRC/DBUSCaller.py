from LBRC.Listener import Listener
from LBRC import dinterface
import dbus
from dbus.exceptions import DBusException
import logging

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
    
    def __init__(self, parent, action):
        self.logger = logging.getLogger('LBRC.Listener.DBUSCall')
        self.parent = parent
        self.service = action['service']
        self.object = action['object']
        self.interface = action['interface']
        self.method = action['method']
        self.arguments = []
        if 'arguments' in action:
            for i in action['arguments']:
                sep = i.find(":")
                arg_type = i[:sep]
                argument = i[(sep+1):]
                self.arguments.append(self._translator[arg_type](argument))
        try:
            if 'bus' in action and action['bus'] == 'system':
                self.bus = dbus.SystemBus()
            else:
                self.bus = dbus.SessionBus()
        except DBusException:
            self.bus = None
                
    def call(self):
        if(self.bus):
            self.logger.debug(str((self.bus, self.service, self.object, self.interface)))
            iface = dinterface(self.bus, self.service, self.object, self.interface)
            # This is intendet (black magic, but has to be called this way!): 
            # pylint: disable-msg=W0142
            iface.__getattr__(self.method).__call__(*self.arguments)
            # pylint: enable-msg=W0142

class DBUSCaller(Listener):
    """
    Class to handle keycodes received by BTServer and issue DBUS Calls
    according to them
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         L{LBRC.config}
        """
        Listener.__init__(self, config, 'DBUSCaller', command_class=DBUSCall)
        
        self.logger.debug("Loaded succesfully")
