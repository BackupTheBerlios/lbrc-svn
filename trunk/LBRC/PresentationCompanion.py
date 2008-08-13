from LBRC.Listener import Listener
import time
import os.path as osp

class CompanionCommand(object):
    def __init__(self, parent, description):
        self.parent = parent
        self.description = description

    def call(self):
        query = {'type': 'PresentationControl'}
        if self.description['command'] == 'show':
            query['type'] = 'displayControl'
            query['command'] = 'showModule'
            query['param'] = 'PresentationControl'
        elif self.description['command'] == 'hide':
            query['type'] = 'displayControl'
            query['command'] = 'hideModule'
            query['param'] = 'PresentationControl'
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

class PresentationCompanion(Listener):
    """
    Class to handle keycodes received by BTServer and issue commands according to them
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         dictionary
        """
        Listener.__init__(self, config, 'PresentationCompanion', command_class=CompanionCommand)
        self.visible = False
        self._write = False
        self.slide = 1
        self.buffer = []
        
        self.logger.debug("Loaded succesfully")
    
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
