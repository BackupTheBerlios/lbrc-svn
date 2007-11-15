from LBRC.Listener import Listener
import os.path as osp
import os
from subprocess import Popen, PIPE
import logging
from LBRC.path import path
from LBRC.l10n import _

class MPlayer(Listener):
    """
    MPlayer
    =======
    
    Class to handle keycodes received by BTServer and issue commands according to them
    
    This module enables you to establish a mplayer instance that you can control via
    the slave protocol of mplayer.
    
    For an explanation of the protocol please see I{tech/slave.txt} in the mplayer documentation.
    In addition to the commands defined there, three more commands are defined:
    
        - B{toggle_onoff}: If a mplayer instance is running close it, else start one new one
        
        If no instance of an mplayer is found (for this module) starts a new instance. If an
        instance is found it is shutdown.
        
        - B{switch_on}: If no mplayer instance is running start one
        
        In contrast to toggle_onoff this command does not shutdown an already running instance but
        instead turns into a noop.
        
        - b{remote_fileselect <path>} Display a file selection menu on the phone
        
        When <path> is provided, this path is used as base for the selection. If
        it is omitted, then the selection starts at the users homedir
        
    For an example see the system wide config file in the MPlayer section.
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         dictionary
        """
        Listener.__init__(self, config, "MPlayer")
        self.path = path()
        self.querytype = None
        self.querymap = None
        self.mplayer = None
    
    def _handle_list_reply(self, index):
        """
        This method is called, when a reply is send from the phone regarding
        the list selection request we send from L{keycode}
        """
        logging.debug("MPlayerListReply: " + self.querytype + " " + str(index))
        if self.querytype == 'fileselection':
            if index < 0:
                self.querytype = None
                self.querymap = None
                return
            try:
                selection = self.querymap[index]
                if selection[2] == 'f':
                    self._execute_command('loadfile "' + selection[1] + '"')
                    self.querytype = None
                    self.querymap = None
                elif selection[2] == 'd':
                    self._query_fileselection(base=selection[1])
            except:
                self.querytype = None
                self.querymap = None
              
    def _query_fileselection(self, base=None):
        """
        Create a fileselection menu. I{base} refers to the directory the selection
        is created for. If base is not supplied, the users home directory will be used.
        """
        self.querymap = []
        if not base:
            base = osp.expanduser("~")
        files = os.listdir(base)
        for file in files:
            if file[0] == ".":
                continue
            fullname = osp.join(base, file)
            file = file.decode('utf-8')
            if osp.isfile(fullname):
                self.querymap.append((file, fullname, 'f'))
            elif osp.isdir(fullname):
                self.querymap.append(("[" + file + "]", fullname, 'd'))
        def sort_filelist(a, b):
            if a[2] == b[2]:
                return cmp(a[0], b[0])
            else:
                if a[2] == 'd':
                    return -1
                else:
                    return 1
        self.querymap.sort(sort_filelist)
        self.querymap.insert(0, ("[..]", osp.normpath(osp.join(base, "..")), 'd'))
        self.querytype = 'fileselection'
        btconnection = self.bluetooth_connector.get_bt_connection()
        btconnection.send_list_query(_("Select file"), 
                                     [i[0] for i in self.querymap],
                                     self._handle_list_reply)

    def _execute_command(self, command):
        logging.debug("MPlayerCommand:" + command)
        if self.mplayer:
            try:
                if command == "quit" or \
                   command == "toggle_onoff":
                    self.mplayer.stdin.write("quit\n")
                    self.mplayer.stdin.flush()
                    self.mplayer = None
                elif command == "remote_fileselect":
                    logging.debug("Fileselect started")
                    self._query_fileselection()
                else:
                    self.mplayer.stdin.write(command + "\n")
                    self.mplayer.stdin.flush()
            except IOError:
                self.mplayer = None
        else:
            if command == "switch_on" or \
               command == "toggle_onoff":
                self.mplayer = Popen(["mplayer",  "-slave", "-idle", "-quiet"], stdin=PIPE)
                self.mplayer.stdin.write("loadfile " + self.path.get_datafile("LBRCback.avi") + "\n")
                self.mplayer.stdin.write("pause\n")

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
                self._execute_command(command["command"])
    
    def set_profile(self, config, profile):
        """
        Switch to new profile

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        for command in self.destruct:
            self._execute_command(command["command"])
        self._interpret_profile(config, profile)
        for command in self.init:
            self._execute_command(command["command"])
                                
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
            for init in self.config.get_profile(config, profile, 'MPlayer')['init']:
                self.init.append(init)
        except:
            pass
        try:
            for destruct in self.config.get_profile(config, profile, 'MPlayer')['destruct']:
                self.destruct.append(destruct)
        except:
            pass
       
        try:
            for action in self.config.get_profile(config, profile, 'MPlayer')['actions']:
                try:
                    mapping = int(action['mapping'])
                except:
                    mapping = 0
                event_tuple = (int(action['keycode']), mapping)
                if not event_tuple in self.actions:
                    self.actions[event_tuple] = []
                self.actions[event_tuple].append(action)
        except:
            pass

    def shutdown(self):
        for command in self.destruct:
            self._execute_command(command["command"])
