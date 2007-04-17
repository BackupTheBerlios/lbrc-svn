#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
# LBRC Configuration Editor.
# Copyright (C) 2007 LBRC team.
# Authors: 
#   Iuri Gomes Diniz <iuri@digizap.com.br>, 2007.
# This file is distributed under the same license as the LBRC package.
#
# TODO:
#   * Write to the config file at end
#   * Document each method
#   * Merge config.glade and keymouseeditwindow in one file
#   * Delete a profile
#   * Change a profile name
#   * Edition of profiles

__extra_epydoc_fields__ = [('signal', 'Signal', 'Signals')]

import os
import sys
import dbus

import gtk
import gtk.glade
import gobject

import LBRC
from LBRC.path import path
from LBRC.config import config

# setting the correct script path before use of _ 
if __name__ == "__main__":
    import LBRC.path
    dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
    LBRC.path.scriptpath = os.path.join(dirname, "..")

from LBRC.l10n import _
LBRC.l10n.init_glade_gettext()

# Colors for each event type
# see: 
#   /etc/X11/rgb.txt, 
#   /usr/lib/X11/rgb.txt, 
#   /usr/share/X11/rgb.txt
colors = { 'key':'snow', 'mousebutton':'bisque', 'mousewheel':'snow', 'mouseaxis':'bisque' }

# More descriptive string for each event type
types_detailed = { 'key':_('KEYBOARD'), 'mousebutton':_('MOUSE BUTTON'), 'mousewheel':_('MOUSE WHEEL'), 'mouseaxis':_('MOUSE AXIS') }


# TIP: Command to get name of handlers from config.glade
# >grep handler LBRC_gtk_gui/config.glade | perl -pe 's/.*"(on_.*?)".*/$1/'


class InputWindow(gobject.GObject):
    #I want to use close signal with the same interface of the others class, so I'm not inheriting from Gtk.Dialog
    __gsignals__ = {
        'close': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }

    def __init__(self, title = "", parent = None):
        
        gobject.GObject.__init__(self)

        self.dialog = gtk.Dialog(
            title, 
            parent, 
            gtk.DIALOG_MODAL, 
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, 
                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
        )

        self.dialog.vbox.add(gtk.Label(title))

        self.input_entry = gtk.Entry()
        
        self.dialog.vbox.add(self.input_entry)
        self.dialog.show_all()

        self.input_entry.connect("changed", self.on_input_changed)
        self.dialog.connect("response", self.on_dialog_response)
        self.dialog.connect("destroy", self.on_dialog_destroy)

        self.modified = False
        self.exit_ok = False

        self.dialog.show()

    def on_input_changed(self, object):
        self.modified = True

    def on_dialog_response(self, object, response):
        if response == gtk.RESPONSE_ACCEPT:
            self.exit_ok = True
        self.dialog.destroy()

    def on_dialog_destroy(self, object):
        if self.exit_ok:
            self.emit("close", self.modified)

    def get_text(self):
        return self.input_entry.get_text();

class KeyMouseEditWindow(gobject.GObject):
    """
    A Window for configuring a key/mouse event.

    @signal: close: (exit_ok)
        This signals is fired when the window is closed. The parameter exit_ok will be True if the use has closed the window by clicking on OK button. The value of the entries must be accessed by get_* methods.

    """
   
    __gsignals__ = {
        'close': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }

    def __init__(self, keycode=None, action=None, repeat=None, type=None):
        gobject.GObject.__init__(self)
        # create widget tree ...
        self.xml = gtk.glade.XML(os.path.join(path().get_guidir(), "keymouseeditwindow.glade"))
        # event types
        i = 0
        self.type = type
        self.reverse_types = {}
        for t in types_detailed:
            self.widget("event-type-combobox").append_text(types_detailed[t])
            self.reverse_types[types_detailed[t]] = t
            if self.type != None and t == self.type:
                self.widget("event-type-combobox").set_active(i)

            i += 1
        
        self.action = action
        if self.action != None:
            self.widget("event-generated-entry").set_text(self.action)

        self.repeat = repeat
        if self.repeat != None:
            self.widget("repeat-frequency-entry").set_text(self.repeat)
        self.keycode = keycode
        if self.keycode != None:
            self.widget("cellphone-keycode-entry").set_text(self.keycode)

        self.xml.signal_autoconnect(self)
        # to sinalize the exit status
        self.exit_ok = None

    def widget(self, name):
        """ Wraper to get a widget from glade's xml"""
        return self.xml.get_widget(name)

    def get_repeat(self):
        """Get the value of repeat entry"""
        return self.repeat

    def get_keycode(self):
        """Get the value of keycode entry"""
        return self.keycode

    def get_action(self):
        """Get the value of action entry"""
        return self.action

    def get_type(self):
        """Get the value of type entry"""
        return self.type

    def on_key_mouse_edit_window_destroy(self, object):
        """Signal handler for catch when the window was destroied"""
        if self.exit_ok == None:
            self.exit_ok = False

        self.emit("close", self.exit_ok)
        return True

    def on_event_type_combobox_changed(self, combobox):
        """Signal handler for catch when the event type combobox widget has be changed"""
        text = combobox.get_active_text()
        if text != None and len(text) > 0:
            self.type = self.reverse_types[text]

    def on_event_generated_entry_changed(self, entry):
        """Signal handler for catch when the event entry has be changed"""
        text = entry.get_text()
        if text != None and len(text) > 0:
            self.action = text

    def on_repeat_frequency_entry_changed(self, entry):
        """Signal handler for catch when the frequency entry has be changed"""
        text = entry.get_text()
        if text != None and len(text) > 0:
            self.repeat = text

    def on_cellphone_keycode_entry_changed(self, object):
        """Signal handler for catch when the keycode entry has be changed"""
        text = entry.get_text()
        if text != None and len(text) > 0:
            self.keycode = text

    def on_cancel_button_clicked(self, button):
        """Signal handler for catch when the cancel button has be pressed"""
        self.exit_ok = False
        self.widget("key-mouse-edit-window").destroy()

    def on_ok_button_clicked(self, button):
        """Signal handler for catch when the ok button has be pressed"""
        self.exit_ok = True
        self.widget("key-mouse-edit-window").destroy()

class ConfigWindow(gobject.GObject):
    """
    Widget to configure LBRC

    @signal: close (was_changed)
        This signal is fired when the config window has be closed if any configuration has be changed the parameter was_changed will be True.

    """
    __gsignals__ = {
        'close': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }

    def __init__(self):
        gobject.GObject.__init__(self)
        # create widget tree ...
        self.xml = gtk.glade.XML(os.path.join(path().get_guidir(), "config.glade"))
        #self.control = ConfigWindowControl()
        self.modified = False

        self._load_config()
        self._fill_window()
        #connnect signals
        self.xml.signal_autoconnect(self)

    def widget(self, name):
        #TODO: just aliase self.widget = self.xml.get_widget
        """Wrapper to get a widget from glade's xml"""
        return self.xml.get_widget(name)

    def _load_config(self):
        """Loads the config file"""
        self.config = config()    
        self.user_profiles = self.config.user['profiles']
        self.system_profiles = self.config.system['profiles']

    def _fill_treeview(self):
        """Fills the table of commands"""

        iter = self.widget("profile-combobox").get_active_iter()
        model = self.widget("profile-combobox").get_model()
        (profileid, config) = model.get(iter, 1, 2)

        profile = {}
        # 0 => keycode, 1 => map_to, 2 => repeat_freq, 3 => EVENT TYPE, 4 => BACKGOROUND COLOR, 5 => EVENT TYPE DESCRIPTION
        mylist = gtk.ListStore(str, str, str, str, str, str)
        if config == 'user':
            self.widget("key-mouse-add-button").set_sensitive(True)
            self.widget("key-mouse-remove-button").set_sensitive(True)
            self.widget("key-mouse-edit-button").set_sensitive(True)
            self.widget("key-mouse-treeview").set_sensitive(True)
            #self.widget("command-add-button").set_sensitive(True)
            profile = self.user_profiles[profileid]
        else:
            self.widget("key-mouse-add-button").set_sensitive(False)
            self.widget("key-mouse-treeview").set_sensitive(False)
            self.widget("key-mouse-remove-button").set_sensitive(False)
            self.widget("key-mouse-edit-button").set_sensitive(False)
            #self.widget("command-add-button").set_sensitive(False)
            profile = self.system_profiles[profileid]
    
        try:
            for map in profile['UinputDispatcher']['actions']:
                type = map['type']
                mylist.append([
                    map['keycode'], 
                    map['map_to'], 
                    map.get('repeat_freq', None),
                    type,
                    colors[type],
                    types_detailed[type]
                ])
        except KeyError:
            pass

        self.widget("key-mouse-treeview").set_model(mylist)

        
    def _fill_window(self):
        # Configuration notebook
        save_current = self.widget("save-current-checkbutton")
        show_bluetooth = self.widget("show-bluetooth-checkbutton")
        uinput_device = self.widget("uinput-device-entry")
        require_pairing = self.widget("require-pairing-checkbutton")
        onetime_pairing = self.widget("onetime-pairing-checkbutton")

        save_current.set_active(self.config.get_config_item_fb("persistent", True))
        show_bluetooth.set_active(self.config.get_config_item_fb("show-bluetooth", False))
        uinput_device.set_text(self.config.get_config_item_fb("uinput-device", ""))
        require_pairing.set_active(self.config.get_config_item_fb("require-pairing", True))
        onetime_pairing.set_active(self.config.get_config_item_fb("remove-pairing", False))
       
        # Profiles combobox
        self._fill_profiles()

        # key-mouse-treeview
        treeview = self.widget("key-mouse-treeview")
        # the text is in model index 5
        # the backgroung is model index 4
        treeview.insert_column_with_attributes(
            0, _("Event type"), 
            gtk.CellRendererText(), text=5, 
            background=4         
        )
        treeview.insert_column_with_attributes(
            1, _("Event generated"), 
            gtk.CellRendererText(), text=1, 
            background=4
        )
        treeview.insert_column_with_attributes(
            2, _("Cellphone keycode"), 
            gtk.CellRendererText(), text=0, 
            background=4
        )

    def _fill_profiles(self, select_last_item=False):
        """Fills the profile-combobox widget"""
        profile = self.widget("profile-combobox")
        
        last_active = profile.get_active()

        # 1 => Displayname, 2 => profile, 3 => config
        profile_model = gtk.ListStore(str, str, str)

        for i in self.system_profiles.keys():
            itemname = '%s (%s)' % (i, _("System"))
            profile_model.append((itemname, i, "system"))
        
        for i in self.user_profiles.keys():
            profile_model.append((i, i, "user"))
            
        profile.set_model(profile_model)

        if select_last_item:
            # walk through profile_model 
            iter = profile_model.get_iter_first()
            while profile_model.iter_next(iter):
                iter = profile_model.iter_next(iter)
            profile.set_active_iter(iter)
        else:
            profile.set_active(last_active)
            #pass


    def _create_new_profile(self, profile_name):
        keys = self.user_profiles.keys() + self.system_profiles.keys()
        if keys and profile_name.lower() in map(str.lower, keys):
            #profile already exists
            print "Profile already exists"
            return False
        self.user_profiles[profile_name] = {}
        return True

    def _edit_key_mouse(self, pos):
        print "Editing pos", pos
        mylist = list(self.widget("key-mouse-treeview").get_model()[pos])
        edit_window = KeyMouseEditWindow(mylist[0], mylist[1], mylist[2], mylist[3])
        edit_window.connect("close", self.on_edit_window_close, pos)

    def on_edit_window_close(self, edit_window, exit_ok, pos):
        if exit_ok == True:
            print "pos: ", pos
            print "repeat: ", edit_window.get_repeat()
            print "keycode: ", edit_window.get_keycode()
            print "action: ", edit_window.get_action()
            print "type: ", edit_window.get_type()

    def on_config_window_destroy(self, destroy):
        self.emit("close", self.modified)
        return True

    def on_save_current_checkbutton_toggled(self, object):
        print "save current checkbutton toggled"

    def on_uinput_device_entry_changed(self, object):
        print "uinput device entry changed"
    
    def on_show_bluetooth_checkbutton_toggled(self, object):
        print "show bluetooth checkbutton toggled"

    def on_require_pairing_checkbutton_toggled(self, object):
        print "require pairing checkbutton toggled"

    def on_onetime_pairing_checkbutton_toggled(self, object):
        print object.get_state()
        print "ontime pairing checkbutton toggled"

    def on_profile_combobox_changed(self, combobox):
        selected_profile = combobox.get_active_text()
        self.widget("profile-notebook").set_sensitive(True)
        if selected_profile in self.user_profiles:
            self.widget("profile-edit-button").set_sensitive(True)
            self.widget("profile-delete-button").set_sensitive(True)
        else:
            self.widget("profile-edit-button").set_sensitive(False)
            self.widget("profile-delete-button").set_sensitive(False)
        self._fill_treeview()

    def on_profile_new_button_clicked(self, button):
        input_window = InputWindow(title=_("What is the name for the new profile?"), parent = self.widget("config-window"))
        input_window.connect("close", self.on_input_window_close, "new-profile")

    def on_input_window_close(self, window, was_modified, type):
        #print "modified:", was_modified, "type:", type, "text:", window.get_text()
        text = window.get_text().strip()
        if type == "new-profile" and len(text) > 0:
            self._create_new_profile(text)
            self._fill_profiles(select_last_item=True)


    def on_profile_edit_button_clicked(self, object):
        print "profile edit button clicked"

    def on_profile_delete_button_clicked(self, object):
        print "profile delete button clicked"

    def on_key_mouse_add_button_clicked(self, object):
        edit_window = KeyMouseEditWindow()
        edit_window.connect("close", self.on_edit_window_close, -1)

    def on_key_mouse_remove_button_clicked(self, object):
        print "keyboard/mouse remove button clicked"

    def on_key_mouse_edit_button_clicked(self, object):
        path, column = self.widget("key-mouse-treeview").get_cursor()
        if path != None:
            self._edit_key_mouse(path[0])

    def on_command_add_button_clicked(self, object):
        print "commands add button clicked"

    def on_command_remove_button_clicked(self, object):
        print "commands remove button clicked"

    def on_command_edit_button_clicked(self, object):
        print "commands edit button clicked"
    
    def on_config_revert_button_clicked(self, object):
        print "config revert button clicked"

    def on_key_mouse_treeview_row_activated(self, object, path, column):
        if path != None:
            self._edit_key_mouse(path[0])

    def on_config_close_button_clicked(self, object):
        self.widget('config-window').destroy()


if __name__ == "__main__":
    p = ConfigWindow()
    p.widget("config-window").connect_after('destroy',lambda x: gtk.main_quit() )
    gtk.main()
