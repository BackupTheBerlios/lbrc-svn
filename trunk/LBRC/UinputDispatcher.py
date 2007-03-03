#!/usr/bin/python

import os, struct, fcntl, time
import os.path as osp
import logging
import gobject
import LBRC.consts as co



class UinputDispatcher(object):
    """
    Class to handle keycodes received by BTServer and issue commands according to them
    """
    def __init__(self, config, profiledata):
        """
        The method initialises the uinput device and prior to that creates the eventsmap
        from the profiledata. In this process all uinput events are recorded and the
        corresponding eventmasks are set on the uinput device. This means, that all
        uinput events, from any profile have to be present at this point!

        @param  config:         configuration data
        @type   config:         dictionary
        @param  profiledata:    profile data
        @type   profiledata:    dictionary
        """        
        self.config = config
        self.profiledata = profiledata
        self.profile = None
        # (keycode,mapping) => [callback_id, calls]
        self.repeathandler = {}

        if 'uinputdevice' in self.config:
            device_file = self.config['uinputdevice']
        else:
            device_file = self._guess_uinput_dev(self)
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

        self._interpret_profiles()

        fcntl.ioctl(self.uinput_dev, co.uinput['UI_DEV_CREATE'])
 
    def set_profile(self, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        self.profile = profile

    def _send_commands(self, commands, freq, calls):
        """
        Issue the output of the configured events. From the configured frequency,
        passed as C{freq} and the number of calls C{calls}, the param for part
        of the event is calculated, if it is not static.

        The commands are all send into the device and avert that a SYN_REPORT
        event is issued, which flushes the events out.

        @param  commands:   Events to be issued
        @type   commands:   list of list of ints/callables
        @param  freq:       calls per second
        @type   freq:       int
        @param  calls:      calls in this repeat cycle
        @type   calls:      int
        """
        for command in commands:
            param = command[2]
            if callable(param):
                param = param(freq, calls)
            self.send_event(command[0], command[1], param)
        self.send_event(co.input['EV_SYN'], co.input['SYN_REPORT'], 0)

    def send_event(self, event, descriptor, param):
        """
        Output event to the uinput device => pack the correct structure and write to open device
        For the relevant event ids and types please refer to consts.py

        @param  event:      event type
        @type   event:      int
        @param  descriptor: event id
        @type   descriptor: int
        @param  param:      parameter for the event
        @type   param:      int
        """
        os.write(self.uinput_dev, struct.pack("LLHHl", time.time(), 0, event, descriptor, param))

    def _repeater(self, event_tuple):
        """
        Handle repeats of keystrokes

        @param  event_tuple:    Event tuple
        @type   event_tuple:    tuple of mapping and keycode
        """
        repeathandler = self.repeathandler
        entry = self.profiles[self.profile][event_tuple];
        repeathandler[event_tuple][1] += 1
        if 'repeat_commands' in entry:
            self._send_commands(entry['repeat_commands'], entry['repeat_freq'], repeathandler[event_tuple][1])
        else:
            self._send_commands(entry['commands'], entry['repeat_freq'], repeathandler[event_tuple][1])
        freq = entry['repeat_func'](entry['repeat_freq'], repeathandler[event_tuple][1])
        repeathandler[event_tuple][0] = gobject.timeout_add(int(1000.0/freq), self._repeater, event_tuple)
        return False

    def switch_profile(self):
        """
        Check whether it is save for us to switch the profile. This is always the case,
        if no keypress handler is running. The keypress has to be completed by a key release,
        or it get really nasty. Currently we do not do this, so we block the switch

        @return:    Is it save to switch profile now?
        @rtype:     bool
        """
        repeathandler = self.repeathandler
        for release_event_tuple in repeathandler:
            entry = self.profiles[self.profile][event_tuple]
            if 'blocking' in entry and entry['blocking']:
                return 0
        for release_event_tuple in repeathandler:
            gobject.source_remove(repeathandler[release_event_tuple][0])
            del repeathandler[release_event_tuple]
        return 1

    def _interpret_profiles(self):
        """
        Interpret the data from the profile and create appropriate uinput events
        additionally record the Events, that will be passed, to set the appropriate
        eventmasks on the uinputdevice
        """
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
                                                             'repeat_func': self._lin_mouse_freq,
                                                             'commands': [[co.input['EV_REL'], ax, lambda x,y: -1 * self._lin_mouse_step(x,y)]]}
                    else:
                        events[(int(axis['keycode']), 0)] = {'repeat_freq': 10, 
                                                             'repeat_func': self._lin_mouse_freq,
                                                             'commands': [[co.input['EV_REL'], ax, lambda x,y: self._lin_mouse_step(x,y)]]}
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
                                          'repeat_func': self._const_key, 
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
        """
        The method maps the incoming keycode and mapping to the associated
        uinput events. And where appropriate it installs a repeathandler.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        int
        @param  keycode:        keycode received
        @type:  keycode:        int
        """
        repeathandler = self.repeathandler
        print "KeyCode: " + str(keycode)
        event_tuple = (keycode, mapping)
        release_event_tuple = (keycode, mapping - 1)
        if release_event_tuple in repeathandler:
            gobject.source_remove(repeathandler[release_event_tuple][0])
            del repeathandler[release_event_tuple]
        if event_tuple in self.profiles[self.profile]:
            entry = self.profiles[self.profile][event_tuple];
            self._send_commands(entry['commands'], 0, 0)
            if 'repeat_freq' in entry:
                repeathandler[event_tuple] = []
                freq = entry['repeat_func'](entry['repeat_freq'], 0)
                repeathandler[event_tuple].append(gobject.timeout_add(int(1000.0/freq), self._repeater, event_tuple))
                repeathandler[event_tuple].append(0)

    @staticmethod
    def _guess_uinput_dev(self):
        """
        Find the uinput device in the system

        First this method checks a few well known places and then desperately search whole /dev hierarchy for devices names
        uinput ...

        @return:    Location of the uinput device
        @rtype:     string
        """
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


    def _lin_mouse_freq(self, x,n):
        """
        linear speed up, stopped at 500 (more can't be handled by the mainloop call back)
        """
        freq = x * (n * 0.75 +1)
        if freq > 500:
            freq = 500
        return freq

    def _lin_mouse_step(self, x,n):
        """
        length of stepps for mouse movement
        """
        freq = self.lin_mouse_freq(x,n);
        if(freq < 500):
            return 2
        else:
            return 3

    def _const_key(self, x, n):
        """
        key repeat is only issued, after 1/2 second, after that
        1/20 s
        """
        if n == 0:
            return 2
        return 20

