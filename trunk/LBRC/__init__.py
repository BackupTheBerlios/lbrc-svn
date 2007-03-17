import dbus
import sys
import json
import os.path as osp

def dinterface(bus, service, obj_path, interface):
    """
    Convenience function to make the interface creation from a
    dbus object, the service, object path and interface much more
    smooth

    @param  bus:        the DBUS bus, where the service resides
    @type   bus:        dbus.Bus
    @param  service:    the service, we call the object from
    @type   service:    string
    @param  obj_path:   path to the object
    @type   obj_path:   string
    @param  interface:  the interface, we want to acquire for the interface
    @type   interface:  string
    @return:    Requested DBUS Interface
    @rtype:     dbus.Interface
    """
    proxy_obj = bus.get_object(service, obj_path)
    return dbus.Interface(proxy_obj, interface)


def write_config(absfilename, config):
    config_file = open(absfilename, 'w')
    json_writer = json.JsonWriter()
    config_data = json_writer.write(config)
    config_file.write(config_data)
    config_file.close()

def read_config(absfilename):
    config = {}
    config_file = open(absfilename)
    config_data = config_file.read()
    json_reader = json.JsonReader()
    config = json_reader.read(config_data)
    config_file.close()
    return config



__all__ = ["dbusinterface", "BTServer", "UinputDispatcher", "CommandExecutor", "write_config" , "read_config"]

