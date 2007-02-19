#!/usr/bin/python

import pygtk
pygtk.require("2.0")
import bluetooth,os,math,gobject,re

bt_address = re.compile("\('([A-Fa-f0-9:]+)', ([0-9]+)\)")

class BTServer(gobject.GObject):
    __gsignals__ = {
        'keycode': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT64,)),
        'connect': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT)),
        'disconnect': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_INT)),
    }
    def __init__(self, name = "LBRC", serverid = "a1e7"):
        gobject.GObject.__init__(self)
        self.name = name
        self.serverid = serverid
        self.port = bluetooth.get_available_port( bluetooth.L2CAP)
        self.connected = None

        self.client_sock = None
        self.server_sock = bluetooth.BluetoothSocket( bluetooth.L2CAP )
        self.server_sock.bind(("", self.port))
        self.server_sock.listen(1)
        
        bluetooth.advertise_service(self.server_sock, self.name, self.serverid)

        self.client_io_watch = None
        self.server_io_watch = gobject.io_add_watch(self.server_sock, gobject.IO_IN, self.handle_connection)

    def shutdown(self):
        pass

    def handle_incoming_data(self, clientsocket, condition):
        data = clientsocket.recv(5)
        if data:
            mapping = ord(data[0])
            keycode = self.byte_array_to_int(data[1:5])
            self.emit('keycode', int(mapping), int(keycode))
        return True

    def handle_disconnection(self, serversocket, condidition):
        gobject.source_remove(self.server_io_watch)
        gobject.source_remove(self.client_io_watch)
        self.emit("disconnect", self.connected[0], self.connected[1])
        self.server_io_watch = gobject.io_add_watch(self.server_sock, gobject.IO_IN, self.handle_connection)
        bluetooth.advertise_service(self.server_sock, self.name, self.serverid)
        return False

    def handle_connection(self, serversocket, condition):
        gobject.source_remove(self.server_io_watch)
        bluetooth.stop_advertising(self.server_sock)

        self.client_sock,client_address = self.server_sock.accept()

        self.connected = client_address
        self.emit("connect", client_address[0], client_address[1])

        self.client_io_watch = gobject.io_add_watch(self.client_sock, gobject.IO_IN, self.handle_incoming_data)
        self.server_io_watch = gobject.io_add_watch(self.client_sock, gobject.IO_HUP, self.handle_disconnection)
        return False

    @staticmethod
    def byte_array_to_int(bytes):
        "Convert byte array to int, assuming most significant byte first"
        exponent = len(bytes) - 1;
        result = 0
        for i in range(len(bytes)):
            factor =  int(math.pow(2, (exponent - i) * 8 ))
            result += ord(bytes[i]) * factor
        return result
