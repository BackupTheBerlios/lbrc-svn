"""Module/Class providing some detection for the installation paths"""
# Theses cases are covered by the module:
#
# - FHS Installations
#   - Packages normaly placed in /usr/local or /usr
#   - Installations under /opt/lbrc
# - "all in one directory installations", like FHS under /opt/lbrc
# - "running from our directory"
#
# Please note: Only the installation into /usr/local or
# /usr will activate dbus activation!

# These entries are for packagers
# PLEASE MODIFY ONLY IF NEEDED - YOU HAVE BEEN WARNED!
#
# To make them take effect you have to set them all!
# These will superseed every other detection scheme
_BIN_DIR = ""
_DATA_DIR = ""
_CONFIG_DIRS = []
# Set _PREFIX if installed into a prefix other than the fhs ones
# is superseeded by the above options, superseeds fhs detection
_PREFIX = ""

import os.path as osp
import sys

_SCRIPTPATH = osp.dirname(osp.abspath(sys.argv[0]))

class path(object):
    """LBRC.path is a singleton holding the paths necessary to run LBRC
    consider it readonly - you have been warned!"""
    # pylint: disable-msg=W0142
    def __new__(cls, *args):
        try:
            return cls._singleton
        except AttributeError:
            # Create singleton - so do some magic here - its intended
            cls._singleton = super(path, cls).__new__(cls, *args)            
            return cls._singleton
    # pylint: enable-msg=W0142
    
    def __init__(self):
        self._local = False
        self.bin_dir = None
        self.data_dir = None
        self.config_dirs = None
        if (not self._init_fixed() and
            not self._init_prefix() and
            not self._init_fhs()):
            self._local = True

    def _init_prefix(self):
        """If _PREFIX is defined, init path to be based on that"""
        if _PREFIX:
            self.bin_dir = osp.join(_PREFIX, 'bin')
            self.data_dir = osp.join(_PREFIX, 'share')
            self.config_dirs = ['/etc', osp.join(_PREFIX, 'share', 'lbrc')]
            return True
        return False

    def _init_fixed(self):
        """Some people have their own ideas about the filesystem layout
        this allows them to have their ideas realised"""
        if _BIN_DIR and _DATA_DIR and _CONFIG_DIRS:
            self.bin_dir = _BIN_DIR
            self.data_dir = _DATA_DIR
            self.config_dirs = _CONFIG_DIRS
            return True
        else:
            return False

    def _init_fhs(self):
        """The FHS allows several places for LBRC to reside - take these
        into account and adjust paths accordingly"""
        if osp.isfile('/usr/local/share/lbrc/j2me/LBRC.jar'):
            self.bin_dir = '/usr/local/bin'
            self.data_dir = '/usr/local/share'
            self.config_dirs = ['/usr/local/etc', '/etc',
                               '/usr/local/share/lbrc/']
            return True
        elif osp.isfile('/usr/share/lbrc/j2me/LBRC.jar'):
            self.bin_dir = '/usr/bin'
            self.data_dir = '/usr/share'
            self.config_dirs = ['/etc', '/usr/share/lbrc/']
            return True
        elif osp.isfile('/opt/lbrc/share/lbrc/j2me/LBRC.jar'):
            self.bin_dir = '/opt/lbrc/bin'
            self.data_dir = '/opt/lbrc/share'
            self.config_dirs = ['/etc', '/opt/etc', '/opt/lbrc/share/lbrc']
            return True
        return False

    def get_localedir(self):
        """
        Return path to directory, where out l10n files
        are located.

        @return:    path to locale dir
        @rtype:     string
        """
        if self._local:
            return osp.join(_SCRIPTPATH, "pot")
        else:
            return osp.join(self.data_dir, 'locale')

    def get_guidir(self):
        """
        Return path to directory where *.glade files 
        are located.

        @return:    path to gui dir
        @rtype:     string
        """
        if self._local:
            return osp.join(_SCRIPTPATH, "LBRC_gtk_gui")
        else:
            return osp.join(self.data_dir, 'lbrc')

    @staticmethod
    def get_userconfigfile():
        """
        Returns absolute path to the user config file
        
        @return:    path to the config file
        @rtype:     string
        """
        return osp.join(osp.expanduser("~"), ".lbrc.conf")

    def get_systemconfigfile(self):
        """
        Returns absolute path to the system config file
        
        @return:    absolute path for a config file
        @rtype:     string
        """
        if self._local:
            return osp.join(_SCRIPTPATH, "lbrc.conf")
        else:
            for location in self.config_dirs:
                fullfilename = osp.join(location, "lbrc.conf")
                if osp.isfile(fullfilename):
                    return fullfilename

    def get_configfiles(self):
        """
        Returns a list of absolute paths to all config files.
        The method verifies that the paths point to a file.

        @return:    list of complete paths to config files
        @rtype:     list of strings
        """
        paths = []

        for filename in self.get_systemconfigfile(), self.get_userconfigfile():
            if osp.isfile(filename):
                paths.append(filename)

        return paths

    def get_datafile(self, name):
        """
        Returns absolute path to a data file with C{name} name

        @param  name:   name of data file
        @type   name:   string
        @return:    absolute path to data file
        @rtype:     string
        """
        if self._local:
            return osp.join(_SCRIPTPATH, name)
        else:
            return osp.join(self.data_dir, 'lbrc', name)

    def get_binfile(self, name):
        """
        Returns absolute path to executable with C{name} name

        @param  name:   name of executable
        @type   name:   string
        @return:    path to executable
        @rtype:     string
        """
        if self._local:
            return osp.join(_SCRIPTPATH, name)
        else:
            return osp.join(self.bin_dir, name)