import os
import gettext

from LBRC.path import path

localedir = path().get_localedir()

gettext.bindtextdomain("LBRC", localedir)
gettext.textdomain("LBRC")
lang = gettext.translation("LBRC", localedir, fallback = True)

def init_glade_gettext():
    # setting locales of glade (if we have glade)
    try:
        import gtk.glade
        gtk.glade.bindtextdomain("LBRC", localedir)
        gtk.glade.textdomain("LBRC")
    except ImportError, e:
        pass

# Bind "_" as marker for the translation of texts. We bind to ugettext, as
# our gui toolkit (gtk2) expects utf-8 strings and the output routines should
# break it down correctly
_ = lang.ugettext
