import logging
import json

from LBRC.path import path
from LBRC.l10n import _

class config(object):
    """
    The config class is a wrapper around the json on disk configuration format.
    """
    def __init__(self):
        self.paths = path()
        self.user = None
        self.system = None
        self.reread()
    
    def reread(self):
        """
        Reread config from disk. There is no distinction between system and user config
        files. Both will be reread.
        """
        try:
            self.user = self._read_config(self.paths.get_userconfigfile())
        except IOError:
            logging.debug(_("Could not open config file: %s"), self.paths.get_userconfigfile())
            self.user = {}
            self.user['generic-config'] = {}
            self.user['profiles'] = {}
        try:
            self.system = self._read_config(self.paths.get_systemconfigfile())
        except IOError:
            logging.debug(_("Could not open config file: %s"), self.paths.get_systemconfigfile())
            self.system = {}
            self.system['generic-config'] = {}
            self.system['profiles'] = {}
    
        self.profile_index = []
        self.profile_index.extend([('system', profile_name) for profile_name in self.system['profiles']])
        self.profile_index.extend([('user', profile_name) for profile_name in self.user['profiles']])

    def get_profile(self, config=None, profile=None, section=None):
        """
        Fetch profile from config files.
        
        @param    config:    config file selection (user/system)
        @type     config:    String
        @param    profile:   profile to fetch data from
        @type     profile:   String
        @param    section:   For which module do we fetch information (== classname)
        @type     section:   String
        """
        if config=='user':
            return self.user['profiles'][profile][section]
        else:
            return self.system['profiles'][profile][section]

    def set_config_item(self, name, value):
        """
        Set generic configuratin value C{name} to C{value}. These
        settings are only stored in the user config
        
        @param    name:    name of configuration value
        @type     name:    String
        @param    value:   value of configuration value
        @type     value:   Object (seriasable)
        """
        self.user['generic-config'][name] = value

    def get_config_item_fb(self, name, default):
        """
        Get a generic configuration value. The value is resolved from
        the user, to the system config file. If the configuration value
        is not found, the supplied default value will be returned.
        
        @param    name:    name of configuration value to fetch
        @type     name:    String
        @param    default: default value, if value is not set in config files
        @type     default: Object
        """
        try:
            return self.user['generic-config'][name]
        except:
            try:
                return self.system['generic-config'][name]
            except:
                return default

    def get_config_item(self, name):
        """
        Fetch the configuration value of name C{name}. It returns a
        dictionary using C{user} and C{system} as keys and the
        corresponting values as value.
        
        @param    namme:    name of configuration value to fetch
        @type     name:     String
        """
        result = {}
        try:
            result['user'] = self.user['generic-config'][name]
        except:
            pass
        try:
            result['system'] = self.system['generic-config'][name]
        except:
            pass
        return result

    def write(self):
        """
        Write user configuration to file
        """
        try:
            self._write_config(self.paths.get_userconfigfile(), self.user)
        except Exception, e:
            logging.error(_("Could not write config file: %s\n%s") % (self.paths.get_userconfigfile(), str(e)))
    
    @staticmethod
    def _write_config(absfilename, config):
        """
        Serialize configuration stored in C{config} and write to file
        
        @param    absfilename:    Filename to store config in
        @type     absfilename:    String
        @param    config:         dictionary holding the config data
        @type     config:         dictionary
        """
        config_file = open(absfilename, 'w')
        json_writer = json.JsonWriter()
        config_data = json_writer.write(config)
        config_file.write(config_data)
        config_file.close()
    
    @staticmethod
    def _read_config(absfilename):
        """
        Parse configuration from file
        
        @param absfilename:    Filename to read data from
        """
        config = {}
        config_file = open(absfilename)
        config_data = config_file.read()
        json_reader = json.JsonReader()
        config = json_reader.read(config_data)
        config_file.close()
        return config