from LBRC.Listener import Listener
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
    def __init__(self, parent, action):
        self.logger = logging.getLogger('LBRC.Listener.DBUSCall')
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
        self.logger.debug(str((self.bus, self.service, self.object, self.interface)))
        iface = dinterface(self.bus, self.service, self.object, self.interface)
        iface.__getattr__(self.method).__call__(*self.arguments)

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