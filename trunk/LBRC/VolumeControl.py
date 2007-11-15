from LBRC.Listener import Listener
import logging
import gobject
import re
from subprocess import Popen, PIPE, call

class VolumeCommand(object):
    def __init__(self, parent, description):
        self.parent = parent
        self.description = description
    
    def call(self):
        description = self.description
        logging.debug("VolumeControl - Doing call for: " + str(description))
        if 'change' in description:
            command = [
                       "/usr/bin/amixer",
                       "-c",
                       str(description["card"]),
                       'sset',
                       str(description["channel"]),
                       str(description["change"])
                       ]
            call( command )
            logging.debug("VolumeControl - Call done: " + str(command))
            self.parent.sendVolumeUpdate()
            
        elif 'ShowVolumeControl' in description:
            query = {'type': "displayControl", 
                     'command': 'showModule',
                     "param": "VolumeControl",
                     };
            if not description['ShowVolumeControl']:
                query['command'] = 'hideModule'
            logging.debug("Getting BT Connection")
            bc = self.parent.bluetooth_connector.get_bt_connection()
            logging.debug("Got: " + str(bc))
            if bc != None:
                bc.send_query(query)
            
            logging.debug("Calling VolumeUpdate")
            self.parent.sendVolumeUpdate()
            
        elif 'ShowChannels' in description:
            self.parent.setVisibleDevices(description['ShowChannels']);

class VolumeControl(Listener):
    """
    Class to handle keycodes received by BTServer and issue commands according to them
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         dictionary
        """
        Listener.__init__(self, config, 'VolumeControl', command_class=VolumeCommand)
        self.devices = []

    def setVisibleDevices(self, devices):
        self.devices = []
        for device in devices:
            self.devices.append({"card": device[0], "channel": device[1]})

    @staticmethod
    def _getVolume(card, channel):
        output = Popen(["/usr/bin/amixer", "-c", str(card), 'sget', str(channel)], stdout=PIPE).communicate()[0]
        regexp = re.compile("\[(\d+)%\]")
        for line in output.split("\n"):
            if "Playback" in line and "%]" in line:
                logging.debug('match')
                ret = regexp.search(line)
                if not ret:
                    next
                else:
                    return ret.group(1)

    def sendVolumeUpdate(self):
        query = {'type': "VolumeControl",
                 "command": "updateVolumes",
                 "volumeData": []
                 }
        for dev in self.devices:
            name = str(dev['card']) + " - " + str(dev['channel'])
            volume = self._getVolume(dev['card'], dev['channel'])
            query['volumeData'].append([name, volume])
        bc = self.bluetooth_connector.get_bt_connection()
        if bc != None:
            bc.send_query(query)

    def shutdown(self):
        for command in self.destruct:
            command.call()
