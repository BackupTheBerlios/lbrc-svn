import logging
import LBRC.json as json
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
    """
    The config class is a wrapper around the json on disk configuration format.
    """
    __gsignals__ = {
                    'config-reread': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
                   }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.logger = logging.getLogger("LBRC.Config")
        self.paths = path()
        self.user = None
        self.system = None
        self.profile_index = []
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
            self.logger.debug(_("Could not open config file: %s"), self.paths.get_userconfigfile())
        
        if not self.user:
            self.user = {}
            self.user['generic-config'] = {}
            self.user['profiles'] = {}
        try:
            self.system = self._read_config(self.paths.get_systemconfigfile())
        except IOError:
            self.logger.debug(_("Could not open config file: %s"), self.paths.get_systemconfigfile())
        
        if not self.system:
            self.system = {}
            self.system['generic-config'] = {}
            self.system['profiles'] = {}
    
        self.profile_index = []
        try:
            self.profile_index.extend([('system', profile_name) for profile_name in self.system['profiles']])
        except KeyError:
            self.logger.debug("Error while adding system profiles - None defined?")
        try:
            self.profile_index.extend([('user', profile_name) for profile_name in self.user['profiles']])
        except KeyError:
            self.logger.debug("Error while adding user profiles - Probably none defined!")
        # pylint: disable-msg=E1101
        self.emit('config-reread')
        # pylint: enable-msg=E1101

    def get_profiles(self):
        return self.profile_index

    def get_profile(self, config_file, profile=None, section=None):
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
            if config_file == 'user':
                _config = self.user['profiles']
            elif config_file == 'system':
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
        except KeyError:
            try:
                return self.system['generic-config'][name]
            except KeyError:
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

        if 'generic-config' in self.user and \
            name in self.user['generic-config']:
            result['user'] = self.user['generic-config'][name]
        if 'generic-config' in self.system and \
            name in self.system['generic-config']:
            result['system'] = self.system['generic-config'][name]
            
        return result

    def write(self):
        """
        Write user configuration to file
        """
        self._write_config(self.paths.get_userconfigfile(), self.user)
    
    @staticmethod
    def _write_config(absfilename, source_config_data):
        """
        Serialize configuration stored in C{config} and write to file
        
        @param    absfilename:    Filename to store config in
        @type     absfilename:    String
        @param    config:         dictionary holding the config data
        @type     config:         dictionary
        """
        try:
            config_file = open(absfilename, 'w')
            config_data = json.write(source_config_data, pretty_print=True)
            config_file.write(config_data)
            config_file.close()
        except IOError:
            logging.getLogger('LBRC.Config').exception(
                                _("Error while writing to: %s") % absfilename)
        except json.ReadException:
            logging.getLogger('LBRC.Config').exception(
                                _("Error while encoding config data to json"))
    
    @staticmethod
    def _read_config(absfilename):
        """
        Parse configuration from file
        
        @param absfilename:    Filename to read data from
        """
        config_hash = {}
        try:
            config_file = open(absfilename)
            config_data = config_file.read()
            config_hash = json.read(config_data)
            config_file.close()
        except IOError:
            logging.getLogger('LBRC.Config').exception(
                                _("Error while opening: %s") % absfilename)
        except json.ReadException:
            logging.getLogger('LBRC.Config').exception(
                                _("Error while interpreting json data in file: %s") % absfilename)
        return config_hash
