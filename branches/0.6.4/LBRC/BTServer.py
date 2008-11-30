"""BTServer module holds classes to handle bluetooth connections for LBRC"""
# -*- coding: UTF-8 -*-
#
# TODO: react to config changes (currently the configs are checked on demand, 
#       so no problem - currently!)
#
# Not sure whether it's a problem in the gobject bindings or
# a false positive, but never the less descendants of gobject.GObject
# have the methods warned as missing by E1101
# pylint: disable-msg=E1101  

__extra_epydoc_fields__ = [('signal', 'Signal', 'Signals')]

from LBRC import dinterface
from LBRC.config import config
import pygtk
pygtk.require("2.0")
import bluetooth
import LBRC.json as json
import logging
import gobject
import dbus
import dbus.glib
        
class BTConnection(gobject.GObject):
    """
    Class to handle a concrete bluetooth connection

    @signal: keycode: (mapping, keycode)

        The signal is fired when a data package is received. The package is
        decoded and the mapping and keycode is extracted. Mapping refers to the
        press state (0 => pressed, 1 => released), the keycode is defined by
        the phone (or a JSR)

    """
    __gsignals__ = {
        'keycode': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                                    (gobject.TYPE_INT, gobject.TYPE_INT64,)),
    }
    def __init__(self, client_sock):
        gobject.GObject.__init__(self)
        self.logger = logging.getLogger('LBRC.BTConnection')
        self.handler = {}
        self.handler['list'] = None
        self.buffer = ""
        self.client_sock = client_sock
        self.client_io_watch = gobject.io_add_watch(
                                           self.client_sock,
                                           gobject.IO_IN, 
                                           self.cb_handle_incoming_data)
        
    def _handle_buffer(self):
        """Analyse buffer of received data and act accordingly"""
        packets = self.buffer.split('\x00')
        # The last packet is either empty (if the last packet was completely 
        # send or we only see a partital package, that we feed back into the 
        # buffer
        self.buffer = packets.pop()
        for packet in packets:
            data = json.read(packet)
            if (data['type'] == "keyCode"):
                mapping = data["mapping"]
                keycode = data["keycode"]
                self.emit('keycode', mapping, keycode)
            elif (data['type'] == "listReply" and self.handler['list']):
                handler = self.handler['list']
                self.handler['list'] = None
                handler(data['selectionIndex'])
            elif (data['type'] == 'debugMessage'):
                self.logger.debug("PHONE (%(function)s): %(message)s" % data )
            else:
                self.logger.debug("Unmatched package: " + str(data))

    def send_list_query(self, title, list_input, callback):
        """Prepare a query to the mobile, that contains a list from which
        the user has to select one entry"""
        package = {}
        package['type'] = "listQuery"
        package['title'] = title
        package['list'] = list_input
        self.send_query(package)
        self.handler['list'] = callback
        
    def send_query(self, package):
        """Send query to phone serialized as json data"""
        self.logger.debug("Sending package:" + str(package))
        message = (json.write(package) + u"\u0000").encode('utf-8')
        self.logger.debug(repr(message))
        try:
            self.client_sock.sendall(message)
        except bluetooth.BluetoothError:
            self.logger.debug(
                            "Trying to send while remote side was disconnected")
        self.logger.debug("Package send done")

    def cb_handle_incoming_data(self, clientsocket, condition):
        """
        Handle incoming data from the client. The data is coded as json objects,
        that are terminated by the NUL char. For the connection we assume a
        UTF-8 transfer encoding.

        With this data the keycode signal is fired, with the mapping as first
        and the keycode as second parameter.

        @type   self:           BTServer
        @param  self:           The BTServer object responsible for handling the connection
        @type   clientsocket:   bluetooth.BluetoothSocket
        @param  clientsocket:   The clientside part of the connection
        @type   condition:      integer (gobject.Enum)
        @param  condition:      The condition of the clientsocket which caused the handler to be called
                                should always be gobject.IO_IN (=1)
        @rtype:         bool
        @return:        always True, as we keep listening on the socket until the connection is shutdown
        """
        self.buffer += clientsocket.recv(1024)
        self.logger.debug("In Buffer: " + repr(self.buffer))
        self._handle_buffer()
        return True
    
    def shutdown(self):
        """Run on shutdown to clear the connection"""
        gobject.source_remove( self.client_io_watch )

class BTServer(gobject.GObject):
    """
    Class to handle communication with a client on a bluetooth phone.

    @signal: keycode: (mapping, keycode)

        The signal is fired when a data package is received. The package is
        decoded and the mapping and keycode is extracted. Mapping refers to the
        press state (0 => pressed, 1 => released), the keycode is defined by
        the phone (or a JSR)
        
        This is a convenience signal, that acts as a relay to the keycode
        signal from the unterlying L{BTConnection}

    @signal: connect: (bluetoothaddress, port)

        The signal is fired on connection from a device. The bluetooth address
        and the connected port are carried as port.

    @signal: disconnect: (bluetoothaddress, port)

        The signal is fired on disconnection from a device. See "connect".

    @signal: connectable_event: (connectable_state)

        The signal is fired on change of connectable settings.  The new state
        is passed as parameter.

    @signal: updated_filter

        The signal is fired when changes to the filter are done
    """
    __gsignals__ = {
        'keycode': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                                    (gobject.TYPE_INT, gobject.TYPE_INT64,)),
        'connect': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                                    (gobject.TYPE_STRING, gobject.TYPE_INT)),
        'disconnect': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                    (gobject.TYPE_STRING, gobject.TYPE_INT)),
        'connectable_event': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                    (gobject.TYPE_STRING,)),
        'updated_filter': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }
    __gproperties__ = {
        'connectable': (gobject.TYPE_STRING, 
                        'connectable settings',
                        'connectable settings: no, yes, filtered',
                        "yes",gobject.PARAM_READWRITE)
    }

    def do_get_property(self, property_param):
        """Property getter"""
        if property_param.name == 'connectable':
            return self.connectable
        else:
            raise AttributeError, 'unknown property %s' % property_param.name

    def do_set_property(self, property_param, value):
        """Property setter"""
        if property_param.name == 'connectable':
            if value in ("no", "yes", "filtered"):
                self.connectable = value
                self._switch_connectable()
            else:
                raise AttributeError, 'illegal value for property connectable'+\
                                      ' (allowed: no, yes, filtered): %s'\
                                      % value
        else:
            raise AttributeError, 'unknown property %s' % property_param.name

    def __init__(self, name = "LBRC", 
                       serverid = "9c6c8dce-9545-11dc-a3c1-0011d8388a56"):
        """
        @param  serverid:   ID associated to the service we announce
        @type   serverid:   string (hexadecimal)
        @param  name:      The name used to announce the service via bluetooth
        @type   name:      string
        @rtype:     BTServer object
        @return:    BTServer object
        """
        gobject.GObject.__init__(self)
        self.logger = logging.getLogger('LBRC.BTServer')
        self.name = name
        self.serverid = serverid
        self.connectable = 'yes'
        self.filter = {}
        
        self.connected = None
        self.bluetooth_connection = None
        self.bluetooth_keycode = None
        self.config = config()
        self.paired_by_us = {}

        self.client_sock = None
        self.server_sock = None

        self.server_io_watch = None

        self.server_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.port = self.server_sock.getsockname()[1] # get listening port
        self.server_sock.listen(1)
        
        self.advertise_id = None

        self._register_bluez_signals()
        self._switch_connectable()

    def _advertise_service(self, state=False):
        """Advertise service via SDP"""
        if not state and self.advertise_id:
            if(type(self.advertise_id) != type({})):
                bluez_db = dinterface(dbus.SystemBus(), 'org.bluez', '/org/bluez', 'org.bluez.Database')
                self.advertise_id = bluez_db.AddServiceRecordFromXML(service_record)
            else:
                self.logger.debug("Entered new codepath for new bluez api")
                manager = dinterface( dbus.SystemBus(), 'org.bluez', '/org/bluez', 'org.bluez.Manager')
                active_connectors = manager.ListAdapters();
                for connector_object in self.advertise_id:
                    if not connector_object in active_connectors:
                        continue
                    connector_interface = dinterface( dbus.SystemBus(), 
                                                      'org.bluez', 
                                                      connector_object,
                                                      'org.bluez.Service')
                    connector_interface.RemoveRecord(self.advertise_id[connector_object]);
            self.advertise_id = None;
        elif state and not self.advertise_id:
            service_record = \
"""
<?xml version="1.0" encoding="UTF-8" ?>
<record>
        <attribute id="0x0001">
             <uuid value="%(serviceid)s" />
        </attribute>
        <attribute id="0x0004">
                <sequence>
                        <sequence>
                                <uuid value="0x0100" />
                        </sequence>
                        <sequence>
                                <uuid value="0x0003" />
                                <uint8 value="%(channel)i" />
                        </sequence>
                </sequence>
        </attribute>
        <attribute id="0x0100">
            <text value="%(name)s" name="name"/>
        </attribute>
</record>
""" % {'serviceid': self.serverid, 
       'name': self.name, 
       'channel': int(self.port) }
            self.logger.debug('Trying to register service: %s' % service_record)
            try:
                bluez_db = dinterface(dbus.SystemBus(), 'org.bluez', '/org/bluez', 'org.bluez.Database')
                self.advertise_id = bluez_db.AddServiceRecordFromXML(service_record)
            except dbus.exceptions.DBusException:
                self.advertise_id = {};
                self.logger.debug("Entered new codepath for new bluez api")
                manager = dinterface( dbus.SystemBus(), 'org.bluez', '/org/bluez', 'org.bluez.Manager')
                for connector_object in manager.ListAdapters():
                    connector_interface = dinterface( dbus.SystemBus(), 
                                                      'org.bluez', 
                                                      connector_object,
                                                      'org.bluez.Service')
                    self.advertise_id[connector_object] = connector_interface.AddRecord(service_record);

    def _switch_connectable(self):
        """Update state according to the settings
        (connectable, filtered, none)"""
        if (self.connectable == 'yes' or self.connectable == 'filtered') and \
           not self.server_io_watch:
            self.server_io_watch = gobject.io_add_watch(
                                                self.server_sock, 
                                                gobject.IO_IN, 
                                                self.cb_handle_connection)
            if BTServer.is_bluez_up():
                self._advertise_service(True)
        elif self.connectable == 'no' and not self.connected:
            if BTServer.is_bluez_up():
                self._advertise_service(False)
            gobject.source_remove(self.server_io_watch)
            self.server_io_watch = None
        self.emit('connectable_event', self.connectable)

    def clear_allowed(self):
        """
        Clear the filter for allowed devices
        """
        self.filter = {}
        self.emit('updated_filter')

    def remove_allowed(self, address):
        """
        Remove C{address} from filter (allowed devices list)

        @type   address:    string
        @param  address:    Address to be removed from filter
        """
        if address in self.filter:
            del self.filter[address]
        self.emit('updated_filter')

    def set_allowed(self, address_list):
        """
        Replace existing filter with the string array provided in C{filter}

        @type   filter:     string array
        @param  filter:     List of addresses allowed to connect
        """
        self.filter = {}
        for address in address_list:
            self.filter[address] = 1
        self.emit('updated_filter')

    def add_allowed(self, address):
        """
        Add address C{address} to the list of allowed devices

        @type   address:    string
        @param  address:    address of device to allow access (string format: xx:xx:xx:xx:xx:xx)
        """
        self.filter[address] = 1
        self.emit('updated_filter')

    def get_allowed(self):
        """
        Returns bluetooth addresses currently allowed to connect

        @rtype:     string array
        @return:    bluetooth addresses allowed to connect
        """
        return self.filter.keys()

    def shutdown(self):
        """
        Called on shutdown

        We tear down the bluetooth connection and disconnect from it,
        if we were connected.
        """
        if self.bluetooth_keycode:
            self.bluetooth_connection.disconnect(self.bluetooth_keycode)
            self.bluetooth_keycode = None
            self.bluetooth_connection.shutdown()

    def cb_handle_disconnection(self, serversocket, condition):
        """
        Handles the shutdown of connections. When the serversocket signals the
        HUP condition.  The handler disconnects from the mainloop by returning
        false.

        This method is called when the connection was shutdown from the
        other side of the connection. The data handler (L{cb_handle_incoming_data})
        for incoming data is disconnected and the disconnect signal is fired. 
        
        If we are in connectable or filtered mode, we will reattach the
        serversocket watch for gtk.IO_IN with L{cb_handle_connection}) as handler.

        @type   self:           BTServer
        @param  self:           The BTServer object responsible for handling the connection
        @type   serversocket:   bluetooth.BluetoothSocket
        @param  serversocket:   A bluetooth socket responsible for handling incoming connections (server side)
        @type   condition:      integer (gobject.Enum)
        @param  condition:      The condition of the serversocket which caused the handler to be called
                                should always be gobject.IO_HUP (=16)
        @rtype:         bool
        @return:        always False, as we only allow one concurrent connection
        """
        self.logger.debug('BTServer: %s disconnected' % (self.connected[0],))
        if self.bluetooth_keycode:
            self.bluetooth_connection.disconnect(self.bluetooth_keycode)
            self.bluetooth_keycode = None
            self.bluetooth_connection.shutdown()
        self.server_io_watch = None
        self.client_sock = None
        if self.connected[0] in self.paired_by_us:
            self.logger.debug('BTServer: We paired this device')
            if self.config.get_config_item_fb("remove-pairing", False):
                self.logger.debug(
                            'BTServer: We remove the pairing for this device')
                self.paired_by_us[self.connected[0]].RemoveBonding(
                            self.connected[0])
            del self.paired_by_us[self.connected[0]]
        self.emit("disconnect", self.connected[0], self.connected[1])
        self.connected = None
        if self.connectable == 'yes' or self.connectable == 'filtered':
            self.server_io_watch = gobject.io_add_watch(
                                                self.server_sock, 
                                                gobject.IO_IN, 
                                                self.cb_handle_connection)
            self._advertise_service(True)
        return False

    def cb_handle_connection(self, serversocket, condition):
        """
        Handles incoming connections. The handler disconnects from the mainloop
        by returning false. 
        
        The function checks whether we are in connectable or filtered mode.
        
        If we are in connectable mode or the remote device is allowed to
        connect, when in filter mode, a client connection is established, the
        corresponding signal is fired, the disconnect handler
        (L{cb_handle_disconnection}) coupled to the serversocket and the client
        handler coupled to the client socket (L{cb_handle_incoming_data}).

        When we are in not-connectable mode or the device is not allowed to
        connect in filtered mode, we close the client socket. If we are in
        filtered mode we reattach this  watch to the mainloop and advertise our
        socket.

        @type   self:           BTServer
        @param  self:           The BTServer object responsible for handling 
                                the connection
        @type   serversocket:   bluetooth.BluetoothSocket
        @param  serversocket:   A bluetooth socket responsible for handling 
                                incoming connections
        @type   condition:      integer (gobject.Enum)
        @param  condition:      The condition of the serversocket which caused
                                the handler to be called
                                should always be gobject.IO_IN (=1)
        @rtype:         bool
        @return:        always False, as we only allow one concurrent connection
        """
        self._advertise_service(False)

        self.client_sock, client_address = self.server_sock.accept()        
        self.logger.debug("Serversocket: %s" % 
                          str(self.server_sock.getsockname()))

        if ( self._check_pairing(client_address) and
            (self.connectable == 'yes' or 
            (self.connectable == 'filtered' and 
             client_address[0] in self.filter))):

            self.connected = client_address

            self.bluetooth_connection = BTConnection(self.client_sock)
            self.bluetooth_keycode = self.bluetooth_connection.connect(
                            "keycode", 
                            lambda btc, mp, kc: self.emit("keycode", mp, kc))
            
            self.server_io_watch = gobject.io_add_watch(
                                                 self.client_sock,
                                                 gobject.IO_HUP,
                                                 self.cb_handle_disconnection)
            self.emit("connect", client_address[0], client_address[1])
        else:
            self.logger.debug("Closing remote connection")
            self.client_sock.close()
            self.client_sock = None
            if self.connectable == 'filtered':
                self.server_io_watch = gobject.io_add_watch(
                                                 self.server_sock,
                                                 gobject.IO_IN, 
                                                 self.cb_handle_connection)
                self._advertise_service(True)
        return False

    def _check_pairing(self, client_address):
        """
        Check whether we need to be paired before allowing a connection.
        
        If one is needed and we are not bonded yet, we initiate a pairing
        request.

        @type   self:           BTServer
        @param  self:           The BTServer object responsible for handling 
                                the connection
        @type   client_address: Tuple
        @param  client_address: Client address 
                                incoming connections

        """
        if not self.config.get_config_item_fb("require-pairing", True):
            self.logger.debug('Pairing not required')
            return True
        self.logger.debug('Check for pairing')
        manager = dinterface( dbus.SystemBus(),
                              'org.bluez',
                              '/',
                              'org.bluez.Manager')
        adapters = manager.ListAdapters()
        paired = False
        for adapter in adapters:
            adapter = dinterface(dbus.SystemBus(), 
                                 'org.bluez', 
                                 adapter, 
                                 'org.bluez.Adapter')
            if adapter.HasBonding(client_address[0]):
                paired = True
                break
            
        if not paired:
            self.logger.debug('We see a new device, that was not yet ' + 
                              'allowed to connect. Beginning pairing!')
            self.logger.debug('Search for adapter, that reaches the phone')
            for adapter in adapters:
                adapter = dinterface(dbus.SystemBus(), 
                                     'org.bluez', 
                                     adapter, 
                                     'org.bluez.Adapter')
                # We asume that an adapter that can resolve the name is the 
                # "right" adapter
                try:
                    name = adapter.GetRemoteName(client_address[0])
                    self.logger.debug('Got name %s - will try to create bonding'
                                       % name)
                    adapter.CreateBonding(client_address[0])
                    self.logger.debug('Bonding returned')
                    if adapter.HasBonding(client_address[0]):
                        self.logger.debug('Bonding successfull')
                        paired = True
                        self.paired_by_us[client_address[0]] = adapter
                    else:
                        self.logger.debug('Bonding failed')
                    break
                except dbus.exceptions.DBusException:
                    self.logger.debug('Exception in BondingCreation' +
                                      ' (DBUS Methods)')
        return paired

    def _register_bluez_signals(self):
        """Register the dbus signals from dbus to register the addition and
        removal of bluetooth adapters"""
        if not BTServer.is_bluez_up():
            return
        manager = dinterface(dbus.SystemBus(), 'org.bluez', '/', 'org.bluez.Manager')
        manager.connect_to_signal("AdapterAdded", self.cb_adapter_added)
        #manager.connect_to_signal("AdapterRemoved", self.cb_adapter_removed)

    def cb_adapter_added(self, adapter):
        """An adapter was added - so start advertising our service on it"""
        self._switch_connectable()

    def get_bt_connection(self):
        """Retrieve Bluetooth Connection"""
        return self.bluetooth_connection

    @staticmethod
    def is_bluez_up():
        """
        Verify if the bluetooth service is up
 
        @rtype:     bool
        @return:    True if bluez if bluez is up, False otherwise
        """
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.bluez.Manager')
        try:
            manager.ListAdapters()
            return True
        except dbus.dbus_bindings.DBusException:
            return False

def stand_alone_test():
    """Do some standalone testing (necessary to check BTServer"""
    def print_args(*args):
        """Print function suitable for use in lambda/callbacks"""
        print args
    btserver = BTServer()
    btserver.connect("keycode", print_args, 'keycode')
    btserver.connect("connect", print_args, 'connect')
    btserver.connect("disconnect", print_args, 'disconnect')
    
    print "You entered Testmode, when you fire up LBRC on your device"
    print "you will see the events (connect, disconnect, keycode), "
    print "your device generates."
    print
    print "To stop, press STRG-C"
    print
    mainloop = gobject.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()

    print
    print "Switching to filtered mode! Allowed: 00:13:FD:93:B1:1B"
    print "To stop, press STRG-C"
    print
    btserver.set_property("connectable", "filtered")
    btserver.add_allowed("00:13:FD:93:B1:1B")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()

    print
    print "Switching to not connectable mode!"
    print "To stop, press STRG-C"
    print
    btserver.set_property("connectable", "no")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()

    print
    print "Switching to connectable mode!"
    print "To stop, press STRG-C"
    print
    btserver.set_property("connectable", "yes")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()

if __name__ == "__main__":
    stand_alone_test()
