# pylint: disable-msg=E0611
import dbus

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