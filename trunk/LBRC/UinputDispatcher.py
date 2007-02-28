#!/usr/bin/python

import os, struct, fcntl, time
import os.path as osp
import logging
import gobject
import LBRC.consts as co

class UinputDispatcher(object):
    def __init__(self, config, profiledata):
        self.config = config
        self.profiledata = profiledata
        self.profile = None
        # (keycode,mapping) => [callback_id, calls]
        self.repeathandler = {}

        if 'uinputdevice' in self.config:
            device_file = self.config['uinputdevice']
        else:
            device_file = self.__guess_uinput_dev(self)
        self.uinput_dev = os.open(device_file, os.O_RDWR)
        dev = ["BlueRemote",            # Name for device
           co.input['BUS_BLUETOOTH'],   # Bus where we stay on
           1,                           # Vender ID
           1,                           # Produkt ID
           1,                           # Version ID
           0                            # We don't support force feedback
        ]
        # No Absolute Values!
        for f in range(64*4):  #absmin
          dev.append(0x00)
        #for f in range(64*1):  #absmax
        #  dev.append(0x00)
        #for f in range(64*2):  #absfuzz,absflat
        #  dev.append(0x00)
        device_structure = struct.pack("80sHHHHi" + 64*4*'I', *dev)
        os.write(self.uinput_dev, device_structure)

        self.__interpret_profiles()

        fcntl.ioctl(self.uinput_dev, co.uinput['UI_DEV_CREATE'])
 
    def set_profile(self, profile):
        self.profile = profile
 
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
            self.send_event(command[0], command[1], param)
        self.send_event(co.input['EV_SYN'], co.input['SYN_REPORT'], 0)

    def send_event(self, event, descriptor, param):
        os.write(self.uinput_dev, struct.pack("LLHHl", time.time(), 0, event, descriptor, param))

    def repeater(self, event_tuple):
        repeathandler = self.repeathandler
        entry = self.profiles[self.profile][event_tuple];
        repeathandler[event_tuple][1] += 1
        if 'repeat_commands' in entry:
            self.send_commands(entry['repeat_commands'], entry['repeat_freq'], repeathandler[event_tuple][1])
        else:
            self.send_commands(entry['commands'], entry['repeat_freq'], repeathandler[event_tuple][1])
        freq = entry['repeat_func'](entry['repeat_freq'], repeathandler[event_tuple][1])
        repeathandler[event_tuple][0] = gobject.timeout_add(int(1000.0/freq), self.repeater, event_tuple)
        return False

    def switch_profile(self):
        repeathandler = self.repeathandler
        # Make sure we handled everythink
        # Currently profile switching while in a keypress handler will lead to problems!!
        # The key would never be released, so we wont go into the switch with keypress active!
        for release_event_tuple in repeathandler:
            entry = self.profiles[self.profile][event_tuple]
            if 'blocking' in entry and entry['blocking']:
                return 0
        for release_event_tuple in repeathandler:
            gobject.source_remove(repeathandler[release_event_tuple][0])
            del repeathandler[release_event_tuple]
        return 1

    # Reads Profile file and creates Eventmap
    def __interpret_profiles(self):
        self.profiles = {}
        keys = []
        relative_axes = []

        for profile_file in self.profiledata:
            for profile in profile_file.keys():
                pd = profile_file[profile]
                events = {}
                commands = {}
                if not 'mouseaxes' in pd:
                    pd['mouseaxes'] = {}
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
                if not 'mousewheel' in pd:
                    pd['mousewheel'] = {}
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
                if not 'mousebuttons' in pd:
                    pd['mousebuttons'] = {}
                for button in pd['mousebuttons']:
                    bt = co.input["BTN_" + button['map_to']]
                    events[(int(button['keycode']),0)] = {'commands': [[co.input['EV_KEY'], bt, 1]]}
                    events[(int(button['keycode']),1)] = {'commands': [[co.input['EV_KEY'], bt, 0]]}
                    if bt not in keys:
                        keys.append(bt)
                if not 'keys' in pd:
                    pd['keys'] = {}
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
                self.profiles[profile] = events
        
        if len(relative_axes) > 0:
            fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_EVBIT'], co.input['EV_REL'])
            for axis in relative_axes:
                fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_RELBIT'], axis)
        if len(keys) > 0:
            fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_EVBIT'], co.input['EV_KEY'])
            for key in keys:
                fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], key)

    def keycode(self, mapping, keycode):
        repeathandler = self.repeathandler
        print "KeyCode: " + str(keycode)
        event_tuple = (keycode, mapping)
        release_event_tuple = (keycode, mapping - 1)
        if release_event_tuple in repeathandler:
            gobject.source_remove(repeathandler[release_event_tuple][0])
            del repeathandler[release_event_tuple]
        if event_tuple in self.profiles[self.profile]:
            entry = self.profiles[self.profile][event_tuple];
            self.send_commands(entry['commands'], 0, 0)
            if 'repeat_freq' in entry:
                repeathandler[event_tuple] = []
                freq = entry['repeat_func'](entry['repeat_freq'], 0)
                repeathandler[event_tuple].append(gobject.timeout_add(int(1000.0/freq), self.repeater, event_tuple))
                repeathandler[event_tuple].append(0)

    @staticmethod
    def __guess_uinput_dev(self):
        known_places = ['/dev/input/uinput', '/dev/misc/uinput']
        for place in known_places:
            logging.debug('Examing %s as uinput device' % (place,))
            if osp.exists(place):
                if not os.access(place, os.R_OK | os.W_OK):
                    logging.warning('%s looks like a uinput device node, but you lack necessary permissions' % (place,))
                else:
                    logging.debug('Asuming we found a suitable uinput device node: %s' % (place,))
                    return place
        logging.debug('None of the well known places for uinput device was found to be ok, beginning search')
        possible_places = []
        for root, dirs, files in os.walk('/dev'):
            if 'uinput' in files:
                if not osp.join(root, 'uinput') in known_places:
                    possible_places.append(osp.join(root, 'uinput'))
                    logging.debug('Possible device node: %s' % (osp.join(root, 'uinput'),))
        for place in possible_places:
            logging.debug('Examing %s as uinput device' % (place,))
            if osp.exists(place):
                if not os.access(place, os.R_OK | os.W_OK):
                    logging.warning('%s looks like a uinput device node, but you lack necessary permissions' % (place,))
                else:
                    logging.debug('Asuming we found a suitable uinput device node: %s' % (place,))
                    return place
        logging.error('No device node found, that looks like a uinput device node - is the kernel module loaded?')
