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
            not cls._init_fhs()):
            cls._local = True

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
            print osp.join(self.data_dir, 'locale')

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

    def get_userconfigfile(self, name):
        """
        Returns absolute path to a user config file with C{name} name

        @param  name:   name of the config file
        @type   name:   string
        @return:    path to the config file
        @rtype:     string
        """
        return osp.join(osp.expanduser("~"), ".lbrc", name)

    def get_systemconfigfile(self, name):
        """
        Returns absolute path to a system config file with C{name} name

        @param name: name of config file
        @type  name: string
        @return:    absolute path for a config file
        @rtype:     string
        """
        if self._local:
            return osp.join(scriptpath, "profiles.conf")
        else:
            for location in self.config_dirs:
                f = osp.join(location, name)
                if osp.isfile(f):
                    return f

    def get_configfiles(self, name):
        """
        Returns a list of absolute paths to all config files with C{name} name and verify if the path is a file.

        @param  name:   name of cofig file
        @type   name:   string
        @return:    list of complete paths to config files
        @rtype:     list of strings
        """
        paths = []

        for f in self.get_systemconfigfile(name),self.get_userconfigfile(name):
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
