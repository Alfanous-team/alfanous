# Portions Copyright (c) 2005 Nokia Corporation 
import sys

__all__ = ["O_NDELAY", "O_DSYNC", "O_RSYNC", "O_DIRECT", "O_LARGEFILE",
           "O_NOFOLLOW", "sep", "readlink", "name", "path"]
           
def _get_exports_list(module):
    try:
        return list(module.__all__)
    except AttributeError:
        return [n for n in dir(module) if n[0] != '_']

from e32posix import *

O_NDELAY    =   O_NONBLOCK
O_DSYNC     =   O_SYNC
O_RSYNC     =   O_SYNC
O_DIRECT    =    16384
O_LARGEFILE =    32768
O_NOFOLLOW  =   131072

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

import ntpath
path = ntpath
del ntpath

import e32posix
__all__.extend([n for n in dir(e32posix) if n[0] != '_'])
del e32posix

name = 'e32'
sep = '\\'
extsep = '.'

sys.modules['os.path'] = path

environ = {}

def readlink(path):
        return path

def utime(path, timetuple):
        pass

def makedirs(name, mode=0777):
    head, tail = path.split(name)
    if not tail:
        head, tail = path.split(head)
    if head and tail and not path.exists(head):
        makedirs(head, mode)
    mkdir(name, mode)

def removedirs(name):
    rmdir(name)
    head, tail = path.split(name)
    if not tail:
        head, tail = path.split(head)
    while head and tail:
        try:
            rmdir(head)
        except error:
            break
        head, tail = path.split(head)

def renames(old, new):
    head, tail = path.split(new)
    if head and tail and not path.exists(head):
        makedirs(head)
    rename(old, new)
    head, tail = path.split(old)
    if head and tail:
        try:
            removedirs(head)
        except error:
            pass
