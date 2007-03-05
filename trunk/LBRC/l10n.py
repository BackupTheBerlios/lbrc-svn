import os
import gettext

from LBRC import get_localedir

gettext.bindtextdomain("LBRC", get_localedir())
gettext.textdomain("LBRC")
lang = gettext.translation("LBRC", get_localedir(), fallback = True)

# Bind "_" as marker for the translation of texts. We bind to ugettext, as
# our gui toolkit (gtk2) expects utf-8 strings and the output routines should
# break it down correctly
_ = lang.ugettext
