#!/usr/bin/python

import pygtk
pygtk.require("2.0")
import bluetooth,os,math,gobject,re

bt_address = re.compile("\('([A-Fa-f0-9:]+)', ([0-9]+)\)")

class BTServer(gobject.GObject):
    """
    Class to handle communication with a client on a Bluetooth Phone.

    These signals are available:
    - keycode: (mapping, keycode)
        The signal is fired when a data package is recieved. The package is
        decoded and the mapping and keycode is extracted. Mapping refers to the
        press state (0 => pressed, 1 => released), the keycode is defined by
        the phone (or a JSR)
    - connect: (bluetoothaddress, port)
        The signal is fired on connection from a device. The bluetooth address
        and the connected port are carried as port.
    - disconnect: (bluetoothaddress, port)
        The signal is fired on disconnection from a device. See "connect".
    - connectable_event: (connectable_state)
        The signal is fired on change of connectable settings.  The new state
        is passed as parameter.
    - updated_filter
        The signal is fired when changes to the filter are done
    """
    __gsignals__ = {
        'keycode': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT64,)),
        'connect': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT)),
        'disconnect': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT)),
        'connectable_event': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
        'updated_filter': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }
    __gproperties__ = {
        'connectable': (gobject.TYPE_STRING, 
                        'connectable settings',
                        'connectable settings: no, yes, filtered',
                        "yes",gobject.PARAM_READWRITE)
    }

    def do_get_property(self, property):
        if property.name == 'connectable':
            return self.connectable
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def do_set_property(self, property, value):
        if property.name == 'connectable':
            if value in ("no", "yes", "filtered"):
                self.connectable = value
                self.__switch_connectable()
            else:
                raise AttributeError, 'illegal value for property connectable (allowed: no, yes, filtered): %s' % value
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def __switch_connectable(self):
        if (self.connectable == 'yes' or self.connectable == 'filtered') and not self.server_io_watch:
            self.server_io_watch = gobject.io_add_watch(self.server_sock, gobject.IO_IN, self.handle_connection)
            bluetooth.advertise_service(self.server_sock, self.name, self.serverid)
        elif self.connectable == 'no' and not self.connected:
            bluetooth.stop_advertising(self.server_sock)
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
        try:
            del self.filter[address]
        except KeyError:
            pass
        self.emit('updated_filter')

    def set_allowed(self, filter):
        """
        Replace existing filter with the string array provided in C{filter}

        @type   filter:     string array
        @param  filter:     List of addresses allowed to connect
        """
        for address in filter:
            self.add_allowed(address)
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
        @return:    Bluetooth Adresses allowed to connect
        """
        return self.filter.keys()
        self.emit('updated_filter')

    def __init__(self, name = "LBRC", serverid = "a1e7"):
        gobject.GObject.__init__(self)
        self.name = name
        self.serverid = serverid
        self.connectable = 'yes'
        self.filter = {}
        self.port = bluetooth.get_available_port( bluetooth.L2CAP)
        self.connected = None

        self.client_sock = None
        self.server_sock = None

        self.client_io_watch = None
        self.server_io_watch = None

        self.server_sock = bluetooth.BluetoothSocket( bluetooth.L2CAP )
        self.server_sock.bind(("", self.port))
        self.server_sock.listen(1)

        self.__switch_connectable()

    def shutdown(self):
        pass

    def handle_incoming_data(self, clientsocket, condition):
        """
        Handle incoming data from the client. We assume a 5 byte payload. This consists
        of one byte providing a X{mapping} (key pressed=>0, key released=>1) and the rest
        encoding an integer (4 byte). This bytestring is passed to L{byte_array_to_int},
        which decodes the bytestring to the original integer X{keycode}.

        With this data the keycode signal is fired, with the mapping as first
        and the keycode as seconde parameter.

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
        data = clientsocket.recv(5)
        if data:
            mapping = ord(data[0])
            keycode = self.byte_array_to_int(data[1:5])
            self.emit('keycode', int(mapping), int(keycode))
        return True

    def handle_disconnection(self, serversocket, condition):
        """
        Handles the shutdown of connections. When the serversocket signals the
        HUP condition.  The handler disconnects from the mainloop by returning
        false.

        This method is called when the connection was shutdown from the
        otherside of the connection. The data handler (L{handle_incoming_data})
        for incoming data is disconnected and the disconnect signal is fired. 
        
        If we are in connectable or filtered mode, we will reattach the
        serversocket watch for gtk.IO_IN with L{handle_connection}) as handler.

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
        gobject.source_remove(self.client_io_watch)
        self.server_io_watch = None
        self.client_io_watch = None
        self.client_sock = None
        self.emit("disconnect", self.connected[0], self.connected[1])
        self.connected = None
        if self.connectable == 'yes' or self.connectable == 'filtered':
            self.server_io_watch = gobject.io_add_watch(self.server_sock, gobject.IO_IN, self.handle_connection)
            bluetooth.advertise_service(self.server_sock, self.name, self.serverid)
        return False

    def handle_connection(self, serversocket, condition):
        """
        Handles incoming connections. The handler disconnects from the mainloop
        by returning false. 
        
        The function checks whether we are in connectable or filtered mode.
        
        If we are in connectable mode or the remote device is allowed to
        connect, when in filter mode, a client connection is established, the
        corresponding signal is fired, the disconnect handler
        (L{handle_disconnection}) coupled to the serversocket and the client
        handler coupled to the client socket (L{handle_incoming_data}).

        When we are in not-connectable mode or the device is not allowed to
        connect in filtered mode, we close the client socket. If we are in
        filtered mode we reattach this  watch to the mainloop and advertise our
        socket.

        @type   self:           BTServer
        @param  self:           The BTServer object responsible for handling the connection
        @type   serversocket:   bluetooth.BluetoothSocket
        @param  serversocket:   A bluetooth socket responsible for handling incoming connections
        @type   condition:      integer (gobject.Enum)
        @param  condition:      The condition of the serversocket which caused the handler to be called
                                should always be gobject.IO_IN (=1)
        @rtype:         bool
        @return:        always False, as we only allow one concurrent connection
        """
        bluetooth.stop_advertising(self.server_sock)

        self.client_sock,client_address = self.server_sock.accept()

        if ( self.connectable == 'yes' or 
            (self.connectable == 'filtered' and client_address[0] in self.filter)):

            self.connected = client_address
            self.emit("connect", client_address[0], client_address[1])

            self.client_io_watch = gobject.io_add_watch(self.client_sock, gobject.IO_IN, self.handle_incoming_data)
            self.server_io_watch = gobject.io_add_watch(self.client_sock, gobject.IO_HUP, self.handle_disconnection)
        else:
            self.client_sock.close()
            self.client_sock = None
            self.server_io_watch = gobject.io_add_watch(self.server_sock, gobject.IO_IN, self.handle_connection)
            bluetooth.advertise_service(self.server_sock, self.name, self.serverid)
            
        return False

    @staticmethod
    def byte_array_to_int(bytes):
        """
        Convert byte array to int, assuming most significant byte first

        @type   bytes:  bytestring
        @param  bytes:  bytestring interpreted as a bytearray representing an integervalue
        @rtype:         integer
        @return:        Interger value of the bytearray supplied
        """
        exponent = len(bytes) - 1;
        result = 0
        for i in range(len(bytes)):
            factor =  int(math.pow(2, (exponent - i) * 8 ))
            result += ord(bytes[i]) * factor
        return result

if __name__ == '__main__':
    def print_args(*args):
        print args

    import gobject
    bt = BTServer()
    bt.connect("keycode", print_args, 'keycode')
    bt.connect("connect", print_args, 'connect')
    bt.connect("disconnect", print_args, 'disconnect')
    
    print "You entered Testmode, when you fireup LBRC on your device"
    print "you will see the events (connect, disconnect, keycode), "
    print "your device generates."
    print
    print "To stop, press STRG-C"
    print
    m = gobject.MainLoop()
    try:
        m.run()
    except KeyboardInterrupt:
        m.quit()

    print
    print "Switching to filtered mode! Allowed: 00:13:FD:93:B1:1B"
    print "To stop, press STRG-C"
    print
    bt.set_property("connectable", "filtered")
    bt.add_allowed("00:13:FD:93:B1:1B")
    try:
        m.run()
    except KeyboardInterrupt:
        m.quit()

    print
    print "Switching to not connectable mode!"
    print "To stop, press STRG-C"
    print
    bt.set_property("connectable", "no")
    try:
        m.run()
    except KeyboardInterrupt:
        m.quit()

    print
    print "Switching to connectable mode!"
    print "To stop, press STRG-C"
    print
    bt.set_property("connectable", "yes")
    try:
        m.run()
    except KeyboardInterrupt:
        m.quit()
