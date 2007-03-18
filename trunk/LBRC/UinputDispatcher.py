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
    def __init__(self, config):
        """
        The method initialises the uinput device and prior to that creates the eventsmap
        from the profiledata. In this process all uinput events are recorded and the
        corresponding eventmasks are set on the uinput device. This means, that all
        uinput events, from any profile have to be present at this point!

        @param  config:         configuration data
        @type   config:         dictionary
        """
        self.invoked = {}

        self.config = config
        
        self.uinput_dev = None
        
        self.open_uinput_dev()
        
        Event.set_uinput_dev(self.uinput_dev)

        self.init = []
        self.actions = {}
        self.destruct = []

    def open_uinput_dev(self):
        if 'uinput-device' in self.config['user']['generic-config']:
            device_file = self.config['user']['generic-config']['uinput-device']
        elif 'uinput-device' in self.config['system']['generic-config']:
            device_file = self.config['system']['generic-config']['uinput-device']
        else:
            device_file = self._guess_uinput_dev(self)
        self.uinput_dev = os.open(device_file, os.O_RDWR)
        dev = ["BlueRemote",            # Name for device
           co.input['BUS_BLUETOOTH'],   # Bus where we stay on
           1,                           # Vendor ID
           1,                           # Product ID
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

        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_EVBIT'], co.input['EV_KEY'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_EVBIT'], co.input['EV_REL'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_RELBIT'], co.input['REL_X'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_RELBIT'], co.input['REL_Y'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_RELBIT'], co.input['REL_Z'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_RELBIT'], co.input['REL_WHEEL'])
        for i in xrange(0,256):
            fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], i)
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_MOUSE'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_TOUCH'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_MOUSE'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_LEFT'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_MIDDLE'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_RIGHT'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_FORWARD'])
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], co.input['BTN_BACK'])
        
        os.write(self.uinput_dev, device_structure)
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_DEV_CREATE'])
 
    def set_profile(self, config, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        logging.debug("UinputDispatcher: set_profile(%s, %s)" % (config, profile))
        # Stop pending events
        for invoked in self.invoked.values():
            for i in invoked:
                i.stop()
        # Set new profile up
        self.invoked  = {}
        self._interpret_profile(config, profile)
    
    def shutdown(self):
        for invoked in self.invoked.values():
            for i in invoked:
                i.stop()

    def _interpret_profile(self, config, profile):
        """
        Interpret the data from the profile and create appropriate uinput events
        additionally record the Events, that will be passed, to set the appropriate
        eventmasks on the uinputdevice
        """
        logging.debug("UinputDispatcher: _interpret_profile(%s, %s)" % (config, profile))
        
        self.init = []
        self.actions = {}
        self.destruct = []

        try:
            for action in self.config[config]['profiles'][profile]['UinputDispatcher']['actions']:
                logging.debug(str(action))
                event_tuple = (int(action['keycode']), 0)
                if not self.actions.has_key(event_tuple):
                    self.actions[event_tuple] = []
                if action['type'] == 'mouseaxis':
                    self.actions[event_tuple].append(MouseAxisEvent(action))
                if action['type'] == 'mousewheel':
                    self.actions[event_tuple].append(MouseWheelEvent(action))
                if action['type'] == 'mousebutton':
                    self.actions[event_tuple].append(MouseButtonEvent(action))
                if action['type'] == 'key':
                    self.actions[event_tuple].append(KeyPressEvent(action))
        except:
            logging.debug("UinputDispatcher: Error when interpreting action clause")
            pass

    def keycode(self, mapping, keycode):
        """
        The method maps the incoming keycode and mapping to the associated
        uinput events. And where appropriate it installs a repeathandler.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        int
        @param  keycode:        keycode received
        @type:  keycode:        int
        """
        logging.debug('Keycode: %i, Mapping: %i' % (keycode, mapping))
        event_tuple = (keycode, mapping)

        if mapping == 0:
            release_event_tuple = (keycode, 1)
        elif mapping == 1:
            release_event_tuple = (keycode, 0)

        if release_event_tuple in self.invoked:
            logging.debug('Stopping invoked UinputEvents')
            for event in self.invoked[release_event_tuple]:
                event.stop()
            del self.invoked[release_event_tuple]

        if event_tuple in self.actions:
            logging.debug('Invoked UinputEvents')
            for entry in self.actions[event_tuple]:
                if not event_tuple in self.invoked:
                    self.invoked[event_tuple] = []
                self.invoked[event_tuple].append(entry)
                entry.activate()

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

class Event(object):
    uinput_dev = None

    def __init__(self):
        # (keycode,mapping) => [callback_id, calls]
        # dictionaries, for handling repeats and cleanups of repeats
        self.repeathandler = []
        self.cleanup = []
        self.commands = []
        self.repeat_freq = 0
        self.repeat_func = None
        self.repeat_commands = []
        self.type = 'Generic Event'

    @classmethod
    def set_uinput_dev(cls, uinput_dev):
        cls.uinput_dev = uinput_dev

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
        freq = self._lin_mouse_freq(x,n);
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

    def _repeater(self):
        """
        Handle repeats of keystrokes
        """
        repeathandler = self.repeathandler
        repeathandler[1] += 1
        if self.repeat_commands:
            self._send_commands(self.repeat_commands, self.repeat_freq, repeathandler[1])
        else:
            self._send_commands(self.commands, self.repeat_freq, repeathandler[1])
        freq = self.repeat_func(self.repeat_freq, repeathandler[1])
        repeathandler[0] = gobject.timeout_add(int(1000.0/freq), self._repeater)
        return False

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
        logging.debug("Event: %i, %i, %i" % (event,descriptor,param))
        os.write(self.uinput_dev, struct.pack("LLHHl", time.time(), 0, event, descriptor, param))

    def activate(self):
        logging.debug("Event activated: " + self.type)
        self._send_commands(self.commands, 0, 0)
        if self.repeat_freq:
            self.repeathandler = []
            freq = self.repeat_func(self.repeat_freq, 0)
            self.repeathandler.append(gobject.timeout_add(int(1000.0/freq), self._repeater))
            self.repeathandler.append(0)

    def stop(self):
        if self.repeathandler:
            gobject.source_remove(self.repeathandler[0])
        if self.cleanup:
            self._send_commands(self.cleanup, 0, 0)

class MouseAxisEvent(Event):
    def __init__(self, action):
        Event.__init__(self)
        self.type = 'MouseAxisEvent'
        axis = co.input["REL_" + action['map_to'][1:2]]
        direction = action['map_to'][0:1]
        self.repeat_freq = 10
        self.repeat_func = self._lin_mouse_freq
        if direction == "-":
            self.commands = [(co.input['EV_REL'], axis, lambda x,y: -1 * self._lin_mouse_step(x,y))]
        else:
            self.commands = [(co.input['EV_REL'], axis, lambda x,y: self._lin_mouse_step(x,y))]

class MouseWheelEvent(Event):
    def __init__(self, action):
        Event.__init__(self)
        self.type = 'MouseWheelEvent'
        axis = co.input["REL_" + action['map_to'][1:]]
        direction = action['map_to'][0:1]
        self.repeat_freq = int(action['repeat_freq'])
        self.repeat_func = lambda x,n: x
        if direction == "-":
            self.commands = [(co.input['EV_REL'], axis, -1)]
        else:
            self.commands = [(co.input['EV_REL'], axis, 1)]

class MouseButtonEvent(Event):
    def __init__(self, action):
        Event.__init__(self)
        self.type = 'MouseButtonEvent'
        bt = co.input["BTN_" + action['map_to']]
        self.commands = [(co.input['EV_KEY'], bt, 1)]
        self.cleanup = [(co.input['EV_KEY'], bt, 0)]

class KeyPressEvent(Event):
    def __init__(self, action):
        Event.__init__(self)
        self.type = 'KeyPressEvent'
        for part in action['map_to'].split("+"):
            k =  co.input["KEY_" + part]
            self.commands.append((co.input['EV_KEY'], k, 1))
            self.repeat_commands.append((co.input['EV_KEY'], k, 1))
            self.repeat_commands.insert(0, (co.input['EV_KEY'], k, 0))
            self.cleanup.insert(0, (co.input['EV_KEY'], k, 0))
            
        if 'repeat_freq' in action:
             self.repeat_freq = int(action['repeat_freq'])
             self.repeat_func = self._const_key
