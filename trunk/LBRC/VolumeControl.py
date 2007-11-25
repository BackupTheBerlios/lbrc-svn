# TODO: Check how much overhead is produced by invoking the gstreamer constructor each time
from LBRC.Listener import Listener
import logging
import gobject
import gst
import gst.interfaces
import re
from subprocess import Popen, PIPE, call

class VolumeCommand(object):
    percent_re = re.compile('([+-])(\d+)%')
    
    def __init__(self, parent, description):
        self.parent = parent
        self.description = description
    
    def _volume_change(self):
        logging.debug("VolumeControl: Start of volume_change")
        option_set = self.parent.default_properties.copy()
        option_set.update(self.description)
        if not "change" in option_set or \
           not "sound_system" in option_set:
            logging.error("Incomplete option_set for Volume Change: " + str(option_set))
            return
        
        if option_set['sound_system'] == 'alsa':
            mixer = gst.element_factory_make('alsamixer')
        elif option_set['sound_system'] == 'oss':
            mixer = gst.element_factory_make('ossmixer')
        else:
            logging.error('Unbekanntes Sound System: ' + option_set['sound_system'])
            return
        
        logging.debug("VolumeControl: Pre set_property")
        if 'device' in option_set:
            mixer.set_property('device', option_set['device'])
        mixer.set_state(gst.STATE_PAUSED)
        if not 'channel' in option_set:
            track = mixer.list_tracks()[0]
        else:
            track = None
            for t in mixer.list_tracks():
                if t.label == option_set['channel']:
                    track = t
                    break
            if track == None:
                logging.error('Specified channel not found!')
        
        logging.debug("VolumeControl: Pre change")
        match = self.percent_re.match(option_set['change'])
        if (match):
            logging.debug('change volume')
            old_volume = mixer.get_volume(track)
            logging.debug('old volume: ' + str(old_volume))
            change = 1
            if match.group(1) == '-':
                change = -1
            change *= int(match.group(2)) * (track.max_volume-track.min_volume) / 100
            new_volume = [ov + change for ov in old_volume]
            mixer.set_volume(track, tuple(new_volume))
        elif option_set['change'] == 'toggle':
            logging.debug('toggle mute')
            mixer.set_mute(track, (not gst.interfaces.MIXER_TRACK_MUTE & track.flags))
        mixer.set_state(gst.STATE_NULL)
        logging.debug("VolumeControl: End of volume_change")
            
    
    def call(self):
        description = self.description
        logging.debug("VolumeControl - Doing call for: " + str(description))
        if 'change' in description:
            try:
                self._volume_change()
            except Exception, e:
                logging.debug(str(e))
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
        elif 'SetDefault' in description:
            logging.debug("Setting defaults")
            try:
                self.parent.default_properties.update(description['SetDefault'])
            except Exception, e:
                logging.debug(str(e))
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
        self.default_properties = {}

    def setVisibleDevices(self, devices):
        self.devices = []
        for device in devices:
            option_set = self.default_properties.copy()
            option_set.update(device)
            self.devices.append(option_set)
        logging.debug("end setVisibleDevices")

    @staticmethod
    def _getVolume(option_set):
        if not "channel" in option_set or \
           not "sound_system" in option_set:
            logging.error("Incomplete option_set for Volume Change: " + str(option_set))
            return
        
        if option_set['sound_system'] == 'alsa':
            mixer = gst.element_factory_make('alsamixer')
        elif option_set['sound_system'] == 'oss':
            mixer = gst.element_factory_make('ossmixer')
        else:
            logging.error('Unbekanntes Sound System: ' + option_set['sound_system'])
            return
        
        logging.debug("VolumeControl: Pre set_property")
        if 'device' in option_set:
            mixer.set_property('device', option_set['device'])
        mixer.set_state(gst.STATE_PAUSED)
        track = None
        for t in mixer.list_tracks():
            if t.label == option_set['channel']:
                track = t
                break
        if track == None:
            logging.error('Specified channel not found!')
        logging.debug("end _getVolume")
        volume = int(100 * mixer.get_volume(track)[0] / track.max_volume)
        mixer.set_state(gst.STATE_NULL)
        return str(volume)

    def sendVolumeUpdate(self):
        query = {'type': "VolumeControl",
                 "command": "updateVolumes",
                 "volumeData": []
                 }
        for dev in self.devices:
            name = str(dev['channel'])
            volume = self._getVolume(dev)
            query['volumeData'].append([name, volume])
        bc = self.bluetooth_connector.get_bt_connection()
        if bc != None:
            bc.send_query(query)

    def shutdown(self):
        for command in self.destruct:
            command.call()
