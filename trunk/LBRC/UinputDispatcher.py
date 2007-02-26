#!/usr/bin/python

import os, struct, fcntl, time
import os.path as osp
import logging
import LBRC.consts as co

class UinputDispatcher(object):
    def __init__(self, device_file="/dev/input/uinput", **kwds):
        device_file = ''
        if 'device_file' in kwds:
            device_file = kwds['device_file']
        else:
            device_file = self.__guess_uinput_dev(self)
        self.uinput_dev = os.open(device_file, os.O_RDWR)
        dev = ["BlueRemote",            # Name for device
           co.input['BUS_BLUETOOTH'],  # Bus where we stay on
           1,                       # Vender ID
           1,                       # Produkt ID
           1,                       # Version ID
           0                        # We don't support force feedback
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
        if 'relative_axes' in kwds:
            fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_EVBIT'], co.input['EV_REL'])
            for axis in kwds['relative_axes']:
                fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_RELBIT'], axis)
        if 'keys' in kwds:
            fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_EVBIT'], co.input['EV_KEY'])
            for key in kwds['keys']:
                fcntl.ioctl(self.uinput_dev, co.uinput['UI_SET_KEYBIT'], key)
        
        fcntl.ioctl(self.uinput_dev, co.uinput['UI_DEV_CREATE'])
    
    def send_event(self, event, descriptor, param):
        os.write(self.uinput_dev, struct.pack("LLHHl", time.time(), 0, event, descriptor, param))

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
