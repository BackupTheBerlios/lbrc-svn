from LBRC.Listener import Listener
import logging
from LBRC.l10n import _

class ProfileSwitcher(Listener):
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
        Listener.__init__(self, config, "ProfileSwitcher")
        self.profilestore = []
        # Default Value for Profileswitcher Keycode will be the star key
        self._keycode = self.config.get_config_item_fb("profile-switch", 42)     

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
            for (type, profile) in self.config.get_profiles():
                if type == 'system':
                    ps.append([ "%s (%s)" % (profile, _("System")), (type,profile)])
                else:
                    ps.append([profile, (type,profile)])
            btconnection = self.bluetooth_connector.get_bt_connection()
            btconnection.send_list_query(_("Switch Profile"), [i[0] for i in ps], self._handle_list_reply)
    
    def _handle_list_reply(self, index):
        """
        This method is called, when a reply is send from the phone regarding
        the list selection request we send from L{keycode}
        """
        # This handler will _silently_ fail, if the selected
        # profile does not exist anymore
        # TODO: implement exceptions for not exisiting profiles
        if index > -1:
            self.core.profile_control.set_profile(self.profilestore[index][1][0], 
                                                  self.profilestore[index][1][1])

    def set_profile(self, config, profile):
        """
        Switch to new profile - here a noop method, as the key
        is defined globally.
        """
        pass

    def shutdown(self):
        # TODO: Create list selection cancel method
        pass