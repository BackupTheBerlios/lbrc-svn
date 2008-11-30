# -*- coding: UTF-8 -*-
# pylint: disable-msg=E1101
# LBRC Configuration Editor.
# Copyright (C) 2007 LBRC team.
# Authors: 
#   Iuri Gomes Diniz <iuri@digizap.com.br>, 2007.
#   Matthias Bläsing <matthias.blaesing@rwth-aachen.de>, 2008
# This file is distributed under the same license as the LBRC package.
#
# TODO:
#   * Write to the config file at end
#     partly done: when called from applet
#   * Document each method
#
# TODO (long time):
#   * join config object into one dbus object
#
# TIP: Command to get name of handlers from config.glade
# >grep handler LBRC_gtk_gui/config.glade | perl -pe 's/.*"(on_.*?)".*/$1/'

__extra_epydoc_fields__ = [('signal', 'Signal', 'Signals')]

from LBRC.config import config
from LBRC.l10n import _
from LBRC.path import path
import LBRC.l10n
import copy
import gobject
import gtk
import gtk.glade
import logging
import os.path as osp
import pango
import sys

# setting the correct script path before use of _ 
if __name__ == "__main__":
    path.scriptpath = osp.join(osp.dirname(osp.abspath(sys.argv[0])), "..")

LBRC.l10n.init_glade_gettext()

# Backgrounddata for events
# key is event type
# 0 => event mappings allowed apart from the predefined onces (see [1])
# 1 => event mappings
# 2 => gtk-liststore of [1]
# 3 => is this repeatable?
# 4 => Translated Description of the event type
types_values = {
                'key': [True, ["LEFTCTRL", "LEFTALT", "RIGHTCTRL", "RIGHTALT",
                               "UP", "DOWN", "LEFT", "RIGHT", "PAGEUP", "PAGEDOWN", 
                               "ENTER", "SPACE", "BACKSPACE", "HOME", "END"], None, True, _('KEYBOARD')],
                'mousebutton': [False, ["LEFT", "MIDDLE", "RIGHT", "MOUSE", "FORWARD", "BACK", "TOUCH"], None, False, _('MOUSE BUTTON')],
                'mousewheel': [False, ["+WHEEL", "-WHEEL", "+HWHEEL", "-HWHEEL"], None, True, _('MOUSE WHEEL')],
                'mouseaxis': [False, ["+X", "-X", "+Y", "-Y", "+Z", "-Z"], None, False, _('MOUSE AXIS')]
                }

x_types_values = {
                'key': [True, [], None, True, _('KEYBOARD')],
                'mousebutton': [False, ["1", "2", "3", "4", "5", "6", "7"], None, False, _('MOUSE BUTTON')],
                'mouseaxis': [False, ["+X", "-X", "+Y", "-Y", "+Z", "-Z"], None, False, _('MOUSE AXIS')]
                }

# Fill with Numbers
for i in xrange(0,10):
    types_values['key'][1].append(str(i))

# Fill with F-Keys
for i in xrange(0,13):
    types_values['key'][1].append("F" + str(i))

# Fill width small keys (a-z)
#for i in xrange(97, 123):
#    types_values['key'][1].append(chr(i))

# Fill with cap keys (A-Z)
for i in xrange(65, 91):
    types_values['key'][1].append(chr(i))

# Create gtk-liststores mentioned above
for name in x_types_values:
    model = gtk.ListStore(str)
    for i in x_types_values[name][1]:
        model.append([i])
    x_types_values[name][2] = model

# Create gtk-liststores mentioned above
for name in types_values:
    model = gtk.ListStore(str)
    for i in types_values[name][1]:
        model.append([i])
    types_values[name][2] = model

# Create reverse mapping from Translated event description to event type
reverse_types = {}
for t in types_values:
    reverse_types[types_values[t][4]] = t

button_press_state = {1: _('Press'), 0: _('Release')}
button_press_state_reverse = {}
for state in button_press_state:
    button_press_state_reverse[button_press_state[state]] = state
button_press_model = gtk.ListStore(str)
for state in button_press_state_reverse:
    button_press_model.append([state])

class InfoWindow(gtk.Frame):
    def __init__(self, **args):
        if 'label' in args:
            gtk.Frame.__init__(self, label=_("Info for %s:") % args['label'])
        else:
            gtk.Frame.__init__(self, label=_("Info:"))
        self.info_display = gtk.TextView()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(self.info_display)
        self.add(scroll)
        self.info_display.set_wrap_mode(gtk.WRAP_WORD)
        self.info_buffer = self.info_display.get_buffer()
        self.info_buffer.create_tag(
            "warning",
            foreground='red'
        )
    
    def set_text(self, text, **kwdargs):
        self.info_buffer.set_text(text)
        if 'type' in kwdargs:
            if kwdargs['type'] == 'warning':
                self.info_buffer.apply_tag_by_name(
                                          "warning",
                                          self.info_buffer.get_start_iter(),
                                          self.info_buffer.get_end_iter())

class SubclassableCellTextRenderer(gtk.GenericCellRenderer):
    __gproperties__= {
        'editable': (gobject.TYPE_BOOLEAN, 'editable', 'is editable', True,
                     gobject.PARAM_READWRITE),
        'text': (gobject.TYPE_STRING, 'text', 'text displayed', '', 
                 gobject.PARAM_READWRITE)
    }
    
    property_names = __gproperties__.keys()
    
    __gsignals__ = {
         'edited': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                    (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT))
    }
    
    def __init__(self, *args):
        gtk.GenericCellRenderer.__init__(self, *args);
        self.set_property('mode', gtk.CELL_RENDERER_MODE_EDITABLE)
    
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)
    
    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
    
    def on_render(self, window, widget, bg_area, cell_area, exp_area, flags):
        x_offset, y_offset, width, height = self.on_get_size(widget, cell_area)
        layout = self.get_layout(widget)

         # Determine state to get text color right.
        if flags & gtk.CELL_RENDERER_SELECTED:
            if widget.get_property('has-focus'):
                state = gtk.STATE_SELECTED
            else:
                state = gtk.STATE_ACTIVE
        else:
            state = gtk.STATE_NORMAL

        widget.style.paint_layout(
            window, state, True, cell_area, widget, 'foo',
            cell_area.x + x_offset, cell_area.y + y_offset, layout
        )
        
    def get_layout(self, widget):
        '''Gets the Pango layout used in the cell in a TreeView widget.'''
        layout = pango.Layout(widget.get_pango_context())
        layout.set_width(-1)    # Do not wrap text.

        if self.text:
            layout.set_text(self.text)
        else:
            layout.set_text('')
        return layout
    
    def on_get_size(self, widget, cell_area):
        # The following size calculations have tested so that the TextView
        # will fully fit in the cell when editing and it will be the same
        # size as a CellRendererText cell with same amount or rows.
        xpad = 2
        ypad = 2
        xalign = 0
        yalign = 0.5
        layout = self.get_layout(widget)
        width, height = layout.get_pixel_size()

        x_offset = xpad
        y_offset = ypad

        if cell_area:
            x_offset = xalign * (cell_area.width - width)
            x_offset = max(x_offset, xpad)
            x_offset = int(round(x_offset, 0))

            y_offset = yalign * (cell_area.height - height)
            y_offset = max(y_offset, ypad)
            y_offset = int(round(y_offset, 0))

        width  = width  + (xpad * 2)
        height = height + (ypad * 2)

        return x_offset, y_offset, width, height


class CellCommandArgumentsEditor(gtk.Entry, gtk.CellEditable):
    __gsignals__ = {
         'edited': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,())
    }
    def __init__(self, *arg):
        gtk.Entry.__init__(self, *arg)
        #gtk.CellEditable.__init__(self, *arg)
        self.set_editable(False)
        
        self.hwindow = gtk.Window()
        self.hwindow.set_position(gtk.WIN_POS_MOUSE)
        self.hwindow.set_decorated(False)
        vbox = gtk.VBox()
        self.liststore = liststore = gtk.ListStore(str)
        self.treeview = treeview = gtk.TreeView(liststore)
        self.hwindow.set_default_size(200,  300)
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "param")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(0, _("Param"), textrenderer, text=0)

        treeview.set_headers_visible(True)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(treeview)
        vbox.pack_start(sw, expand=True, fill=True, padding=0)
        addbutton = gtk.Button(stock=gtk.STOCK_ADD)
        removebutton = gtk.Button(stock=gtk.STOCK_REMOVE)
        addbutton.connect("clicked", self.add_entry)
        removebutton.connect("clicked", self.remove_entry)
        buttonbox = gtk.HButtonBox()
        buttonbox.add(removebutton)
        buttonbox.add(addbutton)
        vbox.pack_start(buttonbox, expand=False, fill=True, padding=0)
        self.hwindow.add(vbox)
        self.hwindow.show_all()

    def add_entry(self, button):
        self.liststore.append(["New Param"])

    def remove_entry(self, button):
        (path, column) = self.treeview.get_cursor()
        if not path: return
        iter = self.liststore.get_iter(path)
        self.liststore.remove(iter)
        
    def set_arguments(self, arguments):
        self.liststore.clear()
        for arg in arguments:
            self.liststore.append([arg])
        self.set_text(", ".join(self.get_arguments()))
            
    def get_arguments(self):
        re = []
        for i in self.liststore:
            re.append(i[0])
        return re
    
    def _treeview_changed(self, cellrenderer, treepath, new_text, ctype):
        model = self.liststore
        iter = model.get_iter(treepath)
        if ctype == 'param':
            model.set(iter, 0, new_text)
        self.set_text(", ".join(self.get_arguments()))

    def do_editing_done(self, *dummy):
        pass
     
    def do_remove_widget(self):
        self.hwindow.destroy()
        
    def do_start_editing(self, *dummy):
        pass
    
class CellCommandArgumentsRenderer(SubclassableCellTextRenderer):
    def on_start_editing(self, event, widget, path, bg_area, cell_area, flags):
        editor = CellCommandArgumentsEditor()
        editor.grab_focus()
        editor.show_all()
        editor.connect("editing-done", lambda *args: self.emit(
                                            "edited", 
                                            path, 
                                            ", ".join(editor.get_arguments()),
                                            editor.get_arguments()))
        return editor
     
gobject.type_register(CellCommandArgumentsEditor)
gobject.type_register(CellCommandArgumentsRenderer)


class CellDBUSArgumentsEditor(gtk.Entry, gtk.CellEditable):
    __gsignals__ = {
         'edited': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,())
    }
    def __init__(self, *arg):
        gtk.Entry.__init__(self, *arg)
        self.set_editable(False)
        
        self.hwindow = gtk.Window()
        self.hwindow.set_position(gtk.WIN_POS_MOUSE)
        self.hwindow.set_decorated(False)
        vbox = gtk.VBox()
        self.liststore = liststore = gtk.ListStore(str, str)
        self.treeview = treeview = gtk.TreeView(liststore)
        self.hwindow.set_default_size(200,  300)

        comborenderer = gtk.CellRendererCombo()
        comborenderer.connect("edited", self._treeview_changed, "type")
        
        dbus_type_model = gtk.ListStore(str)
        dbus_type_model.append(['boolean'])
        dbus_type_model.append(['byte'])
        dbus_type_model.append(['int16'])
        dbus_type_model.append(['int32'])
        dbus_type_model.append(['int64'])
        dbus_type_model.append(['uint16'])
        dbus_type_model.append(['uint32'])
        dbus_type_model.append(['uint64'])
        dbus_type_model.append(['string'])
        dbus_type_model.append(['double'])
        
        comborenderer.set_property("model", dbus_type_model)
        comborenderer.set_property("text-column", 0)
        comborenderer.set_property("editable", True)
        comborenderer.set_property("has-entry", False)
        treeview.insert_column_with_attributes(0, _("Param-Type"), comborenderer, text=0)
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "param")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(1, _("Param"), textrenderer, text=1)

        treeview.set_headers_visible(True)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(treeview)
        vbox.pack_start(sw, expand=True, fill=True, padding=0)
        addbutton = gtk.Button(stock=gtk.STOCK_ADD)
        removebutton = gtk.Button(stock=gtk.STOCK_REMOVE)
        addbutton.connect("clicked", self.add_entry)
        removebutton.connect("clicked", self.remove_entry)
        buttonbox = gtk.HButtonBox()
        buttonbox.add(removebutton)
        buttonbox.add(addbutton)
        vbox.pack_start(buttonbox, expand=False, fill=True, padding=0)
        self.hwindow.add(vbox)
        self.hwindow.show_all()

    def add_entry(self, button):
        self.liststore.append(["boolean", "true"])

    def remove_entry(self, button):
        (path, column) = self.treeview.get_cursor()
        if not path: return
        iter = self.liststore.get_iter(path)
        self.liststore.remove(iter)
        
    def set_arguments(self, arguments):
        self.liststore.clear()
        for arg in arguments:
            (param_type, param) = arg.split(":", 2)
            self.liststore.append([param_type, param])
        self.set_text(", ".join(self.get_arguments()))
            
    def get_arguments(self):
        re = []
        for i in self.liststore:
            re.append(":".join(i))
        return re
    
    def _treeview_changed(self, cellrenderer, treepath, new_text, ctype):
        model = self.liststore
        iter = model.get_iter(treepath)
        if ctype == 'param':
            model.set(iter, 1, new_text)
        elif ctype == 'type':
            model.set(iter, 0, new_text)
        self.set_text(", ".join(self.get_arguments()))

    def do_editing_done(self, *dummy):
         pass
     
    def do_remove_widget(self):
        self.hwindow.destroy()
        
    def do_start_editing(self, *dummy):
         pass

class CellDBUSArgumentsRenderer(SubclassableCellTextRenderer):
    def on_start_editing(self, event, widget, path, bg_area, cell_area, flags):
        editor = CellDBUSArgumentsEditor()
        editor.grab_focus()
        editor.show_all()
        editor.connect("editing-done", lambda *args: self.emit(
                                            "edited", 
                                            path, 
                                            ", ".join(editor.get_arguments()),
                                            editor.get_arguments()))
        return editor
     
gobject.type_register(CellDBUSArgumentsEditor)
gobject.type_register(CellDBUSArgumentsRenderer)

class ProfileQueryWindow(gtk.Dialog):
    """
    Dialog presenting a dialog to the user querying for a new profile name, at
    the time of creation or rename of profiles.
    """
    def __init__(self, query="", title = "", parent = None):
        gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_MODAL, 
                                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, 
                                 gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.cancel_button = None
        self.ok_button = None
        self.action_area.foreach(self.get_buttons)
        
        self.datamodel = gtk.ListStore(str, str, str)
        self.userprofiles = []
        
        table = gtk.Table(2, 3)
        
        self.pcombobox = gtk.ComboBox()
        self.pcombobox.set_model(self.datamodel)
        self.plabel = gtk.Label(_("Basisprofile") + ": ")
        renderer = gtk.CellRendererText()
        self.pcombobox.pack_start(renderer)
        self.pcombobox.add_attribute(renderer, "text", 0)
        
        label = gtk.Label(title)
        label2 = gtk.Label(query + ": ")
        self.input_entry = gtk.Entry()
        
        self.vbox.add(label)
        self.vbox.add(table)
        
        self.warn_name_label = gtk.Image()
        self.warn_name_label.set_from_stock(gtk.STOCK_DIALOG_WARNING, 
                                            gtk.ICON_SIZE_SMALL_TOOLBAR)
        
        table.attach(self.plabel, 0, 1, 0, 1, xoptions=gtk.FILL, 
                                              yoptions=gtk.FILL)
        table.attach(self.pcombobox, 1, 3, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, 
                                                 yoptions=gtk.FILL)
        table.attach(label2, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=gtk.FILL)
        table.attach(self.warn_name_label, 1, 2, 1, 2, xoptions=gtk.FILL, 
                                                       yoptions=gtk.FILL)
        table.attach(self.input_entry, 2, 3, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, 
                                                   yoptions=gtk.FILL)
        
        self.input_entry.connect("changed", self.check_text)
        self.check_text(self.input_entry)
        
        self.input_entry.show()
        label.show()
        label2.show()
        table.show()

    def get_buttons(self, button):
        """
        Get the correct buttons from the dialog and assign them for access
        for disabling the ok button when an illegal name is entered.
        """
        if button.get_property("label") == gtk.STOCK_CANCEL:
            self.cancel_button = button
        elif button.get_property("label") == gtk.STOCK_OK:
            self.ok_button = button

    def check_text(self, entry):
        """
        Check the text of the entry whether it conflicts with an existing
        profile or it is an empty string.
        """
        text = entry.get_text()
        if text == "" or text in self.userprofiles:
            self.warn_name_label.show()
            self.ok_button.set_sensitive(False)
        else:
            self.warn_name_label.hide()
            self.ok_button.set_sensitive(True)

    def get_text(self):
        """
        Retrieve the selected name from the dialog
        """
        return self.input_entry.get_text()
    
    def get_curr_profile(self):
        """
        Get the profile the user selected as base. See set_curr_profile_selection
        for more information.
        """
        treeiter = self.pcombobox.get_active_iter()
        if treeiter:
            return self.datamodel.get(treeiter, 1, 2)
        else:
            return ["emptry", "none"]
    
    def set_curr_profiles(self, dataset):
        """
        Set profiles for selection by the user - see set_curr_profile_selection
        for more info.
        """
        self.datamodel.clear()
        self.datamodel.append(["Leeres Profil", 'empty', 'none'])
        self.userprofiles[:] = []
        for (displayname, profile, configfile) in dataset:
            self.datamodel.append([displayname, profile, configfile])
            if config == 'user':
                self.userprofiles.append(profile)
    
    def set_curr_profile_selection(self, show):
        """
        Show the user a combo box to select the current profile. For example
        when creating a new profile select an old one to base on.
        """
        if show:
            self.plabel.show()
            self.pcombobox.show()
        else:
            self.plabel.hide()
            self.pcombobox.hide()

class ConfigWindowWidget(gtk.VBox):
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }
    
    def __init__(self, config, subaction, modules):
        gtk.VBox.__init__(self)
        self.modules = modules
        self.subaction = subaction
        scrolledwindow = gtk.ScrolledWindow()
        self.treeview = treeview = gtk.TreeView()
        scrolledwindow.add(treeview)
        self.add(scrolledwindow)
        offset = 0
        if subaction == 'actions':
            textrenderer = gtk.CellRendererText()
            #textrenderer.connect("edited", self._treeview_changed, "repeat")
            #textrenderer.set_property("editable-set", True)
            treeview.insert_column_with_attributes(
                        0, 
                        _("Keycode"), 
                        textrenderer,
                        text=0)
            textrenderer = gtk.CellRendererText()
            #textrenderer.connect("edited", self._treeview_changed, "repeat")
            #textrenderer.set_property("editable-set", True)
            treeview.insert_column_with_attributes(
                        1, 
                        _("Mapping"), 
                        textrenderer,
                        text=1)
            offset = 2

        textrenderer = gtk.CellRendererText()
        #textrenderer.connect("edited", self._treeview_changed, "repeat")
        #textrenderer.set_property("editable-set", True)
        treeview.insert_column_with_attributes(
                    offset, 
                    _("Module"), 
                    textrenderer,
                    text=2)
        textrenderer = gtk.CellRendererText()
        #textrenderer.connect("edited", self._treeview_changed, "repeat")
        #textrenderer.set_property("editable-set", True)
        treeview.insert_column_with_attributes(
                    offset+1, 
                    _("Description"), 
                    textrenderer,
                    text=3)      
        
        for i in xrange(0, offset+2):
            treeview.get_column(i).set_resizable(True)
            treeview.get_column(i).set_sort_column_id(i+offset)     
        
        self.config = config
        self.editable = False
        self.entries = gtk.ListStore(str, str, str, str, gobject.TYPE_PYOBJECT)
    
    def set_noprofile(self):
        self.section = None
        self.editable = False
        self.update_view()
    
    def set_profile(self, profileid, config):
        self.entries.clear()
        for mod in self.modules:
            name = mod.name
            config_section = mod.section
            description = mod.description
            try:
                section = self.config.get_profile(config, profileid, config_section)
                for entry in section[self.subaction]:
                    keycode = mapping = ""
                    if 'keycode' in entry:
                        keycode = str(entry['keycode'])
                    if 'mapping' in entry:
                        mapping = str(entry['mapping'])
                    self.entries.append([keycode, mapping, name, description(entry), entry])
            except (LBRC.config.sectionNotFoundException, KeyError):
                pass
        if config == 'system':
            self.set_editable(False)
        else:
            self.set_editable(True)
        self.update_view()
        
    def update_view(self):
        print "Updated view with:" + str(self.entries)
        self.treeview.set_model(self.entries)
        
    def set_editable(self, value):
        self.editable = value
        self.treeview.set_sensitive(value)
        
class UinputKeyMouseEditor(ConfigWindowWidget):
    """
    Widget for configuration of UinputDispatcher
    
    @signal: changed
        This signal is fired, when the config data of this modules was changed in here
    """
    title = _("Keyboard/Mouse (old-deprecated!)")
    config_section = 'UinputDispatcher'
    
    def __init__(self, config):
        ConfigWindowWidget.__init__(self, config)
        
        expander = gtk.Expander(_("Actions"))
        expander.set_expanded(True)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
        infobox = InfoWindow()
        text = "Beware! This module is  deprecated and only provided for " + \
               "backward compatibility. It will probaly removed from the " + \
               "programm in the next release"
        infobox.set_text(text, type="warning")
        vbox.pack_start(infobox, expand=False, fill=True, padding=5)
        
        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        self.addbutton = addbutton = gtk.Button(stock="gtk-add")
        self.removebutton = removebutton = gtk.Button(stock="gtk-remove")
        addbutton.connect("clicked", self.on_addbutton_clicked)
        removebutton.connect("clicked", self.on_removebutton_clicked)
        
        self.treeview = treeview = gtk.TreeView()
        
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
        for i in types_values.values():
            mylist.append([i[4]])
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
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=True, fill=True, padding=0)
        
        self.show_all()
        
    def update_view(self):
        # 0 => keycode, 1 => map_to, 2 => repeat_freq, 3 => EVENT TYPE, 
        # 4 => BACKGOROUND COLOR, 5 => EVENT TYPE DESCRIPTION 6 => is a repeater
        # 7 => model for the event mapping, 8 => do we allow other event mappings (useful for keyboard)
        
        mylist = gtk.ListStore(int, str, int, str, str, str, gobject.TYPE_BOOLEAN, gtk.ListStore,gobject.TYPE_BOOLEAN, gobject.TYPE_PYOBJECT)

        if self.editable:
            self.addbutton.set_sensitive(True)
            self.removebutton.set_sensitive(True)
            self.treeview.set_sensitive(True)
        else:
            self.addbutton.set_sensitive(False)
            self.removebutton.set_sensitive(False)
            self.treeview.set_sensitive(False)
    
        try:
            for map in self.section['actions']:
                type = map['type']
                mylist.append([
                    map['keycode'], 
                    map['map_to'], 
                    int(map.get('repeat_freq', 0)),
                    type,
                    "snow",
                    types_values[type][4],
                    types_values[type][3],
                    types_values[type][2],
                    types_values[type][0],
                    map
                ])
        except KeyError: pass
        except TypeError: pass

        self.treeview.set_model(mylist)        
        
    def _treeview_changed(self, cellrenderer, treepath, new_text, ctype):
        # 0 => keycode, 1 => map_to, 2 => repeat_freq, 3 => EVENT TYPE, 
        # 4 => BACKGOROUND COLOR, 5 => EVENT TYPE DESCRIPTION 6 => is a repeater
        # 7 => model for the event mapping, 8 => do we allow other event mappings (useful for keyboard)
        #
        # TODO: Check that we got valid values
        tv = self.treeview
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
        
        model.set(iter, 0, keycode, 1, map_to, 2, repeat_freq, 3, type, 5, types_values[type][4],
                        6, types_values[type][3], 7, types_values[type][2],
                        8, types_values[type][0])
        
        self.emit('changed')
        
    def on_removebutton_clicked(self, object):
        model = self.treeview.get_model()
        (path, column) = self.treeview.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 9)
        self.section['actions'].remove(entry)
        model.remove(iter)
        self.emit("changed")

    def on_addbutton_clicked(self, object):
        model = self.treeview.get_model()

        map = {'keycode': 0, 'type': 'key', 'map_to': 'A', 'repeat_freq': 0}
        
        if not 'actions' in self.section:
            self.section['actions'] = []
        
        self.section['actions'].append(map)
        
        type = map['type']
        iter = model.append([
            map['keycode'], 
            map['map_to'], 
            int(map.get('repeat_freq', 0)),
            type,
            "snow",
            types_values[type][4],
            types_values[type][3],
            types_values[type][2],
            types_values[type][0],
            map
        ])
        self.treeview.set_cursor(model.get_path(iter))
        self.emit("changed")

class XInputRenderEditor(gtk.Editable, gtk.CellEditable, gobject.GObject):
    def __init__(self, *arg):
        gobject.GObject.__init__(self)
        self.hwindow = gtk.Window()
        self.hwindow.set_position(gtk.WIN_POS_MOUSE)
        self.hwindow.set_decorated(False)
        self.hwindow.set_default_size(200,  300)
        
        vbox = gtk.VBox()

        label = gtk.Label("gga")
        
        vbox.add(label) 
        
        self.hwindow.add(vbox)
        self.hwindow.show_all()

    def add_entry(self, button):
        self.liststore.append(["New Param"])

    def remove_entry(self, button):
        (path, column) = self.treeview.get_cursor()
        if not path: return
        iter = self.liststore.get_iter(path)
        self.liststore.remove(iter)
        
    def set_arguments(self, arguments):
        self.liststore.clear()
        for arg in arguments:
            self.liststore.append([arg])
        self.set_text(", ".join(self.get_arguments()))
            
    def get_arguments(self):
        re = []
        for i in self.liststore:
            re.append(i[0])
        return re

    def do_editing_done(self, *dummy):
        pass
     
    def do_remove_widget(self):
        self.hwindow.destroy()
        
    def do_start_editing(self, *dummy):
        pass

class XInputRenderer(SubclassableCellTextRenderer):
    __gproperties__ = {'type': (gobject.TYPE_STRING, 'type', 
                                'type of the input', "",
                                 gobject.PARAM_READWRITE),}
    def on_start_editing(self, event, widget, path, bg_area, cell_area, flags):
        print type(widget.get_model())
        if self.type == 'key':
            editor = XInputEditorArgumentsEditor()
            editor.grab_focus()
            editor.show_all()
            editor.connect("editing-done", lambda *args: self.emit(
                                            "edited", 
                                            path,
                                            ", ".join(editor.get_arguments()), 
                                            editor.get_arguments()))
            return editor
        else:
            input = gtk.Entry()
            

gobject.type_register(XInputRenderer)
gobject.type_register(XInputRenderEditor)
    

class ConfigWindow(gobject.GObject):
    """
    Widget to configure LBRC

    @signal: close (was_changed)
             This signal is fired when the config window has be closed if any 
             configuration has be changed the parameter was_changed will be True.
    """
    __gsignals__ = {
        'close': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }

    configModules = []

    for i in ('CommandExecutor', 'DBUSCaller', 'MPlayer', 'PresentationCompanion',
              'UinputDispatcher', 'XInput'):
        cm = __import__("LBRC_gtk_gui.config" + i);
        configModules.append( cm.__dict__["config" + i] )

    # TODO: Config item for ProfileSwitcher
    # TODO: Config for VolumeControl

    def __init__(self):
        gobject.GObject.__init__(self)
        # create widget tree ...
        self.xml = gtk.glade.XML(osp.join(path().get_guidir(), "config.glade"))

        self.modified = False
        
        self.logger = logging.getLogger("ConfigWindow")

        # Wrapper to get a widget from glade's xml
        self.widget = self.xml.get_widget

        self.widget("config-window").show_all()

        self._load_config()
        
        self.config_applets = []
        
        renderer = gtk.CellRendererText()
        renderer.set_property("ellipsize", pango.ELLIPSIZE_END)
        self.widget("profile-combobox").clear()
        self.widget("profile-combobox").pack_start(renderer)
        self.widget("profile-combobox").add_attribute(renderer, "text", 0)
        
        self.widget("config_notebook").set_scrollable(True)
        
        for i in ( 'Init', 'Actions', 'Destruct'):
            self.config_applets.append(
              ConfigWindowWidget(self.config, i.lower(), self.configModules)
            )
            self.widget("config_notebook").append_page(
              self.config_applets[-1], gtk.Label(i))
        
        self.widget("config_notebook").show_all()
        self.widget("config_notebook").set_current_page(1)
        
        self._fill_window()
        #connnect signals
        self.xml.signal_autoconnect(self)

    def _change_handler(self, *args):
        self.modified = True

    def _load_config(self):
        """Loads the config file"""
        self.config = config()    
        self.user_profiles = self.config.user['profiles']
        self.system_profiles = self.config.system['profiles']     
        
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

    def _fill_profiles(self, select_item = None):
        """Fills the profile-combobox widget"""
        profile = self.widget("profile-combobox")
        
        last_active = profile.get_active()

        # 1 => Displayname, 2 => profile, 3 => config
        profile_model = gtk.ListStore(str, str, str)

        for i in sorted(self.system_profiles.keys()):
            itemname = '%s (%s)' % (i, _("System"))
            profile_model.append((itemname, i, "system"))
        
        select_iter = None
        
        for i in sorted(self.user_profiles.keys()):
            iter = profile_model.append((i, i, "user"))
            if i == select_item:
                select_iter = iter
            
        profile.set_model(profile_model)

        if select_iter:
            profile.set_active_iter(select_iter)

    def _create_new_profile(self, profile_name, base_profile, base_config):
        keys = self.user_profiles.keys() + self.system_profiles.keys()
        if keys and profile_name.lower() in map(str.lower, keys):
            #profile already exists
            self.logger.debug("New profile name already exists: %s" % 
                               profile_name)
            return False
        try:
            if base_config == 'system':
                old_profile = self.system_profiles[base_profile]
            elif base_config == 'user':
                old_profile = self.user_profiles[base_profile]
            self.user_profiles[profile_name] = copy.deepcopy(old_profile)
        except:
            self.user_profiles[profile_name] = {}
        self.modified = True
        self._fill_profiles(select_item = profile_name)
        self.update_configs()
        return True
    
    def on_config_window_destroy(self, destroy):
        if self.modified:
            self.config.write()
        self.emit("close", self.modified)
        return True

    def on_save_current_checkbutton_toggled(self, object):
        self.config.set_config_item("persistent", object.get_active())
        self.modified = True

    def on_uinput_device_entry_changed(self, object):
        udev_path = object.get_text().strip()
        if udev_path:
            self.config.set_config_item("uinput-device", udev_path)
        else:
            self.config.set_config_item("uinput-device", "")
        self.modified = True
    
    def on_show_bluetooth_checkbutton_toggled(self, object):
        self.config.set_config_item("show-bluetooth", object.get_active())
        self.modified = True

    def on_require_pairing_checkbutton_toggled(self, object):
        self.config.set_config_item("require-pairing", object.get_active())
        self.modified = True

    def on_onetime_pairing_checkbutton_toggled(self, object):
        self.config.set_config_item("remove-pairing", object.get_active())
        self.modified = True

    def on_profile_combobox_changed(self, combobox):
        config_file = combobox.get_model().get(combobox.get_active_iter(), 2)[0]
        if config_file == 'user':
            self.widget("profile-rename-button").set_sensitive(True)
            self.widget("profile-delete-button").set_sensitive(True)
        else:
            self.widget("profile-rename-button").set_sensitive(False)
            self.widget("profile-delete-button").set_sensitive(False)
        self.update_configs()

    def update_configs(self):
        combobox = self.widget("profile-combobox")
        iter = combobox.get_active_iter()
        if iter:
            (profileid, config) = combobox.get_model().get(iter, 1, 2)
            for i in self.config_applets:
                i.set_profile(profileid, config)
        else:
            for i in self.config_applets:
                i.set_noprofile()

    def on_profile_new_button_clicked(self, button):
        input_window = ProfileQueryWindow(query=_("New Name"),
                                   title=_("What is the name for the new profile?"), 
                                   parent = self.widget("config-window"))
        input_window.set_curr_profiles(self.widget("profile-combobox").get_model())
        input_window.set_curr_profile_selection(True)
        responce = input_window.run()
        if responce == gtk.RESPONSE_ACCEPT:
            text = input_window.get_text().strip()
            if len(text) > 0:
                (profile, config_file) = input_window.get_curr_profile()
                self._create_new_profile(text, profile, config_file)
        input_window.destroy()


    def on_profile_rename_button_clicked(self, object):        
        input_window = ProfileQueryWindow(query=_("New Name"),
                                   title=_("Specify the new name for the new profile"), 
                                   parent = self.widget("config-window"))
        input_window.set_curr_profiles(self.widget("profile-combobox").get_model())
        responce = input_window.run()
        if responce == gtk.RESPONSE_ACCEPT:
            text = input_window.get_text().strip()
            iter = self.widget("profile-combobox").get_active_iter()
            if len(text) > 0 and not text in self.user_profiles and iter:
                model = self.widget("profile-combobox").get_model()
                data = model.get(iter,1,2)       
                if data[1] == "user":
                    model.set(iter, 0, text, 1, text)
                    self.user_profiles[text] = self.user_profiles[data[0]]
                    del(self.user_profiles[data[0]])
                    self.modified = True
                    self._fill_profiles(select_item = text)
                    self.update_configs()
        input_window.destroy()

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
            self.update_configs()
            
    def on_config_revert_button_clicked(self, object):
        self._load_config()
        self._fill_window(False)
        self.modified = False

    def on_config_close_button_clicked(self, object):
        self.widget('config-window').destroy()