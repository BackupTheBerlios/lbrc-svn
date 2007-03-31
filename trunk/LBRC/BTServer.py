#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# TODO: maybe rework connection handling (create a separate class for the connection?!)
# TODO: react to config changes (currently the configs are checked on demand, so no problem - currently!)

__extra_epydoc_fields__ = [('signal', 'Signal', 'Signals')]

from LBRC import dinterface
from LBRC.config import config
import pygtk
pygtk.require("2.0")
import bluetooth
import json
import os
import math
import re
import logging
import gobject
import dbus
import dbus.glib

class BTServer(gobject.GObject):
    """
    Class to handle communication with a client on a bluetooth phone.

    @signal: keycode: (mapping, keycode)

        The signal is fired when a data package is received. The package is
        decoded and the mapping and keycode is extracted. Mapping refers to the
        press state (0 => pressed, 1 => released), the keycode is defined by
        the phone (or a JSR)

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
                self._switch_connectable()
            else:
                raise AttributeError, 'illegal value for property connectable (allowed: no, yes, filtered): %s' % value
        else:
            raise AttributeError, 'unknown property %s' % property.name

    def _switch_connectable(self):
        if (self.connectable == 'yes' or self.connectable == 'filtered') and not self.server_io_watch:
            self.server_io_watch = gobject.io_add_watch(self.server_sock, gobject.IO_IN, self.handle_connection)
            if BTServer.is_bluez_up():
                bluetooth.advertise_service(self.server_sock, self.name, self.serverid)
        elif self.connectable == 'no' and not self.connected:
            if BTServer.is_bluez_up():
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
        self.filter = {}
        for address in filter:
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

    def __init__(self, name = "LBRC", serverid = "a1e7"):
        """
        @param  serverid:   ID associated to the service we announce
        @type   serverid:   string (hexadecimal)
        @param  name:      The name used to announce the service via bluetooth
        @type   name:      string
        @rtype:     BTServer object
        @return:    BTServer object
        """
        gobject.GObject.__init__(self)
        self.handler = {}
        self.handler['list'] = None
        self.buffer = ""
        self.name = name
        self.serverid = serverid
        self.connectable = 'yes'
        self.filter = {}
        self.port = bluetooth.get_available_port( bluetooth.RFCOMM )
        self.connected = None
        self.config = config()
        self.paired_by_us = {}

        self.client_sock = None
        self.server_sock = None

        self.client_io_watch = None
        self.server_io_watch = None

        self.server_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.server_sock.bind(("", self.port))
        self.server_sock.listen(1)

        self._register_bluez_signals()
        self._switch_connectable()

    def shutdown(self):
        pass

    def _handle_buffer(self):
        packets = self.buffer.split(u"\u0000")
        # The last packet is either empty (if the last packet was completely send
        # or we only see a partital package, that we feed back into the buffer
        self.buffer = packets.pop()            
        for packet in packets:
            data = json.read(packet.encode('utf-8'))
            if (data['type'] == "keyCode"):
                mapping = data["mapping"]
                keycode = data["keycode"]
                self.emit('keycode', mapping, keycode)
            elif (data['type'] == "listReply" and self.handler['list']):
                self.handler['list'](data['selectionIndex'])
                self.handler['list'] = None
            else:
                logging.debug("Unmatched package: " + str(data))

    def send_list_query(self, title, list, callback):
        package = {}
        package['type'] = "listQuery"
        package['title'] = title
        package['list'] = list
        self._send_query(package)
        self.handler['list'] = callback
        
    def _send_query(self, package):
        message = (json.write(package) + u"\u0000").encode('utf-8')
        logging.debug(repr(message))
        self.client_sock.sendall(message)

    def handle_incoming_data(self, clientsocket, condition):
        """
        Handle incoming data from the client. We assume a 5 byte payload. This consists
        of one byte providing a X{mapping} (key pressed=>0, key released=>1) and the rest
        encoding an integer (4 byte). This bytestring is passed to L{byte_array_to_int},
        which decodes the bytestring to the original integer X{keycode}.

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
        logging.debug("In Buffer: " + self.buffer)
        self._handle_buffer()
        return True

    def handle_disconnection(self, serversocket, condition):
        """
        Handles the shutdown of connections. When the serversocket signals the
        HUP condition.  The handler disconnects from the mainloop by returning
        false.

        This method is called when the connection was shutdown from the
        other side of the connection. The data handler (L{handle_incoming_data})
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
        logging.debug('BTServer: %s disconnected' % (self.connected[0],))
        gobject.source_remove(self.client_io_watch)
        self.server_io_watch = None
        self.client_io_watch = None
        self.client_sock = None
        if self.connected[0] in self.paired_by_us:
            logging.debug('BTServer: We paired this device')
            if self.config.get_config_item_fb("remove-pairing", False):
                logging.debug('BTServer: We remove the pairing for this device')
                self.paired_by_us[self.connected[0]].RemoveBonding(self.connected[0])
            del self.paired_by_us[self.connected[0]]
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
        logging.debug("Serversocket: " + str(self.server_sock.getsockname()))

        if ( self._check_pairing(client_address) and
            (self.connectable == 'yes' or 
            (self.connectable == 'filtered' and client_address[0] in self.filter))):

            self.connected = client_address
            self.emit("connect", client_address[0], client_address[1])

            self.client_io_watch = gobject.io_add_watch(self.client_sock, gobject.IO_IN, self.handle_incoming_data)
            self.server_io_watch = gobject.io_add_watch(self.client_sock, gobject.IO_HUP, self.handle_disconnection)
        else:
            logging.debug("BTServer: Closing remote connection")
            self.client_sock.close()
            self.client_sock = None
            if self.connectable == 'filtered':
                self.server_io_watch = gobject.io_add_watch(self.server_sock, gobject.IO_IN, self.handle_connection)
                bluetooth.advertise_service(self.server_sock, self.name, self.serverid)
            
        return False

    def _check_pairing(self, client_address):
        # Check whether we need pairing!
        if not self.config.get_config_item_fb("require-pairing", True):
            logging.debug('BTServer: Pairing not required')
            return True
        logging.debug('BTServer: Check for pairing')
        manager = dinterface(dbus.SystemBus(), 'org.bluez', '/org/bluez', 'org.bluez.Manager')
        adapters = manager.ListAdapters()
        paired = False
        for adapter in adapters:
            adapter = dinterface(dbus.SystemBus(), 'org.bluez', adapter, 'org.bluez.Adapter')
            if adapter.HasBonding(client_address[0]):
                paired = True
                break
            
        if not paired:
            logging.debug('We see a new device, that was not yet allowed to connect. Beginning pairing!')
            logging.debug('Search for adapter, that reaches the phone')
            for adapter in adapters:
                adapter = dinterface(dbus.SystemBus(), 'org.bluez', adapter, 'org.bluez.Adapter')
                # We asume that an adapter that can resolve the name is the "right" adapter
                try:
                    name = adapter.GetRemoteName(client_address[0])
                    logging.debug('Got name %s - will try to create bonding' % (name, ))
                    adapter.CreateBonding(client_address[0])
                    logging.debug('Bonding returned')
                    if adapter.HasBonding(client_address[0]):
                        logging.debug('Bonding successfull')
                        paired = True
                        self.paired_by_us[client_address[0]] = adapter
                    else:
                        logging.debug('Bonding failed')
                    break
                except:
                    logging.debug('Exception in BondingCreation (DBUS Methods)')
                    pass
        return paired

    def _register_bluez_signals(self):
        if not BTServer.is_bluez_up():
            return
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.bluez', '/org/bluez'),'org.bluez.Manager')
        manager.connect_to_signal("AdapterAdded", self._adapter_added)
        manager.connect_to_signal("AdapterRemoved", self._adapter_removed)
 
    def _adapter_removed(self, adapter):
        pass

    def _adapter_added(self,adapter): 
        self._switch_connectable()

    @staticmethod
    def is_bluez_up():
        """
        Verify if the bluetooth service is up
 
        @rtype:     bool
        @return:    True if bluez if bluez is up, False otherwise
        """
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.bluez', '/org/bluez'),'org.bluez.Manager')
        try:
            manager.ListAdapters()
            return True
        except dbus.dbus_bindings.DBusException:
            return False

if __name__ == '__main__':
    def print_args(*args):
        print args

    import gobject
    bt = BTServer()
    bt.connect("keycode", print_args, 'keycode')
    bt.connect("connect", print_args, 'connect')
    bt.connect("disconnect", print_args, 'disconnect')
    
    print "You entered Testmode, when you fire up LBRC on your device"
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
