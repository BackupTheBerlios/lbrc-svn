#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import glob
import os
import os.path as osp
from distutils.core import setup

# patch distutils if it can't cope with the "classifiers" or "download_url"
# keywords (prior to python 2.3.0).
from distutils.dist import DistributionMetadata
if not hasattr(DistributionMetadata, 'classifiers'):
    DistributionMetadata.classifiers = None
if not hasattr(DistributionMetadata, 'download_url'):
    DistributionMetadata.download_url = None

doc = []
for afile in glob.glob('doc/*'):
    if osp.isfile(afile):
        doc.append(afile)
idoc = []
for afile in glob.glob('doc/includes/*'):
    if osp.isfile(afile):
        idoc.append(afile)
mdoc = []
for afile in glob.glob('doc/mappings/*'):
    if osp.isfile(afile):
        mdoc.append(afile)

data_files = []
data_files.append(('share/lbrc', ['profiles.conf', 
                                       'LBRC.svg',
                                       'LBRC_gtk_gui/config.glade',
                                       'LBRC_gtk_gui/keymouseeditwindow.glade',
                                       ]
                 ))
data_files.append(('share/dbus-1/services', ['LBRCdbus.service']))
data_files.append(('share/doc/python-lbrc', doc))
data_files.append(('share/doc/python-lbrc/includes', idoc))
data_files.append(('share/doc/python-lbrc/mappings', mdoc))
data_files.append(('share/lbrc/j2me/', ['j2me/bin/LBRC.jar', 'j2me/bin/LBRC.jad']))
for (path, dirs, files) in os.walk("pot"):
    if "LBRC.mo" in files:
        target = path.replace("pot", "share/locale", 1)
        data_files.append((target, [osp.join(path, "LBRC.mo")]))

setup(name='LBRC',
      description = 'Linux Bluetooth Remote Control',
      version='0.4',
      author = 'Matthias Blaesing',
      author_email = 'matthias.blaesing@rwth-aachen.de',
      url = 'http://lbrc.berlios.de/',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['remotecontrol', 'bluetooth', 'j2me'],
      packages=['LBRC', 'LBRC_gtk_gui'],
      scripts=['LBRCdbus.py', 'LBRC-applet'],
      data_files=data_files
      )

