import sys
import os.path as osp

scriptpath = osp.dirname(osp.abspath(sys.argv[0]))

def get_configfile(name):
    if scriptpath.startswith('/usr/bin'):
        return osp.join(osp.expanduser("~"), ".lbrc", name)
    else:
        return osp.join(scriptpath, name)

def get_datafiles(name):
    paths = []
    dataprefix = []
    dataprefix.append('/usr/share/lbrc/')
    dataprefix.append(osp.expanduser("~/.lbrc/"))
    if not scriptpath.startswith('/usr/bin'):
        dataprefix[1] = scriptpath
    for dp in dataprefix:
        f = osp.join(dp, name)
        if osp.isfile(f):
            paths.append(f)
    return paths

def get_binfile(name):
    if scriptpath.startswith('/usr/bin'):
        return osp.join('/usr/bin/', name)
    else:
        return osp.join(scriptpath, name)

__all__ = ["dbusinterface", "BTServer", "UinputDispatcher"]
