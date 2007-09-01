import logging
import json
import gobject

from LBRC.path import path
from LBRC.l10n import _

class configValueNotFound(Exception):
    """
    Base class for L{noConfigException}, L{profileNotFoundException}
    and L{sectionNotFoundException}. These are fired, when a config
    value could not be fetched.
    """

class profileNotFoundException(configValueNotFound):
    """
    Raised, when a profile is queried that does not exist
    """
    
class sectionNotFoundException(configValueNotFound): 
    """
    Raised, when a section is queried, that does not exist
    """
    
class noConfigException(configValueNotFound):
    """
    Raised, when a config is queried, that does not exist
    """

class config(gobject.GObject):
    __gsignals__ = {
                    'config-reread': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
                   }
    """
    The config class is a wrapper around the json on disk configuration format.
    """
    def __init__(self):
        gobject.GObject.__init__(self)
        self.paths = path()
        self.user = None
        self.system = None
        self.reread()
    
    def reread(self):
        """
        Reread config from disk. There is no distinction between system and user config
        files. Both will be reread.
        """
        self.user = None
        self.system = None
        try:
            self.user = self._read_config(self.paths.get_userconfigfile())
        except IOError:
            pass
        if not self.user:
            logging.debug(_("Could not open config file: %s"), self.paths.get_userconfigfile())
            self.user = {}
            self.user['generic-config'] = {}
            self.user['profiles'] = {}
        try:
            self.system = self._read_config(self.paths.get_systemconfigfile())
        except IOError:
            pass
        if not self.system:
            logging.debug(_("Could not open config file: %s"), self.paths.get_systemconfigfile())
            self.system = {}
            self.system['generic-config'] = {}
            self.system['profiles'] = {}
    
        self.profile_index = []
        self.profile_index.extend([('system', profile_name) for profile_name in self.system['profiles']])
        self.profile_index.extend([('user', profile_name) for profile_name in self.user['profiles']])
        self.emit('config-reread')

    def get_profiles(self):
        return self.profile_index

    def get_profile(self, config, profile=None, section=None):
        """
        Fetch profile from config files. If C{profile} or C{section} are set to
        C{None} or completly omitted, the whole config/profile is returned. If
        C{section} is set, C{profile} also has to be set!
        
        @param    config:    config file selection (user/system)
        @type     config:    String
        @param    profile:   profile to fetch data from
        @type     profile:   String
        @param    section:   For which module do we fetch information (== classname)
        @type     section:   String
        """
        _config = None
        _profile = None
        _section = None
        try:
            if config == 'user':
                _config = self.user['profiles']
            elif config == 'system':
                _config = self.system['profiles']
            _profile = _config[profile]
            _section = _profile[section]
        except (KeyError, TypeError):
            if not _config:
                raise noConfigException()
            elif not _profile and not profile:
                return _config
            elif not _profile and not type(_profile) == type({}):
                raise profileNotFoundException()
            elif not _section and not section:
                return _profile
            elif not _section:
                raise sectionNotFoundException()
        return _section            

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
        
        @param    name:    name of configuration value to fetch
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
        config_data = json.write(config)
        config_file.write(config_data)
        config_file.close()
    
    @staticmethod
    def _read_config(absfilename):
        """
        Parse configuration from file
        
        @param absfilename:    Filename to read data from
        """
        config = {}
        try:
             config_file = open(absfilename)
             config_data = config_file.read()
             config = json.read(config_data)
             config_file.close()
        except Exception, e:
             logging.error(_("Could not read config file: %s\n%s") % (absfilename, str(e)))
             config = {}
        return config