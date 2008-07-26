"""See class documentation of MPlayer"""

from LBRC.Listener import Listener
from LBRC.path import path
from LBRC.l10n import _
from subprocess import Popen, PIPE
import logging
import os
import os.path as osp

class MPlayerStartupException(Exception):
    """
    Exception is thrown, when MPlayer can't be connected of started.
    """
    pass

class CommandWrapper(dict):
    """This is a very thin wrapper around a dict, so that it can be used
    as a ListenerCommand class. So that the super._interpret_profile can
    be used and only keycode has to be implemented in MPlayer"""
    def __init__(self, dummy, description):
        """
        dummy is needed to be compatible with the rest of the CommandClasses
        """
        dict.__init__(self)
        self.update(description)

class MPlayerEngine(object):
    """
    Just a wrapper
    """
    def __init__(self, **kwdargs):
        self.path = path()
        self.logger = logging.getLogger('LBRC.Listener.MPlayerEngine')
        self.stdin = None
        if 'fifo' in kwdargs:
            fifo = kwdargs['fifo']
            if not osp.exists(fifo):
                self.logger.debug("FIFO does not exist: %s" % fifo)
                raise MPlayerStartupException()
            try:
                mplayer_fd = os.open(fifo, os.O_NONBLOCK | os.O_WRONLY)
                self.mplayer_pipe = os.fdopen(mplayer_fd, "w")
            except IOError, exception:
                self.logger.error("Failed to open FIFO: %s\n%s" % 
                                  (fifo, str(exception)))
                raise MPlayerStartupException()
        else:
            self.mplayer = Popen(["mplayer",  "-slave", "-idle", "-quiet"], 
                                  stdin=PIPE)
            try:
                self.mplayer_pipe = self.mplayer.stdin
                self.command("loadfile %s" % 
                             self.path.get_datafile("LBRCback.avi"))
                self.command("pause")
            except IOError, exception:
                self.logger.error("Failed to connect to MPlayer: %s\n%s" % 
                                  (fifo, str(exception)))

    def command(self, command):
        """Send command to mplayer instance"""
        self.mplayer_pipe.write(command + "\n")
        self.mplayer_pipe.flush()
        
    def disconnect(self):
        """Close connection to running mplayer instance"""
        self.mplayer_pipe.close()

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
        
        - b{connect_fifo <fifo_path>} Connect to a running mplayer instance
        
        Connect to a mplayer instance, that is running in slave mode and listens
        on the fifo supplied by <fifo_path>
        
        - b{disconnect_fifo} Disconnect from running mplayer
        
    For an example see the system wide config file in the MPlayer section.
    """
    def __init__(self, config):
        """
        @param  config:         configuration data
        @type   config:         dictionary
        """
        Listener.__init__(self, config, "MPlayer", command_class=CommandWrapper)
        self.path = path()
        self.querytype = None
        self.querymap = None
        self.mplayer = None
    
    def _handle_list_reply(self, index):
        """
        This method is called, when a reply is send from the phone regarding
        the list selection request we send from L{keycode}
        """
        self.logger.debug("ListReply: " + self.querytype + " " + str(index))
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
            except IOError:
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
        for filename in files:
            if filename[0] == ".":
                continue
            fullname = osp.join(base, filename)
            filename = filename.decode('utf-8')
            if osp.isfile(fullname):
                self.querymap.append((filename, fullname, 'f'))
            elif osp.isdir(fullname):
                self.querymap.append(("[" + filename + "]", fullname, 'd'))
                
        def sort_filelist(file1, file2):
            """
            Custom sort method for sort function. Sorts directories before
            files and each group alphabetically
            """
            if file1[2] == file2[2]:
                return cmp(file1[0], file2[0])
            else:
                if file1[2] == 'd':
                    return -1
                else:
                    return 1
        self.querymap.sort(sort_filelist)
        self.querymap.insert(0, ("[..]", 
                                 osp.normpath(osp.join(base, "..")), 
                                 'd'))
        self.querytype = 'fileselection'
        btconnection = self.bluetooth_connector.get_bt_connection()
        btconnection.send_list_query(_("Select file"), 
                                     [i[0] for i in self.querymap],
                                     self._handle_list_reply)

    def _execute_command_non_running(self, command):
        """Excute commands assuming a mplayer instance is not present"""
        if command == "switch_on" or \
           command == "toggle_onoff":
            try:
                self.mplayer = MPlayerEngine()
            except MPlayerStartupException, exception:
                self.logger.error("Error while starting MPlayer: %s" %
                                   repr(exception))
                self.mplayer = None
        elif "connect_fifo" == command[0:12]:
            try:
                self.mplayer = MPlayerEngine({'fifo': command[13:]})
            except MPlayerStartupException, exception:
                self.logger.error("Error while connection to MPlayer " +
                                  " FIFO: %s" % repr(exception))
                self.mplayer = None
    
    def _execute_command_running(self, command):
        """Excute commands assuming a mplayer instance is present"""
        try:
            if command == "quit" or \
               command == "toggle_onoff":
                self.mplayer.command("quit")
                self.mplayer = None
            elif command.startswith("remote_fileselect"):
                if len(command) > 18:
                    self._query_fileselection(command[18:])
                else:
                    self._query_fileselection()
            elif command == 'disconnect_fifo':
                self.mplayer.disconnect()
                self.mplayer = None
            else:
                self.mplayer.command(command)
        except IOError:
            self.mplayer = None
        
    def _execute_command(self, command):
        """Interpret a command"""
        self.logger.debug("Command:" + command)
        if self.mplayer:
            self._execute_command_running(command)
        else:
            self._execute_command_non_running(command)

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
                                
    def shutdown(self):
        """Execute destruct command, when we shutdown"""
        for command in self.destruct:
            self._execute_command(command["command"])
