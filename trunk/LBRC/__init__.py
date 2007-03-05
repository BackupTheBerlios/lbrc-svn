import sys
import os.path as osp

scriptpath = osp.dirname(osp.abspath(sys.argv[0]))

def get_localedir():
    """
    Return path to directory, where out l10n files
    are located.

    @return:    path to locale dir
    @rtype:     string
    """
    if scriptpath.startswith('/usr/bin'):
        return "/usr/share/locale"
    else:
        return osp.join(scriptpath, "pot")

def get_configfile(name):
    """
    Returns absolute path to configfile, with C{name} name

    @param  name:   name of configfile
    @type   name:   string
    @return:    path to configfile
    @rtype:     string
    """
    if scriptpath.startswith('/usr/bin'):
        return osp.join(osp.expanduser("~"), ".lbrc", name)
    else:
        return osp.join(scriptpath, name)

def get_datafiles(name):
    """
    Returns absolute path to datafiles, with C{name} name

    @param  name:   name of datafile
    @type   name:   string
    @return:    list of complete paths to datafiles
    @rtype:     list of strings
    """
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
    """
    Returns absolute path to executable, with C{name} name

    @param  name:   name of executable
    @type   name:   string
    @return:    path to executable
    @rtype:     string
    """

    if scriptpath.startswith('/usr/bin'):
        return osp.join('/usr/bin/', name)
    else:
        return osp.join(scriptpath, name)

__all__ = ["dbusinterface", "BTServer", "UinputDispatcher", "CommandExecutor", "get_binfile", "get_datafiles", "get_configfile", "get_localedir"]
