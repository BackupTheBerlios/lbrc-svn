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
import dbus.glib

import copy

import gtk
import gtk.glade
import gobject
import pango

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

button_press_state = {1: _('Press'), 0: _('Release')}
button_press_state_reverse = {}
for state in button_press_state:
    button_press_state_reverse[button_press_state[state]] = state
button_press_model = gtk.ListStore(str)
for state in button_press_state_reverse:
    button_press_model.append([state])

# TIP: Command to get name of handlers from config.glade
# >grep handler LBRC_gtk_gui/config.glade | perl -pe 's/.*"(on_.*?)".*/$1/'

class CellCommandArgumentsEditor(gtk.Entry, gtk.CellEditable):
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

    def do_editing_done(*args):
         pass
     
    def do_remove_widget(self):
        self.hwindow.destroy()
        
    def do_start_editing(*args):
         pass

class CellCommandArgumentsRenderer(gtk.GenericCellRenderer):
    __gproperties__= {
        "backupdata": (gobject.TYPE_PYOBJECT, "Backup", "Backup", gobject.PARAM_READWRITE),
        'editable': (gobject.TYPE_BOOLEAN, 'editable', 'is editable', True, gobject.PARAM_READWRITE),
        'text': (gobject.TYPE_STRING, 'text', 'text displayed', '', gobject.PARAM_READWRITE)
    }
    __gsignals__ = {
         'edited': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                    (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT))
    }

    property_names = __gproperties__.keys()
    
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)
    
    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
    
    def __init__(self, *args):
        gtk.GenericCellRenderer.__init__(self, *args)
        self.set_property('mode', gtk.CELL_RENDERER_MODE_EDITABLE)
    
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


    def on_start_editing(self, event, widget, path, bg_area, cell_area, flags):
         editor = CellCommandArgumentsEditor()
         try:
             editor.set_arguments(self.get_property("backupdata")['arguments'])
         except:
             empty_array = []
             editor.set_arguments(empty_array)
             self.get_property("backupdata")['arguments'] = empty_array
         editor.grab_focus()
         editor.show_all()
         editor.connect("editing-done", lambda *args: self.emit("edited", path, ", ".join(editor.get_arguments()), editor.get_arguments()))
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

    def do_editing_done(*args):
         pass
     
    def do_remove_widget(self):
        self.hwindow.destroy()
        
    def do_start_editing(*args):
         pass

class CellDBUSArgumentsRenderer(gtk.GenericCellRenderer):
    __gproperties__= {
        "backupdata": (gobject.TYPE_PYOBJECT, "Backup", "Backup", gobject.PARAM_READWRITE),
        'editable': (gobject.TYPE_BOOLEAN, 'editable', 'is editable', True, gobject.PARAM_READWRITE),
        'text': (gobject.TYPE_STRING, 'text', 'text displayed', '', gobject.PARAM_READWRITE)
    }
    __gsignals__ = {
         'edited': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                    (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT))
    }

    property_names = __gproperties__.keys()
    
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)
    
    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
    
    def __init__(self, *args):
        gtk.GenericCellRenderer.__init__(self, *args)
        self.set_property('mode', gtk.CELL_RENDERER_MODE_EDITABLE)
    
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


    def on_start_editing(self, event, widget, path, bg_area, cell_area, flags):
         editor = CellDBUSArgumentsEditor()
         try:
             editor.set_arguments(self.get_property("backupdata")['arguments'])
         except:
             empty_array = []
             editor.set_arguments(empty_array)
             self.get_property("backupdata")['arguments'] = empty_array
         editor.grab_focus()
         editor.show_all()
         editor.connect("editing-done", lambda *args: self.emit("edited", path, ", ".join(editor.get_arguments()), editor.get_arguments()))
         return editor
     
gobject.type_register(CellDBUSArgumentsEditor)
gobject.type_register(CellDBUSArgumentsRenderer)

class InputWindow(gtk.Dialog):
    def __init__(self, query="", title = "", parent = None):
        gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, 
                                                                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.datamodel = gtk.ListStore(str, str, str)
        self.userprofiles = []
        
        table = gtk.Table(2,2)
        
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
        
        table.attach(self.plabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=gtk.FILL)
        table.attach(self.pcombobox, 1, 2, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.FILL)
        table.attach(label2, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=gtk.FILL)
        table.attach(self.input_entry, 1, 2, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.FILL)
        
        self.input_entry.show()
        label.show()
        label2.show()
        table.show()

    def get_text(self):
        return self.input_entry.get_text()
    
    def get_curr_profile(self):
        iter = self.pcombobox.get_active_iter()
        if iter:
            return self.datamodel.get(iter, 1, 2)
        else:
            return ["emptry", "none"]
    
    def set_curr_profiles(self, model):
        self.datamodel.clear()
        self.datamodel.append(["Leeres Profil", 'empty', 'none'])
        self.userprofiles[:] = []
        for (displayname, profile, config) in model:
            self.datamodel.append([displayname, profile, config])
            if config == 'user':
                self.userprofiles.append(profile)
    
    def set_curr_profile_selection(self, show):
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
    def __init__(self, config):
        gtk.VBox.__init__(self)
        self.config = config
        self.editable = False
        self.section = None
    
    def set_noprofile(self):
        self.section = None
        self.editable = False
        self.update_view()
    
    def set_profile(self, profileid, config):
        try:
            self.section = self.config.get_profile(config, profileid, self.config_section)
        except LBRC.config.sectionNotFoundException:
            profile = self.config.get_profile(config, profileid)
            self.section = {}
            if config == 'user':
                profile[self.config_section] = self.section
        if config == 'system':
            self.set_editable(False)
        else:
            self.set_editable(True)
        self.update_view()
        
    def update_view(self):
        pass
        
    def set_editable(self, value):
        self.editable = value
        self.set_sensitive(value)
    
    def on_expander_activate(self, expander):
        # Set packing for expander in Boxes
        parent = expander.get_parent()
        if not parent: return
        if not isinstance(parent, gtk.Box): return
        old_state = expander.get_expanded()
        (expand, fill, padding, pack_type) = parent.query_child_packing(expander)
        if old_state:
            expand = False
            fill = False
        else:
            expand = True
            fill = True
        parent.set_child_packing(expander, expand, fill, padding, pack_type)
        
class KeyMouseEditor(ConfigWindowWidget):
    """
    Widget for configuration of UinputDispatcher
    
    @signal: changed
        This signal is fired, when the config data of this modules was changed in here
    """
    title = _("Keyboard/Mouse")
    config_section = 'UinputDispatcher'
    
    def __init__(self, config):
        ConfigWindowWidget.__init__(self, config)
        
        expander = gtk.Expander(_("Actions"))
        expander.set_expanded(True)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
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
                    types_detailed[type],
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
        
        model.set(iter, 0, keycode, 1, map_to, 2, repeat_freq, 3, type, 5, types_detailed[type],
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
            colors[type],
            types_detailed[type],
            types_values[type][3],
            types_values[type][2],
            types_values[type][0],
            map
        ])
        self.treeview.set_cursor(model.get_path(iter))
        self.emit("changed")

class DBusCallerEditor(ConfigWindowWidget):
    """
    Widget for configuration of DBUSCaller
    
    @signal: changed
        This signal is fired, when the config data of this modules was changed in here
    """
    title = _("DBUSCaller")
    config_section = 'DBUSCaller'
    
    def __init__(self, config):
        ConfigWindowWidget.__init__(self, config)
 
        #======================
         
        expander = gtk.Expander(_("On Initialisation"))
        expander.set_expanded(False)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        self.addbutton_init = addbutton = gtk.Button(stock="gtk-add")
        self.removebutton_init = removebutton = gtk.Button(stock="gtk-remove")
        addbutton.connect("clicked", self.on_addbutton_init_clicked)
        removebutton.connect("clicked", self.on_removebutton_init_clicked)
        
        self.treeview_init = treeview = gtk.TreeView()
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_init_changed, "service")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            0, 
            _("Service"), 
            textrenderer, 
            text=0
        )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_init_changed, "object")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            1, 
            _("Object"), 
            textrenderer,
            text=1,
        )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_init_changed, "interface")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            2, 
            _("Interface"), 
            textrenderer,
            text=2,
        )        
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_init_changed, "method")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            3, 
            _("Method"), 
            textrenderer,
            text=3,
        )
        
        textrenderer = CellDBUSArgumentsRenderer()
        textrenderer.connect("edited", self._treeview_init_changed, "arguments")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            4, 
            _("Arguments"), 
            textrenderer,
            text=4,
            backupdata=5
        )        
        
        treeview.get_column(0).set_resizable(True)
        treeview.get_column(0).set_sort_column_id(0)
        treeview.get_column(1).set_resizable(True)
        treeview.get_column(1).set_sort_column_id(1)
        treeview.get_column(2).set_resizable(True)
        treeview.get_column(2).set_sort_column_id(2)
        treeview.get_column(3).set_resizable(True)
        treeview.get_column(3).set_sort_column_id(3)
        treeview.get_column(4).set_resizable(True)
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=False, fill=False, padding=0)
        
        #======================
        
        expander = gtk.Expander(_("Actions"))
        expander.set_expanded(True)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
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
            _("Keycode"), 
            textrenderer, 
            text=0
        )

        comborenderer = gtk.CellRendererCombo()
        comborenderer.connect("edited", self._treeview_changed, "state")
        comborenderer.set_property("model", button_press_model)
        comborenderer.set_property("text-column", 0)
        comborenderer.set_property("editable", True)
        comborenderer.set_property("has-entry", False)
        treeview.insert_column_with_attributes(
            1, 
            _("State"), 
                comborenderer,
                text=1
            )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "service")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            2, 
            _("Service"), 
            textrenderer, 
            text=2
        )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "object")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            3, 
            _("Object"), 
            textrenderer,
            text=3
        )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "interface")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            4, 
            _("Interface"), 
            textrenderer,
            text=4,
        )        
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "method")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            5, 
            _("Method"), 
            textrenderer,
            text=5,
        )
        
        textrenderer = CellDBUSArgumentsRenderer()
        textrenderer.connect("edited", self._treeview_changed, "arguments")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            6, 
            _("Arguments"), 
            textrenderer,
            text=6,
            backupdata=7
        )        
        
        treeview.get_column(0).set_resizable(True)
        treeview.get_column(0).set_sort_column_id(0)
        treeview.get_column(1).set_resizable(True)
        treeview.get_column(1).set_sort_column_id(1)
        treeview.get_column(2).set_resizable(True)
        treeview.get_column(2).set_sort_column_id(2)
        treeview.get_column(3).set_resizable(True)
        treeview.get_column(3).set_sort_column_id(3)
        treeview.get_column(4).set_resizable(True)
        treeview.get_column(4).set_sort_column_id(4)
        treeview.get_column(5).set_resizable(True)
        treeview.get_column(5).set_sort_column_id(5)
        treeview.get_column(6).set_resizable(True)
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=True, fill=True, padding=0)

        #======================
         
        expander = gtk.Expander(_("On Destruction"))
        expander.set_expanded(False)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        self.addbutton_destruct = addbutton = gtk.Button(stock="gtk-add")
        self.removebutton_destruct = removebutton = gtk.Button(stock="gtk-remove")
        addbutton.connect("clicked", self.on_addbutton_destruct_clicked)
        removebutton.connect("clicked", self.on_removebutton_destruct_clicked)
        
        self.treeview_destruct = treeview = gtk.TreeView()
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_destruct_changed, "service")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            0, 
            _("Service"), 
            textrenderer, 
            text=0
        )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_destruct_changed, "object")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            1, 
            _("Object"), 
            textrenderer,
            text=1,
        )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_destruct_changed, "interface")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            2, 
            _("Interface"), 
            textrenderer,
            text=2,
        )        
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_destruct_changed, "method")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            3, 
            _("Method"), 
            textrenderer,
            text=3,
        )
        
        textrenderer = CellDBUSArgumentsRenderer()
        textrenderer.connect("edited", self._treeview_destruct_changed, "arguments")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            4, 
            _("Arguments"), 
            textrenderer,
            text=4,
            backupdata=5
        )        
        
        treeview.get_column(0).set_resizable(True)
        treeview.get_column(0).set_sort_column_id(0)
        treeview.get_column(1).set_resizable(True)
        treeview.get_column(1).set_sort_column_id(1)
        treeview.get_column(2).set_resizable(True)
        treeview.get_column(2).set_sort_column_id(2)
        treeview.get_column(3).set_resizable(True)
        treeview.get_column(3).set_sort_column_id(3)
        treeview.get_column(4).set_resizable(True)
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=False, fill=False, padding=0)
        
        #======================

        self.show_all()
        
    def update_view(self):
        mylist = gtk.ListStore(str, str, str, str, str, gobject.TYPE_PYOBJECT)

        if self.editable:
            self.addbutton_init.set_sensitive(True)
            self.removebutton_init.set_sensitive(True)
            self.treeview_init.set_sensitive(True)
        else:
            self.addbutton_init.set_sensitive(False)
            self.removebutton_init.set_sensitive(False)
            self.treeview_init.set_sensitive(False)
    
        try:
            for map in self.section['init']:
                args = ''
                if 'arguments' in map:
                    args = ", ".join(map['arguments'])
                mylist.append([
                               map['service'],
                               map['object'],
                               map['interface'],
                               map['method'],
                               args,
                               map
                ])
        except KeyError: pass
        except TypeError: pass

        self.treeview_init.set_model(mylist)
 
        mylist = gtk.ListStore(int, str, str, str, str, str, str, gobject.TYPE_PYOBJECT)

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
                args = ''
                if 'arguments' in map:
                    args = ", ".join(map['arguments'])
                try:
                    mapping = button_press_state[int(map['mapping'])]
                except:
                    mapping = button_press_state[0]
                mylist.append([
                               int(map['keycode']),
                               mapping,
                               map['service'],
                               map['object'],
                               map['interface'],
                               map['method'],
                               args,
                               map
                ])
        except KeyError: pass
        except TypeError: pass

        self.treeview.set_model(mylist)
        
        mylist = gtk.ListStore(str, str, str, str, str, gobject.TYPE_PYOBJECT)

        if self.editable:
            self.addbutton_destruct.set_sensitive(True)
            self.removebutton_destruct.set_sensitive(True)
            self.treeview_destruct.set_sensitive(True)
        else:
            self.addbutton_destruct.set_sensitive(False)
            self.removebutton_destruct.set_sensitive(False)
            self.treeview_destruct.set_sensitive(False)
    
        try:
            for map in self.section['destruct']:
                args = ''
                if 'arguments' in map:
                    args = ", ".join(map['arguments'])
                mylist.append([
                               map['service'],
                               map['object'],
                               map['interface'],
                               map['method'],
                               args,
                               map
                ])
        except KeyError: pass
        except TypeError: pass

        self.treeview_destruct.set_model(mylist)     
        
    def _treeview_changed(self, cellrenderer, treepath, *args):
        if len(args) == 2:
            new_text = args[0]
            ctype = args[1]
        elif len(args) == 3:
            new_text = args[0]
            object = args[1]
            ctype = args[2]
        tv = self.treeview
        model = tv.get_model()
        iter = model.get_iter(treepath)
        # TODO: Handle arguments
        
        if ctype == 'keycode':
            model.set(iter, 0, int(new_text))
            model.get_value(iter, 7)['keycode'] = int(new_text)
        elif ctype == 'state':
            try:
                state = button_press_state_reverse[new_text]
            except:
                state = 0
                new_text = 'Release'
            model.set(iter, 1, new_text)
            model.get_value(iter, 7)['mapping'] = state
        elif ctype == 'service':
            model.set(iter, 2, new_text)
            model.get_value(iter, 7)['service'] = new_text
        elif ctype == 'object':
            model.set(iter, 3, new_text)
            model.get_value(iter, 7)['object'] = new_text
        elif ctype == 'interface':
            model.set(iter, 4, new_text)
            model.get_value(iter, 7)['interface'] = new_text
        elif ctype == 'method':
            model.set(iter, 5, new_text)
            model.get_value(iter, 7)['method'] = new_text
        elif ctype == 'arguments':
            model.set(iter, 6, new_text)
            model.get_value(iter, 7)['arguments'] = object
        self.emit('changed')

    def _treeview_init_changed(self, cellrenderer, treepath,*args):
        if len(args) == 2:
            new_text = args[0]
            ctype = args[1]
        elif len(args) == 3:
            new_text = args[0]
            object = args[1]
            ctype = args[2]
        tv = self.treeview_init
        model = tv.get_model()
        iter = model.get_iter(treepath)
        # TODO: Handle arguments    
        if ctype == 'service':
            model.set(iter, 0, new_text)
            model.get_value(iter, 7)['service'] = new_text
        elif ctype == 'object':
            model.set(iter, 1, new_text)
            model.get_value(iter, 7)['object'] = new_text
        elif ctype == 'interface':
            model.set(iter, 2, new_text)
            model.get_value(iter, 7)['interface'] = new_text
        elif ctype == 'method':
            model.set(iter, 3, new_text)
            model.get_value(iter, 7)['method'] = new_text
        elif ctype == 'arguments':
            model.set(iter, 4, new_text)
            model.get_value(iter, 5)['arguments'] = args[0]
        self.emit('changed')
    
    def _treeview_destruct_changed(self, cellrenderer, treepath, *args):
        if len(args) == 2:
            new_text = args[0]
            ctype = args[1]
        elif len(args) == 3:
            new_text = args[0]
            object = args[1]
            ctype = args[2]
        tv = self.treeview_destruct
        model = tv.get_model()
        iter = model.get_iter(treepath)
        # TODO: Handle arguments    
        if ctype == 'service':
            model.set(iter, 0, new_text)
            model.get_value(iter, 7)['service'] = new_text
        elif ctype == 'object':
            model.set(iter, 1, new_text)
            model.get_value(iter, 7)['object'] = new_text
        elif ctype == 'interface':
            model.set(iter, 2, new_text)
            model.get_value(iter, 7)['interface'] = new_text
        elif ctype == 'method':
            model.set(iter, 3, new_text)
            model.get_value(iter, 7)['method'] = new_text
        elif ctype == 'arguments':
            model.set(iter, 4, new_text)
            model.get_value(iter, 5)['arguments'] = args[0]
        self.emit('changed')

    def on_addbutton_init_clicked(self, object):
        model = self.treeview_init.get_model()

        map = {'service': 'service', 'object': 'object', 'interface': 'interface', 'method':'method'}
        
        if not 'init' in self.section:
            self.section['init'] = []
        
        self.section['init'].append(map)
        
        iter = model.append([
            map['service'],
            map['object'],
            map['interface'],
            map['method'],
            "",
            map
        ])
        self.treeview_init.set_cursor(model.get_path(iter))
        self.emit("changed")
        pass
    
    def on_addbutton_destruct_clicked(self, object):
        model = self.treeview_destruct.get_model()

        map = {'service': 'service', 'object': 'object', 'interface': 'interface', 'method':'method'}
        
        if not 'destruct' in self.section:
            self.section['destruct'] = []
        
        self.section['destruct'].append(map)
        
        iter = model.append([
            map['service'],
            map['object'],
            map['interface'],
            map['method'],
            "",
            map
        ])
        self.treeview_destruct.set_cursor(model.get_path(iter))
        self.emit("changed")

    def on_addbutton_clicked(self, object):
        model = self.treeview.get_model()

        map = {'keycode': 0, 'mapping': 0, 'service': 'service', 'object': 'object', 'interface': 'interface', 'method':'method'}
        
        if not 'actions' in self.section:
            self.section['actions'] = []
        
        self.section['actions'].append(map)
        
        iter = model.append([
            map['keycode'], 
            button_press_state[map['mapping']], 
            map['service'],
            map['object'],
            map['interface'],
            map['method'],
            "",
            map
        ])
        self.treeview.set_cursor(model.get_path(iter))
        self.emit("changed")

    def on_removebutton_init_clicked(self, object):
        model = self.treeview_init.get_model()
        (path, column) = self.treeview_init.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 5)
        self.section['init'].remove(entry)
        model.remove(iter)
        self.emit("changed")
    
    def on_removebutton_destruct_clicked(self, object):
        model = self.treeview_destruct.get_model()
        (path, column) = self.treeview_destruct.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 5)
        self.section['destruct'].remove(entry)
        model.remove(iter)
        self.emit("changed")        
        
    def on_removebutton_clicked(self, object):
        model = self.treeview.get_model()
        (path, column) = self.treeview.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 7)
        self.section['actions'].remove(entry)
        model.remove(iter)
        self.emit("changed")
    
class CommandExecutorEditor(ConfigWindowWidget):
    """
    Widget for configuration of CommandExecutor
    
    @signal: changed
        This signal is fired, when the config data of this modules was changed in here
    """
    title = _("CommandExecutor")
    config_section = 'CommandExecutor'
    
    def __init__(self, config):
        ConfigWindowWidget.__init__(self, config)
 
        #======================
         
        expander = gtk.Expander(_("On Initialisation"))
        expander.set_expanded(False)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        self.addbutton_init = addbutton = gtk.Button(stock="gtk-add")
        self.removebutton_init = removebutton = gtk.Button(stock="gtk-remove")
        addbutton.connect("clicked", self.on_addbutton_init_clicked)
        removebutton.connect("clicked", self.on_removebutton_init_clicked)
        
        self.treeview_init = treeview = gtk.TreeView()
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_init_changed, "command")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            0, 
            _("Command"), 
            textrenderer, 
            text=0
        )
        
        textrenderer = CellCommandArgumentsRenderer()
        textrenderer.connect("edited", self._treeview_init_changed, "arguments")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            1, 
            _("Arguments"), 
            textrenderer,
            text=1,
            backupdata=2
        )        
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=False, fill=False, padding=0)
        
        #======================
        
        expander = gtk.Expander(_("Actions"))
        expander.set_expanded(True)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
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
            _("Keycode"), 
            textrenderer, 
            text=0
        )

        comborenderer = gtk.CellRendererCombo()
        comborenderer.connect("edited", self._treeview_changed, "state")
        comborenderer.set_property("model", button_press_model)
        comborenderer.set_property("text-column", 0)
        comborenderer.set_property("editable", True)
        comborenderer.set_property("has-entry", False)
        treeview.insert_column_with_attributes(
            1, 
            _("State"), 
                comborenderer,
                text=1
            )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "command")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            2, 
            _("Command"), 
            textrenderer, 
            text=2
        )
        
        textrenderer = CellCommandArgumentsRenderer()
        textrenderer.connect("edited", self._treeview_changed, "arguments")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            3, 
            _("Command"), 
            textrenderer,
            text=3,
            backupdata=4
        )        
        
        treeview.get_column(0).set_resizable(True)
        treeview.get_column(0).set_sort_column_id(0)
        treeview.get_column(1).set_resizable(True)
        treeview.get_column(1).set_sort_column_id(1)
        treeview.get_column(2).set_resizable(True)
        treeview.get_column(2).set_sort_column_id(2)
        treeview.get_column(3).set_resizable(True)
        treeview.get_column(3).set_sort_column_id(3)
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=True, fill=True, padding=0)

        #======================
         
        expander = gtk.Expander(_("On Destruction"))
        expander.set_expanded(False)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        self.addbutton_destruct = addbutton = gtk.Button(stock="gtk-add")
        self.removebutton_destruct = removebutton = gtk.Button(stock="gtk-remove")
        addbutton.connect("clicked", self.on_addbutton_destruct_clicked)
        removebutton.connect("clicked", self.on_removebutton_destruct_clicked)
        
        self.treeview_destruct = treeview = gtk.TreeView()
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_destruct_changed, "command")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            0, 
            _("Command"), 
            textrenderer, 
            text=0
        )
        
        textrenderer = CellCommandArgumentsRenderer()
        textrenderer.connect("edited", self._treeview_destruct_changed, "arguments")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            1, 
            _("Arguments"), 
            textrenderer,
            text=1,
            backupdata=2
        )
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=False, fill=False, padding=0)
        
        #======================

        self.show_all()
        
    def update_view(self):
        mylist = gtk.ListStore(str, str, gobject.TYPE_PYOBJECT)

        if self.editable:
            self.addbutton_init.set_sensitive(True)
            self.removebutton_init.set_sensitive(True)
            self.treeview_init.set_sensitive(True)
        else:
            self.addbutton_init.set_sensitive(False)
            self.removebutton_init.set_sensitive(False)
            self.treeview_init.set_sensitive(False)
    
        try:
            for map in self.section['init']:
                args = ''
                if 'arguments' in map:
                    args = ", ".join(map['arguments'])
                mylist.append([map['command'], args, map])
        except KeyError: pass
        except TypeError: pass

        self.treeview_init.set_model(mylist)
 
        mylist = gtk.ListStore(int, str, str, str, gobject.TYPE_PYOBJECT)

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
                args = ''
                if 'arguments' in map:
                    args = ", ".join(map['arguments'])
                try:
                    mapping = button_press_state[int(map['mapping'])]
                except:
                    mapping = button_press_state[0]
                mylist.append([int(map['keycode']),
                               mapping,
                               map['command'],
                               args,
                               map])
        except KeyError: pass
        except TypeError: pass

        self.treeview.set_model(mylist)
        
        mylist = gtk.ListStore(str, str, str, str, str, gobject.TYPE_PYOBJECT)

        if self.editable:
            self.addbutton_destruct.set_sensitive(True)
            self.removebutton_destruct.set_sensitive(True)
            self.treeview_destruct.set_sensitive(True)
        else:
            self.addbutton_destruct.set_sensitive(False)
            self.removebutton_destruct.set_sensitive(False)
            self.treeview_destruct.set_sensitive(False)
    
        try:
            for map in self.section['destruct']:
                args = ''
                if 'arguments' in map:
                    args = ", ".join(map['arguments'])
                mylist.append([map['command'], args, map])
        except KeyError: pass
        except TypeError: pass

        self.treeview_destruct.set_model(mylist)     
        
    def _treeview_changed(self, cellrenderer, treepath, *args):
        if len(args) == 2:
            new_text = args[0]
            ctype = args[1]
        elif len(args) == 3:
            new_text = args[0]
            object = args[1]
            ctype = args[2]
        tv = self.treeview
        model = tv.get_model()
        iter = model.get_iter(treepath)
        
        if ctype == 'keycode':
            model.set(iter, 0, int(new_text))
            model.get_value(iter, 4)['keycode'] = int(new_text)
        elif ctype == 'state':
            try:
                state = button_press_state_reverse[new_text]
            except:
                state = 0
                new_text = 'Release'
            model.set(iter, 1, new_text)
            model.get_value(iter, 4)['mapping'] = state
        elif ctype == 'command':
            model.set(iter, 2, new_text)
            model.get_value(iter, 4)['command'] = new_text
        elif ctype == 'arguments':
            model.set(iter, 3, new_text)
            model.get_value(iter, 4)['arguments'] = object
        self.emit('changed')

    def _treeview_init_changed(self, cellrenderer, treepath,*args):
        if len(args) == 2:
            new_text = args[0]
            ctype = args[1]
        elif len(args) == 3:
            new_text = args[0]
            object = args[1]
            ctype = args[2]
        tv = self.treeview_init
        model = tv.get_model()
        iter = model.get_iter(treepath)    
        if ctype == 'command':
            model.set(iter, 0, new_text)
            model.get_value(iter, 2)['command'] = new_text
        elif ctype == 'arguments':
            model.set(iter, 1, new_text)
            model.get_value(iter, 2)['arguments'] = args[0]
        self.emit('changed')
    
    def _treeview_destruct_changed(self, cellrenderer, treepath, *args):
        if len(args) == 2:
            new_text = args[0]
            ctype = args[1]
        elif len(args) == 3:
            new_text = args[0]
            object = args[1]
            ctype = args[2]
        tv = self.treeview_destruct
        model = tv.get_model()
        iter = model.get_iter(treepath)   
        if ctype == 'command':
            model.set(iter, 0, new_text)
            model.get_value(iter, 2)['service'] = new_text
        elif ctype == 'arguments':
            model.set(iter, 1, new_text)
            model.get_value(iter, 2)['arguments'] = args[0]
        self.emit('changed')

    def on_addbutton_init_clicked(self, object):
        model = self.treeview_init.get_model()

        map = {'command': 'command'}
        
        if not 'init' in self.section:
            self.section['init'] = []
        
        self.section['init'].append(map)
        
        iter = model.append([map['command'], "", map])
        self.treeview_init.set_cursor(model.get_path(iter))
        self.emit("changed")
        pass
    
    def on_addbutton_destruct_clicked(self, object):
        model = self.treeview_destruct.get_model()

        map = {'command':'command'}
        
        if not 'destruct' in self.section:
            self.section['destruct'] = []
        
        self.section['destruct'].append(map)
        
        iter = model.append([map['command'], "", map])
        self.treeview_destruct.set_cursor(model.get_path(iter))
        self.emit("changed")

    def on_addbutton_clicked(self, object):
        model = self.treeview.get_model()

        map = {'keycode': 0, 'mapping': 0, 'command': 'command'}
        
        if not 'actions' in self.section:
            self.section['actions'] = []
        
        self.section['actions'].append(map)
        
        iter = model.append([
            map['keycode'], 
            button_press_state[map['mapping']], 
            map['command'],
            "",
            map
        ])
        self.treeview.set_cursor(model.get_path(iter))
        self.emit("changed")
        
    def on_removebutton_init_clicked(self, object):
        model = self.treeview_init.get_model()
        (path, column) = self.treeview_init.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 2)
        self.section['init'].remove(entry)
        model.remove(iter)
        self.emit("changed")
    
    def on_removebutton_destruct_clicked(self, object):
        model = self.treeview_destruct.get_model()
        (path, column) = self.treeview_destruct.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 2)
        self.section['destruct'].remove(entry)
        model.remove(iter)
        self.emit("changed")        
        
    def on_removebutton_clicked(self, object):
        model = self.treeview.get_model()
        (path, column) = self.treeview.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 4)
        self.section['actions'].remove(entry)
        model.remove(iter)
        self.emit("changed")
    


class MPlayerEditor(ConfigWindowWidget):
    """
    Widget for configuration of MPlayer
    
    @signal: changed
        This signal is fired, when the config data of this modules was changed in here
    """
    title = _("MPlayer")
    config_section = 'MPlayer'
    
    def __init__(self, config):
        ConfigWindowWidget.__init__(self, config)
 
        #======================
         
        expander = gtk.Expander(_("On Initialisation"))
        expander.set_expanded(False)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        self.addbutton_init = addbutton = gtk.Button(stock="gtk-add")
        self.removebutton_init = removebutton = gtk.Button(stock="gtk-remove")
        addbutton.connect("clicked", self.on_addbutton_init_clicked)
        removebutton.connect("clicked", self.on_removebutton_init_clicked)
        
        self.treeview_init = treeview = gtk.TreeView()
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_init_changed, "command")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            0, 
            _("Command"), 
            textrenderer, 
            text=0
        )
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=False, fill=False, padding=0)
        
        #======================
        
        expander = gtk.Expander(_("Actions"))
        expander.set_expanded(True)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
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
            _("Keycode"), 
            textrenderer, 
            text=0
        )

        comborenderer = gtk.CellRendererCombo()
        comborenderer.connect("edited", self._treeview_changed, "state")
        comborenderer.set_property("model", button_press_model)
        comborenderer.set_property("text-column", 0)
        comborenderer.set_property("editable", True)
        comborenderer.set_property("has-entry", False)
        treeview.insert_column_with_attributes(
            1, 
            _("State"), 
                comborenderer,
                text=1
            )
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_changed, "command")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            2, 
            _("Command"), 
            textrenderer, 
            text=2
        )
        
        treeview.get_column(0).set_resizable(True)
        treeview.get_column(0).set_sort_column_id(0)
        treeview.get_column(1).set_resizable(True)
        treeview.get_column(1).set_sort_column_id(1)
        treeview.get_column(2).set_resizable(True)
        treeview.get_column(2).set_sort_column_id(2)
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=True, fill=True, padding=0)

        #======================
         
        expander = gtk.Expander(_("On Destruction"))
        expander.set_expanded(False)
        expander.connect("activate", self.on_expander_activate)
        
        vbox = gtk.VBox()
        
        hbuttonbox = gtk.HButtonBox()
        hbuttonbox.set_layout(gtk.BUTTONBOX_START)
        self.addbutton_destruct = addbutton = gtk.Button(stock="gtk-add")
        self.removebutton_destruct = removebutton = gtk.Button(stock="gtk-remove")
        addbutton.connect("clicked", self.on_addbutton_destruct_clicked)
        removebutton.connect("clicked", self.on_removebutton_destruct_clicked)
        
        self.treeview_destruct = treeview = gtk.TreeView()
        
        textrenderer = gtk.CellRendererText()
        textrenderer.connect("edited", self._treeview_destruct_changed, "command")
        textrenderer.set_property("editable", True)
        treeview.insert_column_with_attributes(
            0, 
            _("Command"), 
            textrenderer, 
            text=0
        )
        
        hbuttonbox.add(addbutton)
        hbuttonbox.add(removebutton)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(treeview)
        
        vbox.pack_start(hbuttonbox, expand=False, fill=True, padding=0)
        vbox.pack_start(scrolled, expand=True, fill=True, padding=0)
        expander.add(vbox)
        self.pack_start(expander, expand=False, fill=False, padding=0)
        
        #======================
        
        self.show_all()

    def update_view(self):
        mylist = gtk.ListStore(str, gobject.TYPE_PYOBJECT)

        if self.editable:
            self.addbutton_init.set_sensitive(True)
            self.removebutton_init.set_sensitive(True)
            self.treeview_init.set_sensitive(True)
        else:
            self.addbutton_init.set_sensitive(False)
            self.removebutton_init.set_sensitive(False)
            self.treeview_init.set_sensitive(False)
    
        try:
            for map in self.section['init']:
                mylist.append([map['command'], map])
        except KeyError: pass
        except TypeError: pass

        self.treeview_init.set_model(mylist)
 
        mylist = gtk.ListStore(int, str, str, gobject.TYPE_PYOBJECT)

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
                try:
                    mapping = button_press_state[int(map['mapping'])]
                except:
                    mapping = button_press_state[0]
                mylist.append([int(map['keycode']), mapping, map['command'], map])
        except KeyError: pass
        except TypeError: pass

        self.treeview.set_model(mylist)
        
        mylist = gtk.ListStore(str, gobject.TYPE_PYOBJECT)

        if self.editable:
            self.addbutton_destruct.set_sensitive(True)
            self.removebutton_destruct.set_sensitive(True)
            self.treeview_destruct.set_sensitive(True)
        else:
            self.addbutton_destruct.set_sensitive(False)
            self.removebutton_destruct.set_sensitive(False)
            self.treeview_destruct.set_sensitive(False)
    
        try:
            for map in self.section['destruct']:
                mylist.append([map['command'], map ])
        except KeyError: pass
        except TypeError: pass

        self.treeview_destruct.set_model(mylist)     
        
    def _treeview_changed(self, cellrenderer, treepath, new_text, ctype):
        tv = self.treeview
        model = tv.get_model()
        iter = model.get_iter(treepath)
        
        if ctype == 'keycode':
            model.set(iter, 0, int(new_text))
            model.get_value(iter, 3)['keycode'] = int(new_text)
        elif ctype == 'state':
            try:
                state = button_press_state_reverse[new_text]
            except:
                state = 0
                new_text = 'Release'
            model.set(iter, 1, new_text)
            model.get_value(iter, 3)['mapping'] = state
        elif ctype == 'command':
            model.set(iter, 2, new_text)
            model.get_value(iter, 3)['command'] = new_text
            
        self.emit('changed')

    def _treeview_init_changed(self, cellrenderer, treepath, new_text, ctype):
        tv = self.treeview_init
        model = tv.get_model()
        iter = model.get_iter(treepath)

        if ctype == 'command':
            model.set(iter, 0, new_text)
            model.get_value(iter, 1)['command'] = new_text

        self.emit('changed')
    
    def _treeview_destruct_changed(self, cellrenderer, treepath, new_text, ctype):
        tv = self.treeview_destruct
        model = tv.get_model()
        iter = model.get_iter(treepath)
 
        if ctype == 'command':
            model.set(iter, 0, new_text)
            model.get_value(iter, 1)['service'] = new_text

        self.emit('changed')

    def on_addbutton_init_clicked(self, object):
        model = self.treeview_init.get_model()

        map = {'command': 'New command'}
        
        if not 'init' in self.section:
            self.section['init'] = []
        
        self.section['init'].append(map)
        
        iter = model.append([map['command'], map])
        self.treeview_init.set_cursor(model.get_path(iter))
        self.emit("changed")
    
    def on_addbutton_destruct_clicked(self, object):
        model = self.treeview_destruct.get_model()

        map = {'command': 'New command'}
        
        if not 'destruct' in self.section:
            self.section['destruct'] = []
        
        self.section['destruct'].append(map)
        
        iter = model.append([map['command'], map])
        self.treeview_destruct.set_cursor(model.get_path(iter))
        self.emit("changed")

    def on_addbutton_clicked(self, object):
        model = self.treeview.get_model()

        map = {'keycode': 0, 'mapping': 0, 'command': 'New command'}
        
        if not 'actions' in self.section:
            self.section['actions'] = []
        
        self.section['actions'].append(map)
        
        iter = model.append([map['keycode'], button_press_state[map['mapping']], map['command'], map])
        self.treeview.set_cursor(model.get_path(iter))
        self.emit("changed")

    def on_removebutton_init_clicked(self, object):
        model = self.treeview_init.get_model()
        (path, column) = self.treeview_init.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 1)
        self.section['init'].remove(entry)
        model.remove(iter)
        self.emit("changed")
    
    def on_removebutton_destruct_clicked(self, object):
        model = self.treeview_destruct.get_model()
        (path, column) = self.treeview_destruct.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 1)
        self.section['destruct'].remove(entry)
        model.remove(iter)
        self.emit("changed")        
        
    def on_removebutton_clicked(self, object):
        model = self.treeview.get_model()
        (path, column) = self.treeview.get_cursor()
        if not path: return
        iter = model.get_iter(path)
        entry = model.get_value(iter, 3)
        self.section['actions'].remove(entry)
        model.remove(iter)
        self.emit("changed")
    
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
        
        self.config_applets = []
        
        renderer = gtk.CellRendererText()
        renderer.set_property("ellipsize", pango.ELLIPSIZE_END)
        self.widget("profile-combobox").clear()
        self.widget("profile-combobox").pack_start(renderer)
        self.widget("profile-combobox").add_attribute(renderer, "text", 0)
        
        for i in (KeyMouseEditor, DBusCallerEditor, MPlayerEditor, CommandExecutorEditor):
            applet = i(self.config)
            applet.connect("changed", self._change_handler)
            applet.set_noprofile()
            self.config_applets.append(applet)
            self.widget("config_notebook").append_page(applet, gtk.Label(applet.title))
            
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

        #if select_last_item:
        #    # walk through profile_model 
        #    iter = profile_model.get_iter_first()
        #    while profile_model.iter_next(iter):
        #        iter = profile_model.iter_next(iter)
        #    profile.set_active_iter(iter)
        #else:
        #    profile.set_active(last_active)

    def _create_new_profile(self, profile_name, base_profile, base_config):
        keys = self.user_profiles.keys() + self.system_profiles.keys()
        if keys and profile_name.lower() in map(str.lower, keys):
            #profile already exists
            print "Profile already exists"
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
        self._fill_profiles()
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
        iter = combobox.get_active_iter()
        (profileid, config) = combobox.get_model().get(iter, 1, 2)
        if config == 'user':
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
        input_window = InputWindow(query=_("New Name"),
                                   title=_("What is the name for the new profile?"), 
                                   parent = self.widget("config-window"))
        input_window.set_curr_profiles(self.widget("profile-combobox").get_model())
        input_window.set_curr_profile_selection(True)
        responce = input_window.run()
        if responce == gtk.RESPONSE_ACCEPT:
            text = input_window.get_text().strip()
            if len(text) > 0:
                (profile, config) = input_window.get_curr_profile()
                self._create_new_profile(text, profile, config)
                #self._fill_profiles(select_last_item=True)
        input_window.destroy()



    def on_profile_rename_button_clicked(self, object):        
        input_window = InputWindow(query=_("New Name"),
                                   title=_("Specify the new name for the new profile"), 
                                   parent = self.widget("config-window"))
        responce = input_window.run()
        if responce == gtk.RESPONSE_ACCEPT:
            text = input_window.get_text().strip()
            iter = self.widget("profile-combobox").get_active_iter()
            if len(text) > 0 and not text in self.user_profiles and iter:
                # TODO: Handle rename with name clash
                model = self.widget("profile-combobox").get_model()
                data = model.get(iter,1,2)       
                if data[1] == "user":
                    model.set(iter, 0, text, 1, text)
                    self.user_profiles[text] = self.user_profiles[data[0]]
                    del(self.user_profiles[data[0]])
                    self.modified = True
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

if __name__ == "__main__":
    p = ConfigWindow()
    p.widget("config-window").connect_after('destroy',lambda x: gtk.main_quit() )
    gtk.main()
