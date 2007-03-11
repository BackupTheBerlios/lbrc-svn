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
# done this :-)
#


import os
import sys

import gtk
import gtk.glade

#from LBRC.l10n import _
from LBRC import get_guidir, get_localedir


# Command to get name of handlers 
# >grep handler LBRC_gtk_gui/config.glade | perl -pe 's/.*"(on_.*?)".*/$1/'

class ConfigWindow:
    def __init__(self):
        # create widget tree ...
        gtk.glade.bindtextdomain("LBRC", get_localedir())
        gtk.glade.textdomain("LBRC")
        self.xml = gtk.glade.XML(os.path.join(get_guidir(), "config.glade"))
        #self.control = ConfigWindowControl()
        self.xml.signal_autoconnect(self)

    def on_config_window_destroy(self, destroy):
        print "config window destroy"
        return True

    def on_save_current_checkbutton_toggled(self, object):
        print "save current checkbutton toggled"

    def on_uinput_device_entry_changed(self, object):
        print "uinput device entry changed"
    
    def on_show_bluetooth_checkbutton_toggled(self, object):
        print "show bluetooth checkbutton toggled"

    def on_profile_combobox_changed(self, object):
        print "profile combobox changed"

    def on_profile_new_button_clicked(self, button):
        print "profile new button clicked"

    def on_profile_edit_button_clicked(self, object):
        print "profle edit button clicked"

    def on_profile_delete_button_clicked(self, object):
        print "profile delete button clicked"

    def on_key_mouse_add_button_clicked(self, object):
        print "keyboard/mouse add button clicked"

    def on_key_mouse_remove_button_clicked(self, object):
        print "keyboard/mouse remove button clicked"

    def on_key_mouse_edit_button_clicked(self, object):
        print "keyboard/mouse edit button clicked"

    def on_command_add_button_clicked(self, object):
        print "commands add button clicked"

    def on_command_remove_button_clicked(self, object):
        print "commands remove button clicked"

    def on_command_edit_button_clicked(self, object):
        print "commands edit button clicked"
    
    def on_config_revert_button_clicked(self, object):
        print "config revert button clicked"

    def on_config_close_button_clicked(self, object):
        print "config close button clicked"


if __name__ == "__main__":
    dirname = os.path.dirname(os.path.abspath(sys.argv[0]))
    get_guidir = lambda: dirname
    get_localedir = lambda: os.path.join(dirname, "..", "pot")
    p = ConfigWindow()
    p.xml.get_widget("config-window").connect('hide',lambda x: gtk.main_quit() )
    gtk.main()
