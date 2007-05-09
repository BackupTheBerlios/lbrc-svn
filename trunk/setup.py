#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import glob
import os
import os.path as osp
from subprocess import call
from distutils.core import setup
from distutils.command.build import build

def gen_locale():
    for file in glob.glob("pot/*.po"):
        lang = file[:-3]
        try:
            os.makedirs(osp.join(lang, 'LC_MESSAGES'), 0755)
        except OSError:
            pass
        call(['msgfmt', '-o', osp.join(lang, 'LC_MESSAGES', 'LBRC.mo'), file])

class custom_build(build):
    def run(self):
        call(["./build_dbus_uinput_bridge"])
        gen_locale()
        build.run(self)

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
                                       'LBRC_gtk_gui/config.glade'
                                       ]
                 ))
data_files.append(('share/dbus-1/services', ['LBRCdbus.service']))
data_files.append(('share/doc/python-lbrc', doc))
data_files.append(('share/doc/python-lbrc/includes', idoc))
data_files.append(('share/doc/python-lbrc/mappings', mdoc))
data_files.append(('share/lbrc/j2me/', ['j2me-build/LBRC.jar', 'j2me-build/LBRC.jad']))
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
      scripts=['LBRCdbus.py', 'LBRC-applet', 'uinputbridge'],
      cmdclass = {'build': custom_build},
      data_files=data_files
      )

