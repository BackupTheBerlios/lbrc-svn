import dbus
import sys
import json
import os.path as osp

scriptpath = osp.dirname(osp.abspath(sys.argv[0]))

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

def get_localedir():
    """
    Return path to directory, where out l10n files
    are located.

    @return:    path to locale dir
    @rtype:     string
    """

    #FIXME: must read it from instalation script
    if scriptpath.startswith('/usr/bin'):
        return "/usr/share/locale"
    else:
        return osp.join(scriptpath, "pot")

def get_guidir():
    """
    Return path to directory where *.glade files 
    are located.

    @return:    path to gui dir
    @rtype:     string
    """

    #FIXME: must read it from instalation script
    if scriptpath.startswith('/usr/bin'):
        return "/usr/share/lbrc"
    else:
        return osp.join(scriptpath, "LBRC_gtk_gui")

def get_userconfigfile(name):
    """
    Returns absolute path to a user config file with C{name} name

    @param  name:   name of the config file
    @type   name:   string
    @return:    path to the config file
    @rtype:     string
    """

    #FIXME: must read it from instalation script
    if scriptpath.startswith('/usr/bin'):
        return osp.join(osp.expanduser("~"), ".lbrc", name)
    else:
        return osp.join(scriptpath, name)


def get_systemconfigfile(name):
    """
    Returns absolute path to a system config file with C{name} name

    @param name: name of config file
    @type  name: string
    @return:    absolute path for a config file
    @rtype:     string
    """
    
    #FIXME: must read it from instalation script
    return osp.join('/usr/share/lbrc', name)

def get_configfiles(name):
    """
    Returns a list of absolute paths to all config files with C{name} name and verify if the path is a file.

    @param  name:   name of cofig file
    @type   name:   string
    @return:    list of complete paths to config files
    @rtype:     list of strings
    """
    paths = []

    # there's no more data prefix, but this cobe maybe util in futher
    #dataprefix = []
    #for dp in dataprefix:
    #    f = osp.join(dp, name)
    #    if osp.isfile(f):
    #        paths.append(f)
    for f in get_systemconfigfile(name),get_userconfigfile(name):
        if osp.isfile(f):
            paths.append(f)

    return paths

def get_datafile(name):
    """
    Returns absolute path to a data file with C{name} name

    @param  name:   name of data file
    @type   name:   string
    @return:    absolute path to data file
    @rtype:     string
    """

    #FIXME: must read it from instalation script
    if scriptpath.startswith('/usr/bin'):
        return osp.join('/usr/share/lbrc', name)
    else:
        return osp.join(scriptpath, name)

def get_binfile(name):
    """
    Returns absolute path to executable with C{name} name

    @param  name:   name of executable
    @type   name:   string
    @return:    path to executable
    @rtype:     string
    """

    #FIXME: must read it from instalation script
    if scriptpath.startswith('/usr/bin'):
        return osp.join('/usr/bin/', name)
    else:
        return osp.join(scriptpath, name)

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



__all__ = ["dbusinterface", "BTServer", "UinputDispatcher", "CommandExecutor", "get_binfile", "get_userconfigfile", "get_systemconfigfile", "get_configfiles", "get_guidir", "get_localedir", "write_config" , "read_config"]

