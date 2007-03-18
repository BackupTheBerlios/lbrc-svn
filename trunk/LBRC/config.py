import logging
import json

from LBRC.path import path
from LBRC.l10n import _

class config(object):
    def __init__(self):
        self.paths = path()
        self.user = None
        self.system = None
        self.reread()
    
    def reread(self):
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
        if config=='user':
            return self.user['profiles'][profile][section]
        else:
            return self.system['profiles'][profile][section]

    def set_config_item(self, name, value):
        self.user['generic-config'][name] = value

    def get_config_item(self, name):
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
        try:
            self._write_config(self.paths.get_userconfigfile(), self.user)
        except Exception, e:
            logging.error(_("Could not write config file: %s\n%s") % (self.paths.get_userconfigfile(), str(e)))
    
    @staticmethod
    def _write_config(absfilename, config):
        config_file = open(absfilename, 'w')
        json_writer = json.JsonWriter()
        config_data = json_writer.write(config)
        config_file.write(config_data)
        config_file.close()
    
    @staticmethod
    def _read_config(absfilename):
        config = {}
        config_file = open(absfilename)
        config_data = config_file.read()
        json_reader = json.JsonReader()
        config = json_reader.read(config_data)
        config_file.close()
        return config
    

    
