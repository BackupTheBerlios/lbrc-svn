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
        self.c_reader, self.c_writer = os.pipe()
        self.i_reader, self.i_writer = os.pipe()

        self.pid = os.fork()
        if self.pid:
            # We are the parent
            os.close(self.c_writer)
            os.close(self.i_writer)
            gobject.io_add_watch(self.c_reader, gobject.IO_IN, self.read);
            gobject.io_add_watch(self.i_reader, gobject.IO_IN, self.info);
        else:
            # The Child does the work ...
            os.close(self.c_reader)
            os.close(self.i_reader)
            while 1:
                server_sock = bluetooth.BluetoothSocket( bluetooth.L2CAP )
                port = bluetooth.get_available_port( bluetooth.L2CAP)
                server_sock.bind(("",port))
                server_sock.listen(1)
                bluetooth.advertise_service(server_sock, self.name, self.serverid)
                client_sock,client_address = server_sock.accept()
                bluetooth.stop_advertising(server_sock)
                os.write(self.i_writer, "CONNECT " + str(client_address))
                data = client_sock.recv(5)
                while 1:
                    os.write(self.c_writer, data)
                    data = client_sock.recv(5)
                    if len(data) == 0:
                        break
                client_sock.close()
                server_sock.close()
                os.write(self.i_writer, "DISCONNECT " + str(client_address))

    def shutdown(self):
        os.kill(self.pid, 15)

    def info(self, source, condition):
        data = os.read(self.i_reader, 1024)
        if data[0:7] == "CONNECT":
            matched = bt_address.match(data[8:])
            self.emit("connect", matched.group(1), int(matched.group(2)))
        elif data[0:10] == "DISCONNECT":
            matched = bt_address.match(data[11:])
            self.emit("disconnect",  matched.group(1), int(matched.group(2)))
        return True

    def read(self, source, condition):
        data = os.read(self.c_reader, 5)
        mapping = ord(data[0])
        keycode = self.byte_array_to_int(data[1:5])
        self.emit('keycode', int(mapping), int(keycode))
        return True

    @staticmethod
    def byte_array_to_int(bytes):
        "Convert byte array to int, assuming most significant byte first"
        exponent = len(bytes) - 1;
        result = 0
        for i in range(len(bytes)):
            factor =  int(math.pow(2, (exponent - i) * 8 ))
            result += ord(bytes[i]) * factor
        return result
