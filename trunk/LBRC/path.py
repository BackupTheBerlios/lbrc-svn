# These entries are for packagers
# To make them take effect you have to set them all!
# 
# PLEASE MODIFY ONLY IF NEEDED
#
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
#
#
# TODO:
# - add "all in one detection and configuration"

prefix = ""
bin_dir = ""
data_dir = ""
config_dirs = []

import os.path as osp
import sys

scriptpath = osp.dirname(osp.abspath(sys.argv[0]))

class path(object):
    @classmethod
    def _class_init(cls):
        cls._local = False
        if (not cls._init_fixed() and
            not cls._init_prefix() and
            not cls._init_fhs()):
            cls._local = True

    @classmethod
    def _init_prefix(cls):
        if prefix:
            cls.bin_dir = osp.join(prefix, 'bin')
            cls.data_dir = osp.join(data_dir, 'share')
            cls.config_dir = ['/etc', osp.join(prefix, 'share', 'lbrc')]
            return True
        return False

    @classmethod
    def _init_fixed(cls):
        if bin_dir and data_dir and config_dirs:
            cls.bin_dir = bin_dir
            cls.data_dir = data_dir
            cls.config_dirs = config_dirs
            return True
        else:
            return False

    @classmethod
    def _init_fhs(cls):
        if osp.isfile('/usr/local/share/lbrc/j2me/LBRC.jar'):
            cls.bin_dir = '/usr/local/bin'
            cls.data_dir = '/usr/local/share'
            cls.config_dirs = ['/usr/local/etc', '/etc',
                               '/usr/local/share/lbrc/']
            return True
        elif osp.isfile('/usr/share/lbrc/j2me/LBRC.jar'):
            cls.bin_dir = '/usr/bin'
            cls.data_dir = '/usr/share'
            cls.config_dirs = ['/etc', '/usr/share/lbrc/']
            return True
        elif osp.isfile('/opt/lbrc/share/lbrc/j2me/LBRC.jar'):
            cls.bin_dir = '/opt/lbrc/bin'
            cls.data_dir = '/opt/lbrc/share'
            cls.config_dirs = ['/etc', '/opt/etc', '/opt/lbrc/share/lbrc']
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
            return osp.join(scriptpath, "pot")
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
            return osp.join(scriptpath, "LBRC_gtk_gui")
        else:
            return osp.join(self.data_dir, 'lbrc')

    def get_userconfigfile(self):
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
            return osp.join(scriptpath, "lbrc.conf")
        else:
            for location in self.config_dirs:
                f = osp.join(location, "lbrc.conf")
                if osp.isfile(f):
                    return f

    def get_configfiles(self):
        """
        Returns a list of absolute paths to all config files.
        The method verifies that the paths point to a file.

        @return:    list of complete paths to config files
        @rtype:     list of strings
        """
        paths = []

        for f in self.get_systemconfigfile(),self.get_userconfigfile():
            if osp.isfile(f):
                paths.append(f)

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
            return osp.join(scriptpath, name)
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
            return osp.join(scriptpath, name)
        else:
            return osp.join(self.bin_dir, name)

path._class_init()
