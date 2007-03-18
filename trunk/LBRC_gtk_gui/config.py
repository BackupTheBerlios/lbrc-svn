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
#   * Write to the config file
#   * edit of profile
#   * creation of a new profile
#   * Document each method
#  


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
    dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
    LBRC.scriptpath = os.path.join(dirname, "..")

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

class KeyMouseEditWindow(gobject.GObject):
    
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
        return self.xml.get_widget(name)

    def get_repeat(self):
        return self.repeat

    def get_keycode(self):
        return self.keycode

    def get_action(self):
        return self.action

    def get_type(self):
        return self.type

    def on_key_mouse_edit_window_destroy(self, object):
        if self.exit_ok == None:
            self.exit_ok = False

        self.emit("close", self.exit_ok)
        return True

    def on_event_type_combobox_changed(self, combobox):
        text = combobox.get_active_text()
        if text != None and len(text) > 0:
            self.type = self.reverse_types[text]

    def on_event_generated_entry_changed(self, entry):
        text = entry.get_text()
        if text != None and len(text) > 0:
            self.action = text

    def on_repeat_frequency_entry_changed(self, entry):
        text = entry.get_text()
        if text != None and len(text) > 0:
            self.repeat = text

    def on_cellphone_keycode_entry_changed(self, object):
        text = entry.get_text()
        if text != None and len(text) > 0:
            self.keycode = text

    def on_cancel_button_clicked(self, button):
        self.exit_ok = False
        self.widget("key-mouse-edit-window").destroy()

    def on_ok_button_clicked(self, button):
        self.exit_ok = True
        self.widget("key-mouse-edit-window").destroy()

class ConfigWindow:
    def __init__(self):
        # create widget tree ...
        self.xml = gtk.glade.XML(os.path.join(path().get_guidir(), "config.glade"))
        #self.control = ConfigWindowControl()
        self.modified = False
        self.lbrc = LBRC.dinterface(dbus.SessionBus(), 'custom.LBRC', '/custom/LBRC', 'custom.LBRC')

        self._load_config()
        self._fill_window()
        #connnect signals
        self.xml.signal_autoconnect(self)

    def widget(self, name):
        return self.xml.get_widget(name)

    def _load_config(self):
        self.config = config()    
        self.user_profiles = self.config.user['profiles']
        self.system_profiles = self.config.system['profiles']

    def _fill_treeview(self):
        selected_profile = self.widget("profile-combobox").get_active_text()
        profile = {}
        # 0 => keycode, 1 => map_to, 2 => repeat_freq, 3 => EVENT TYPE, 4 => BACKGOROUND COLOR, 5 => EVENT TYPE DESCRIPTION
        mylist = gtk.ListStore(str, str, str, str, str, str)
        if selected_profile in self.user_profiles:
            self.widget("key-mouse-add-button").set_sensitive(True)
            self.widget("key-mouse-remove-button").set_sensitive(True)
            self.widget("key-mouse-edit-button").set_sensitive(True)
            self.widget("key-mouse-treeview").set_sensitive(True)
            #self.widget("command-add-button").set_sensitive(True)
            profile = self.user_profiles[selected_profile]
        else:
            self.widget("key-mouse-add-button").set_sensitive(False)
            self.widget("key-mouse-treeview").set_sensitive(False)
            self.widget("key-mouse-remove-button").set_sensitive(False)
            self.widget("key-mouse-edit-button").set_sensitive(False)
            #self.widget("command-add-button").set_sensitive(False)
            profile = self.system_profiles[selected_profile]
        
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
        self.widget("key-mouse-treeview").set_model(mylist)

        
    def _fill_window(self):
        # Configuration notebook
        save_current = self.widget("save-current-checkbutton")
        show_bluetooth = self.widget("show-bluetooth-checkbutton")
        uinput_device = self.widget("uinput-device-entry")
        
        save_current.set_active(self.config.get_config_item_fb("persistent", True))
        show_bluetooth.set_active(self.config.get_config_item_fb("show-bluetooth", False))
        uinput_device.set_text(self.config.get_config_item_fb("uinput-device", ""))
       
        # Profiles
        profile = self.widget("profile-combobox")

        for i in self.system_profiles.keys() + self.user_profiles.keys():
            profile.append_text(i)

        # create the treeview's
        for treeview in self.widget("key-mouse-treeview"), self.widget("command-treeview"):
            treeview.insert_column_with_attributes(0, _("Event type"), gtk.CellRendererText(), text=5, background=4)
            treeview.insert_column_with_attributes(1, _("Event generated"), gtk.CellRendererText(), text=1, background=4)
            treeview.insert_column_with_attributes(2, _("Cellphone keycode"), gtk.CellRendererText(), text=0, background=4)
            #treeview.set_model(gtk.ListStore(str, str))
            #treeview.get_model().append(["example", "target"])

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
        print "config window destroy"
        return True

    def on_save_current_checkbutton_toggled(self, object):
        print "save current checkbutton toggled"

    def on_uinput_device_entry_changed(self, object):
        print "uinput device entry changed"
    
    def on_show_bluetooth_checkbutton_toggled(self, object):
        print "show bluetooth checkbutton toggled"

    def on_profile_combobox_changed(self, combobox):
        #print "profile combobox changed"
        #from pprint import pprint 
        #pprint(*kargs)
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
        print "profile new button clicked"

    def on_profile_edit_button_clicked(self, object):
        print "profle edit button clicked"

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
