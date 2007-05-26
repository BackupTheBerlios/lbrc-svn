import time
import os.path as osp

class CompanionCommand(object):
    def __init__(self, parent, description):
        self.parent = parent
        self.description = description

    def call(self):
        query = {'type': 'presentationControl'}
        if self.description['command'] == 'show':
            query['command'] = 'showModule'
        elif self.description['command'] == 'hide':
            query['command'] = 'hideModule'
        elif self.description['command'] == 'nextSlide':
            self.parent.change_slide(1)
            query['command'] = 'changeSlide'
            query['param'] = 1
        elif self.description['command'] == 'previousSlide':
            self.parent.change_slide(-1)
            query['command'] = 'changeSlide'
            query['param'] = -1
        elif self.description['command'] == 'startPresentation':
            self.parent.set_slide(1)
            query['command'] = 'setSlide'
            query['param'] = 1
        elif self.description['command'] == 'stopPresentation':
            self.parent.write()
        elif self.description['command'] == 'toggleWrite':
            self.parent.set_write(not self.parent.get_write())
        if 'command' in query:
            bc = self.parent.bluetooth_connector.get_bt_connection()
            if bc:
                bc.send_query(query)

class PresentationCompanion(object):
    """
    Class to handle keycodes received by BTServer and issue commands according to them
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         dictionary
        """
        self.config = config
        self.visible = False
        self.bluetooth_connector = None
        self.core = None
        self._write = False
        self.slide = 1
        self.buffer = []
        self.init = []
        self.actions = {}
        self.destruct = []
        
    def set_bluetooth_connector(self, bc):
        """
        Set our bluetooth connector, that allows us to issue the presentation
        of a list, from which the user can choose the new profile
        
        @param    bc:    Bluetooth Adapter
        @type     bc:    L{BTServer}
        """
        self.bluetooth_connector = bc        

    def set_core(self, core):
        """
        Set the core, where the administration of the profiles happens
        Currently this is dbusinterface
        
        @param   core:    Core, where profiles are handled
        @type    core:    L{dbusinterface}
        """
        self.core = core
        
    def keycode(self, mapping, keycode):
        """
        The method maps the incoming keycode and mapping to the associated
        command and spawns a subprocess for them.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        int
        @param  keycode:        keycode received
        @type   keycode:        int
        """
 
        event_tuple = (keycode, mapping)
        if event_tuple in self.actions:
            for command in self.actions[event_tuple]:
                command.call()
    
    def set_profile(self, config, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        for command in self.destruct:
            command.call()
        self._interpret_profile(config, profile)
        for command in self.init:
            command.call()
                                
    def _interpret_profile(self, config, profile):
        """
        Interpret the profile data from the profile.conf(s) and push the commands into
        an array and call it, when the appropriate keycodes and mappings are received.

        If no mapping is provided, we assume mapping = 0 => keypress
        """
        self.init = []
        self.actions = {}
        self.destruct = []
        try:
            for init in self.config.get_profile(config, profile, 'PresentationCompanion')['init']:
                self.init.append(CompanionCommand(self, init))
        except:
            pass
        try:
            for destruct in self.config.get_profile(config, profile, 'PresentationCompanion')['destruct']:
                self.destruct.append(CompanionCommand(self, destruct))
        except:
            pass
       
        try:
            for action in self.config.get_profile(config, profile, 'PresentationCompanion')['actions']:
                try:
                    mapping = int(action['mapping'])
                except:
                    mapping = 0
                event_tuple = (int(action['keycode']), mapping)
                if not event_tuple in self.actions:
                    self.actions[event_tuple] = []
                self.actions[event_tuple].append(CompanionCommand(self, action))
        except:
            pass
    
    def change_slide(self, slide_change):
        self.slide = self.slide + int(slide_change)
        self.log("Slide %4d" % (self.slide,))
    
    def set_slide(self, slide):
        self.slide = int(slide)
        self.log("Slide %4d" % (self.slide,))
    
    def log(self, message):
        self.buffer.append([time.time(), message])
    
    def get_write(self):
        return self._write
    
    def set_write(self, value):
        if value:
            self._write = True
        else:
            self._write = False
    
    def write(self):
        if self._write and self.buffer:
            first_time = time.localtime(self.buffer[0][0])
            filename = time.strftime("Presentation %Y-%m-%d %H:%M:%S", first_time)
            f = open(osp.join(osp.expanduser("~"), filename), "w")
            last_event = None
            for i in self.buffer:
                tstring = time.strftime("%H:%M:%S", time.localtime(i[0]))
                if last_event:
                    diff = '%5ds' % (i[0] - last_event, )
                else:
                    diff = ' START'
                last_event = i[0]
                f.write(tstring + " " + diff + " " + i[1] + "\n")
            f.close()
            
        self.buffer = []
    
    def shutdown(self):
        pass