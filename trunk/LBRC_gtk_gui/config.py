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
#     partly done: when called from applet
#   * Document each method
#   * Edition of profiles
#     partly done: Uinput
#
# TODO (long time):
#   * join config object into one dbus object

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

reverse_types = {}
for t in types_detailed:
    reverse_types[types_detailed[t]] = t
    
types_values = {
                'key': [True, ["LEFTCTRL", "LEFTALT", "RIGHTCTRL", "RIGHTALT",
                               "UP", "DOWN", "LEFT", "RIGHT", "PAGEUP", "PAGEDOWN", 
                               "ENTER", "SPACE", "BACKSPACE", "HOME", "END"], None, True],
                'mousebutton': [False, ["LEFT", "MIDDLE", "RIGHT", "MOUSE", "FORWARD", "BACK", "TOUCH"], None, False],
                'mousewheel': [False, ["+WHEEL", "-WHEEL", "+HWHEEL", "-HWHEEL"], None, True],
                'mouseaxis': [False, ["+X", "-X", "+Y", "-Y", "+Z", "-Z"], None, False]
                }

for i in xrange(0,10):
    types_values['key'][1].append(str(i))

for i in xrange(0,13):
    types_values['key'][1].append("F" + str(i))
    
for i in xrange(97, 123):
    types_values['key'][1].append(chr(i))
    
for i in xrange(65, 90):
    types_values['key'][1].append(chr(i))

for name in types_values:
    model = gtk.ListStore(str)
    for i in types_values[name][1]:
        model.append([i])
    types_values[name][2] = model

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
        # TODO: use one global config glade object
        self.xml = gtk.glade.XML(os.path.join(path().get_guidir(), "config.glade"))
        #self.control = ConfigWindowControl()
        self.modified = False

        # Wrapper to get a widget from glade's xml
        self.widget = self.xml.get_widget

        self.widget("config-window").show_all()

        self._load_config()
        self._fill_window()
        #connnect signals
        self.xml.signal_autoconnect(self)

    def _load_config(self):
        """Loads the config file"""
        self.config = config()    
        self.user_profiles = self.config.user['profiles']
        self.system_profiles = self.config.system['profiles']

    def _fill_treeview(self):
        """Fills the table of commands"""
        iter = self.widget("profile-combobox").get_active_iter()
        
        # 0 => keycode, 1 => map_to, 2 => repeat_freq, 3 => EVENT TYPE, 
        # 4 => BACKGOROUND COLOR, 5 => EVENT TYPE DESCRIPTION 6 => is a repeater
        # 7 => model for the event mapping, 8 => do we allow other event mappings (useful for keyboard)
        
        mylist = gtk.ListStore(int, str, int, str, str, str, gobject.TYPE_BOOLEAN, gtk.ListStore,gobject.TYPE_BOOLEAN, gobject.TYPE_PYOBJECT)
        
        if not iter:
            self.widget("key-mouse-treeview").set_model(mylist)
            return 
        model = self.widget("profile-combobox").get_model()
        (profileid, config) = model.get(iter, 1, 2)

        profile = {}

        if config == 'user':
            self.widget("key-mouse-add-button").set_sensitive(True)
            self.widget("key-mouse-remove-button").set_sensitive(True)
            self.widget("key-mouse-treeview").set_sensitive(True)
            #self.widget("command-add-button").set_sensitive(True)
            profile = self.user_profiles[profileid]
        else:
            self.widget("key-mouse-add-button").set_sensitive(False)
            self.widget("key-mouse-treeview").set_sensitive(False)
            #self.widget("command-add-button").set_sensitive(False)
            profile = self.system_profiles[profileid]
    
        #try:
        for map in profile['UinputDispatcher']['actions']:
            type = map['type']
            mylist.append([
                map['keycode'], 
                map['map_to'], 
                int(map.get('repeat_freq', 0)),
                type,
                colors[type],
                types_detailed[type],
                types_values[type][3],
                types_values[type][2],
                types_values[type][0],
                map
            ])
        #except KeyError:
        #    pass

        self.widget("key-mouse-treeview").set_model(mylist)
        
    def _fill_window(self, initial=True):
        # Configuration notebook
        save_current = self.widget("save-current-checkbutton")
        show_bluetooth = self.widget("show-bluetooth-checkbutton")
        uinput_device = self.widget("uinput-device-entry")
        require_pairing = self.widget("require-pairing-checkbutton")
        onetime_pairing = self.widget("onetime-pairing-checkbutton")

        save_current.set_active(self.config.get_config_item_fb("persistent", True))
        show_bluetooth.set_active(self.config.get_config_item_fb("show-bluetooth", True))
        uinput_device.set_text(self.config.get_config_item_fb("uinput-device", ""))
        require_pairing.set_active(self.config.get_config_item_fb("require-pairing", True))
        onetime_pairing.set_active(self.config.get_config_item_fb("remove-pairing", False))
       
        # Profiles combobox
        self._fill_profiles()

        if initial:
            treeview = self.widget("key-mouse-treeview")
            
            textrenderer = gtk.CellRendererText()
            textrenderer.connect("edited", self._treeview_changed, "keycode")
            textrenderer.set_property("editable", True)
            treeview.insert_column_with_attributes(
                0, 
                _("Cellphone keycode"), 
                textrenderer, 
                text=0
            )
            
            comborenderer = gtk.CellRendererCombo()
            comborenderer.connect("edited", self._treeview_changed, "type")
            mylist = gtk.ListStore(str)
            for i in types_detailed.values():
                mylist.append([i])
            comborenderer.set_property("model", mylist)
            comborenderer.set_property("text-column", 0)
            comborenderer.set_property("editable", True)
            comborenderer.set_property("has-entry", False)
            treeview.insert_column_with_attributes(
                1, 
                _("Event type"), 
                comborenderer,
                text=5
            )
 
            comborenderer = gtk.CellRendererCombo()
            comborenderer.connect("edited", self._treeview_changed, "event")
            comborenderer.set_property("text-column", 0)
            comborenderer.set_property("editable", True)
            #comborenderer.set_property("has-entry", True)           
            treeview.insert_column_with_attributes(
                2, 
                _("Event generated"), 
                comborenderer,
                model=7,
                has_entry=8,
                text=1
            )
            
            textrenderer = gtk.CellRendererText()
            textrenderer.connect("edited", self._treeview_changed, "repeat")
            textrenderer.set_property("editable-set", True)
            treeview.insert_column_with_attributes(
                3, 
                _("Repeatfrequency"), 
                textrenderer,
                text=2,
                editable = 6,
                visible=6
            )
            treeview.get_column(0).set_resizable(True)
            treeview.get_column(0).set_sort_column_id(0)
            treeview.get_column(1).set_resizable(True)
            treeview.get_column(1).set_sort_column_id(5)
            treeview.get_column(2).set_resizable(True)
            treeview.get_column(2).set_sort_column_id(1)

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

    def _create_new_profile(self, profile_name):
        keys = self.user_profiles.keys() + self.system_profiles.keys()
        if keys and profile_name.lower() in map(str.lower, keys):
            #profile already exists
            print "Profile already exists"
            return False
        self.modified = True
        self.user_profiles[profile_name] = {}
        return True

    def _treeview_changed(self, cellrenderer, treepath, new_text, ctype):
        # 0 => keycode, 1 => map_to, 2 => repeat_freq, 3 => EVENT TYPE, 
        # 4 => BACKGOROUND COLOR, 5 => EVENT TYPE DESCRIPTION 6 => is a repeater
        # 7 => model for the event mapping, 8 => do we allow other event mappings (useful for keyboard)
        #
        # TODO: Check that we got valid values
        tv = self.widget("key-mouse-treeview")
        model = tv.get_model()
        iter = model.get_iter(treepath)
        (keycode, map_to, repeat_freq, type, row) = model.get(iter, 0, 1, 2, 3, 9)      
        
        if ctype == 'type':
            row["type"] = type = reverse_types[new_text]
            row["map_to"] = map_to = types_values[type][1][0]
            repeat_freq = 0
            if repeat_freq in row: del row["repeat_freq"]
        elif ctype == 'keycode':
            row["keycode"] = keycode = int(new_text)
        elif ctype == 'event':
            row["map_to"] = map_to = new_text
        elif ctype == 'repeat':
            row["repeat_freq"] = repeat_freq = int(new_text)
        
        model.set(iter, 0, keycode, 1, map_to, 2, repeat_freq, 3, type, 4, colors[type], 
                        5, types_detailed[type], 6, types_values[type][3], 7, types_values[type][2],
                        8, types_values[type][0])
        
        self.modified = True
                    
    def on_config_window_destroy(self, destroy):
        if self.modified:
            self.config.write()
        self.emit("close", self.modified)
        return True

    def on_save_current_checkbutton_toggled(self, object):
        self.config.set_config_item("persistent", object.get_active())
        self.modified = True
        print "save current checkbutton toggled"

    def on_uinput_device_entry_changed(self, object):
        path = object.get_text()
        path = path.strip()
        if path:
            self.config.set_config_item("uinput-device", path)
        else:
            self.config.set_config_item("uinput-device", "")
        self.modified = True
        print "uinput device entry changed"
    
    def on_show_bluetooth_checkbutton_toggled(self, object):
        self.config.set_config_item("show-bluetooth", object.get_active())
        self.modified = True
        print "show bluetooth checkbutton toggled"

    def on_require_pairing_checkbutton_toggled(self, object):
        self.config.set_config_item("require-pairing", object.get_active())
        self.modified = True
        print "require pairing checkbutton toggled"

    def on_onetime_pairing_checkbutton_toggled(self, object):
        self.config.set_config_item("remove-pairing", object.get_active())
        self.modified = True
        print "ontime pairing checkbutton toggled"

    def on_profile_combobox_changed(self, combobox):
        selected_profile = combobox.get_active_text()
        self.widget("profile-notebook").set_sensitive(True)
        if selected_profile in self.user_profiles:
            self.widget("profile-rename-button").set_sensitive(True)
            self.widget("profile-delete-button").set_sensitive(True)
        else:
            self.widget("profile-rename-button").set_sensitive(False)
            self.widget("profile-delete-button").set_sensitive(False)
        self._fill_treeview()

    def on_profile_new_button_clicked(self, button):
        input_window = InputWindow(title=_("What is the name for the new profile?"), 
                                   parent = self.widget("config-window"))
        input_window.connect("close", self.on_input_window_close, "new-profile")

    def on_input_window_close(self, window, was_modified, type):
        text = window.get_text().strip()
        if type == "new-profile" and len(text) > 0:
            self._create_new_profile(text)
            self._fill_profiles(select_last_item=True)
        elif type == "rename-profile" and len(text) > 0:
            if text in self.user_profiles:
                # TODO: Handle rename with name clash
                return
            iter = self.widget("profile-combobox").get_active_iter()
            if not iter:
                return
            model = self.widget("profile-combobox").get_model()
            data = model.get(iter,1,2)       
            if data[1] == "user":
                model.set(iter, 0, text, 1, text)
                self.user_profiles[text] = self.user_profiles[data[0]]
                del(self.user_profiles[data[0]])
                self.modified = True
                self._fill_treeview()
                

    def on_profile_rename_button_clicked(self, object):        
        input_window = InputWindow(title=_("Specify the new name for the new profile"), 
                                   parent = self.widget("config-window"))
        input_window.connect("close", self.on_input_window_close, "rename-profile")

    def on_profile_delete_button_clicked(self, object):
        iter = self.widget("profile-combobox").get_active_iter()
        if not iter:
            return
        model = self.widget("profile-combobox").get_model()
        data = model.get(iter,1,2)
        if data[1] == "user":
            del self.user_profiles[data[0]]
            self.modified = True
            model.remove(iter)
            self._fill_treeview()

    def on_key_mouse_add_button_clicked(self, object):
        edit_window = KeyMouseEditWindow(parent=self.widget("config-window"))
        #edit_window.connect("close", self.on_edit_window_close, -1)
        edit_window.run()

    def on_key_mouse_remove_button_clicked(self, object):
        print "keyboard/mouse remove button clicked"

    def on_command_add_button_clicked(self, object):
        print "commands add button clicked"

    def on_command_remove_button_clicked(self, object):
        print "commands remove button clicked"

    def on_command_edit_button_clicked(self, object):
        print "commands edit button clicked"
    
    def on_config_revert_button_clicked(self, object):
        self._load_config()
        self._fill_window(False)
        self.modified = False

    def on_config_close_button_clicked(self, object):
        self.widget('config-window').destroy()

if __name__ == "__main__":
    p = ConfigWindow()
    p.widget("config-window").connect_after('destroy',lambda x: gtk.main_quit() )
    gtk.main()
