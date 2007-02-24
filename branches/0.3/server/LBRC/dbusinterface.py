#!/usr/bin/python

import bluetooth
import sys
import json
import os
import gobject
import dbus
import dbus.service
import dbus.glib

from LBRC.UinputDispatcher import UinputDispatcher
import LBRC.consts as co
from LBRC.BTServer import BTServer

class LBRCdbus(dbus.service.Object):
    def __init__(self):
        if self.check_running_instance():
            sys.exit(0)
        bus_name = dbus.service.BusName('custom.LBRC', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/custom/LBRC")
        self.__read_config()
        self.btserver = BTServer()
        [used_keys, used_relative_axes] = self.__read_profiles()
        self.uinput_dispatch = UinputDispatcher(
            keys=used_keys, 
            relative_axes=used_relative_axes,
            device_file = self.config['uinputdevice']
        )
        # (keycode,mapping) => [callback_id, calls]
        self.repeathandler = {}
        self.btserver.connect('keycode', self.handler)
        self.btserver.connect('connect', lambda btserver, btadress, port: 
                                         self.connect_cb(bluetooth.lookup_name(btadress), btadress, port))
        self.btserver.connect('disconnect', lambda btserver, btadress, port:
                                         self.disconnect_cb(bluetooth.lookup_name(btadress), btadress, port))
        self.cur_profile = self.profiles.keys()[0]
        if ( "defaultprofile" in self.config and
             self.config['defaultprofile'] in self.profiles):
            self.cur_profile = self.config['defaultprofile']
        self.events = self.profiles[self.cur_profile]['events']

    def check_running_instance(self):
        proxy_obj = dbus.SessionBus().get_object('custom.LBRC', '/custom/LBRC')
        lbrc_interface = dbus.Interface(proxy_obj, 'custom.LBRC')
        try:
            lbrc_interface.get_profiles()
            return 1
        except:
            return 0

    @dbus.service.method('custom.LBRC', in_signature='s', out_signature=None)
    def set_profile(self, profileid):
        if profileid in self.profiles and not profileid == self.cur_profile:
            if self.pre_profile_switch():
                self.events = self.profiles[profileid]['events']
                self.cur_profile = profileid
                self.profile_change(profileid, self.profiles[profileid]['name'])

    @dbus.service.method('custom.LBRC', out_signature="a(ss)")
    def get_profiles(self):
        return [(i[0], i[1]['name']) for i in self.profiles.iteritems()]

    @dbus.service.method('custom.LBRC', out_signature="ss")
    def get_profile(self):
        return (self.cur_profile, self.profiles[self.cur_profile]['name'])

    @dbus.service.method('custom.LBRC', in_signature='as')
    def set_allowed(self, filter):
        self.btserver.set_allowed(filter)

    @dbus.service.method('custom.LBRC', in_signature='s')
    def add_allowed(self, address):
        self.btserver.add_allowed(address)

    @dbus.service.method('custom.LBRC', out_signature='as')
    def get_allowed(self):
        return self.btserver.get_allowed()

    @dbus.service.method('custom.LBRC', in_signature='s')
    def remove_allowed(self, address):
        self.btserver.remove_allowed(address)

    @dbus.service.method('custom.LBRC', out_signature='')
    def clear_allowed(self):
        self.btserver.clear_allowed()

    @dbus.service.method('custom.LBRC', out_signature='')
    def set_connectable_on(self):
        self.btserver.set_property('connectable', 'yes')

    @dbus.service.method('custom.LBRC', out_signature='')
    def set_connectable_filtered(self):
        self.btserver.set_property('connectable', 'filtered')

    @dbus.service.method('custom.LBRC', out_signature='')
    def set_connectable_off(self):
        self.btserver.set_property('connectable', 'no')

    @dbus.service.signal('custom.LBRC', signature='s')
    def connectable_event(self, state):
        pass

    @dbus.service.signal('custom.LBRC', signature='')
    def update_filter(self):
        pass

    @dbus.service.signal('custom.LBRC', signature="ssi")
    def connect_cb(self, btname, btadress, port):
        pass

    @dbus.service.signal('custom.LBRC', signature="ssi")
    def disconnect_cb(self, btname, btadress, port):
        pass

    @dbus.service.signal('custom.LBRC', signature="ix")
    def keycode_cb(self, mapping, keycode):
        pass

    @dbus.service.signal('custom.LBRC', signature='ss')
    def profile_change(self, id, name):
        pass

    def __read_config(self):
        # abspath points to the directory which hold our graphics, which
        # is the path where we are staying
        abspath = os.path.dirname(os.path.abspath(sys.argv[0]))
        config_file = open(abspath + "/config.conf")
        config_data = config_file.read()
        json_reader = json.JsonReader()
        self.config = json_reader.read(config_data)
        config_file.close()
        self.config['abspath'] = abspath

    # Reads Profile file and creates Eventmap
    def __read_profiles(self):
        profiles_file = open(self.config['abspath'] + "/profiles.conf")
        profiles_data = profiles_file.read()
        json_reader = json.JsonReader()
        profiles = json_reader.read(profiles_data)
        profiles_file.close()
        del profiles_data
        self.profiles = {}
        keys = []
        relative_axes = []
        for profile in profiles.keys():
            pd = profiles[profile]
            events = {}
            for axis in pd['mouseaxes']:
                ax = co.input["REL_" + axis['map_to'][1:2]]
                if axis['map_to'][0:1] == "-":
                    events[(int(axis['keycode']), 0)] = {'repeat_freq': 10, 
                                                         'repeat_func': self.lin_mouse_freq,
                                                         'commands': [[co.input['EV_REL'], ax, lambda x,y: -1 * self.lin_mouse_step(x,y)]]}
                else:
                    events[(int(axis['keycode']), 0)] = {'repeat_freq': 10, 
                                                         'repeat_func': self.lin_mouse_freq,
                                                         'commands': [[co.input['EV_REL'], ax, lambda x,y: self.lin_mouse_step(x,y)]]}
                if ax not in relative_axes:
                    relative_axes.append(ax)

            for axis in pd['mousewheel']:
                ax = co.input["REL_" + axis['map_to'][1:]]
                if axis['map_to'][0:1] == "-":
                    events[(int(axis['keycode']),0)] = {'repeat_freq': int(axis['repeat_freq']), 
                                                        'repeat_func': lambda x,n: x,
                                                        'commands': [[co.input['EV_REL'], ax, -1]]}
                else:
                    events[(int(axis['keycode']),0)] = {'repeat_freq': int(axis['repeat_freq']), 
                                                        'repeat_func': lambda x,n: x,
                                                        'commands': [[co.input['EV_REL'], ax, 1]]}
                if ax not in relative_axes:
                    relative_axes.append(ax)

            for button in pd['mousebuttons']:
                bt = co.input["BTN_" + button['map_to']]
                events[(int(button['keycode']),0)] = {'commands': [[co.input['EV_KEY'], bt, 1]]}
                events[(int(button['keycode']),1)] = {'commands': [[co.input['EV_KEY'], bt, 0]]}
                if bt not in keys:
                    keys.append(bt)

            for key in pd['keys']:
                k =  co.input["KEY_" + key['map_to']]
                events[(int(key['keycode']),0)] = {'repeat_freq': int(key['repeat_freq']), 
                                      'repeat_func': self.const_key, 
                                      'repeat_commands': [[co.input['EV_KEY'], k, 0], [co.input['EV_KEY'], k, 1] ] , 
                                      'commands': [[co.input['EV_KEY'], k, 1]],
                                      'blocking': 1}
                events[(int(key['keycode']),1)] = {'commands': [[co.input['EV_KEY'], k, 0]]}
                if k not in keys:
                    keys.append(k)
            self.profiles[profile] = {'events': events, 'name': pd['name'] }
        return[keys, relative_axes]

    def lin_mouse_freq(self, x,n):
        freq = x * (n * 0.75 +1)
        if freq > 500:
            freq = 500
        return freq

    def lin_mouse_step(self, x,n):
        freq = self.lin_mouse_freq(x,n);
        if(freq < 500):
            return 2
        else:
            return 3

    def const_key(self, x, n):
        if n == 0:
            return 2
        return 20

    def send_commands(self, commands, freq, calls):
        for command in commands:
            param = command[2]
            if callable(param):
                param = param(freq, calls)
            self.uinput_dispatch.send_event(command[0], command[1], param)
        self.uinput_dispatch.send_event(co.input['EV_SYN'], co.input['SYN_REPORT'], 0)

    def pre_profile_switch(self):
        repeathandler = self.repeathandler
        # Make sure we handled everythink
        # Currently profile switching while in a keypress handler will lead to problems!!
        # The key would never be released, so we wont go into the switch with keypress active!
        for release_event_tuple in repeathandler:
            entry = self.events[event_tuple]
            if 'blocking' in entry and entry['blocking']:
                return 0
        for release_event_tuple in repeathandler:
            gobject.source_remove(repeathandler[release_event_tuple][0])
            del repeathandler[release_event_tuple]
        return 1

    def repeater(self, event_tuple):
        repeathandler = self.repeathandler
        entry = self.events[event_tuple];
        repeathandler[event_tuple][1] += 1
        if 'repeat_commands' in entry:
            self.send_commands(entry['repeat_commands'], entry['repeat_freq'], repeathandler[event_tuple][1])
        else:
            self.send_commands(entry['commands'], entry['repeat_freq'], repeathandler[event_tuple][1])
        freq = entry['repeat_func'](entry['repeat_freq'], repeathandler[event_tuple][1])
        repeathandler[event_tuple][0] = gobject.timeout_add(int(1000.0/freq), self.repeater, event_tuple)
        return False

    def handler(self, btserver, map, keycode):
        self.keycode_cb(map, keycode)
        repeathandler = self.repeathandler
        print "KeyCode: " + str(keycode)
        event_tuple = (keycode, map)
        release_event_tuple = (keycode, map - 1)
        if release_event_tuple in repeathandler:
            gobject.source_remove(repeathandler[release_event_tuple][0])
            del repeathandler[release_event_tuple]
        if event_tuple in self.events:
            entry = self.events[event_tuple];
            self.send_commands(entry['commands'], 0, 0)
            if 'repeat_freq' in entry:
                repeathandler[event_tuple] = []
                freq = entry['repeat_func'](entry['repeat_freq'], 0)
                repeathandler[event_tuple].append(gobject.timeout_add(int(1000.0/freq), self.repeater, event_tuple))
                repeathandler[event_tuple].append(0)
        return True

    def run(self):
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    @dbus.service.method('custom.LBRC')
    @dbus.service.signal('custom.LBRC')
    def shutdown(self):
        self.btserver.shutdown()
        self.mainloop.quit()

if __name__ == '__main__':
    brs = LBRCdbus()
    brs.run()
    sys.exit(0)
