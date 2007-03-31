import logging
from LBRC.l10n import _

class ProfileSwitcher(object):
    """
    This is the ProfileSwitcher Plugin. It's prinziply a "normal" plugin, but
    it is configured in the generic-config section, so that one global key
    can be defined. This allows you to switch fast between multiple profile.
    
    One use-case would be the dual use of the phone as a mouse and a music
    remote control.
    """
    def __init__(self, config):
        """
        Initialize the Plugin - In this plugin we only read the profile-switch key
        from the generic-config section of the config file. This key is interpreted
        as a keycode, that is generated, when a profile change shall be issued.
        
        @param  config:         configuration data
        @type   config:         L{LBRC.config}
        """
        self.config = config
        self.init = []
        self.actions = {}
        self.descruct = []
        self.bluetooth_connector = None
        self.core = None
        self.profilestore = []
        # Default Value for Profileswitcher Keycode will be the star key
        self._keycode = self.config.get_config_item_fb("profile-switch", 42)

    def set_bluetooth_connector(self, bc):
        """
        Set our bluetooth connector, that allows us to issue the presentation
        of a list, from which the user can choose the new profile
        
        @param    bc:    Bluetooth Adapter
        @type     bc:    L{BTServer}
        """
        self.bluetooth_connector = bc        

    def set_core(self, core):
        """
        Set the core, where the administration of the profiles happens
        Currently this is dbusinterface
        
        @param   core:    Core, where profiles are handled
        @type    core:    L{dbusinterface}
        """
        self.core = core

    def keycode(self, mapping, keycode):
        """
        More or less a dummy method, that in this class only checks
        whether the supplied keycode is the configured keycode and
        the mapping maps to key release. If this is the case
        the list is generated from the L{dbusinterface} and send to the phone via
        a L{BTServer} Instance.

        @param  mapping:        mapping state of the keycode
        @type   mapping:        Integer
        @param  keycode:        keycode received
        @type   keycode:        Integer
        """
        if self._keycode and \
           keycode == self._keycode and \
           mapping == 1:
            self.profilestore = ps = []
            for ( type, profile) in self.core.get_profiles():
                if type == 'system':
                    ps.append([ "%s (%s)" % (profile, _("System")), (type,profile)])
                else:
                    ps.append([profile, (type,profile)])
            self.bluetooth_connector.send_list_query(_("Switch Profile"), [i[0] for i in ps], self._handle_list_reply)
    
    def _handle_list_reply(self, index):
        """
        This method is called, when a reply is send from the phone regarding
        the list selection request we send from L{keycode}
        """
        # This handler will _silently_ fail, if the selected
        # profile does not exist anymore
        # TODO: implement exceptions for not exisiting profiles
        if index > -1:
            self.core.set_profile(self.profilestore[index][1][0], 
                                  self.profilestore[index][1][1])

    def set_profile(self, config, profile):
        """
        Switch to new profile - here a noop method, as the key
        is defined globally.

        @param  profile:    the profile we switch to
        @type   profile:    string
        """
        pass

    def shutdown(self):
        # TODO: Create list selection cancel method
        pass
        #for command in self.destruct:
        #    command.call()
