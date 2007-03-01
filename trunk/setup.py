#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import glob
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

setup(name='LBRC',
      description = 'Linux Bluetooth Remote Control',
      version='0.4',
      author = 'Matthias Bläsing',
      author_email = 'matthias.blaesing@rwth-aachen.de',
      url = 'http://lbrc.berlios.de/',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['remotecontrol', 'bluetooth', 'j2me'],
      packages=['LBRC'],
      scripts=['LBRCdbus.py', 'LBRCgui'],
      data_files=[('/usr/share/lbrc', ['profiles.conf', 'LBRC.svg']),
                  ('/usr/share/dbus-1/services', ['LBRCdbus.service']),
                  ('/usr/share/doc/python-lbrc', doc),
                  ('/usr/share/doc/python-lbrc/includes', idoc),
                  ('/usr/share/doc/python-lbrc/mappings', mdoc),
                  ],
      )

